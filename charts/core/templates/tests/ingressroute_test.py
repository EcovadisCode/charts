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


class IngressRouteTemplateFileTest(unittest.TestCase):

    def test_ingressroute_rendering(self):
        docs = render_chart(
            values={},
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertRegex(docs[0]["kind"], "IngressRoute")

    def test_ingressroute_with_middleware_rendering(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "stripPrefixes": [
                                    "/vadisservice"
                                ]
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "IngressRoute")
        self.assertRegex(docs[1]["kind"], "Middleware")

    def test_tls_is_enabled_by_default(self):
        docs = render_chart(
            values={},
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertIsNotNone(docs[0]["spec"]["tls"])

    def test_host_rule_and_middleware_created(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "stripPrefixes": [
                                    "/unittests"
                                ]
                            }
                        ]
                    },
                    "envVarsEnabled": True,
                    "envVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST"
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertEqual(
            "Host(`unittest.ecovadis-itlab.com`) && PathPrefix(`/unittests`)",
            jmespath.search(
                "spec.routes[0].match", docs[0])
        )

        self.assertEqual(
            "RELEASE-NAME-charts-core-http-stripprefix",
            jmespath.search(
                "spec.routes[0].middlewares[0].name", docs[0])
        )

        self.assertEqual(
            "/unittests",
            jmespath.search(
                "spec.stripPrefix.prefixes[0]", docs[1])
        )

    def test_host_rule_withour_strip_prefix(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http"
                            }
                        ]
                    },
                    "envVarsEnabled": True,
                    "envVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST"
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertEqual(
            "Host(`unittest.ecovadis-itlab.com`)",
            jmespath.search(
                "spec.routes[0].match", docs[0])
        )

    def test_tls_option_not_added_when_specified(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "isTlsEnabled": False
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertIsNone(jmespath.search(
            "spec.tls", docs[0]))

    def test_middleware_not_generated_when_option_is_disabled(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "isStripprefixEnabled": False,
                                "isRetryEnabled": False,
                                "ruleName": "http"
                            }
                        ]
                    },
                    "envVarsEnabled": True,
                    "envVars": {
                        "ASPNETCORE_ENVIRONMENT": "UNITTEST"
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertIsNone(jmespath.search(
            "spec.routes[0].middlewares", docs[0]))

    def test_host_rule_and_retry_middleware_created(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "isRetryEnabled": True
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertEqual(
            "RELEASE-NAME-charts-core-http-retry",
            jmespath.search(
                "spec.routes[0].middlewares[0].name", docs[0])
        )
    
    def test_host_rule_and_retry_middleware_configured(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "isRetryEnabled": True,
                                "retry": {
                                    "attempts": 5,
                                    "initialInterval": "500ms"
                                    }
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertRegex(docs[1]["kind"], "Middleware")
        self.assertEqual(
            "500ms",
            jmespath.search(
                "spec.retry.initialInterval", docs[1])
        )

    def test_host_rule_and_circuitbreaker_middleware_created(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "isRetryEnabled": False,
                                "isCircuitBreakerEnabled": True
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertEqual(
            "RELEASE-NAME-charts-core-http-circuitbreaker",
            jmespath.search(
                "spec.routes[0].middlewares[0].name", docs[0])
        )


    def test_host_rule_and_circuitbreaker_middleware_configured(self):
        docs = render_chart(
            values={
                "global": {
                    "ingressRoutes": {
                        "enabled": True,
                        "domain": "ecovadis-itlab.com",
                        "routes": [
                            {
                                "ruleName": "http",
                                "isRetryEnabled": False,
                                "isCircuitBreakerEnabled": True,
                                "circuitBreaker": {
                                    "expression": "NetworkErrorRatio() > 0.10"
                                    }
                            }
                        ]
                    }
                }
            },
            name=".",
            show_only=["templates/CRD/ingressroute.yaml"]
        )
        self.assertRegex(docs[1]["kind"], "Middleware")
        self.assertEqual(
            "NetworkErrorRatio() > 0.10",
            jmespath.search(
                "spec.circuitBreaker.expression", docs[1])
        )