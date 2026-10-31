# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in the name of MV2 of Munim, Inc.
import unittest

import citecheck as cc

PEPS = {
    594: "Removing dead batteries from the standard library",
    683: "Immortal Objects, Using a Fixed Refcount",
    689: "Unstable C API tier",
    697: "Limited C API for Extending Opaque Types",
    803: "Stable ABI for Free-Threaded Builds",
    3156: 'Asynchronous IO Support Rebooted: the "asyncio" Module',
}

LINES = [
    "* :ref:`PEP 697 <whatsnew312-pep697>`, unstable C API tier",
    "* :ref:`PEP 683 <whatsnew312-pep683>`, immortal objects",
    "",
    '   :pep:`3156` -- Asynchronous IO Support Rebooted: the "asyncio" Module',
    "The new :mod:`asyncio` module (defined in :pep:`3156`) provides a standard",
    "* :pep:`594`:",
    "  :ref:`Many legacy standard library modules have been deprecated",
    "* :pep:`803`, :pep:`820 <820>`: stable ABI",
    "* :pep:`697`: Introduce the :ref:`Unstable C API tier <unstable-c-api>`,",
]


class StemTests(unittest.TestCase):
    def test_stems(self):
        self.assertEqual(cc.stem("unstable"), "unstabl")
        self.assertEqual(cc.stem("limited"), "limit")
        self.assertEqual(cc.stem("classes"), "class")
        self.assertEqual(cc.stem("class"), "class")
        self.assertEqual(cc.stem("inlining"), "inlin")
        self.assertEqual(cc.stem("inlined"), "inlin")
        self.assertEqual(cc.stem("inline"), "inlin")
        self.assertEqual(cc.stem("types"), "type")
        self.assertEqual(cc.stem("status"), "status")
        self.assertEqual(cc.stem("dictionaries"), "dictionari")
        self.assertEqual(cc.stem("dictionary"), "dictionari")

    def test_clean_and_tokens(self):
        self.assertEqual(cc.clean(":ref:`Unstable C API tier <unstable-c-api>`,"),
                         "Unstable C API tier,")
        self.assertEqual(cc.content_tokens("Introduce the Unstable C API tier ,"),
                         ["introduc", "unstabl", "c", "api", "tier"])
        self.assertEqual(cc.title_tokens(PEPS[697]),
                         ["api", "c", "extend", "limit", "opaqu", "type"])


class ExtractTests(unittest.TestCase):
    def test_pairs(self):
        got = cc.extract(LINES)
        self.assertEqual([g[0] for g in got], [1, 2, 4, 6, 9])
        self.assertEqual([g[1] for g in got], [697, 683, 3156, 594, 697])
        self.assertEqual([g[2] for g in got], [",", ",", "--", ":", ":"])
        self.assertEqual(got[0][3], "unstable C API tier")
        self.assertEqual(got[1][3], "immortal objects")
        self.assertFalse(got[1][4])
        self.assertTrue(got[3][4])


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.rows = cc.audit({"Doc/whatsnew/3.12.rst": "\n".join(LINES)}, PEPS)

    def test_flags(self):
        self.assertEqual([r["flag"] for r in self.rows],
                         ["miscite", "ok", "ok", "ok", "miscite"])
        self.assertEqual(self.rows[0]["best_other"], 689)
        self.assertEqual(self.rows[4]["best_other"], 689)
        self.assertEqual(self.rows[0]["cited_score"], 0.3333)
        self.assertEqual(self.rows[0]["best_other_score"], 1.0)
        self.assertEqual(self.rows[2]["cited_score"], 1.0)
        self.assertAlmostEqual(self.rows[1]["cited_score"], 0.4)
        self.assertAlmostEqual(self.rows[3]["cited_score"], 0.4)

    def test_grade(self):
        g = cc.grade(self.rows)
        self.assertEqual(g["P1_positive_control"]["verdict"], "HELD")
        self.assertEqual(g["P1_positive_control"]["n"], 2)
        self.assertEqual(g["P2_dash_titles_match"]["n"], 1)
        self.assertEqual(g["P2_dash_titles_match"]["verdict"], "HELD")
        self.assertEqual(g["flags"], {"miscite": 2, "ok": 3})
        self.assertEqual(g["miscite_leads"], [])

    def test_unknown_pep(self):
        rows = cc.audit({"Doc/x.rst": "PEP 9999: Something big here"}, PEPS)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["flag"], "unknown_pep")
        g = cc.grade(rows)
        self.assertEqual(g["P1_positive_control"]["verdict"], "NOT_TESTABLE")
        self.assertEqual(len(g["unknown_pep"]), 1)


if __name__ == "__main__":
    unittest.main()
