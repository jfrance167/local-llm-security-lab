"""Independent acceptance cases written before the worker draft was obtained."""
import unittest
from llm_lab.report import parse_eval


def row(**changes):
    result = dict(entry_type='eval', probe='probe.example', detector='detector.example',
                  passed=2, fails=1, nones=1, total_evaluated=3, total_processed=4)
    result.update(changes)
    return result


class EvalTests(unittest.TestCase):
    def test_counts(self):
        r = parse_eval(row())
        self.assertEqual(r, dict(probe='probe.example', detector='detector.example',
            passed=2, fails=1, unscored=1, evaluated=3, processed=4,
            status='findings', pass_rate=2/3))

    def test_zero_is_inconclusive(self):
        r = parse_eval(row(passed=0, fails=0, nones=4, total_evaluated=0))
        self.assertEqual(r['status'], 'inconclusive')
        self.assertIsNone(r['pass_rate'])

    def test_no_findings_does_not_include_unscored(self):
        r = parse_eval(row(passed=3, fails=0))
        self.assertEqual(r['status'], 'no_findings')
        self.assertEqual(r['unscored'], 1)

    def test_invalid_count_types_and_ranges(self):
        for name in ('passed', 'fails', 'nones', 'total_evaluated', 'total_processed'):
            for bad in (True, False, -1, 1.0, '1', None, 10_000_001, float('nan')):
                with self.subTest(name=name, bad=bad), self.assertRaises(ValueError):
                    parse_eval(row(**{name: bad}))

    def test_required_fields(self):
        for key in row():
            r = row()
            del r[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_eval(r)

    def test_required_counts_even_when_zero(self):
        for key in ('passed', 'fails', 'nones', 'total_evaluated', 'total_processed'):
            r = row(passed=0, fails=0, nones=0, total_evaluated=0, total_processed=0)
            del r[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                parse_eval(r)

    def test_exact_dict(self):
        class Custom(dict):
            pass
        with self.assertRaises(ValueError):
            parse_eval(Custom(row()))

    def test_negative_nones_with_consistent_totals(self):
        with self.assertRaises(ValueError):
            parse_eval(row(nones=-1, total_processed=2))

    def test_consistency(self):
        for changes in (dict(total_evaluated=4), dict(total_processed=5)):
            with self.assertRaises(ValueError):
                parse_eval(row(**changes))

    def test_labels_and_entry_type(self):
        for field in ('probe', 'detector'):
            for bad in ('', 'x'*201, 1, None):
                with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                    parse_eval(row(**{field:bad}))
        with self.assertRaises(ValueError):
            parse_eval(row(entry_type='attempt'))
        for bad in ([], None, 1):
            with self.assertRaises(ValueError):
                parse_eval(bad)

    def test_no_mutation(self):
        r = row(extra={'unsafe':'ignored'})
        before = repr(r)
        parse_eval(r)
        self.assertEqual(repr(r), before)


if __name__ == '__main__':
    unittest.main()
