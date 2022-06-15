import unittest
from os import remove
from os import sep
from os.path import dirname, realpath
from shutil import copyfile
import json
import jmespath

from tests.helm_template_generator import render_chart

ROOT_FOLDER = realpath(dirname(realpath(__file__)) + "/..")


class ConfigMapTemplateFileTest(unittest.TestCase):

    def test_config_map_rendering(self):
        docs = render_chart(
            values={},
            name=".",
            show_only=["templates/environment-configmap.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "ConfigMap")

    def test_should_add_environment_variables_to_config_map(self):
        docs = render_chart(
            values={
                "global": {
                    "envVarsEnabled": True,
                    "envVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTESTS",
                        "CERTIFICATE": "PyTest"
                    }
                }
            },
            name=".",
            show_only=["templates/environment-configmap.yaml"]
        )

        self.assertEqual(
            {
                "ASPNETCORE_ENVIRONMENT": "UNITTESTS",
                "CERTIFICATE": "PyTest"
            },
            jmespath.search(
                "data", docs[0])
        )
