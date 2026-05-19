import subprocess
import sys
from functools import lru_cache
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from typing import Any, Dict, Tuple

import jmespath
import os
import jsonschema
import requests
import yaml
import json
from kubernetes.client.api_client import ApiClient

api_client = ApiClient()

BASE_URL_SPEC = "https://raw.githubusercontent.com/instrumenta/kubernetes-json-schema/master/v1.18.0"


@lru_cache(maxsize=None)
def create_validator(api_version, kind):
    api_version = api_version.lower()
    kind = kind.lower()

    if '/' in api_version:
        ext, _, api_version = api_version.partition("/")
        ext = ext.split(".")[0]
        url = f'{BASE_URL_SPEC}/{kind}-{ext}-{api_version}.json'
    else:
        url = f'{BASE_URL_SPEC}/{kind}-{api_version}.json'
    request = requests.get(url)
    request.raise_for_status()
    schema = request.json()
    jsonschema.Draft7Validator.check_schema(schema)
    validator = jsonschema.Draft7Validator(schema)
    return validator


def validate_k8s_object(instance):
    chart = jmespath.search("metadata.labels.chart", instance)

    validate = create_validator(instance.get(
        "apiVersion"), instance.get("kind"))
    validate.validate(instance)


def render_chart(name=".", values=None, show_only=None, validate_schema=False):
    """
    Function that renders a helm chart into dictionaries. For helm chart testing only
    """
    values = values or {}
    with TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, f'values.yaml')
        command = ["helm", "template", name]
        with open(tmp_file, 'w') as fh:
            content = yaml.dump(values)
            fh.write(content)
            fh.flush()
            if values:
                command.extend(["-f", fh.name])
        if show_only:
            for i in show_only:
                command.extend(["--show-only", i])
        print(command)
        templates = subprocess.check_output(command)
        k8s_objects = yaml.full_load_all(templates)
        k8s_objects = [k8s_object for k8s_object in k8s_objects if k8s_object]
        return k8s_objects


def prepare_k8s_lookup_dict(k8s_objects) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Helper to create a lookup dict from k8s_objects.
    The keys of the dict are the k8s object's kind and name
    """
    k8s_obj_by_key = {
        (k8s_object["kind"], k8s_object["metadata"]["name"]): k8s_object for k8s_object in k8s_objects
    }
    return k8s_obj_by_key


def render_k8s_object(obj, type_to_render):
    """
    Function that renders dictionaries into k8s objects. For helm chart testing only.
    """
    return api_client._ApiClient__deserialize_model(obj, type_to_render)  # pylint: disable=W0212


def get_random_json_file_name():
     return NamedTemporaryFile().name.split(os.sep)[-1] + ".json"

def create_test_json_file( filename):
    appsettings_file_content={
        "settings": "test",
        "nestedsettings": {
            "settings": "nested"
        }
    }
    with open(filename, 'w') as fp:
        json.dump(appsettings_file_content, fp)
