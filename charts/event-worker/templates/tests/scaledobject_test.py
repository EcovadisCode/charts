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
            show_only=["templates/scaled-object.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "ScaledObject")

    def test_should_overwrite_basic_values(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "pollingInterval": 1,
                        "cooldownPeriod": 2,
                        "initialCooldownPeriod": 3,
                        "minReplicaCount": 4,
                        "maxReplicaCount": 5
                    }
                }

            },
            name=".",
            show_only=["templates/scaled-object.yaml"]
        )

        self.assertEqual(
            1,
            jmespath.search("spec.pollingInterval", docs[0])
        )
        self.assertEqual(
            2,
            jmespath.search("spec.cooldownPeriod", docs[0])
        )
        self.assertEqual(
            3,
            jmespath.search("spec.initialCooldownPeriod", docs[0])
        )
        self.assertEqual(
            4,
            jmespath.search("spec.minReplicaCount", docs[0])
        )
        self.assertEqual(
            5,
            jmespath.search("spec.maxReplicaCount", docs[0])
        )

    def test_failback_should_be_half_of_max_replicas(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "maxReplicaCount": 7
                    }
                }

            },
            name=".",
            show_only=["templates/scaled-object.yaml"]
        )
        expected = 4
        got = jmespath.search("spec.fallback.replicas", docs[0])
        self.assertEqual(
            expected,
            got
        )

    def test_triggers_should_be_set(self):
        docs = render_chart(
            values= {
                "global": {
                    "keda": {
                        "triggers": {
                            "azureServiceBus": {
                                "connectionStringKeyVaultSecretName": "ConnectionStrings--ServiceBus",
                                "triggers": [{
                                    "enabled": True,
                                    "queueName": "testqueue",
                                    "topicName": "testtopic",
                                    "subscriptionName": "testsubscription",
                                    "messageCount": 99,
                                    "activationMessageCount": 23,
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/scaled-object.yaml"]
        )

        self.assertEqual(
            "testqueue",
            jmespath.search("spec.triggers[0].metadata.queueName", docs[0])
        )
        self.assertEqual(
            "testtopic",
            jmespath.search("spec.triggers[0].metadata.topicName", docs[0])
        )
        self.assertEqual(
            "testsubscription",
            jmespath.search("spec.triggers[0].metadata.subscriptionName", docs[0])
        )
        self.assertEqual(
            "99",
            jmespath.search("spec.triggers[0].metadata.messageCount", docs[0])
        )
        self.assertEqual(
            "23",
            jmespath.search("spec.triggers[0].metadata.activationMessageCount", docs[0])
        )
