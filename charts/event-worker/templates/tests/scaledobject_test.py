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
                        "azure": {
                          "clientIdSecretKey": 'AzureIdentity__ClientSecret' 
                        },
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

    def test_mssql_trigger_should_be_set_with_discrete_params(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "triggers": {
                            "azureServiceBus": {
                                "triggers": []
                            },
                            "mssql": {
                                "triggers": [{
                                    "enabled": True,
                                    "host": "myserver.database.windows.net",
                                    "port": "1433",
                                    "database": "mydb",
                                    "username": "myuser",
                                    "query": "SELECT COUNT(*) FROM backlog WHERE state='running' OR state='queued'",
                                    "targetValue": 1,
                                    "activationTargetValue": 2,
                                }]
                            }
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/scaled-object.yaml"]
        )
        mssql_triggers = jmespath.search("spec.triggers[?type=='mssql']", docs[0])
        self.assertEqual(1, len(mssql_triggers))
        trigger = mssql_triggers[0]

        self.assertEqual(
            "myserver.database.windows.net",
            jmespath.search("metadata.host", trigger)
        )
        self.assertEqual(
            "1433",
            jmespath.search("metadata.port", trigger)
        )
        self.assertEqual(
            "mydb",
            jmespath.search("metadata.database", trigger)
        )
        self.assertEqual(
            "myuser",
            jmespath.search("metadata.username", trigger)
        )
        self.assertEqual(
            "SELECT COUNT(*) FROM backlog WHERE state='running' OR state='queued'",
            jmespath.search("metadata.query", trigger)
        )
        self.assertEqual(
            "1",
            jmespath.search("metadata.targetValue", trigger)
        )
        self.assertEqual(
            "2",
            jmespath.search("metadata.activationTargetValue", trigger)
        )
        # Compared case-insensitively: the release name casing rendered by Helm
        # differs between versions (3.x renders RELEASE-NAME, 4.x release-name).
        self.assertEqual(
            "release-name-charts-event-worker-servicebus",
            jmespath.search("authenticationRef.name", trigger).lower()
        )

    def test_mssql_trigger_port_should_default_to_1433(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "triggers": {
                            "azureServiceBus": {
                                "triggers": []
                            },
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
            show_only=["templates/scaled-object.yaml"]
        )

        self.assertEqual(
            "1433",
            jmespath.search("spec.triggers[?type=='mssql']|[0].metadata.port", docs[0])
        )

    def test_mssql_trigger_should_use_connection_string_from_env_when_provided(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "triggers": {
                            "azureServiceBus": {
                                "triggers": []
                            },
                            "mssql": {
                                "triggers": [{
                                    "enabled": True,
                                    "connectionStringFromEnv": "MSSQL_CONNECTION_STRING",
                                    "query": "SELECT 1",
                                    "targetValue": 1,
                                }]
                            }
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/scaled-object.yaml"]
        )
        mssql_trigger = jmespath.search("spec.triggers[?type=='mssql']|[0]", docs[0])

        self.assertEqual(
            "MSSQL_CONNECTION_STRING",
            jmespath.search("metadata.connectionStringFromEnv", mssql_trigger)
        )
        self.assertIsNone(
            jmespath.search("metadata.host", mssql_trigger)
        )

    def test_mssql_trigger_should_not_be_rendered_when_disabled(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "triggers": {
                            "mssql": {
                                "triggers": [{
                                    "enabled": False,
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
            show_only=["templates/scaled-object.yaml"]
        )

        self.assertEqual(
            [],
            jmespath.search("spec.triggers[?type=='mssql']", docs[0])
        )

    def test_mssql_and_servicebus_triggers_can_coexist(self):
        docs = render_chart(
            values={
                "global": {
                    "keda": {
                        "triggers": {
                            "azureServiceBus": {
                                "triggers": [{
                                    "enabled": True,
                                    "queueName": "testqueue",
                                }]
                            },
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
            show_only=["templates/scaled-object.yaml"]
        )

        types = jmespath.search("spec.triggers[*].type", docs[0])
        self.assertEqual(["azure-servicebus", "mssql"], types)
