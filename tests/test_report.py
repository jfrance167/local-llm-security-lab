import json
from pathlib import Path
import tempfile
import unittest
from llm_lab import report
from test_eval import row

INIT = {'entry_type':'init','version':'0.17.0','run':'synthetic'}
END = {'entry_type':'completion','run':'synthetic'}


class ReportTests(unittest.TestCase):
    def analyze(self, records):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.jsonl'
            path.write_bytes(records if isinstance(records, bytes) else
                ''.join(json.dumps(r)+'\n' for r in records).encode())
            return report.analyze_report(path)

    def test_complete(self):
        result = self.analyze([INIT, row(), END])
        self.assertTrue(result['run_complete'])
        self.assertEqual(result['status'], 'findings')

    def test_incomplete_is_inconclusive(self):
        result = self.analyze([INIT, row(passed=3, fails=0)])
        self.assertFalse(result['run_complete'])
        self.assertEqual(result['status'], 'inconclusive')

    def test_zero_or_no_evaluations(self):
        for records in ([INIT, END], [INIT, row(passed=0, fails=0, nones=4, total_evaluated=0), END]):
            self.assertEqual(self.analyze(records)['status'], 'inconclusive')

    def test_multi_detector_not_summed(self):
        result = self.analyze([INIT, row(), row(detector='other'), END])
        self.assertEqual(len(result['evaluations']), 2)
        self.assertNotIn('pass_rate', result)
        self.assertNotIn('total_evaluated', result)

    def test_attempt_is_not_a_pass(self):
        result = self.analyze([INIT, {'entry_type':'attempt','status':2,'outputs':['text']}, END])
        self.assertEqual(result['evaluations'], [])
        self.assertEqual(result['status'], 'inconclusive')

    def test_invalid_order_ids_and_duplicates(self):
        for records in ([row(), END], [INIT, INIT], [INIT, END, row()],
            [INIT, row(), row(), END], [INIT, {'entry_type':'completion','run':'other'}],
            [dict(INIT,version='0.16.0'), END], []):
            with self.subTest(records=records), self.assertRaises(ValueError):
                self.analyze(records)

    def test_malformed_json_and_utf8(self):
        for raw in (b'{bad}\n', b'[]\n', b'\xff\n', b'\n', b'{}\n',
                    b'{"entry_type":"init","entry_type":"eval"}\n',
                    b'{"entry_type":"init","bad":NaN}\n',
                    b'{"entry_type":"init","bad":Infinity}\n',
                    b'['*1500+b']'*1500):
            with self.subTest(raw=raw[:80]), self.assertRaises(ValueError):
                self.analyze(raw)

    def test_line_limit(self):
        with self.assertRaises(ValueError):
            self.analyze(b'x'*(report.MAX_LINE_BYTES+1))

    def test_file_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'large.jsonl'
            with path.open('wb') as source:
                source.truncate(report.MAX_REPORT_BYTES+1)
            with self.assertRaises(ValueError):
                report.analyze_report(path)

    def test_record_limit(self):
        with self.assertRaises(ValueError):
            self.analyze([INIT]+[{'entry_type':'attempt'}]*report.MAX_RECORDS)

    def test_json_output_escaping(self):
        label = 'x\n\u001b[31m<script>'
        result = self.analyze([INIT, row(probe=label), END])
        encoded = json.dumps(result, ensure_ascii=True, allow_nan=False)
        self.assertNotIn('\u001b', encoded)
        self.assertEqual(json.loads(encoded)['evaluations'][0]['probe'], label)


if __name__ == '__main__':
    unittest.main()
