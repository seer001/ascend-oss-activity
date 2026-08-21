import csv
import json
import os
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

import mine_gitcode_activity as miner


class MineGitCodeActivityTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.repos_dir = self.root / "repos"
        self.repos_dir.mkdir()
        self.repositories = {}
        for repository in miner.REPOSITORIES:
            directory_name = "cann-catlass" if repository == "catlass" else repository
            repo_path = self.repos_dir / directory_name
            self._git(None, "init", "-q", "-b", "master", str(repo_path))
            self._git(repo_path, "config", "user.name", "Test Committer")
            self._git(repo_path, "config", "user.email", "committer@example.test")
            self._git(
                repo_path,
                "remote",
                "add",
                "origin",
                f"https://gitcode.com/cann/{repository}.git",
            )
            self.repositories[repository] = repo_path

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _git(self, repo_path, *args, env=None):
        command = ["git"]
        if repo_path is not None:
            command.extend(("-C", str(repo_path)))
        command.extend(args)
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
        )
        if result.returncode != 0:
            self.fail(result.stderr.decode("utf-8", errors="replace"))
        return result.stdout.decode("utf-8", errors="replace").strip()

    def _commit(
        self,
        repository,
        path,
        subject,
        name,
        email,
        author_date,
        committer_date=None,
    ):
        repo_path = self.repositories[repository]
        file_path = repo_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        previous = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        file_path.write_text(previous + subject + "\n", encoding="utf-8")
        self._git(repo_path, "add", "--", path)
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_AUTHOR_NAME": name,
                "GIT_AUTHOR_EMAIL": email,
                "GIT_AUTHOR_DATE": author_date + "T12:00:00+00:00",
                "GIT_COMMITTER_NAME": "Test Committer",
                "GIT_COMMITTER_EMAIL": "committer@example.test",
                "GIT_COMMITTER_DATE": (committer_date or author_date)
                + "T12:00:00+00:00",
            }
        )
        self._git(repo_path, "commit", "-q", "-m", subject, env=environment)
        return self._git(repo_path, "rev-parse", "HEAD")

    def _populate_repositories(self):
        self._commit(
            "ops-transformer",
            "attention/kernel.py",
            "core change by alice@huawei.com",
            "Alice",
            "ALICE@HUAWEI.COM",
            "2025-01-02",
        )
        self._commit(
            "ops-transformer",
            "common/generated.py",
            "generated files",
            "CANN Service",
            "service@cann.team",
            "2025-02-02",
        )
        self._commit(
            "ops-transformer",
            "docs/note.md",
            "documentation",
            "Outside Contributor",
            "outside@example.org",
            "2025-03-02",
        )

        transformer = self.repositories["ops-transformer"]
        self._git(transformer, "checkout", "-q", "-b", "feature")
        self._commit(
            "ops-transformer",
            "ffn/feature.py",
            "partner operator",
            "Partner Engineer",
            "partner@h-partners.com",
            "2025-03-10",
        )
        self._git(transformer, "checkout", "-q", "master")
        self._commit(
            "ops-transformer",
            "docs/master.md",
            "master documentation",
            "Alice",
            "alice@huawei.com",
            "2025-03-15",
        )
        merge_environment = os.environ.copy()
        merge_environment.update(
            {
                "GIT_AUTHOR_NAME": "Alice",
                "GIT_AUTHOR_EMAIL": "alice@huawei.com",
                "GIT_AUTHOR_DATE": "2025-04-01T12:00:00+00:00",
                "GIT_COMMITTER_NAME": "Test Committer",
                "GIT_COMMITTER_EMAIL": "committer@example.test",
                "GIT_COMMITTER_DATE": "2025-04-01T12:00:00+00:00",
            }
        )
        self._git(
            transformer,
            "merge",
            "-q",
            "--no-ff",
            "feature",
            "-m",
            "Merge feature",
            env=merge_environment,
        )
        future_hash = self._commit(
            "ops-transformer",
            "moe/future.py",
            "future authored work",
            "Future Partner",
            "future@huawei-partners.com",
            "2025-05-01",
            committer_date="2025-04-15",
        )

        self._commit(
            "ops-math",
            "math/operator.py",
            "partner math",
            "Math Partner",
            "math@huawei-partners.com",
            "2025-01-20",
        )
        self._commit(
            "ops-math",
            "conversion/generated.py",
            "automated conversion",
            "Release Robot",
            "release@huawei.com",
            "2025-02-20",
        )

        self._commit(
            "catlass",
            "include/catlass.h",
            "catlass include",
            "Alice",
            "alice@huawei.com",
            "2025-01-25",
        )
        return future_hash

    def test_pipeline_cutoff_tiers_merge_core_paths_and_determinism(self):
        future_hash = self._populate_repositories()
        output_one = self.root / "output-one"
        output_two = self.root / "output-two"
        cutoff = date(2025, 4, 30)

        miner.run_pipeline(self.repos_dir, output_one, cutoff)
        miner.run_pipeline(self.repos_dir, output_two, cutoff)

        for filename in miner.OUTPUT_FILENAMES:
            self.assertEqual(
                (output_one / filename).read_bytes(),
                (output_two / filename).read_bytes(),
                filename,
            )

        summary = json.loads((output_one / "gitcode_summary.json").read_text())
        self.assertEqual(summary["as_of"], "2025-04-30")
        self.assertEqual(summary["date_basis"], "author_date")
        self.assertEqual(summary["ref"], "master")
        self.assertIn("linkable pseudonyms", summary["privacy_note"])
        self.assertEqual(summary["totals"]["total_commits"], 9)
        self.assertEqual(
            summary["totals"]["author_date_range"],
            ["2025-01-02", "2025-04-01"],
        )
        self.assertEqual(
            summary["totals"]["unique_pseudonymous_author_identities"], 6
        )
        self.assertEqual(
            {
                tier: values["commits"]
                for tier, values in summary["totals"]["domain_tiers"].items()
            },
            {
                "automation": 2,
                "huawei_domain": 4,
                "other": 1,
                "partner_domain": 2,
            },
        )
        self.assertEqual(summary["totals"]["non_merge_non_automation_commits"], 6)
        self.assertEqual(summary["totals"]["core_path_commits"], 4)
        self.assertEqual(summary["totals"]["core_path_share"], 0.666667)
        self.assertEqual(
            summary["totals"]["monthly_counts"],
            {"2025-01": 3, "2025-02": 2, "2025-03": 3, "2025-04": 1},
        )

        for repository, repo_summary in summary["repositories"].items():
            self.assertEqual(repo_summary["ref"], "master")
            self.assertEqual(
                repo_summary["origin_url"],
                f"https://gitcode.com/cann/{repository}.git",
            )
            self.assertEqual(
                repo_summary["resolved_sha"],
                self._git(self.repositories[repository], "rev-parse", "master"),
            )

        commit_lines = (output_one / "gitcode_commits.jsonl").read_text().splitlines()
        records = [json.loads(line) for line in commit_lines]
        self.assertEqual(len(records), 9)
        self.assertFalse(any(record["hash"] == future_hash for record in records))
        self.assertFalse(any("email" in record or "name" in record for record in records))
        self.assertNotIn("alice@huawei.com", "\n".join(commit_lines).lower())
        self.assertNotIn("@", "\n".join(commit_lines))
        self.assertIn("[redacted-email]", "\n".join(commit_lines))

        merge = next(record for record in records if record["subject"] == "Merge feature")
        self.assertTrue(merge["is_merge"])
        attention = next(
            record for record in records if record["subject"].startswith("core change")
        )
        documentation = next(
            record for record in records if record["subject"] == "documentation"
        )
        robot = next(
            record for record in records if record["subject"] == "automated conversion"
        )
        self.assertTrue(attention["touches_core"])
        self.assertEqual(attention["top_level_dirs"], ["attention"])
        self.assertFalse(documentation["touches_core"])
        self.assertEqual(documentation["top_level_dirs"], ["docs"])
        self.assertEqual(merge["top_level_dirs"], [])
        self.assertEqual(robot["domain_tier"], "automation")
        self.assertTrue(robot["is_automation"])

        with (output_one / "gitcode_monthly.csv").open(newline="") as source:
            monthly_rows = list(csv.DictReader(source))
        january_total = next(
            row
            for row in monthly_rows
            if row["repository"] == "ALL" and row["month"] == "2025-01"
        )
        self.assertEqual(january_total["total_commits"], "3")
        self.assertEqual(january_total["core_path_commits"], "3")

        self._commit(
            "ops-transformer",
            "attention/backdated.py",
            "later backdated commit",
            "Alice",
            "alice@huawei.com",
            "2025-01-10",
            committer_date="2025-06-01",
        )
        moving_output = self.root / "moving-output"
        replay_output = self.root / "replay-output"
        miner.run_pipeline(self.repos_dir, moving_output, cutoff)
        self.assertEqual(
            json.loads((moving_output / "gitcode_summary.json").read_text())["totals"][
                "total_commits"
            ],
            10,
        )
        replay_shas = miner.load_replay_shas(output_one / "gitcode_summary.json")
        miner.run_pipeline(
            self.repos_dir, replay_output, cutoff, replay_shas=replay_shas
        )
        for filename in miner.OUTPUT_FILENAMES:
            self.assertEqual(
                (output_one / filename).read_bytes(),
                (replay_output / filename).read_bytes(),
                f"fixed-SHA replay changed {filename}",
            )

    def test_automation_name_rule_matches_tokens_not_substrings(self):
        for name, email, expected_tier, expected_automation in (
            ("cann-robot", "cann@cann.team", "automation", True),
            ("ascend-robot", "someone@huawei.com", "automation", True),
            ("i-robot", "ci@example.org", "automation", True),
            ("dependabot[bot]", "x@users.noreply.github.com", "automation", True),
            ("dev-botany", "dev-botany@h-partners.com", "partner_domain", False),
            ("sampleRobotics_QA", "sample-robotics@huawei.com", "huawei_domain", False),
            ("Abbott", "abbott@example.org", "other", False),
        ):
            tier, is_automation = miner._classify_domain_tier(name, email)
            self.assertEqual((tier, is_automation), (expected_tier, expected_automation), name)

    def test_missing_repository_fails_without_creating_outputs(self):
        self._commit(
            "ops-transformer",
            "attention/a.py",
            "initial",
            "Alice",
            "alice@huawei.com",
            "2025-01-01",
        )
        self._commit(
            "ops-math",
            "math/a.py",
            "initial",
            "Alice",
            "alice@huawei.com",
            "2025-01-01",
        )
        catlass_path = self.repositories["catlass"]
        catlass_path.rename(self.root / "catlass-away")
        output = self.root / "output"

        with self.assertRaisesRegex(miner.PipelineError, "missing repository catlass"):
            miner.run_pipeline(self.repos_dir, output, date(2025, 1, 31))
        self.assertFalse(output.exists())

    def test_non_public_or_wrong_origin_is_rejected(self):
        self._commit(
            "ops-transformer",
            "attention/a.py",
            "initial",
            "Alice",
            "alice@huawei.com",
            "2025-01-01",
        )
        self._git(
            self.repositories["ops-transformer"],
            "remote",
            "set-url",
            "origin",
            "git@gitcode.com:cann/ops-transformer.git",
        )

        with self.assertRaisesRegex(miner.PipelineError, "public HTTPS GitCode URL"):
            miner.run_pipeline(self.repos_dir, self.root / "output", date(2025, 1, 31))

    def test_shallow_clone_is_rejected(self):
        self._commit(
            "ops-transformer",
            "attention/a.py",
            "first",
            "Alice",
            "alice@huawei.com",
            "2025-01-01",
        )
        self._commit(
            "ops-transformer",
            "attention/b.py",
            "second",
            "Alice",
            "alice@huawei.com",
            "2025-01-02",
        )
        original = self.repositories["ops-transformer"]
        shallow = self.root / "shallow-ops-transformer"
        self._git(
            None,
            "clone",
            "-q",
            "--depth=1",
            original.as_uri(),
            str(shallow),
        )
        self._git(
            shallow,
            "remote",
            "set-url",
            "origin",
            "https://gitcode.com/cann/ops-transformer.git",
        )
        original.rename(self.root / "full-ops-transformer-away")
        shallow.rename(original)

        with self.assertRaisesRegex(miner.PipelineError, "shallow clone"):
            miner.run_pipeline(self.repos_dir, self.root / "output", date(2025, 1, 31))

    def test_log_marker_cannot_collide_with_a_changed_path(self):
        raw_log = (
            miner.LOG_MARKER
            + b"a" * 40
            + b"\x00"
            + b"2025-01-01T00:00:00+00:00\x00Alice\x00alice@example.org\x00\x00subject\x00\n"
            + b"GITCODE_ACTIVITY_COMMIT\x00"
        )

        records = miner._parse_log("ops-transformer", raw_log, date(2025, 1, 31))
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0]["touches_core"])


if __name__ == "__main__":
    unittest.main()
