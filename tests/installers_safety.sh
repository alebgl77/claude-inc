#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/claude-inc-installer-tests.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
assert_file_text() { [ "$(cat "$1")" = "$2" ] || fail "unexpected content in $1"; }
pass_case() { printf 'ok: %s\n' "$1"; }
hash_test_file() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi; }
test_mode() { if stat -c '%a' "$1" >/dev/null 2>&1; then stat -c '%a' "$1"; else stat -f '%Lp' "$1"; fi; }

make_fixture() {
  local fixture="$1"
  mkdir -p "$fixture/skills/alpha" "$fixture/skills/beta" "$fixture/agents" "$fixture/commands" "$fixture/onboarding" "$fixture/bin" "$fixture/.claude-plugin"
  cp "$REPO_ROOT/install.sh" "$fixture/install.sh"
  printf 'alpha-v1\n' >"$fixture/skills/alpha/data.txt"
  printf '# Alpha\n' >"$fixture/skills/alpha/SKILL.md"
  printf '# Beta\n' >"$fixture/skills/beta/SKILL.md"
  printf 'agent-v1\n' >"$fixture/agents/head.md"
  printf 'command-v1\n' >"$fixture/commands/company.md"
  printf '# Onboarding\n' >"$fixture/onboarding/ONBOARDING.md"
  printf '{"name":"fixture"}\n' >"$fixture/.claude-plugin/plugin.json"
  printf '#!/usr/bin/env bash\nif [ "${1:-}" = version ]; then echo "company v1.2.0"; else echo company; fi\n' >"$fixture/bin/company"
  chmod +x "$fixture/bin/company"
}

run_global() {
  local fixture="$1" home="$2"; shift 2
  HOME="$home" bash "$fixture/install.sh" "$@" >/dev/null
}

run_remote() {
  local installer="$1" home="$2" cache="$3" repository="$4"; shift 4
  HOME="$home" CLAUDE_INC_HOME="$cache" CLAUDE_INC_REPO_URL="$repository" bash -s -- "$@" <"$installer" >/dev/null
}

expect_failure() {
  if "$@" >"$TEST_ROOT/failure.out" 2>&1; then fail "command unexpectedly succeeded: $*"; fi
  grep -Eqi 'collision|modified|symbolic|special|unsafe|reparse|lock|executable|changed|hook|recovery|invalid|canonical|incomplete|appeared|cleanup' "$TEST_ROOT/failure.out" || fail "failure was not actionable"
}

# Clean install, path with spaces, CLI symlink, manifest, and idempotence.
fixture="$TEST_ROOT/source with spaces"; home="$TEST_ROOT/home with spaces"
make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home"
pass_case "clean install and idempotence"
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v1
  assert_file_text "$home/.claude/agents/head.md" agent-v1
assert_file_text "$home/.claude/commands/company.md" command-v1
[ -L "$home/.local/bin/company" ] || fail "CLI is not a symlink"
[ -f "$home/.claude/.claude-inc-manifest-v1" ] || fail "manifest missing"
grep -Fq $'cli\tcompany\tsymlink\t' "$home/.claude/.claude-inc-cli-manifest-v1" || fail "CLI type and target missing from global CLI manifest"
run_global "$fixture" "$home"

# An intact managed entry can update.
printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"
printf 'command-v2\n' >"$fixture/commands/company.md"
run_global "$fixture" "$home"
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v2
assert_file_text "$home/.claude/commands/company.md" command-v2
pass_case "managed update"

# File claims preserve modes that cannot be expressed through a 0666 create.
case "$(uname -s)" in
  MINGW*|MSYS*) pass_case "file claim mode checks skipped on Windows emulation" ;;
  *)
    mode_fixture="$TEST_ROOT/file mode source"; mode_home="$TEST_ROOT/file mode home"; make_fixture "$mode_fixture"; mkdir -p "$mode_home"
    chmod 755 "$mode_fixture/agents/head.md"; chmod 700 "$mode_fixture/commands/company.md"
    run_global "$mode_fixture" "$mode_home" --no-bin
    assert_file_text "$mode_home/.claude/agents/head.md" agent-v1
    assert_file_text "$mode_home/.claude/commands/company.md" command-v1
    [ "$(test_mode "$mode_home/.claude/agents/head.md")" = 755 ] || fail "agent claim lost executable mode"
    [ "$(test_mode "$mode_home/.claude/commands/company.md")" = 700 ] || fail "command claim lost staged mode"
    run_global "$mode_fixture" "$mode_home" --no-bin
    pass_case "agent and command file claim modes"
    ;;
esac

# A modified managed file blocks the whole update and remains unchanged.
printf 'user-agent\n' >"$home/.claude/agents/head.md"
printf 'alpha-v3\n' >"$fixture/skills/alpha/data.txt"
expect_failure run_global "$fixture" "$home"
assert_file_text "$home/.claude/agents/head.md" user-agent
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v2
pass_case "managed modification refusal"

# An extra file in a managed directory is a modification.
fixture="$TEST_ROOT/extra source"; home="$TEST_ROOT/extra home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin
assert_file_text "$home/.claude/commands/company.md" command-v1
printf 'extra\n' >"$home/.claude/skills/alpha/user.txt"
expect_failure run_global "$fixture" "$home" --no-bin
[ -f "$home/.claude/skills/alpha/user.txt" ] || fail "extra file was removed"
pass_case "extra file refusal"

# Divergent unmanaged skill collision remains untouched.
fixture="$TEST_ROOT/skill source"; home="$TEST_ROOT/skill home"; make_fixture "$fixture"
mkdir -p "$home/.claude/skills/alpha"; printf 'user-skill\n' >"$home/.claude/skills/alpha/data.txt"
expect_failure run_global "$fixture" "$home" --no-bin
assert_file_text "$home/.claude/skills/alpha/data.txt" user-skill
[ ! -e "$home/.claude/agents/head.md" ] || fail "partial agent install after skill collision"
pass_case "skill collision"

# Divergent unmanaged agent collision remains untouched.
fixture="$TEST_ROOT/agent source"; home="$TEST_ROOT/agent home"; make_fixture "$fixture"
mkdir -p "$home/.claude/agents"; printf 'user-agent\n' >"$home/.claude/agents/head.md"
expect_failure run_global "$fixture" "$home" --no-bin
assert_file_text "$home/.claude/agents/head.md" user-agent
[ ! -e "$home/.claude/skills/alpha" ] || fail "partial skill install after agent collision"
pass_case "agent collision"

# A late CLI collision prevents every earlier planned copy.
fixture="$TEST_ROOT/cli source"; home="$TEST_ROOT/cli home"; make_fixture "$fixture"
mkdir -p "$home/.local/bin"; printf 'user-cli\n' >"$home/.local/bin/company"
expect_failure run_global "$fixture" "$home"
assert_file_text "$home/.local/bin/company" user-cli
[ ! -e "$home/.claude" ] || fail "target mutated before late CLI collision"
pass_case "late CLI collision"

# A legacy v1.2 layout is adopted only when every entry is identical.
fixture="$TEST_ROOT/adopt source"; home="$TEST_ROOT/adopt home"; make_fixture "$fixture"
mkdir -p "$home/.claude/skills" "$home/.claude/agents" "$home/.local/bin"
cp -R "$fixture/skills/alpha" "$home/.claude/skills/alpha"
cp "$fixture/agents/head.md" "$home/.claude/agents/head.md"
ln -s "$fixture/bin/company" "$home/.local/bin/company"
run_global "$fixture" "$home"
[ -f "$home/.claude/.claude-inc-manifest-v1" ] || fail "legacy layout was not adopted"
pass_case "legacy adoption"

# Symlinks inside skills and special destination files fail closed.
fixture="$TEST_ROOT/types source"; home="$TEST_ROOT/types home"; make_fixture "$fixture"
mkdir -p "$home/.claude/skills/alpha" "$home/external"; printf 'outside\n' >"$home/external/data.txt"
ln -s "$home/external/data.txt" "$home/.claude/skills/alpha/data.txt"
expect_failure run_global "$fixture" "$home" --no-bin
[ -L "$home/.claude/skills/alpha/data.txt" ] || fail "skill symlink was changed"
pass_case "skill symlink refusal"

case "$(uname -s)" in
  MINGW*|MSYS*) pass_case "special file refusal skipped on Windows emulation" ;;
  *)
    fixture="$TEST_ROOT/special source"; home="$TEST_ROOT/special home"; make_fixture "$fixture"
    mkdir -p "$home/.claude/agents"; mkfifo "$home/.claude/agents/head.md"
    expect_failure run_global "$fixture" "$home" --no-bin
    [ -p "$home/.claude/agents/head.md" ] || fail "special file was changed"
    pass_case "special file refusal"
    ;;
esac

# Project scope and --no-bin do not touch global destinations.
fixture="$TEST_ROOT/project source"; home="$TEST_ROOT/project home"; project="$TEST_ROOT/project with spaces"
make_fixture "$fixture"; mkdir -p "$home" "$project"
(cd "$project" && HOME="$home" bash "$fixture/install.sh" --project --no-bin >/dev/null)
assert_file_text "$project/.claude/skills/alpha/data.txt" alpha-v1
assert_file_text "$project/.claude/commands/company.md" command-v1
[ ! -e "$home/.local/bin/company" ] || fail "--no-bin installed a CLI"
[ ! -e "$project/CLAUDE.md" ] || fail "installer unexpectedly copied root CLAUDE.md"
pass_case "project no-bin and paths with spaces"

fixture="$TEST_ROOT/project cli source"; home="$TEST_ROOT/project cli home"; project="$TEST_ROOT/project cli workspace"
make_fixture "$fixture"; mkdir -p "$home" "$project"
(cd "$project" && HOME="$home" bash "$fixture/install.sh" --project >/dev/null)
! grep -q $'^cli\t' "$project/.claude/.claude-inc-manifest-v1" || fail "project manifest claimed global CLI"
grep -q $'^cli\t' "$home/.claude/.claude-inc-cli-manifest-v1" || fail "project install did not record global CLI ownership"
pass_case "project CLI ownership separation"

# A late command collision blocks all earlier planned copies.
fixture="$TEST_ROOT/command source"; home="$TEST_ROOT/command home"; make_fixture "$fixture"
mkdir -p "$home/.claude/commands"; printf 'user-command\n' >"$home/.claude/commands/company.md"
expect_failure run_global "$fixture" "$home" --no-bin
assert_file_text "$home/.claude/commands/company.md" user-command
[ ! -e "$home/.claude/skills/alpha" ] || fail "partial install before command collision"
pass_case "command collision"

# A non-canonical manifest is rejected before it can influence stale pruning.
fixture="$TEST_ROOT/malicious manifest source"; home="$TEST_ROOT/malicious manifest home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin
manifest="$home/.claude/.claude-inc-manifest-v1"
printf 'claude-inc-manifest-v1\nskill\t.\tdir\t%064d\ncommand\t../company.md\tfile\t%064d\n' 0 0 >"$manifest"
manifest_before="$(hash_test_file "$manifest")"
expect_failure run_global "$fixture" "$home" --no-bin
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v1
[ "$(hash_test_file "$manifest")" = "$manifest_before" ] || fail "invalid manifest was modified"
pass_case "malicious manifest refusal"

# An incomplete local runtime is rejected before target creation.
fixture="$TEST_ROOT/incomplete local source"; home="$TEST_ROOT/incomplete local home"; make_fixture "$fixture"; rm "$fixture/onboarding/ONBOARDING.md"; mkdir -p "$home"
expect_failure run_global "$fixture" "$home" --no-bin
[ ! -e "$home/.claude" ] || fail "incomplete local source mutated target"
pass_case "incomplete local runtime refusal"

# A held lock refuses the installation before target mutation.
fixture="$TEST_ROOT/lock source"; home="$TEST_ROOT/lock home"; make_fixture "$fixture"
mkdir -p "$home/.claude.claude-inc-install.lock"
expect_failure run_global "$fixture" "$home" --no-bin
[ ! -e "$home/.claude" ] || fail "lock refusal mutated target"
rm -rf "$home/.claude.claude-inc-install.lock"
pass_case "exclusive lock"

# A TOCTOU mutation after staging is caught immediately before entry apply.
fixture="$TEST_ROOT/toctou source"; home="$TEST_ROOT/toctou home"; make_fixture "$fixture"; mkdir -p "$home"
hook="$TEST_ROOT/toctou-hook.sh"
printf '#!/usr/bin/env bash\nif [ "$1" = before-entry ] && [ "$2" = skill ]; then mkdir -p "$4"; printf race > "$4/user.txt"; fi\n' >"$hook"; chmod +x "$hook"
expect_failure env CLAUDE_INC_TEST_HOOK="$hook" HOME="$home" bash "$fixture/install.sh" --no-bin
assert_file_text "$home/.claude/skills/alpha/user.txt" race
pass_case "TOCTOU refusal"

# A manifest modified after its snapshot blocks the apply and is not overwritten.
fixture="$TEST_ROOT/manifest race source"; home="$TEST_ROOT/manifest race home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"
hook="$TEST_ROOT/manifest-race-hook.sh"
printf '#!/usr/bin/env bash\nif [ "$1" = after-stage ]; then printf "externally changed\\n" > "$4/.claude-inc-manifest-v1"; fi\n' >"$hook"; chmod +x "$hook"
expect_failure env CLAUDE_INC_TEST_HOOK="$hook" HOME="$home" bash "$fixture/install.sh" --no-bin
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v1
assert_file_text "$home/.claude/.claude-inc-manifest-v1" 'externally changed'
pass_case "manifest snapshot race refusal"

# Content created after backup is never overwritten and the old backup is retained.
fixture="$TEST_ROOT/post-backup race source"; home="$TEST_ROOT/post-backup race home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"
hook="$TEST_ROOT/post-backup-race-hook.sh"
printf '#!/usr/bin/env bash\nif [ "$1" = after-backup ] && [ "$2" = skill ] && [ "$3" = alpha ]; then mkdir "$4"; printf external > "$4/external.txt"; fi\n' >"$hook"; chmod +x "$hook"
expect_failure env CLAUDE_INC_TEST_HOOK="$hook" HOME="$home" bash "$fixture/install.sh" --no-bin
assert_file_text "$home/.claude/skills/alpha/external.txt" external
recovery="$(find "$home/.claude" -maxdepth 1 -type d -name '.claude-inc-rollback.*' -print -quit)"
[ -n "$recovery" ] || fail "post-backup race did not retain recovery directory"
assert_file_text "$recovery/skills/alpha/data.txt" alpha-v1
rm -rf "$home/.claude/skills/alpha" "$recovery" "$home/.claude.claude-inc-install.lock"
pass_case "post-backup no-clobber refusal"

# The file claim also refuses a command created after its old copy was backed up.
fixture="$TEST_ROOT/command post-backup source"; home="$TEST_ROOT/command post-backup home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'command-v2\n' >"$fixture/commands/company.md"
hook="$TEST_ROOT/command-post-backup-hook.sh"
printf '#!/usr/bin/env bash\nif [ "$1" = after-backup ] && [ "$2" = command ]; then printf external > "$4"; fi\n' >"$hook"; chmod +x "$hook"
expect_failure env CLAUDE_INC_TEST_HOOK="$hook" HOME="$home" bash "$fixture/install.sh" --no-bin
assert_file_text "$home/.claude/commands/company.md" external
recovery="$(find "$home/.claude" -maxdepth 1 -type d -name '.claude-inc-rollback.*' -print -quit)"
[ -n "$recovery" ] || fail "command no-clobber race did not retain recovery directory"
assert_file_text "$recovery/commands/company.md" command-v1
rm -f "$home/.claude/commands/company.md"; rm -rf "$recovery" "$home/.claude.claude-inc-install.lock"
pass_case "command post-backup no-clobber refusal"

# Apply failure restores the old bytes and removes all temporary manifests.
fixture="$TEST_ROOT/apply failure source"; home="$TEST_ROOT/apply failure home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"
hook="$TEST_ROOT/apply-failure-hook.sh"
printf '#!/usr/bin/env bash\nif [ "$1" = after-backup ] && [ "$2" = skill ] && [ "$3" = alpha ]; then exit 1; fi\n' >"$hook"; chmod +x "$hook"
expect_failure env CLAUDE_INC_TEST_HOOK="$hook" HOME="$home" bash "$fixture/install.sh" --no-bin
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v1
! find "$home/.claude" -maxdepth 1 \( -name '*.tmp.*' -o -name '.claude-inc-rollback.*' \) -print | grep -q . || fail "successful rollback left temporary data"
pass_case "apply rollback"

# Restoration failure retains its backup, journal, and lock for manual recovery.
fixture="$TEST_ROOT/restore failure source"; home="$TEST_ROOT/restore failure home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"
hook="$TEST_ROOT/restore-failure-hook.sh"
printf '#!/usr/bin/env bash\nif [ "$2" = skill ] && [ "$3" = alpha ] && { [ "$1" = after-backup ] || [ "$1" = before-restore ]; }; then exit 1; fi\n' >"$hook"; chmod +x "$hook"
expect_failure env CLAUDE_INC_TEST_HOOK="$hook" HOME="$home" bash "$fixture/install.sh" --no-bin
recovery="$(find "$home/.claude" -maxdepth 1 -type d -name '.claude-inc-rollback.*' -print -quit)"
[ -n "$recovery" ] || fail "failed restoration did not retain recovery directory"
[ -f "$recovery/skills/alpha/data.txt" ] || fail "failed restoration did not retain backup"
[ -f "$recovery/journal.tsv" ] || fail "failed restoration did not retain journal"
[ -d "$home/.claude.claude-inc-install.lock" ] || fail "failed restoration did not retain lock"
rm -rf "$recovery" "$home/.claude.claude-inc-install.lock" "$home/.claude/skills/alpha"
pass_case "failed restoration retention"

# Upstream removal prunes intact managed entries and blocks modified ones.
fixture="$TEST_ROOT/remove source"; home="$TEST_ROOT/remove home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; rm -rf "$fixture/skills/alpha"; run_global "$fixture" "$home" --no-bin
[ ! -e "$home/.claude/skills/alpha" ] || fail "intact upstream removal was not pruned"
fixture="$TEST_ROOT/remove modified source"; home="$TEST_ROOT/remove modified home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'user-skill\n' >"$home/.claude/skills/alpha/data.txt"; rm -rf "$fixture/skills/alpha"
expect_failure run_global "$fixture" "$home" --no-bin; assert_file_text "$home/.claude/skills/alpha/data.txt" user-skill
pass_case "upstream removals"

# Unix modes are ownership data, and a non-executable CLI source is rejected.
case "$(uname -s)" in
  MINGW*|MSYS*) pass_case "Unix mode checks skipped on Windows emulation" ;;
  *)
    fixture="$TEST_ROOT/mode source"; home="$TEST_ROOT/mode home"; make_fixture "$fixture"; mkdir -p "$home"
    run_global "$fixture" "$home" --no-bin; chmod 600 "$home/.claude/skills/alpha/data.txt"
    expect_failure run_global "$fixture" "$home" --no-bin; [ "$(stat -c '%a' "$home/.claude/skills/alpha/data.txt" 2>/dev/null || stat -f '%Lp' "$home/.claude/skills/alpha/data.txt")" = 600 ] || fail "local mode was overwritten"
    chmod 644 "$home/.claude/skills/alpha/data.txt"; chmod 700 "$home/.claude/skills/alpha"
    expect_failure run_global "$fixture" "$home" --no-bin; [ "$(stat -c '%a' "$home/.claude/skills/alpha" 2>/dev/null || stat -f '%Lp' "$home/.claude/skills/alpha")" = 700 ] || fail "local skill root mode was overwritten"
    fixture="$TEST_ROOT/nonexec source"; home="$TEST_ROOT/nonexec home"; make_fixture "$fixture"; mkdir -p "$home"; chmod -x "$fixture/bin/company"
    expect_failure run_global "$fixture" "$home"; [ ! -e "$home/.claude" ] || fail "non-executable source mutated target"
    pass_case "Unix mode and executable source checks"
    ;;
esac

# TERM during apply invokes cleanup once and restores the unique backup.
fixture="$TEST_ROOT/signal source"; home="$TEST_ROOT/signal home"; make_fixture "$fixture"; mkdir -p "$home"
run_global "$fixture" "$home" --no-bin; printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"
hook="$TEST_ROOT/signal-hook.sh"; cleanup_log="$TEST_ROOT/cleanup.log"
printf '#!/usr/bin/env bash\nif [ "$1" = after-backup ] && [ "$2" = skill ] && [ "$3" = alpha ]; then kill -TERM "$PPID"; fi\n' >"$hook"; chmod +x "$hook"
set +e
CLAUDE_INC_TEST_HOOK="$hook" CLAUDE_INC_TEST_CLEANUP_LOG="$cleanup_log" HOME="$home" bash "$fixture/install.sh" --no-bin >"$TEST_ROOT/signal.out" 2>&1
signal_code=$?
set -e
[ "$signal_code" -eq 143 ] || fail "TERM did not preserve exit 143: $signal_code"
[ "$(wc -l <"$cleanup_log" | tr -d ' ')" -eq 1 ] || fail "cleanup ran more than once"
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v1
pass_case "signal cleanup once"

# A held cache lock blocks remote work before cloning or touching a target.
fixture="$TEST_ROOT/cache lock origin"; cache="$TEST_ROOT/locked cache"; home="$TEST_ROOT/cache lock home"; make_fixture "$fixture"
git -C "$fixture" init >/dev/null; git -C "$fixture" config user.email tests@example.com; git -C "$fixture" config user.name 'Installer Tests'; git -C "$fixture" config commit.gpgsign false
git -C "$fixture" add -f .; git -C "$fixture" commit -m v1 >/dev/null
mkdir -p "$home" "$cache.claude-inc-cache.lock"
expect_failure run_remote "$REPO_ROOT/install.sh" "$home" "$cache" "$fixture" --no-bin
[ ! -e "$home/.claude" ] || fail "cache lock refusal mutated target"
! find "$TEST_ROOT" -maxdepth 1 -type d -name 'locked cache.candidate.*' -print | grep -q . || fail "cache lock refusal cloned a candidate"
rm -rf "$cache.claude-inc-cache.lock"
pass_case "remote cache lock refusal"

# While one remote install owns the cache lock, a second target cannot enter preflight.
cache="$TEST_ROOT/concurrent cache"; home="$TEST_ROOT/concurrent first home"; second_home="$TEST_ROOT/concurrent second home"; mkdir -p "$home" "$second_home"
hook="$TEST_ROOT/concurrent-cache-hook.sh"; second_out="$TEST_ROOT/concurrent-second.out"
printf '#!/usr/bin/env bash\nif [ "$1" = after-cache-lock ]; then env -u CLAUDE_INC_TEST_HOOK HOME="$SECOND_HOME" bash -s -- --no-bin < "$INSTALLER" > "$SECOND_OUT" 2>&1; code=$?; [ "$code" -ne 0 ] && grep -Eqi "cache lock|holds the remote cache lock" "$SECOND_OUT"; fi\n' >"$hook"; chmod +x "$hook"
SECOND_HOME="$second_home" SECOND_OUT="$second_out" INSTALLER="$REPO_ROOT/install.sh" CLAUDE_INC_TEST_HOOK="$hook" run_remote "$REPO_ROOT/install.sh" "$home" "$cache" "$fixture" --no-bin
[ -f "$home/.claude/skills/alpha/data.txt" ] || fail "first concurrent installer did not complete"
[ ! -e "$second_home/.claude" ] || fail "second concurrent installer mutated its target"
pass_case "remote cache concurrency serialization"

# A candidate missing runtime payload is rejected without changing the active cache.
good_origin="$TEST_ROOT/good runtime origin"; bad_origin="$TEST_ROOT/missing runtime origin"; cache="$TEST_ROOT/existing runtime cache"; home="$TEST_ROOT/missing runtime home"
make_fixture "$good_origin"; git -C "$good_origin" init >/dev/null; git -C "$good_origin" config user.email tests@example.com; git -C "$good_origin" config user.name 'Installer Tests'; git -C "$good_origin" config commit.gpgsign false; git -C "$good_origin" add -f .; git -C "$good_origin" commit -m good >/dev/null
make_fixture "$bad_origin"; rm "$bad_origin/onboarding/ONBOARDING.md"; git -C "$bad_origin" init >/dev/null; git -C "$bad_origin" config user.email tests@example.com; git -C "$bad_origin" config user.name 'Installer Tests'; git -C "$bad_origin" config commit.gpgsign false; git -C "$bad_origin" add -f .; git -C "$bad_origin" commit -m incomplete >/dev/null
git clone "$good_origin" "$cache" >/dev/null; cache_before="$(git -C "$cache" rev-parse HEAD)"; mkdir -p "$home"
expect_failure run_remote "$REPO_ROOT/install.sh" "$home" "$cache" "$bad_origin" --no-bin
[ "$(git -C "$cache" rev-parse HEAD)" = "$cache_before" ] || fail "incomplete candidate changed active cache"
[ ! -e "$home/.claude" ] || fail "incomplete candidate mutated target"
! find "$TEST_ROOT" -maxdepth 1 -type d -name 'existing runtime cache.candidate.*' -print | grep -q . || fail "incomplete candidate was retained"
pass_case "incomplete remote runtime refusal"

# A spoofed legacy CLI link is not adopted from an unauthenticated cache.
fixture="$TEST_ROOT/legacy origin"; make_fixture "$fixture"; git -C "$fixture" init >/dev/null; git -C "$fixture" config user.email tests@example.com; git -C "$fixture" config user.name 'Installer Tests'; git -C "$fixture" config commit.gpgsign false; git -C "$fixture" add -f .; git -C "$fixture" commit -m legacy >/dev/null
cache="$TEST_ROOT/spoofed legacy cache"; home="$TEST_ROOT/spoofed legacy home"; git clone "$fixture" "$cache" >/dev/null; printf '# dirty\n' >>"$cache/bin/company"; mkdir -p "$home/.local/bin"
ln -s "$cache/bin/company" "$home/.local/bin/company"; spoof_before="$(readlink "$home/.local/bin/company")"
expect_failure run_remote "$REPO_ROOT/install.sh" "$home" "$cache" "$fixture"
[ "$(readlink "$home/.local/bin/company")" = "$spoof_before" ] || fail "spoofed legacy CLI link changed"
[ ! -e "$home/.claude" ] || fail "spoofed legacy adoption mutated target"
pass_case "spoofed legacy CLI refusal"

# A clean legacy checkout with the expected remote and HEAD is adopted.
cache="$TEST_ROOT/authentic legacy cache"; home="$TEST_ROOT/authentic legacy home"; git clone "$fixture" "$cache" >/dev/null; mkdir -p "$home/.local/bin"
ln -s "$cache/bin/company" "$home/.local/bin/company"
run_remote "$REPO_ROOT/install.sh" "$home" "$cache" "$fixture"
grep -Fq $'cli\tcompany\tsymlink\t' "$home/.claude/.claude-inc-cli-manifest-v1" || fail "authentic legacy CLI ownership was not recorded"
canonical_cache="$(cd -P "$cache" >/dev/null 2>&1 && pwd)" || fail "authentic legacy cache could not be canonicalized"
case "$(readlink "$home/.local/bin/company")" in "${canonical_cache}.checkouts"/*/bin/company) : ;; *) fail "authentic legacy CLI did not move to immutable checkout" ;; esac
pass_case "authentic legacy CLI adoption"

# A blocked remote upgrade leaves the active cache, CLI link, and destinations unchanged.
fixture="$TEST_ROOT/remote origin"; active="$TEST_ROOT/active cache"; home="$TEST_ROOT/remote home"
make_fixture "$fixture"
git -C "$fixture" init >/dev/null; git -C "$fixture" config user.email tests@example.com; git -C "$fixture" config user.name 'Installer Tests'; git -C "$fixture" config commit.gpgsign false
git -C "$fixture" add -f .; git -C "$fixture" commit -m v1 >/dev/null
git clone "$fixture" "$active" >/dev/null; mkdir -p "$home"
HOME="$home" bash "$active/install.sh" >/dev/null
active_before="$(hash_test_file "$active/skills/alpha/data.txt")"; cli_before="$(readlink "$home/.local/bin/company")"
printf 'alpha-v2\n' >"$fixture/skills/alpha/data.txt"; git -C "$fixture" add -f .; git -C "$fixture" commit -m v2 >/dev/null
printf 'user-command\n' >"$home/.claude/commands/company.md"
set +e
HOME="$home" CLAUDE_INC_HOME="$active" CLAUDE_INC_REPO_URL="file://$fixture" bash -s -- <"$REPO_ROOT/install.sh" >"$TEST_ROOT/remote.out" 2>&1
remote_code=$?
set -e
[ "$remote_code" -ne 0 ] || fail "blocked remote upgrade unexpectedly succeeded"
[ "$(hash_test_file "$active/skills/alpha/data.txt")" = "$active_before" ] || fail "blocked remote upgrade changed active cache"
[ "$(readlink "$home/.local/bin/company")" = "$cli_before" ] || fail "blocked remote upgrade changed CLI link"
assert_file_text "$home/.claude/skills/alpha/data.txt" alpha-v1; assert_file_text "$home/.claude/commands/company.md" user-command
[ ! -e "$active.checkouts" ] || fail "blocked remote upgrade promoted a checkout"
! find "$TEST_ROOT" -maxdepth 1 -type d -name 'active cache.candidate.*' -print | grep -q . || fail "blocked remote upgrade left a candidate"
pass_case "blocked remote upgrade"

printf 'Bash installer safety tests passed\n'
