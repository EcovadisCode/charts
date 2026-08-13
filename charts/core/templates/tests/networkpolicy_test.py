import unittest

import jmespath

from tests.helm_template_generator import render_chart


# ---------------------------------------------------------------------------
# Helpers
#
# These locate rules by what they contain rather than by their position in the
# list. Adding a port or a peer to the template used to break every assertion
# below it; now it only affects the assertions that actually care.
# ---------------------------------------------------------------------------

def render(**flags):
    """Render the chart with defaultNetworkPolicyEnabled plus any extra flags."""
    values = {"global": dict({"defaultNetworkPolicyEnabled": True}, **flags)}
    return render_chart(
        values=values,
        name=".",
        show_only=["templates/network-policy.yaml"],
    )[0]


def render_cilium(**flags):
    values = {"global": dict({"defaultNetworkPolicyEnabled": True}, **flags)}
    return render_chart(
        values=values,
        name=".",
        show_only=["templates/cilium-network-policy.yaml"],
    )[0]


def rules(doc, direction):
    return jmespath.search("spec.%s" % direction, doc) or []


def peers(rule, direction):
    return rule.get("to" if direction == "egress" else "from") or []


def rule_with_ipblock(doc, direction, cidr="0.0.0.0/0"):
    """The rule whose peer list contains the given CIDR, or None."""
    for rule in rules(doc, direction):
        for peer in peers(rule, direction):
            if (peer.get("ipBlock") or {}).get("cidr") == cidr:
                return rule
    return None


def rule_with_namespace_label(doc, direction, key, value):
    for rule in rules(doc, direction):
        for peer in peers(rule, direction):
            labels = (peer.get("namespaceSelector") or {}).get("matchLabels") or {}
            if labels.get(key) == value:
                return rule
    return None


def rule_with_pod_labels(doc, direction, labels):
    for rule in rules(doc, direction):
        for peer in peers(rule, direction):
            if (peer.get("podSelector") or {}).get("matchLabels") == labels:
                return rule
    return None


def intra_namespace_rule(doc, direction):
    """The `podSelector: {}` catch-all rule for the current namespace."""
    for rule in rules(doc, direction):
        peer_list = peers(rule, direction)
        if len(peer_list) == 1 and peer_list[0] == {"podSelector": {}}:
            return rule
    return None


def port_numbers(rule):
    return {p["port"] for p in (rule or {}).get("ports", []) if "port" in p}


def has_port(rule, port, protocol=None, end_port=None):
    for entry in (rule or {}).get("ports", []):
        if entry.get("port") != port:
            continue
        if protocol is not None and entry.get("protocol") != protocol:
            continue
        if end_port is not None and entry.get("endPort") != end_port:
            continue
        return True
    return False


def peer_kinds(rule, direction):
    """Set of peer types present on a rule, e.g. {"ipBlock", "podSelector"}."""
    kinds = set()
    for peer in peers(rule, direction):
        kinds.update(peer.keys())
    return kinds


class NetworkPolicyTemplateFileTest(unittest.TestCase):

    # -- rendering / structure ---------------------------------------------

    def test_networkpolicy_is_rendered(self):
        doc = render(redisNetworkPolicyEnabled=False)
        self.assertEqual("NetworkPolicy", doc["kind"])
        self.assertEqual("networking.k8s.io/v1", doc["apiVersion"])

    def test_policy_is_absent_when_disabled(self):
        # Rendered without --show-only: helm treats an unmatched --show-only as
        # an error, so we render the whole chart and look for the kind instead.
        docs = render_chart(
            values={"global": {"defaultNetworkPolicyEnabled": False}},
            name=".",
        )
        self.assertEqual([], [d for d in docs if d.get("kind") == "NetworkPolicy"])

    def test_intra_namespace_traffic_is_allowed_both_ways(self):
        doc = render()
        self.assertIsNotNone(intra_namespace_rule(doc, "ingress"))
        self.assertIsNotNone(intra_namespace_rule(doc, "egress"))

    def test_environment_namespace_selector(self):
        # Release namespace defaults to "default", so environment == "default".
        doc = render()
        self.assertIsNotNone(
            rule_with_namespace_label(doc, "ingress", "environment", "default"))
        egress = rule_with_namespace_label(doc, "egress", "environment", "default")
        self.assertIsNotNone(egress)
        self.assertEqual({8443, 8000, 80, 443}, port_numbers(egress))

    def test_kube_dns_egress(self):
        doc = render()
        rule = rule_with_pod_labels(doc, "egress", {"k8s-app": "kube-dns"})
        self.assertIsNotNone(rule)
        self.assertTrue(has_port(rule, 53, protocol="UDP"))

    # -- the external (ipBlock) rules ---------------------------------------

    def test_external_ingress_ports(self):
        doc = render(redisNetworkPolicyEnabled=True, postgresNetworkPolicyEnabled=True)
        rule = rule_with_ipblock(doc, "ingress")
        self.assertIsNotNone(rule)
        self.assertTrue({443, 80, 8443, 8000}.issubset(port_numbers(rule)))

    def test_external_egress_covers_both_tls_ports(self):
        # 8433 is a long-standing typo for 8443; both are allowed until the
        # former is confirmed unused. See charts/core/README.md.
        rule = rule_with_ipblock(render(), "egress")
        self.assertTrue({8433, 8443}.issubset(port_numbers(rule)))

    def test_postgres_port_opt_in(self):
        self.assertNotIn(5432, port_numbers(rule_with_ipblock(render(), "egress")))
        rule = rule_with_ipblock(render(postgresNetworkPolicyEnabled=True), "egress")
        self.assertIn(5432, port_numbers(rule))

    def test_zyte_proxy_ports_opt_in(self):
        doc = render(redisNetworkPolicyEnabled=False, zyteProxyNetworkPolicyEnabled=True)
        rule = rule_with_ipblock(doc, "egress")
        self.assertTrue({8010, 8011, 8014}.issubset(port_numbers(rule)))

    def test_mongodb_wide_range_opt_in(self):
        rule = rule_with_ipblock(render(mongodbNetworkPolicyEnabled=True), "egress")
        self.assertTrue(has_port(rule, 1024, end_port=65535))

    def test_mongodb_strict_uses_single_port(self):
        rule = rule_with_ipblock(
            render(mongodbStrictNetworkPolicyEnabled=True), "egress")
        self.assertIn(27017, port_numbers(rule))
        self.assertFalse(has_port(rule, 1024, end_port=65535))

    def test_sql_redirect_port_range_opt_in(self):
        rule = rule_with_ipblock(render(sqlNetworkPolicyEnabled=True), "egress")
        self.assertIn(1433, port_numbers(rule))
        self.assertTrue(has_port(rule, 11000, end_port=11999))

    # -- Cilium compatibility ----------------------------------------------

    def test_ipblock_rules_carry_selector_peers(self):
        # Cilium never matches Pod IPs through ipBlock, so the same ports have
        # to be reachable via selectors for in-cluster peers.
        doc = render()
        for direction in ("egress", "ingress"):
            rule = rule_with_ipblock(doc, direction)
            self.assertEqual(
                {"ipBlock", "namespaceSelector", "podSelector"},
                peer_kinds(rule, direction),
                "%s ipBlock rule is missing selector peers" % direction,
            )

    def test_node_egress_policy_allows_host_entities(self):
        # ipBlock cannot match node addresses under Cilium, so IMDS
        # (169.254.169.254, link-local -> `host`) needs an entity rule.
        doc = render_cilium()
        self.assertEqual("CiliumNetworkPolicy", doc["kind"])
        self.assertEqual("cilium.io/v2", doc["apiVersion"])
        entities = jmespath.search("spec.egress[0].toEntities", doc)
        self.assertEqual(["host", "remote-node"], entities)

    def test_node_egress_policy_targets_the_same_pods(self):
        np = render()
        cnp = render_cilium()
        self.assertEqual(
            jmespath.search("spec.podSelector.matchLabels", np),
            jmespath.search("spec.endpointSelector.matchLabels", cnp),
        )

    def test_node_egress_policy_declares_no_ingress(self):
        # Deliberate: these pods sit behind Traefik on a ClusterIP Service, so
        # nothing reaches them from a node address.
        self.assertNotIn("ingress", render_cilium()["spec"])

    def test_node_egress_policy_follows_the_networkpolicy_switch(self):
        docs = render_chart(
            values={"global": {"defaultNetworkPolicyEnabled": False}},
            name=".",
        )
        self.assertEqual(
            [], [d for d in docs if d.get("kind") == "CiliumNetworkPolicy"])

    def test_selector_peers_do_not_widen_the_port_list(self):
        # The selector peers must sit inside the existing rule so they inherit
        # its ports; a separate peerless rule would allow every port.
        doc = render(postgresNetworkPolicyEnabled=True, redisNetworkPolicyEnabled=True)
        rule = rule_with_ipblock(doc, "egress")
        self.assertTrue(port_numbers(rule), "external egress rule lost its ports")
        for candidate in rules(doc, "egress"):
            self.assertTrue(
                peers(candidate, "egress"),
                "found an egress rule with no peers - that allows all destinations",
            )
