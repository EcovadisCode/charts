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


class ScaledObjectTemplateFileTest(unittest.TestCase):

    def test_deployment_rendering(self):
        docs = render_chart(
            values={},
            name=".",
            show_only=["templates/trigger-authentication.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "TriggerAuthentication")


    def test_triggers_should_be_set(self):
        docs = render_chart(
            values= {
                "global": {
                    "keda": {
                        "azure": {
                            "clientIdSecretName": "testsecret"
                        },
                        "triggers": {
                            "azureServiceBus": {
                                "connectionStringKeyVaultSecretName": "testkeyvaultsecret"
                            }
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/trigger-authentication.yaml"]
        )

        self.assertEqual(
            "testsecret",
            jmespath.search("spec.azureKeyVault.credentials.clientSecret.valueFrom.secretKeyRef.name", docs[0])
        )
        self.assertEqual(
            "testkeyvaultsecret",
            jmespath.search("spec.azureKeyVault.secrets[0].name", docs[0])
        )

    def test_should_render_with_pod_identity_when_only_mssql_trigger_configured(self):
        # Regression test: TriggerAuthentication must render (using pod identity)
        # even when azureServiceBus.triggers is empty/unset, since mssql triggers
        # share the same authenticationRef and rely on this resource existing.
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "triggers": {
                            "mssql": {
                                "triggers": [{
                                    "enabled": True,
                                    "host": "myserver.database.windows.net",
                                    "database": "mydb",
                                    "username": "myuser",
                                    "query": "SELECT 1",
                                    "targetValue": 1,
                                }]
                            }
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/trigger-authentication.yaml"]
        )

        self.assertEqual(1, len(docs))
        self.assertEqual("TriggerAuthentication", docs[0]["kind"])
        self.assertEqual(
            "azure-workload",
            jmespath.search("spec.podIdentity.provider", docs[0])
        )

