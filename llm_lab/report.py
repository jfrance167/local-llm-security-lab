"""Bounded Garak 0.17.0 JSONL analysis. Counts are not authenticated evidence.

The worker draft informed parse_eval; Codex completed strict validation and
file handling. See docs/worker-evaluation.md. No report content is executed.
"""
import json
from pathlib import Path

MAX_LINE_BYTES = 1_048_576
MAX_REPORT_BYTES = 16_777_216
MAX_RECORDS = 10_000


def parse_eval(row):
    """Validate a detector evaluation; keep unscored observations separate."""
    if type(row) is not dict or row.get('entry_type') != 'eval':
        raise ValueError('Expected an eval object')
    for field in ('probe', 'detector'):
        value = row.get(field)
        if type(value) is not str or not 1 <= len(value) <= 200:
            raise ValueError(f'Invalid {field}')
    fields = ('passed', 'fails', 'nones', 'total_evaluated', 'total_processed')
    for field in fields:
        value = row.get(field)
        if type(value) is not int or not 0 <= value <= 10_000_000:
            raise ValueError(f'Invalid {field}')
    passed, fails, unscored, evaluated, processed = (row[f] for f in fields)
    if passed + fails != evaluated or evaluated + unscored != processed:
        raise ValueError('Inconsistent evaluation counts')
    status = 'inconclusive' if evaluated == 0 else ('findings' if fails else 'no_findings')
    return dict(probe=row['probe'], detector=row['detector'], passed=passed, fails=fails,
                unscored=unscored, evaluated=evaluated, processed=processed,
                status=status, pass_rate=None if evaluated == 0 else passed/evaluated)


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError('Non-finite JSON number')


def analyze_report(path):
    """Read <=16MiB regular JSONL evidence; reject malformed input atomically.

    Completion means a matching completion marker was reported. It does not
    authenticate the producer. Detector denominators can overlap, so no summed
    pass rate is produced. Attempt snapshots are never treated as passes.
    """
    path = Path(path)
    if not path.is_file():
        raise ValueError('Report must be a regular file')
    if path.stat().st_size > MAX_REPORT_BYTES:
        raise ValueError('Report exceeds byte limit')
    init = None
    completed = False
    evaluations = []
    seen = set()
    total_bytes = records = 0
    with path.open('rb') as source:
        while True:
            line = source.readline(MAX_LINE_BYTES + 1)
            if not line:
                break
            total_bytes += len(line)
            if len(line) > MAX_LINE_BYTES or total_bytes > MAX_REPORT_BYTES:
                raise ValueError('Report exceeds byte limit')
            if not line.strip():
                raise ValueError('Blank JSONL record')
            records += 1
            if records > MAX_RECORDS:
                raise ValueError('Report exceeds record limit')
            try:
                row = json.loads(line.decode('utf-8'), object_pairs_hook=_no_duplicates,
                                 parse_constant=_reject_constant)
            except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
                raise ValueError(f'Malformed record at line {records}') from exc
            if type(row) is not dict or type(row.get('entry_type')) is not str:
                raise ValueError(f'Invalid record at line {records}')
            kind = row['entry_type']
            if completed:
                raise ValueError('Records after completion')
            if kind == 'init':
                if init is not None or evaluations:
                    raise ValueError('Duplicate or late init')
                if row.get('version') != '0.17.0':
                    raise ValueError('Only Garak 0.17.0 reports are supported')
                run = row.get('run')
                if type(run) is not str or not 1 <= len(run) <= 200:
                    raise ValueError('Invalid run identifier')
                init = row
            elif kind == 'completion':
                if init is None or row.get('run') != init['run']:
                    raise ValueError('Completion must match init run')
                completed = True
            elif kind == 'eval':
                if init is None:
                    raise ValueError('Eval before init')
                evaluation = parse_eval(row)
                key = (evaluation['probe'], evaluation['detector'])
                if key in seen:
                    raise ValueError('Duplicate probe/detector evaluation')
                seen.add(key)
                evaluations.append(evaluation)
            # Other metadata and attempt snapshots remain raw source evidence.
            # They do not add passes, failures, or unique completed observations.
    if init is None:
        raise ValueError('Missing init record')
    any_scored = any(e['evaluated'] > 0 for e in evaluations)
    status = 'inconclusive' if not completed or not any_scored else (
        'findings' if any(e['fails'] for e in evaluations) else 'no_findings')
    return dict(version=init['version'], run=init['run'], run_complete=completed,
                status=status, records=records, evaluations=evaluations)
