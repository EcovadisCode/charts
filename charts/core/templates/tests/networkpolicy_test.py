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


class NetworkPolicyTemplateFileTest(unittest.TestCase):

    def test_networkpolicy_rendering_zyte(self):
        docs = render_chart(
            values={
                "global": {
                    "defaultNetworkPolicyEnabled": True,
                    "redisNetworkPolicyEnabled": False,
                    "zyteProxyNetworkPolicyEnabled": True
                }
            },
            name=".",
            show_only=["templates/network-policy.yaml"]
        )
        self.assertRegex(docs[0]["kind"], "NetworkPolicy")
        self.assertEqual(
            {"port": 8010},
            jmespath.search("spec.egress[-1].ports[0]", docs[0])
        )
        self.assertEqual(
            {"port": 8011},
            jmespath.search("spec.egress[-1].ports[1]", docs[0])
        )
        self.assertEqual(
            {"port": 8014},
            jmespath.search("spec.egress[-1].ports[2]", docs[0])
        )

    def test_networkpolicy_rendering(self):
        docs = render_chart(
            values={
                "global": {
                    "defaultNetworkPolicyEnabled": True,
                    "redisNetworkPolicyEnabled": False
                }
            },
            name=".",
            show_only=["templates/network-policy.yaml"]
        )
        self.assertRegex(docs[0]["kind"], "NetworkPolicy")

    def test_default_networkpolicy_rendering(self):
        docs = render_chart(
            values={
                "global": {
                    "defaultNetworkPolicyEnabled": True,
                    "redisNetworkPolicyEnabled": True,
                    "postgresNetworkPolicyEnabled": True
                }
            },
            name=".",
            show_only=["templates/network-policy.yaml"]
        )
        self.assertRegex(docs[0]["kind"], "NetworkPolicy")
        self.assertIsNotNone(
            jmespath.search("spec.ingress[0].from[0].podSelector", docs[0])
        )
        self.assertIsNotNone(
            jmespath.search(
                "spec.ingress[1].from[0].namespaceSelector", docs[0])
        )
        self.assertEqual(
            "default",
            jmespath.search(
                "spec.ingress[1].from[0].namespaceSelector.matchLabels.environment", docs[0])
        )

        self.assertIsNotNone(
            jmespath.search("spec.ingress[2].from[0].ipBlock", docs[0])
        )

        self.assertEqual(
            {"port": 443},
            jmespath.search("spec.ingress[2].ports[0]", docs[0])
        )

        self.assertEqual(
            {"port": 80},
            jmespath.search("spec.ingress[2].ports[1]", docs[0])
        )

        self.assertEqual(
            {"port": 8443},
            jmespath.search("spec.ingress[2].ports[2]", docs[0])
        )

        self.assertEqual(
            {"port": 8000},
            jmespath.search("spec.ingress[2].ports[3]", docs[0])
        )

        self.assertIsNotNone(
            jmespath.search("spec.ingress[3].from[0].ipBlock", docs[0])
        )

        self.assertEqual(
            {"port": 443},
            jmespath.search("spec.ingress[3].ports[0]", docs[0])
        )

        self.assertEqual(
            {"port": 80},
            jmespath.search("spec.ingress[3].ports[1]", docs[0])
        )

        self.assertIsNotNone(
            jmespath.search("spec.egress[0].to[0].podSelector", docs[0])
        )

        self.assertIsNotNone(
            jmespath.search("spec.egress[1].to[0].namespaceSelector", docs[0])
        )

        self.assertEqual(
            {"k8s-app": "kube-dns"},
            jmespath.search(
                "spec.egress[1].to[0].podSelector.matchLabels", docs[0])
        )

        self.assertEqual(
            {'port': 53, 'protocol': 'UDP'},
            jmespath.search("spec.egress[1].ports[0]", docs[0])
        )

        self.assertEqual(
            {'port': 5432},
            jmespath.search("spec.egress[8].ports[0]", docs[0])
        )

        self.assertEqual(
            "default",
            jmespath.search(
                "spec.egress[2].to[0].namespaceSelector.matchLabels.environment", docs[0])
        )