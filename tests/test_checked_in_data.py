"""Regression checks for every checked-in activity snapshot.

The legacy GitHub snapshot lives at the repository root. New GitHub and
GitCode snapshots live in date-stamped directories under ``data``. These
tests discover all of those datasets, derive their cutoffs from snapshot
metadata, and verify that their aggregates remain recomputable from the
checked-in rows.

The tests read only repository files; they need no network and no clones.
Any manual edit that breaks internal consistency or data minimization fails.
"""

import csv
import json
import re
import unittest
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / "data"

EMAIL_RE = re.compile(
    r"(?i)(?<![A-Z0-9._%+\-])[A-Z0-9._%+\-]+@"
    r"[A-Z0-9\-]+(?:\.[A-Z0-9\-]+)*(?![A-Z0-9.\-])"
)
DATED_DATASET_RE = re.compile(r"^(github|gitcode)-(\d{4}-\d{2}-\d{2})$")
DATED_STATUS_SNAPSHOT_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.json$")

GITHUB_REPOS = (
    "vllm-ascend",
    "triton-ascend",
    "torch_npu",
    "sglang",
    "llama.cpp",
    "lmdeploy",
    "pytorch",
    "transformers",
)

GITCODE_CORE_PATHS = {
    "ops-transformer": {
        "attention",
        "common",
        "experimental",
        "ffn",
        "gmm",
        "mamba",
        "mc2",
        "mhc",
        "moe",
        "posembedding",
        "torch_extension",
    },
    "ops-math": {"common", "conversion", "experimental", "math", "random"},
    "catlass": {"include", "python", "experimental"},
}

K3_CASE_WINDOW_START = date(2026, 7, 26)
K3_CASE_WINDOW_END = date(2026, 8, 1)
K3_COMPLETE_SCHEMA_START = date(2026, 8, 8)
K3_CASE_REPOS = {
    "sgl-project/sglang",
    "vllm-project/vllm-ascend",
}
K3_STATUS_FIELDS = {
    "repo",
    "number",
    "title",
    "state",
    "createdAt",
    "mergedAt",
    "updatedAt",
    "closedAt",
}


def load_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def parse_iso_date(value, context):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise AssertionError(f"{context}: expected an ISO date, found {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise AssertionError(f"{context}: invalid ISO date {value!r}") from exc


def parse_github_timestamp(value, context):
    if not isinstance(value, str):
        raise AssertionError(f"{context}: expected a GitHub timestamp, found {value!r}")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise AssertionError(
            f"{context}: invalid GitHub UTC timestamp {value!r}"
        ) from exc


def dated_dataset_dirs(kind):
    datasets = []
    if not DATA_ROOT.is_dir():
        return datasets
    for candidate in sorted(DATA_ROOT.iterdir()):
        if not candidate.is_dir():
            continue
        match = DATED_DATASET_RE.fullmatch(candidate.name)
        if match and match.group(1) == kind:
            datasets.append((candidate, parse_iso_date(match.group(2), candidate.name)))
    return datasets


def github_snapshots():
    snapshots = [(ROOT, None)]
    snapshots.extend(dated_dataset_dirs("github"))
    return snapshots


def github_snapshot_cutoff(summary, directory_date, label):
    extended_window = summary.get("extended_window")
    if not (
        isinstance(extended_window, list)
        and len(extended_window) == 2
        and all(isinstance(value, str) for value in extended_window)
    ):
        raise AssertionError(f"{label}: invalid extended_window metadata")

    cutoff_text = extended_window[1]
    cutoff = parse_iso_date(cutoff_text, f"{label} extended_window cutoff")
    for field in ("snapshot_as_of", "generated"):
        value = summary.get(field)
        if value is not None and value != cutoff_text:
            raise AssertionError(
                f"{label}: {field} {value!r} does not match cutoff {cutoff_text!r}"
            )
    if directory_date is not None and directory_date != cutoff:
        raise AssertionError(
            f"{label}: directory date {directory_date} does not match cutoff {cutoff}"
        )
    return cutoff_text


class GitHubSnapshotConsistencyTest(unittest.TestCase):
    @staticmethod
    def recompute_window(rows, end):
        rows = [row for row in rows if row["date"] <= end]
        count = len(rows)
        affiliations = defaultdict(int)
        lines_added = defaultdict(int)
        monthly = defaultdict(int)
        authors = defaultdict(set)
        for row in rows:
            affiliations[row["affiliation"]] += 1
            lines_added[row["affiliation"]] += row.get("insertions", 0)
            monthly[row["date"][:7]] += 1
            authors[row["affiliation"]].add(row["name_hash"])
        huawei_commits = affiliations["confirmed"] + affiliations["likely"]
        huawei_lines = lines_added["confirmed"] + lines_added["likely"]
        total_lines = sum(lines_added.values())
        return {
            "commits": count,
            "commits_confirmed": affiliations["confirmed"],
            "commits_likely": affiliations["likely"],
            "commits_unknown": affiliations["unknown"],
            "huawei_commit_share": (
                round(huawei_commits / count, 3) if count else None
            ),
            "lines_added_total": total_lines or None,
            "lines_added_huawei": huawei_lines or None,
            "huawei_loc_share": (
                round(huawei_lines / total_lines, 3) if total_lines else None
            ),
            "authors_confirmed": len(authors["confirmed"]),
            "authors_likely": len(authors["likely"]),
            "authors_unknown": len(authors["unknown"]),
            "monthly": dict(sorted(monthly.items())),
        }

    def test_summary_recomputable_from_rows(self):
        snapshots = github_snapshots()
        self.assertTrue(snapshots, "no GitHub snapshots discovered")
        for snapshot_dir, directory_date in snapshots:
            label = str(snapshot_dir.relative_to(ROOT)) if snapshot_dir != ROOT else "root"
            with self.subTest(snapshot=label):
                summary = json.loads((snapshot_dir / "summary.json").read_text())
                cutoff = github_snapshot_cutoff(summary, directory_date, label)
                heim_window = summary.get("heim_window")
                self.assertIsInstance(heim_window, list, label)
                self.assertEqual(len(heim_window), 2, label)
                heim_end = parse_iso_date(
                    heim_window[1], f"{label} Heim-window cutoff"
                ).isoformat()
                self.assertEqual(set(summary["repos"]), set(GITHUB_REPOS), label)

                for repo in GITHUB_REPOS:
                    rows = load_jsonl(
                        snapshot_dir / f"raw_{repo.replace('/', '_')}.jsonl"
                    )
                    self.assertTrue(
                        all(row["date"] <= cutoff for row in rows),
                        f"{label} {repo}: row after snapshot cutoff",
                    )
                    reference = summary["repos"][repo]
                    for window_name, end in (
                        ("heim_window", heim_end),
                        ("extended_window", cutoff),
                    ):
                        recomputed = self.recompute_window(rows, end)
                        for key, value in recomputed.items():
                            self.assertEqual(
                                reference[window_name][key],
                                value,
                                f"{label} {repo} {window_name} {key}",
                            )

    def test_rows_are_pseudonymized(self):
        for snapshot_dir, directory_date in github_snapshots():
            label = str(snapshot_dir.relative_to(ROOT)) if snapshot_dir != ROOT else "root"
            with self.subTest(snapshot=label):
                summary = json.loads((snapshot_dir / "summary.json").read_text())
                github_snapshot_cutoff(summary, directory_date, label)
                for repo in GITHUB_REPOS:
                    rows = load_jsonl(
                        snapshot_dir / f"raw_{repo.replace('/', '_')}.jsonl"
                    )
                    for row in rows:
                        self.assertNotIn("name", row, f"{label} {repo}")
                        self.assertNotIn("email", row, f"{label} {repo}")
                        self.assertIn("identity_hash", row, f"{label} {repo}")
                        self.assertIn("name_hash", row, f"{label} {repo}")
                        self.assertIn("domain", row, f"{label} {repo}")
                        self.assertIsNone(
                            EMAIL_RE.search(row["subject"]),
                            f"{label} {repo}: email-like text in {row['hash']}",
                        )


class GitCodeSnapshotConsistencyTest(unittest.TestCase):
    @staticmethod
    def statistics(rows):
        eligible = [row for row in rows if not row["is_merge"] and not row["is_automation"]]
        tiers = Counter(row["domain_tier"] for row in rows)
        dates = sorted(row["date"] for row in rows)
        return {
            "total_commits": len(rows),
            "author_date_range": [dates[0], dates[-1]] if dates else [None, None],
            "unique_pseudonymous_author_identities": len(
                {row["identity_hash"] for row in rows}
            ),
            "tiers": tiers,
            "non_merge_non_automation_commits": len(eligible),
            "core_path_commits": sum(row["touches_core"] for row in eligible),
            "monthly_counts": dict(
                sorted(Counter(row["month"] for row in rows).items())
            ),
        }

    def load_snapshot(self, snapshot_dir, directory_date):
        label = str(snapshot_dir.relative_to(ROOT))
        summary = json.loads((snapshot_dir / "gitcode_summary.json").read_text())
        cutoff = parse_iso_date(summary.get("as_of"), f"{label} as_of")
        self.assertEqual(directory_date, cutoff, f"{label}: dirname/as_of mismatch")
        self.assertEqual(summary.get("date_basis"), "author_date", label)
        rows = load_jsonl(snapshot_dir / "gitcode_commits.jsonl")
        self.assertTrue(
            all(parse_iso_date(row["date"], f"{label} row date") <= cutoff for row in rows),
            f"{label}: row after snapshot cutoff",
        )
        return label, summary, rows

    def test_summary_recomputable_from_rows(self):
        snapshots = dated_dataset_dirs("gitcode")
        self.assertTrue(snapshots, "no GitCode snapshots discovered")
        for snapshot_dir, directory_date in snapshots:
            with self.subTest(snapshot=snapshot_dir.name):
                label, summary, rows = self.load_snapshot(snapshot_dir, directory_date)
                self.assertEqual(summary["schema_version"], 2, label)
                by_repo = defaultdict(list)
                for row in rows:
                    by_repo[row["repository"]].append(row)

                scopes = [("totals", rows)]
                scopes.extend(
                    (name, by_repo[name]) for name in summary["repositories"]
                )
                for name, scoped_rows in scopes:
                    reference = (
                        summary["totals"]
                        if name == "totals"
                        else summary["repositories"][name]
                    )
                    recomputed = self.statistics(scoped_rows)
                    for key in (
                        "total_commits",
                        "author_date_range",
                        "unique_pseudonymous_author_identities",
                        "non_merge_non_automation_commits",
                        "core_path_commits",
                        "monthly_counts",
                    ):
                        self.assertEqual(
                            reference[key], recomputed[key], f"{label} {name} {key}"
                        )
                    for tier, values in reference["domain_tiers"].items():
                        self.assertEqual(
                            values["commits"],
                            recomputed["tiers"][tier],
                            f"{label} {name} {tier}",
                        )

    def test_monthly_csv_matches_rows(self):
        for snapshot_dir, directory_date in dated_dataset_dirs("gitcode"):
            with self.subTest(snapshot=snapshot_dir.name):
                label, _, rows = self.load_snapshot(snapshot_dir, directory_date)
                with (snapshot_dir / "gitcode_monthly.csv").open(newline="") as handle:
                    csv_rows = list(csv.DictReader(handle))
                all_rows = [row for row in csv_rows if row["repository"] == "ALL"]
                monthly = Counter(row["month"] for row in rows)
                self.assertEqual(
                    {row["month"]: int(row["total_commits"]) for row in all_rows},
                    dict(monthly),
                    label,
                )
                eligible = [
                    row for row in rows if not row["is_merge"] and not row["is_automation"]
                ]
                core_by_month = Counter(
                    row["month"] for row in eligible if row["touches_core"]
                )
                self.assertEqual(
                    {
                        row["month"]: int(row["core_path_commits"])
                        for row in all_rows
                        if int(row["core_path_commits"])
                    },
                    dict(core_by_month),
                    label,
                )

    def test_rows_are_data_minimized_and_auditable(self):
        for snapshot_dir, directory_date in dated_dataset_dirs("gitcode"):
            with self.subTest(snapshot=snapshot_dir.name):
                label, summary, rows = self.load_snapshot(snapshot_dir, directory_date)
                self.assertEqual(set(summary["repositories"]), set(GITCODE_CORE_PATHS), label)
                for row in rows:
                    self.assertNotIn("name", row, label)
                    self.assertNotIn("email", row, label)
                    self.assertIsNone(
                        EMAIL_RE.search(row["subject"]),
                        f"{label}: email-like text in subject {row['hash']}",
                    )
                    expected = bool(
                        set(row["top_level_dirs"])
                        & GITCODE_CORE_PATHS[row["repository"]]
                    )
                    self.assertEqual(
                        row["touches_core"],
                        expected,
                        f"{label}: touches_core mismatch for {row['hash']}",
                    )


class K3StatusSnapshotConsistencyTest(unittest.TestCase):
    def status_snapshots(self):
        snapshot_dir = ROOT / "k3-adaptation" / "snapshots"
        snapshots = []
        for path in sorted(snapshot_dir.iterdir()):
            match = DATED_STATUS_SNAPSHOT_RE.fullmatch(path.name)
            if match:
                snapshots.append((path, parse_iso_date(match.group(1), path.name)))
        return snapshots

    def validate_complete_case_set(self, path, snapshot_date, payload):
        cases = payload.get("case_prs")
        self.assertIsInstance(cases, list, path.name)
        self.assertEqual(len(cases), 17, path.name)

        case_keys = []
        for index, record in enumerate(cases):
            context = f"{path.name} case_prs[{index}]"
            self.assertIsInstance(record, dict, context)
            self.assertFalse(K3_STATUS_FIELDS - set(record), context)
            self.assertIn(record["repo"], K3_CASE_REPOS, context)
            self.assertIsInstance(record["number"], int, context)
            self.assertGreater(record["number"], 0, context)
            self.assertIsInstance(record["title"], str, context)
            self.assertTrue(record["title"].strip(), context)
            self.assertIn(record["state"], {"OPEN", "CLOSED", "MERGED"}, context)

            created_at = parse_github_timestamp(record["createdAt"], f"{context} createdAt")
            updated_at = parse_github_timestamp(record["updatedAt"], f"{context} updatedAt")
            self.assertLessEqual(created_at, updated_at, context)
            self.assertLessEqual(updated_at.date(), snapshot_date, context)
            self.assertGreaterEqual(created_at.date(), K3_CASE_WINDOW_START, context)
            self.assertLessEqual(created_at.date(), K3_CASE_WINDOW_END, context)

            event_times = {}
            for field in ("mergedAt", "closedAt"):
                value = record[field]
                event_times[field] = (
                    None
                    if value is None
                    else parse_github_timestamp(value, f"{context} {field}")
                )
                if event_times[field] is not None:
                    self.assertLessEqual(created_at, event_times[field], context)
                    self.assertLessEqual(event_times[field].date(), snapshot_date, context)

            if record["state"] == "OPEN":
                self.assertIsNone(event_times["mergedAt"], context)
                self.assertIsNone(event_times["closedAt"], context)
            elif record["state"] == "CLOSED":
                self.assertIsNone(event_times["mergedAt"], context)
                self.assertIsNotNone(event_times["closedAt"], context)
            else:
                self.assertIsNotNone(event_times["mergedAt"], context)

            case_keys.append((record["repo"], record["number"]))

        self.assertEqual(len(case_keys), len(set(case_keys)), path.name)
        return set(case_keys)

    def test_status_snapshot_schemas_and_case_set(self):
        snapshots = self.status_snapshots()
        self.assertTrue(snapshots, "no K3 status snapshots discovered")
        complete_case_sets = []
        for path, filename_date in snapshots:
            with self.subTest(snapshot=path.name):
                payload = json.loads(path.read_text())
                payload_date = parse_iso_date(payload.get("date"), f"{path.name} date")
                self.assertEqual(filename_date, payload_date, path.name)
                self.assertIn("query", payload, path.name)
                self.assertIn("repos", payload, path.name)
                self.assertIn("total_raw_matches", payload, path.name)

                if "case_prs" in payload:
                    complete_case_sets.append(
                        (path.name, self.validate_complete_case_set(path, payload_date, payload))
                    )
                elif payload_date >= K3_COMPLETE_SCHEMA_START:
                    self.fail(f"{path.name}: complete snapshot is missing case_prs")
                else:
                    legacy_case = payload.get("sglang_pr_32604")
                    self.assertIsInstance(legacy_case, dict, path.name)
                    for field in ("title", "state", "updatedAt", "mergedAt"):
                        self.assertIn(field, legacy_case, path.name)
                    self.assertIn(legacy_case["state"], {"OPEN", "CLOSED", "MERGED"})
                    parse_github_timestamp(
                        legacy_case["updatedAt"], f"{path.name} legacy updatedAt"
                    )

        self.assertTrue(complete_case_sets, "no complete K3 status snapshot discovered")
        baseline_name, baseline_cases = complete_case_sets[0]
        for name, cases in complete_case_sets[1:]:
            self.assertEqual(cases, baseline_cases, f"{name} differs from {baseline_name}")


if __name__ == "__main__":
    unittest.main()
