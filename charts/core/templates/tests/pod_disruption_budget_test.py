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


class PodDisruptionBudgetTemplateFileTest(unittest.TestCase):

    def test_poddisruptionbudget_rendering(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True
                    },
                    "replicaCount": 2
                }
            },
            name=".",
            show_only=["templates/pod-disruption-budget.yaml"]
        )
        self.assertRegex(docs[0]["kind"], "PodDisruptionBudget")

    def test_poddisruptionbudget_min_available_overwriten(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True,
                        "minAvailable": "2"
                    },
                    "replicaCount": 2
                }
            },
            name=".",
            show_only=["templates/pod-disruption-budget.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "PodDisruptionBudget")

        self.assertEqual(
            2,
            jmespath.search("spec.minAvailable", docs[0])
        )

    def test_poddisruptionbudget_not_rendered_when_pdb_disabled(self):
        docs = render_chart(
            values={
                "global":
                {
                    "podDisruptionBudget": {
                        "enabled": False,
                    },
                    "replicaCount": 2
                }
            },
            name="."
        )

        for template in docs:
            self.assertNotRegex(template["kind"], "PodDisruptionBudget")

    def test_poddisruptionbudget_not_rendered_when_replica_count_too_low(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True,
                    },
                    "replicaCount": 1
                }
            },
            name="."
        )

        for template in docs:
            self.assertNotRegex(template["kind"], "PodDisruptionBudget")

    def test_poddisruptionbudget_max_unavailable_rendered_at_one_replica(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True,
                        "maxUnavailable": 1
                    },
                    "replicaCount": 1
                }
            },
            name=".",
            show_only=["templates/pod-disruption-budget.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "PodDisruptionBudget")

        self.assertEqual(
            1,
            jmespath.search("spec.maxUnavailable", docs[0])
        )
        self.assertIsNone(jmespath.search("spec.minAvailable", docs[0]))

    def test_poddisruptionbudget_not_rendered_when_keda_min_replica_count_too_low(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True,
                    },
                    "keda": {
                        "enabled": True,
                        "minReplicaCount": 1
                    },
                    "replicaCount": 2
                }
            },
            name="."
        )

        for template in docs:
            self.assertNotRegex(template["kind"], "PodDisruptionBudget")

    def test_poddisruptionbudget_rendered_from_keda_min_replica_count(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True,
                    },
                    "keda": {
                        "enabled": True,
                        "minReplicaCount": 2
                    }
                }
            },
            name=".",
            show_only=["templates/pod-disruption-budget.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "PodDisruptionBudget")

        self.assertEqual(
            "50%",
            jmespath.search("spec.minAvailable", docs[0])
        )

    def test_poddisruptionbudget_uses_replica_count_when_keda_disabled(self):
        docs = render_chart(
            values={
                "global": {
                    "podDisruptionBudget": {
                        "enabled": True,
                    },
                    "keda": {
                        "enabled": False,
                        "minReplicaCount": 1
                    },
                    "replicaCount": 2
                }
            },
            name=".",
            show_only=["templates/pod-disruption-budget.yaml"]
        )

        self.assertRegex(docs[0]["kind"], "PodDisruptionBudget")
