import unittest
from os import remove
from os import sep
from os.path import dirname, realpath
from shutil import copyfile
import jmespath

from tests.helm_template_generator import render_chart
from tests.helm_template_generator import get_random_json_file_name
from tests.helm_template_generator import create_test_json_file
ROOT_FOLDER = realpath(dirname(realpath(__file__)) + "/..")


class SecretTemplateFileTest(unittest.TestCase):

    def test_files_added_when_glob_pattern_is_used(self):
        filename1 = get_random_json_file_name()
        filename2 = get_random_json_file_name()

        create_test_json_file(filename1)
        create_test_json_file(filename2)

        docs = render_chart(
            values={
                "global": {
                    "appConfigFilesEnabled": True,
                    "appConfigFiles": {
                        "globPattern": "**.json",
                        "dir": "/app/",
                        "filesList": []
                    }
                }
            },
            name=".",
            show_only=["templates/appsettings-secret.yaml"]
        )
        self.assertIsNotNone(docs[0]["stringData"][filename1], docs[0])
        self.assertIsNotNone(docs[0]["stringData"][filename2], docs[0])
        remove(filename1)
        remove(filename2)