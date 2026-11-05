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


def outside_world_egress_ports(doc):
    """Ports of the egress rule that targets 0.0.0.0/0, wherever it sits in the list."""
    rules = jmespath.search("spec.egress[?to[0].ipBlock.cidr == '0.0.0.0/0']", doc)
    assert len(rules) == 1, f"expected one 0.0.0.0/0 egress rule, got {len(rules)}"
    return rules[0]["ports"]


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
        ports = outside_world_egress_ports(docs[0])
        self.assertIn({"port": 8010}, ports)
        self.assertIn({"port": 8011}, ports)
        self.assertIn({"port": 8014}, ports)

    def test_mongodbnetworkpolicy(self):
        docs = render_chart(
        values={
            "global": {
                "defaultNetworkPolicyEnabled": True,
                "mongodbNetworkPolicyEnabled": True,
            }
        },
        name=".",
        show_only=["templates/network-policy.yaml"]
        )
        self.assertIn(
            {"port": 1024, "endPort": 65535},
            outside_world_egress_ports(docs[0])
        )

    def test_strictmongodbnetworkpolicy(self):
        docs = render_chart(
        values={
            "global": {
                "defaultNetworkPolicyEnabled": True,
                "mongodbStrictNetworkPolicyEnabled": True,
            }
        },
        name=".",
        show_only=["templates/network-policy.yaml"]
        )
        self.assertIn(
            {"port": 27017},
            outside_world_egress_ports(docs[0])
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

        self.assertIn(
            {'port': 5432},
            outside_world_egress_ports(docs[0])
        )

        self.assertEqual(
            "default",
            jmespath.search(
                "spec.egress[2].to[0].namespaceSelector.matchLabels.environment", docs[0])
        )