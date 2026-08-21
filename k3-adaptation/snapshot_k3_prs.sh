#!/usr/bin/env bash
# Snapshot the Kimi-K3 discovery counts and the status of the manually
# classified Ascend/NPU-targeted Kimi-K3 pull requests.
#
# Caliber warning: discovery counts are RAW full-text search matches (PRs
# that merely mention "Kimi-K3" are included). They are an upper bound, not
# a curated list of adaptation PRs. The case-set statuses are limited to the
# pull requests listed in CASE_PRS, which were classified manually from the
# frozen 2026-07-26..2026-08-01 candidate window under the rule in METHOD.md.
#
# Requires: gh (authenticated, read-only), python3.
set -euo pipefail

DATE=$(date +%F)
OUT="${1:-$(dirname "$0")/snapshots/${DATE}.json}"
mkdir -p "$(dirname "$OUT")"

QUERY="Kimi-K3"
LIMIT=300
REPOS=(
  vllm-project/vllm
  sgl-project/sglang
  vllm-project/vllm-ascend
)

# Manually classified Ascend/NPU-targeted Kimi-K3 pull requests
# (repo:number). Selection rule and classification table: METHOD.md.
CASE_PRS=(
  sgl-project/sglang:32544
  sgl-project/sglang:32604
  vllm-project/vllm-ascend:12950
  vllm-project/vllm-ascend:12951
  vllm-project/vllm-ascend:12952
  vllm-project/vllm-ascend:12953
  vllm-project/vllm-ascend:13036
  vllm-project/vllm-ascend:13037
  vllm-project/vllm-ascend:13041
  vllm-project/vllm-ascend:13065
  vllm-project/vllm-ascend:13071
  vllm-project/vllm-ascend:13143
  vllm-project/vllm-ascend:13225
  vllm-project/vllm-ascend:13277
  vllm-project/vllm-ascend:13286
  vllm-project/vllm-ascend:13315
  vllm-project/vllm-ascend:13323
)

WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

# All gh output goes through files, never through shell string interpolation,
# so titles containing quotes or backslashes cannot corrupt the JSON.
SEARCH_MANIFEST="$WORKDIR/search.tsv"
CASE_MANIFEST="$WORKDIR/cases.tsv"
: > "$SEARCH_MANIFEST"
: > "$CASE_MANIFEST"

i=0
for repo in "${REPOS[@]}"; do
  i=$((i + 1))
  file="$WORKDIR/search-$i.json"
  gh search prs "$QUERY" --repo "$repo" --limit "$LIMIT" --json number > "$file"
  printf '%s\t%s\n' "$repo" "$file" >> "$SEARCH_MANIFEST"
done

i=0
for pair in "${CASE_PRS[@]}"; do
  i=$((i + 1))
  repo="${pair%:*}"
  number="${pair##*:}"
  file="$WORKDIR/pr-$i.json"
  gh pr view "$number" --repo "$repo" \
    --json number,title,state,createdAt,mergedAt,updatedAt,closedAt > "$file"
  printf '%s\t%s\n' "$repo" "$file" >> "$CASE_MANIFEST"
done

RETRIEVED_AT_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 - "$OUT" "$DATE" "$RETRIEVED_AT_UTC" "$QUERY" "$LIMIT" "$SEARCH_MANIFEST" "$CASE_MANIFEST" <<'EOF'
import json
import sys

out_path, date, retrieved_at_utc, query, limit_text, search_manifest, case_manifest = sys.argv[1:8]
limit = int(limit_text)


def read_manifest(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            repo, _, file_path = line.rstrip("\n").partition("\t")
            yield repo, file_path


repos = {}
for repo, file_path in read_manifest(search_manifest):
    with open(file_path, encoding="utf-8") as handle:
        matches = len(json.load(handle))
    repos[repo] = {"raw_matches": matches, "limit_reached": matches >= limit}

cases = []
for repo, file_path in read_manifest(case_manifest):
    with open(file_path, encoding="utf-8") as handle:
        record = json.load(handle)
    record["repo"] = repo
    cases.append(record)
cases.sort(key=lambda record: (record["repo"], record["number"]))

output = {
    "date": date,
    "retrieved_at_utc": retrieved_at_utc,
    "query": f"{query} (raw full-text PR search, limit {limit})",
    "repos": repos,
    "total_raw_matches": sum(entry["raw_matches"] for entry in repos.values()),
    "case_prs": cases,
}
with open(out_path, "w", encoding="utf-8") as handle:
    json.dump(output, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
print(json.dumps(output, indent=2, ensure_ascii=False))
EOF
