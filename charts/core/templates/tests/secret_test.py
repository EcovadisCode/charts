import unittest
from os import remove
from os import sep
from os.path import dirname, realpath
from shutil import copyfile
import json
import jmespath

from tests.helm_template_generator import render_chart
from tests.helm_template_generator import get_random_json_file_name
from tests.helm_template_generator import create_test_json_file

ROOT_FOLDER = realpath(dirname(realpath(__file__)) + "/..")


class SecretTemplateFileTest(unittest.TestCase):

    def test_secret_rendering(self):
        docs = render_chart(
            values={},
            name=".",
            show_only=["templates/environment-secret.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "Secret")

    def test_should_add_environment_variables_to_config_map(self):
        docs = render_chart(
            values={
                "global": {
                    "secEnvVarsEnabled": True,
                    "secEnvVars": {
                        "secretKey": "secretValue",
                        "secretKey2": "secretValue2"
                    }
                }
            },
            name=".",
            show_only=["templates/environment-secret.yaml"]
        )

        self.assertEqual(
            {
                "secretKey": "c2VjcmV0VmFsdWU=",
                "secretKey2": "c2VjcmV0VmFsdWUy"
            },
            jmespath.search(
                "data", docs[0])
        )

