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


class DeploymentTemplateFileTest(unittest.TestCase):

    def test_deployment_rendering(self):
        docs = render_chart(
            values={},
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "Deployment")

    def test_should_overwrite_container_image(self):
        docs = render_chart(
            values={
                "global": {
                    "image": {
                        "repository": "test.image.repository",
                        "imagePullSecret": "test-image-pull-secret",
                        "pullPolicy": "Always",
                        "name": "testimage",
                        "tag": "1.0.0"
                    }
                }

            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            'test.image.repository/testimage:1.0.0',
            jmespath.search("spec.template.spec.containers[0].image", docs[0])
        )

        self.assertEqual(
            'Always',
            jmespath.search(
                "spec.template.spec.containers[0].imagePullPolicy", docs[0])
        )

        self.assertEqual(
            'test-image-pull-secret',
            jmespath.search(
                "spec.template.spec.imagePullSecrets[0].name", docs[0])
        )

        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.imagePullSecrets[0].command", docs[0])
        )

        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.imagePullSecrets[0].args", docs[0])
        )

    def test_should_overwrite_command_and_args(self):
        docs = render_chart(
            values={
                "global": {
                    "image": {
                        "command": ["test", "command"],
                        "args": ["arg1", "arg2"]
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            ['test', 'command'],
            jmespath.search(
                "spec.template.spec.containers[0].command", docs[0])
        )

        self.assertEqual(
            ['arg1', 'arg2'],
            jmespath.search("spec.template.spec.containers[0].args", docs[0])
        )

    def test_should_overwrite_replica_count(self):
        docs = render_chart(
            values={
                "global": {
                    "replicaCount": "10",
                    "autoscaling": {
                        "enabled": False
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            10,
            jmespath.search("spec.replicas", docs[0])
        )

    def test_should_remove_replicas_when_autoscaling_enabled(self):
        docs = render_chart(
            values={
                "global": {
                    "autoscaling": {
                        "enabled": True
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertIsNone(
            jmespath.search("spec.replicas", docs[0])
        )

    def test_should_overwrite_serviceaccount_name(self):
        docs = render_chart(
            values={
                "global": {
                    "serviceAccount": {
                        "create": True,
                        "name": "test-service-account",
                        "rules": [
                            {
                                "apiGroups": ["*"],
                                "resources": ["*"],
                                "verbs": ["read"]
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            "test-service-account",
            jmespath.search("spec.template.spec.serviceAccountName", docs[0])
        )

    def test_should_add_environment_variable_only_from_config_map(self):
        docs = render_chart(
            values={
                "global": {
                    "secEnvVarsEnabled": False,
                    "envVarsEnabled": True,
                    "envVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST",
                        "Variable1": "Value1",
                        "Variable2": "Value2"
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            "RELEASE-NAME-charts-dotnet-core",
            jmespath.search(
                "spec.template.spec.containers[0].envFrom[0].configMapRef.name", docs[0])
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].envFrom[0].secretRef", docs[0])
        )

    def test_should_add_environment_variable_only_from_secret(self):
        docs = render_chart(
            values={
                "global": {
                    "envVarsEnabled": False,
                    "secEnvVarsEnabled": True,
                    "secEnvVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST",
                        "Variable1": "Value1",
                        "Variable2": "Value2"
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            "RELEASE-NAME-charts-dotnet-core-secure",
            jmespath.search(
                "spec.template.spec.containers[0].envFrom[0].secretRef.name", docs[0])
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].envFrom[0].configMapRef", docs[0])
        )

    def test_should_not_add_envrionment_variables(self):
        docs = render_chart(
            values={
                "global": {
                    "envVarsEnabled": False,
                    "secEnvVarsEnabled": False,
                    "secEnvVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST",
                        "Variable1": "Value1",
                        "Variable2": "Value2"
                    },
                    "envVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST",
                        "Variable1": "Value1",
                        "Variable2": "Value2"
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].envFrom[0].configMapRef", docs[0])
        )

        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].envFrom[0].secretRef", docs[0])
        )

        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].envFrom", docs[0])
        )

    def test_should_overwrite_readiness_probe(self):
        docs = render_chart(
            values={
                "global": {
                    "image": {
                        "readinessProbe": {
                            "httpGet": {
                                "path": "/test/path",
                                "port": "443"
                            },
                            "periodSeconds": 42,
                            "initialDelaySeconds": 42,
                            "successThreshold": 42,
                            "timeoutSeconds": 42,
                            "failureThreshold": 42,
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            {
                "httpGet": {
                    "path": "/test/path",
                    "port": "443"
                },
                "periodSeconds": 42,
                "initialDelaySeconds": 42,
                "successThreshold": 42,
                "timeoutSeconds": 42,
                "failureThreshold": 42,
            },
            jmespath.search(
                "spec.template.spec.containers[0].readinessProbe", docs[0])
        )


    def test_should_overwrite_livenessProbe_probe(self):
        docs = render_chart(
            values={
                "global": {
                    "image": {
                        "livenessProbe": {
                            "httpGet": {
                                "path": "/test/path",
                                "port": "443"
                            },
                            "periodSeconds": 42,
                            "successThreshold": 42,
                            "failureThreshold": 42,
                            "timeoutSeconds": 42,
                            "initialDelaySeconds": 42
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            {
                "httpGet": {
                    "path": "/test/path",
                    "port": "443"
                },
                "initialDelaySeconds": 42,
                "periodSeconds": 42,
                "successThreshold": 42,
                "failureThreshold": 42,
                "timeoutSeconds": 42
            },
            jmespath.search(
                "spec.template.spec.containers[0].livenessProbe", docs[0])
        )

    def test_should_add_requests_and_limits_resources(self):
        docs = render_chart(
            values={
                "global": {
                    "resources": {
                        "requests": {
                            "cpu": "10m",
                            "memory": "10Mi"
                        },
                        "limits": {
                            "cpu": "1000m",
                            "memory": "1000Mi"
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            {
                "requests": {
                    "cpu": "10m",
                    "memory": "10Mi"
                },
                "limits": {
                    "cpu": "1000m",
                    "memory": "1000Mi"
                }
            },
            jmespath.search(
                "spec.template.spec.containers[0].resources", docs[0])
        )

    def test_should_add_only_requests(self):
        docs = render_chart(
            values={
                "global": {
                    "resources": {
                        "requests": {
                            "cpu": "10m",
                            "memory": "10Mi"
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            {
                "requests": {
                    "cpu": "10m",
                    "memory": "10Mi"
                }
            },
            jmespath.search(
                "spec.template.spec.containers[0].resources", docs[0])
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].resources.limits", docs[0])
        )

    def test_should_add_only_limits(self):
        docs = render_chart(
            values={
                "global": {
                    "resources": {
                        "limits": {
                            "cpu": "10m",
                            "memory": "10Mi"
                        }
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            {
                "limits": {
                    "cpu": "10m",
                    "memory": "10Mi"
                }
            },
            jmespath.search(
                "spec.template.spec.containers[0].resources", docs[0])
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].resources.requests", docs[0])
        )

    def test_should_not_add_volume_mounts(self):
        docs = render_chart(
            values={
                "global": {
                    "appConfigFilesEnabled": False,
                    "appConfigFiles": {
                        "globPattern": "**.json",
                        "dir": "/app/",
                        "filesList": []
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.containers[0].volumeMounts", docs[0])
        )
        self.assertIsNone(
            jmespath.search(
                "spec.template.spec.volumes", docs[0])
        )

    def test_should_create_json_file_and_add_volume(self):
        filename = get_random_json_file_name()
        create_test_json_file(filename)
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
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            "/app/" + filename,
            jmespath.search(
                "spec.template.spec.containers[0].volumeMounts[0].mountPath", docs[0])
        )

        self.assertEqual(
            filename,
            jmespath.search(
                "spec.template.spec.containers[0].volumeMounts[0].subPath", docs[0])
        )

        self.assertEqual(
            "configuration-volume",
            jmespath.search(
                "spec.template.spec.volumes[0].name", docs[0])
        )

        self.assertEqual(
            "RELEASE-NAME-charts-dotnet-core-files",
            jmespath.search(
                "spec.template.spec.volumes[0].secret.secretName", docs[0])
        )
        remove(filename)

    def test_should_overwrite_progressDeadlineSeconds(self):
        docs = render_chart(
            values={
                "global": {
                    "progressDeadlineSeconds": "120"
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            120,
            jmespath.search(
                "spec.progressDeadlineSeconds", docs[0])
        )

    def test_should_overwrite_revision_history_limit(self):
        docs = render_chart(
            values={
                "global": {
                    "revisionHistoryLimit": "7"
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            7,
            jmespath.search(
                "spec.revisionHistoryLimit", docs[0])
        )

    def test_should_overwrite_min_ready_seconds(self):
        docs = render_chart(
            values={
                "global": {
                    "minReadySeconds": "3"
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            3,
            jmespath.search(
                "spec.minReadySeconds", docs[0])
        )

    def test_should_add_aad_label(self):
        docs = render_chart(
            values={
                "global": {
                    "additionalLabelsEnabled": "true",
                    "additionalLabels": {
                        "aad_pod_id": "pod_label"
                    }
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )

        self.assertEqual(
            "pod_label",
            jmespath.search(
                "metadata.labels.aad_pod_id", docs[0])
        )

    def test_termination_grace_period_should_not_be_enabled(self):
        docs = render_chart(
            values={
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertIsNone(
            jmespath.search("spec.terminationGracePeriodSeconds", docs[0])
        )

    def test_termination_grace_period_is_overwritten(self):
        docs = render_chart(
            values={
                "global": {
                    "terminationGracePeriodSeconds": 500
                }
            },
            name=".",
            show_only=["templates/deployment.yaml"]
        )
        self.assertEqual(
            500,
            jmespath.search("spec.template.spec.terminationGracePeriodSeconds", docs[0])
        )