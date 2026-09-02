#!/usr/bin/env bash
# Claude, Inc. installer: puts 8 departments and 50 employees on your payroll.
# Flags: --project, --no-bin, --onboard
set -euo pipefail

REPO_URL="${CLAUDE_INC_REPO_URL:-https://github.com/alebgl77/claude-inc}"
: "${HOME:?HOME must be set}"
CLONE_DIR="${CLAUDE_INC_HOME:-$HOME/.claude-inc}"
MANIFEST_VERSION="claude-inc-manifest-v1"
MANIFEST_NAME=".claude-inc-manifest-v1"
CLI_MANIFEST_NAME=".claude-inc-cli-manifest-v1"

die() { printf 'claude-inc: %s\n' "$*" >&2; exit 1; }
need_command() { command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"; }
remove_known_path() { if [ -L "$1" ] || [ -f "$1" ]; then rm -f "$1"; elif [ -d "$1" ]; then rm -rf "$1"; fi; }

PROJECT="no"; NO_BIN="no"; ONBOARD="no"
for argument in "$@"; do
  case "$argument" in
    --project) PROJECT="yes" ;;
    --no-bin) NO_BIN="yes" ;;
    --onboard) ONBOARD="yes" ;;
    *) die "unknown flag: $argument" ;;
  esac
done

for command in dirname basename mkdir cp rm mv find sort awk mktemp stat cat ln; do need_command "$command"; done
if [ "$NO_BIN" = "no" ]; then need_command readlink; fi
if command -v sha256sum >/dev/null 2>&1; then HASH_TOOL="sha256sum"
elif command -v shasum >/dev/null 2>&1; then HASH_TOOL="shasum"
elif command -v openssl >/dev/null 2>&1; then HASH_TOOL="openssl"
else die "a SHA-256 tool is required (sha256sum, shasum, or openssl)"; fi
if stat -c '%a' "$HOME" >/dev/null 2>&1; then MODE_STYLE="gnu"
elif stat -f '%Lp' "$HOME" >/dev/null 2>&1; then MODE_STYLE="bsd"
else die "stat cannot read Unix file modes"; fi

if [ -t 1 ]; then B=$'\033[1m'; OR=$'\033[38;5;208m'; G=$'\033[32m'; R=$'\033[0m'; else B=""; OR=""; G=""; R=""; fi
say() { printf '%s\n' "${OR}${B}claude-inc${R} $*"; }

sha256_file() {
  case "$HASH_TOOL" in
    sha256sum) sha256sum "$1" | awk '{print tolower($1)}' ;;
    shasum) shasum -a 256 "$1" | awk '{print tolower($1)}' ;;
    openssl) openssl dgst -sha256 "$1" | awk '{print tolower($NF)}' ;;
  esac
}

file_mode() { if [ "$MODE_STYLE" = "gnu" ]; then stat -c '%a' "$1"; else stat -f '%Lp' "$1"; fi; }
sha256_text() {
  local temporary digest
  temporary="$(mktemp "${TMPDIR:-/tmp}/claude-inc-text.XXXXXX")" || return 1
  printf '%s' "$1" >"$temporary"; digest="$(sha256_file "$temporary")" || { rm -f "$temporary"; return 1; }
  rm -f "$temporary"; printf '%s\n' "$digest"
}

reject_unsafe_field() { case "$1" in *$'\t'*|*$'\n'*|*$'\r'*) die "unsupported tab or newline in managed name or path: $1" ;; esac; }

fingerprint_file() {
  local content mode
  [ ! -L "$1" ] || { printf 'symbolic links are not allowed here: %s\n' "$1" >&2; return 1; }
  [ -f "$1" ] || { printf 'expected a regular file: %s\n' "$1" >&2; return 1; }
  content="$(sha256_file "$1")" || return 1; mode="$(file_mode "$1")" || return 1
  sha256_text "F\t$mode\t$content\n"
}

fingerprint_directory() {
  local path="$1" index entry relative digest
  [ ! -L "$path" ] || { printf 'symbolic links are not allowed here: %s\n' "$path" >&2; return 1; }
  [ -d "$path" ] || { printf 'expected a directory: %s\n' "$path" >&2; return 1; }
  index="$(mktemp "${TMPDIR:-/tmp}/claude-inc-tree.XXXXXX")" || return 1
  if ! (
    cd "$path"
    printf 'R\t%s\n' "$(file_mode .)"
    LC_ALL=C find . -mindepth 1 -print | LC_ALL=C sort | while IFS= read -r entry; do
      relative="${entry#./}"
      case "$relative" in *$'\t'*|*$'\n'*|*$'\r'*) printf 'unsupported name in managed directory: %s\n' "$path/$relative" >&2; exit 1 ;; esac
      if [ -L "$entry" ]; then printf 'symbolic links are not allowed inside managed directories: %s\n' "$path/$relative" >&2; exit 1
      elif [ -d "$entry" ]; then printf 'D\t%s\t%s\n' "$relative" "$(file_mode "$entry")"
      elif [ -f "$entry" ]; then digest="$(sha256_file "$entry")" || exit 1; printf 'F\t%s\t%s\t%s\n' "$relative" "$(file_mode "$entry")" "$digest"
      else printf 'special files are not allowed inside managed directories: %s\n' "$path/$relative" >&2; exit 1; fi
    done
  ) >"$index"; then rm -f "$index"; return 1; fi
  digest="$(sha256_file "$index")" || { rm -f "$index"; return 1; }
  rm -f "$index"; printf '%s\n' "$digest"
}

canonical_regular_file() {
  local directory base
  [ ! -L "$1" ] || { printf 'source file must not be a symbolic link: %s\n' "$1" >&2; return 1; }
  [ -f "$1" ] || { printf 'expected a regular file: %s\n' "$1" >&2; return 1; }
  directory="$(cd -P "$(dirname "$1")" >/dev/null 2>&1 && pwd)" || return 1
  base="$(basename "$1")"; printf '%s/%s\n' "$directory" "$base"
}

resolved_link_target() {
  local current="$1" raw directory base depth=0
  [ -L "$current" ] || return 1
  while [ -L "$current" ]; do
    depth=$((depth + 1)); [ "$depth" -le 40 ] || return 1
    raw="$(readlink "$current")" || return 1
    case "$raw" in /*) current="$raw" ;; *) current="$(dirname "$current")/$raw" ;; esac
    directory="$(cd -P "$(dirname "$current")" >/dev/null 2>&1 && pwd)" || return 1
    base="$(basename "$current")"; current="$directory/$base"
  done
  [ -f "$current" ] || { printf 'company CLI link does not resolve to a regular file: %s\n' "$1" >&2; return 1; }
  canonical_regular_file "$current"
}

assert_safe_container() {
  if [ -L "$1" ]; then die "$2 must not be a symbolic link: $1"
  elif [ -e "$1" ] && [ ! -d "$1" ]; then die "$2 must be a directory: $1"; fi
}

valid_slug() {
  case "$1" in ''|.|..|*[!a-z0-9-]*|-*|*-|*--*) return 1 ;; *) return 0 ;; esac
}

valid_managed_name() {
  local stem
  reject_unsafe_field "$2"
  case "$1" in
    skill) valid_slug "$2" ;;
    agent) case "$2" in *.md) stem="${2%.md}"; valid_slug "$stem" ;; *) return 1 ;; esac ;;
    command) [ "$2" = "company.md" ] ;;
    cli) [ "$2" = "company" ] ;;
    *) return 1 ;;
  esac
}

canonicalize_cache_path() {
  local path="$1" parent base
  case "$path" in /*) : ;; *) path="$(pwd)/$path" ;; esac
  if [ -d "$path" ] && [ ! -L "$path" ]; then (cd -P "$path" >/dev/null 2>&1 && pwd); return; fi
  parent="$(dirname "$path")"; base="$(basename "$path")"
  [ "$base" != "." ] && [ "$base" != ".." ] || return 1
  parent="$(cd -P "$parent" >/dev/null 2>&1 && pwd)" || return 1
  printf '%s/%s\n' "$parent" "$base"
}

validate_runtime_payload() {
  local root="$1" count=0 directory name file
  for directory in skills agents commands onboarding bin .claude-plugin; do
    assert_safe_container "$root/$directory" "$directory source"
    [ -d "$root/$directory" ] || die "incomplete source payload, missing directory: $root/$directory"
  done
  for file in install.sh bin/company commands/company.md onboarding/ONBOARDING.md .claude-plugin/plugin.json; do
    fingerprint_file "$root/$file" >/dev/null || die "incomplete or unsafe source payload, required file missing: $root/$file"
  done
  [ -x "$root/bin/company" ] || die "company CLI source is not executable; fix its mode before installing: $root/bin/company"
  for directory in "$root"/skills/*/; do
    [ -d "$directory" ] || continue; directory="${directory%/}"; name="$(basename "$directory")"
    valid_managed_name skill "$name" || die "non-canonical skill source name: $name"
    fingerprint_file "$directory/SKILL.md" >/dev/null || die "incomplete skill runtime payload: $directory/SKILL.md"
    count=$((count + 1))
  done
  [ "$count" -gt 0 ] || die "incomplete source payload: no skills found in $root/skills"
  count=0
  for file in "$root"/agents/*.md; do
    [ -f "$file" ] || continue; name="$(basename "$file")"
    valid_managed_name agent "$name" || die "non-canonical agent source name: $name"
    fingerprint_file "$file" >/dev/null || die "unsafe agent runtime payload: $file"
    count=$((count + 1))
  done
  [ "$count" -gt 0 ] || die "incomplete source payload: no agents found in $root/agents"
}

runtime_payload_matches() {
  local left="$1" right="$2" directory file
  validate_runtime_payload "$left"; validate_runtime_payload "$right"
  for directory in skills agents commands onboarding; do
    [ "$(fingerprint_directory "$left/$directory")" = "$(fingerprint_directory "$right/$directory")" ] || return 1
  done
  for file in bin/company install.sh .claude-plugin/plugin.json; do
    [ "$(fingerprint_file "$left/$file")" = "$(fingerprint_file "$right/$file")" ] || return 1
  done
}

authenticated_legacy_cli_target() {
  local root="$1" expected_remote="$2" origin head blob actual status mode
  [ -d "$root/.git" ] && [ ! -L "$root" ] || return 1
  origin="$(git -C "$root" config --get remote.origin.url 2>/dev/null)" || return 1
  [ "$origin" = "$expected_remote" ] || return 1
  head="$(git -C "$root" rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || return 1
  case "$head" in *[!0-9a-fA-F]*|'') return 1 ;; esac
  status="$(git -C "$root" status --porcelain --untracked-files=normal 2>/dev/null)" || return 1
  [ -z "$status" ] || return 1
  blob="$(git -C "$root" rev-parse 'HEAD:bin/company' 2>/dev/null)" || return 1
  actual="$(git -C "$root" hash-object -- bin/company 2>/dev/null)" || return 1
  [ "$blob" = "$actual" ] || return 1
  mode="$(git -C "$root" ls-tree HEAD -- bin/company 2>/dev/null | awk 'NR == 1 { print $1 }')"
  [ "$mode" = "100755" ] || return 1
  canonical_regular_file "$root/bin/company"
}

run_test_hook() {
  [ -n "${CLAUDE_INC_TEST_HOOK:-}" ] || return 0
  if ! "$CLAUDE_INC_TEST_HOOK" "$@"; then
    printf 'claude-inc: test hook failed at %s for %s/%s\n' "${1:-unknown}" "${2:-unknown}" "${3:-unknown}" >&2
    return 1
  fi
}

# Resolve the source. A remote update is cloned separately and never pulls the active cache.
REMOTE_MODE="no"; REMOTE_CANDIDATE=""; REMOTE_FINAL=""; REMOTE_FINAL_WAS_NEW="no"
LEGACY_CLI_TARGET=""; CLI_TARGET_DESIRED=""; CACHE_LOCK=""; CACHE_LOCK_HELD="no"
SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"; SCRIPT_DIR=""
if [ -n "$SCRIPT_SOURCE" ] && [ -f "$SCRIPT_SOURCE" ]; then SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_SOURCE")" >/dev/null 2>&1 && pwd || true)"; fi
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/install.sh" ] && [ ! -L "$SCRIPT_DIR/install.sh" ]; then
  SRC="$SCRIPT_DIR"; validate_runtime_payload "$SRC"; say "installing from local checkout: $SRC"
else
  need_command git
  CLONE_DIR="$(canonicalize_cache_path "$CLONE_DIR")" || die "cache parent must already exist and be canonicalizable: $CLONE_DIR"
  CACHE_LOCK="${CLONE_DIR}.claude-inc-cache.lock"
  REMOTE_MODE="yes"; REMOTE_CANDIDATE="${CLONE_DIR}.candidate.$$.$RANDOM"
  bootstrap_release() {
    [ -n "$REMOTE_CANDIDATE" ] && remove_known_path "$REMOTE_CANDIDATE" || true
    if [ "$CACHE_LOCK_HELD" = "yes" ]; then remove_known_path "$CACHE_LOCK" || true; CACHE_LOCK_HELD="no"; fi
  }
  bootstrap_signal() { local code="$1"; trap - EXIT HUP INT TERM; bootstrap_release; exit "$code"; }
  bootstrap_exit() { local code=$?; trap - EXIT HUP INT TERM; bootstrap_release; exit "$code"; }
  trap bootstrap_exit EXIT
  trap 'bootstrap_signal 129' HUP; trap 'bootstrap_signal 130' INT; trap 'bootstrap_signal 143' TERM
  if ! mkdir "$CACHE_LOCK" 2>/dev/null; then die "another installation holds the remote cache lock: $CACHE_LOCK"; fi
  CACHE_LOCK_HELD="yes"
  run_test_hook after-cache-lock cache cache "$CLONE_DIR" "$CACHE_LOCK"
  if [ -e "$CLONE_DIR" ] && [ ! -d "$CLONE_DIR/.git" ]; then die "cache path exists but is not a git checkout: $CLONE_DIR"; fi
  if [ -d "$CLONE_DIR/.git" ]; then
    LEGACY_CLI_TARGET="$(authenticated_legacy_cli_target "$CLONE_DIR" "$REPO_URL" 2>/dev/null || true)"
  fi
  [ ! -e "$REMOTE_CANDIDATE" ] || die "temporary checkout path already exists: $REMOTE_CANDIDATE"
  say "cloning immutable candidate from $REPO_URL"
  if ! git clone --depth 1 "$REPO_URL" "$REMOTE_CANDIDATE" >/dev/null; then
    remove_known_path "$REMOTE_CANDIDATE" || true; REMOTE_CANDIDATE=""; trap - HUP INT TERM; die "failed to clone remote candidate"
  fi
  trap - HUP INT TERM
  REMOTE_COMMIT="$(git -C "$REMOTE_CANDIDATE" rev-parse HEAD)" || die "cannot resolve candidate commit"
  case "$REMOTE_COMMIT" in *[!0-9a-fA-F]*|'') die "invalid candidate commit: $REMOTE_COMMIT" ;; esac
  REMOTE_FINAL="${CLONE_DIR}.checkouts/$REMOTE_COMMIT"
  SRC="$REMOTE_CANDIDATE"; validate_runtime_payload "$SRC"; CLI_TARGET_DESIRED="$REMOTE_FINAL/bin/company"
fi

if [ "$NO_BIN" = "no" ] && [ ! -x "$SRC/bin/company" ]; then
  die "company CLI source is not executable; fix its mode before installing: $SRC/bin/company"
fi

if [ "$PROJECT" = "yes" ]; then TARGET="$(pwd)/.claude"; else TARGET="$HOME/.claude"; fi
TARGET_SKILLS="$TARGET/skills"; TARGET_AGENTS="$TARGET/agents"; TARGET_COMMANDS="$TARGET/commands"
MANIFEST="$TARGET/$MANIFEST_NAME"; CLI_DEST="$HOME/.local/bin/company"; CLI_MANIFEST="$HOME/.claude/$CLI_MANIFEST_NAME"
PLAN="$(mktemp "${TMPDIR:-/tmp}/claude-inc-plan.XXXXXX")"
PROPOSED="$(mktemp "${TMPDIR:-/tmp}/claude-inc-manifest.XXXXXX")"
CLI_PROPOSED="$(mktemp "${TMPDIR:-/tmp}/claude-inc-cli-manifest.XXXXXX")"
MANIFEST_SNAPSHOT="absent"; CLI_MANIFEST_SNAPSHOT="absent"
STAGE=""; ROLLBACK=""; APPLIED=""; COMMITTED="no"; CLEANUP_RAN="no"; ROLLBACK_FAILED="no"; MANIFEST_TEMP=""; CLI_MANIFEST_TEMP=""; CLI_STAGE_LINK=""
TARGET_LOCK="$TARGET.claude-inc-install.lock"; CLI_LOCK="$HOME/.claude-inc-cli-install.lock"; TARGET_LOCK_HELD="no"; CLI_LOCK_HELD="no"

destination_for() {
  case "$1" in
    skill) printf '%s/%s\n' "$TARGET_SKILLS" "$2" ;;
    agent) printf '%s/%s\n' "$TARGET_AGENTS" "$2" ;;
    command) printf '%s/%s\n' "$TARGET_COMMANDS" "$2" ;;
    cli) printf '%s\n' "$CLI_DEST" ;;
    meta-main) printf '%s\n' "$MANIFEST" ;;
    meta-cli) printf '%s\n' "$CLI_MANIFEST" ;;
    *) return 1 ;;
  esac
}
stage_path_for() {
  case "$1" in
    skill) printf '%s/skills/%s\n' "$STAGE" "$2" ;;
    agent) printf '%s/agents/%s\n' "$STAGE" "$2" ;;
    command) printf '%s/commands/%s\n' "$STAGE" "$2" ;;
    *) return 1 ;;
  esac
}
backup_path_for() {
  case "$1" in
    skill) printf '%s/skills/%s\n' "$ROLLBACK" "$2" ;;
    agent) printf '%s/agents/%s\n' "$ROLLBACK" "$2" ;;
    command) printf '%s/commands/%s\n' "$ROLLBACK" "$2" ;;
    cli) printf '%s/cli/company\n' "$ROLLBACK" ;;
    meta-main) printf '%s/manifests/main\n' "$ROLLBACK" ;;
    meta-cli) printf '%s/manifests/cli\n' "$ROLLBACK" ;;
    *) return 1 ;;
  esac
}

inspect_destination() {
  local target digest
  if [ -L "$2" ]; then
    [ "$1" = "cli" ] || { printf 'symbolic links are not allowed for managed %s: %s\n' "$1" "$2" >&2; return 1; }
    target="$(resolved_link_target "$2")" || return 1; reject_unsafe_field "$target"; printf 'symlink\t%s\n' "$target"
  elif [ -d "$2" ]; then digest="$(fingerprint_directory "$2")" || return 1; printf 'dir\t%s\n' "$digest"
  elif [ -f "$2" ]; then digest="$(fingerprint_file "$2")" || return 1; printf 'file\t%s\n' "$digest"
  elif [ -e "$2" ]; then printf 'special files are not allowed as managed destinations: %s\n' "$2" >&2; return 1
  else printf 'absent\t-\n'; fi
}

state_matches() {
  local state state_type state_value
  state="$(inspect_destination "$1" "$2")" || return 1
  state_type="${state%%$'\t'*}"; state_value="${state#*$'\t'}"
  [ "$state_type" = "$3" ] && [ "$state_value" = "$4" ]
}

rollback_changes() {
  local reverse kind name had_old prior_type prior_value desired_type desired_value destination backup failed="no"
  [ -n "$APPLIED" ] && [ -f "$APPLIED" ] || return 0
  reverse="$(mktemp "${TMPDIR:-/tmp}/claude-inc-rollback-order.XXXXXX")" || return 1
  awk '{ rows[NR]=$0 } END { for (i=NR; i>=1; i--) print rows[i] }' "$APPLIED" >"$reverse" || { rm -f "$reverse"; return 1; }
  while IFS=$'\t' read -r kind name had_old prior_type prior_value desired_type desired_value; do
    [ -n "$kind" ] || continue
    destination="$(destination_for "$kind" "$name")" || { failed="yes"; continue; }
    backup="$(backup_path_for "$kind" "$name")" || { failed="yes"; continue; }
    if ! run_test_hook before-restore "$kind" "$name" "$destination" "$backup"; then
      printf 'claude-inc: simulated or external restoration failure for %s/%s; backup retained at %s\n' "$kind" "$name" "$backup" >&2
      failed="yes"; continue
    fi
    if [ "$had_old" = "yes" ]; then
      if [ -e "$backup" ] || [ -L "$backup" ]; then
        if ! state_matches "$kind" "$backup" "$prior_type" "$prior_value"; then
          printf 'claude-inc: recovery backup failed verification: %s\n' "$backup" >&2; failed="yes"; continue
        fi
        if [ -e "$destination" ] || [ -L "$destination" ]; then
          if ! state_matches "$kind" "$destination" "$desired_type" "$desired_value"; then
            printf 'claude-inc: recovery refused to overwrite unexpected content: %s\n' "$destination" >&2; failed="yes"; continue
          fi
          if ! remove_known_path "$destination"; then failed="yes"; continue; fi
        fi
        mkdir -p "$(dirname "$destination")" || { failed="yes"; continue; }
        if ! mv "$backup" "$destination"; then printf 'claude-inc: restoration failed; backup retained at %s\n' "$backup" >&2; failed="yes"; continue; fi
        if ! state_matches "$kind" "$destination" "$prior_type" "$prior_value"; then printf 'claude-inc: restored destination failed verification: %s\n' "$destination" >&2; failed="yes"; fi
      elif ! state_matches "$kind" "$destination" "$prior_type" "$prior_value"; then
        printf 'claude-inc: required recovery backup is missing: %s\n' "$backup" >&2; failed="yes"
      fi
    else
      if [ -e "$backup" ] || [ -L "$backup" ]; then printf 'claude-inc: unexpected recovery backup retained at %s\n' "$backup" >&2; failed="yes"
      elif [ -e "$destination" ] || [ -L "$destination" ]; then
        if state_matches "$kind" "$destination" "$desired_type" "$desired_value"; then remove_known_path "$destination" || failed="yes"
        else printf 'claude-inc: recovery refused to remove unexpected content: %s\n' "$destination" >&2; failed="yes"; fi
      fi
    fi
  done <"$reverse"
  rm -f "$reverse"
  [ "$failed" = "no" ] || { ROLLBACK_FAILED="yes"; printf 'claude-inc: automatic recovery incomplete; retain and inspect %s\n' "$ROLLBACK" >&2; return 1; }
  return 0
}

cleanup_once() {
  local requested="$1" recovery_ok="yes"
  [ "$CLEANUP_RAN" = "no" ] || return 0
  CLEANUP_RAN="yes"
  if [ -n "${CLAUDE_INC_TEST_CLEANUP_LOG:-}" ]; then printf 'cleanup\n' >>"$CLAUDE_INC_TEST_CLEANUP_LOG" 2>/dev/null || true; fi
  if [ "$COMMITTED" != "yes" ] && ! rollback_changes; then recovery_ok="no"; fi
  [ -n "$STAGE" ] && remove_known_path "$STAGE" || true
  [ -n "$CLI_STAGE_LINK" ] && remove_known_path "$CLI_STAGE_LINK" || true
  [ -n "$REMOTE_CANDIDATE" ] && remove_known_path "$REMOTE_CANDIDATE" || true
  if [ "$COMMITTED" != "yes" ] && [ "$REMOTE_FINAL_WAS_NEW" = "yes" ] && [ "$recovery_ok" = "yes" ]; then remove_known_path "$REMOTE_FINAL" || true; fi
  if [ "$recovery_ok" = "yes" ]; then [ -n "$ROLLBACK" ] && remove_known_path "$ROLLBACK" || true
  elif [ -n "$ROLLBACK" ]; then printf 'claude-inc: recovery data preserved at %s\n' "$ROLLBACK" >&2; fi
  [ -n "$MANIFEST_TEMP" ] && remove_known_path "$MANIFEST_TEMP" || true
  [ -n "$CLI_MANIFEST_TEMP" ] && remove_known_path "$CLI_MANIFEST_TEMP" || true
  if [ "$recovery_ok" = "yes" ]; then
    if [ "$CLI_LOCK_HELD" = "yes" ]; then remove_known_path "$CLI_LOCK" || true; CLI_LOCK_HELD="no"; fi
    if [ "$TARGET_LOCK_HELD" = "yes" ]; then remove_known_path "$TARGET_LOCK" || true; TARGET_LOCK_HELD="no"; fi
    if [ "$CACHE_LOCK_HELD" = "yes" ]; then remove_known_path "$CACHE_LOCK" || true; CACHE_LOCK_HELD="no"; fi
  else
    printf 'claude-inc: installation locks retained until manual recovery completes: %s' "$TARGET_LOCK" >&2
    [ "$CLI_LOCK_HELD" = "yes" ] && printf ', %s' "$CLI_LOCK" >&2
    [ "$CACHE_LOCK_HELD" = "yes" ] && printf ', %s' "$CACHE_LOCK" >&2
    printf '\n' >&2
  fi
  rm -f "$PLAN" "$PROPOSED" "$CLI_PROPOSED" 2>/dev/null || true
  CLEANUP_STATUS="$requested"
  if [ "$recovery_ok" != "yes" ] && [ "$CLEANUP_STATUS" -eq 0 ]; then CLEANUP_STATUS=1; fi
}
on_exit() { local code=$?; trap - EXIT HUP INT TERM; set +e; cleanup_once "$code"; exit "$CLEANUP_STATUS"; }
on_signal() { local code="$1"; trap - EXIT HUP INT TERM; set +e; cleanup_once "$code"; exit "$CLEANUP_STATUS"; }
trap on_exit EXIT
trap 'on_signal 129' HUP
trap 'on_signal 130' INT
trap 'on_signal 143' TERM

if ! mkdir "$TARGET_LOCK" 2>/dev/null; then die "another installation holds the target lock: $TARGET_LOCK"; fi
TARGET_LOCK_HELD="yes"
if [ "$NO_BIN" = "no" ] && [ "$CLI_LOCK" != "$TARGET_LOCK" ]; then
  if ! mkdir "$CLI_LOCK" 2>/dev/null; then die "another installation holds the global CLI lock: $CLI_LOCK"; fi
  CLI_LOCK_HELD="yes"
fi

assert_safe_container "$TARGET" "install target"
assert_safe_container "$TARGET_SKILLS" "skills target"
assert_safe_container "$TARGET_AGENTS" "agents target"
assert_safe_container "$TARGET_COMMANDS" "commands target"
if [ "$NO_BIN" = "no" ]; then
  assert_safe_container "$HOME/.local" "CLI parent"; assert_safe_container "$HOME/.local/bin" "CLI directory"; assert_safe_container "$HOME/.claude" "global CLI ownership directory"
fi

load_manifest() {
  local path="$1" proposed="$2" scope="$3" snapshot
  if [ -L "$path" ]; then die "manifest must not be a symbolic link: $path"
  elif [ -e "$path" ]; then
    [ -f "$path" ] || die "manifest is not a regular file: $path"
    cp -p "$path" "$proposed" || die "cannot snapshot ownership manifest: $path"
    snapshot="$(fingerprint_file "$proposed")" || die "cannot fingerprint ownership manifest snapshot: $path"
    awk -F '\t' -v header="$MANIFEST_VERSION" -v scope="$scope" '
      function slug(value) { return value ~ /^[a-z0-9][a-z0-9-]*$/ && value !~ /^-/ && value !~ /-$/ && value !~ /--/ }
      NR == 1 { if ($0 != header) exit 10; next }
      NF != 4 { exit 11 }
      scope == "main" && $1 !~ /^(skill|agent|command)$/ { exit 12 }
      scope == "cli" && $1 != "cli" { exit 13 }
      $1 == "skill" && !slug($2) { exit 14 }
      $1 == "agent" && ($2 !~ /\.md$/ || !slug(substr($2, 1, length($2) - 3))) { exit 14 }
      $1 == "command" && $2 != "company.md" { exit 14 }
      $1 == "cli" && $2 != "company" { exit 14 }
      $3 !~ /^(dir|file|symlink)$/ { exit 15 }
      ($1 == "skill" && $3 != "dir") || (($1 == "agent" || $1 == "command") && $3 != "file") { exit 16 }
      $1 == "cli" && $3 != "symlink" { exit 16 }
      ($1 != "cli" && $3 == "symlink") { exit 17 }
      ($3 == "dir" || $3 == "file") && (length($4) != 64 || $4 !~ /^[0-9a-fA-F]+$/) { exit 18 }
      $3 == "symlink" && $4 !~ /^\// { exit 18 }
      { key=$1 "\t" $2; if (seen[key]++) exit 19 }
      END { if (NR < 1) exit 20 }
    ' "$proposed" || die "invalid or unsupported ownership manifest: $path"
    [ "$(fingerprint_file "$path")" = "$snapshot" ] || die "ownership manifest changed while it was being snapshotted: $path"
    printf 'file:%s\n' "$snapshot"
  else
    printf '%s\n' "$MANIFEST_VERSION" >"$proposed"; printf 'absent\n'
  fi
}
MANIFEST_SNAPSHOT="$(load_manifest "$MANIFEST" "$PROPOSED" main)"
if [ "$NO_BIN" = "no" ]; then CLI_MANIFEST_SNAPSHOT="$(load_manifest "$CLI_MANIFEST" "$CLI_PROPOSED" cli)"
else printf '%s\n' "$MANIFEST_VERSION" >"$CLI_PROPOSED"; fi

manifest_store_for() { if [ "$1" = "cli" ]; then printf '%s\n' "$CLI_PROPOSED"; else printf '%s\n' "$PROPOSED"; fi; }
manifest_record() { local store; store="$(manifest_store_for "$1")"; awk -F '\t' -v kind="$1" -v name="$2" '$1 == kind && $2 == name { print $3 "\t" $4; exit }' "$store"; }
set_manifest_record() {
  local store next; store="$(manifest_store_for "$1")"; next="$(mktemp "${TMPDIR:-/tmp}/claude-inc-manifest-next.XXXXXX")"
  awk -F '\t' -v kind="$1" -v name="$2" 'NR == 1 || !($1 == kind && $2 == name)' "$store" >"$next"
  if [ "$3" != "absent" ]; then printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >>"$next"; fi
  mv "$next" "$store"
}

plan_entry() {
  local destination current old current_type current_value old_type old_value migration="no"
  valid_managed_name "$1" "$2" || die "non-canonical managed name for $1: $2"
  reject_unsafe_field "$4"; destination="$(destination_for "$1" "$2")"
  current="$(inspect_destination "$1" "$destination")" || die "unsafe destination for $1 '$2': $destination"
  current_type="${current%%$'\t'*}"; current_value="${current#*$'\t'}"; old="$(manifest_record "$1" "$2")"
  if [ -n "$old" ]; then
    old_type="${old%%$'\t'*}"; old_value="${old#*$'\t'}"
    [ "$current_type" != "absent" ] || die "managed $1 '$2' is missing; restore it or remove its manifest entry before retrying"
    [ "$current_type" = "$old_type" ] && [ "$current_value" = "$old_value" ] || die "managed $1 '$2' was modified; no files were changed: $destination"
  elif [ "$current_type" != "absent" ]; then
    if [ "$1" = "cli" ] && [ -n "$LEGACY_CLI_TARGET" ] && [ "$current_type" = "symlink" ] && [ "$current_value" = "$LEGACY_CLI_TARGET" ]; then migration="yes"; fi
    if [ "$migration" != "yes" ]; then
      [ "$current_type" = "$3" ] && [ "$current_value" = "$4" ] || die "unmanaged collision for $1 '$2'; no files were changed. Move or remove it after review: $destination"
    fi
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$current_type" "$current_value" >>"$PLAN"
  set_manifest_record "$1" "$2" "$3" "$4"
}

# Preflight every source and destination before the first target mutation.
assert_safe_container "$SRC/skills" "skills source"; assert_safe_container "$SRC/agents" "agents source"; assert_safe_container "$SRC/commands" "commands source"
n_skills=0
for directory in "$SRC"/skills/*/; do [ -d "$directory" ] || continue; directory="${directory%/}"; name="$(basename "$directory")"; digest="$(fingerprint_directory "$directory")" || die "unsafe skill source: $directory"; plan_entry skill "$name" dir "$digest"; n_skills=$((n_skills + 1)); done
n_agents=0
for file in "$SRC"/agents/*.md; do [ -f "$file" ] || continue; name="$(basename "$file")"; digest="$(fingerprint_file "$file")" || die "unsafe agent source: $file"; plan_entry agent "$name" file "$digest"; n_agents=$((n_agents + 1)); done
COMMAND_SOURCE="$SRC/commands/company.md"; COMMAND_HASH="$(fingerprint_file "$COMMAND_SOURCE")" || die "unsafe /company command source: $COMMAND_SOURCE"
plan_entry command company.md file "$COMMAND_HASH"
if [ "$NO_BIN" = "no" ]; then
  [ -x "$SRC/bin/company" ] || die "company CLI source is not executable; fix its mode before installing: $SRC/bin/company"
  if [ -z "$CLI_TARGET_DESIRED" ]; then CLI_TARGET_DESIRED="$(canonical_regular_file "$SRC/bin/company")" || die "unsafe company CLI source: $SRC/bin/company"; fi
  reject_unsafe_field "$CLI_TARGET_DESIRED"; plan_entry cli company symlink "$CLI_TARGET_DESIRED"
fi

# Remove upstream entries only when their installed bytes still match ownership.
STALE_SCAN="$(mktemp "${TMPDIR:-/tmp}/claude-inc-stale.XXXXXX")"; cp "$PROPOSED" "$STALE_SCAN"
while IFS=$'\t' read -r kind name type value; do
  [ "$kind" != "$MANIFEST_VERSION" ] || continue
  if ! awk -F '\t' -v kind="$kind" -v name="$name" '$1 == kind && $2 == name { found=1 } END { exit !found }' "$PLAN"; then
    destination="$(destination_for "$kind" "$name")"
    current="$(inspect_destination "$kind" "$destination")" || die "unsafe stale destination for $kind '$name': $destination"
    current_type="${current%%$'\t'*}"; current_value="${current#*$'\t'}"
    [ "$current_type" = "$type" ] && [ "$current_value" = "$value" ] || die "upstream removed $kind '$name', but its installed copy was modified; no files were changed: $destination"
    printf '%s\t%s\tabsent\t-\t%s\t%s\n' "$kind" "$name" "$current_type" "$current_value" >>"$PLAN"
    set_manifest_record "$kind" "$name" absent -
  fi
done <"$STALE_SCAN"
rm -f "$STALE_SCAN"

verify_manifest_snapshot() {
  local path="$1" snapshot="$2" now
  if [ "$snapshot" = "absent" ]; then [ ! -e "$path" ] && [ ! -L "$path" ] || return 1
  else [ -f "$path" ] && [ ! -L "$path" ] || return 1; now="file:$(fingerprint_file "$path")"; [ "$now" = "$snapshot" ] || return 1; fi
}
verify_manifest_snapshots() {
  verify_manifest_snapshot "$MANIFEST" "$MANIFEST_SNAPSHOT" || die "ownership manifest changed during installation; retry"
  if [ "$NO_BIN" = "no" ]; then verify_manifest_snapshot "$CLI_MANIFEST" "$CLI_MANIFEST_SNAPSHOT" || die "CLI ownership manifest changed during installation; retry"; fi
}
verify_all_snapshots() {
  local kind name desired_type desired_value prior_type prior_value destination
  verify_manifest_snapshots
  while IFS=$'\t' read -r kind name desired_type desired_value prior_type prior_value; do
    [ -n "$kind" ] || continue; destination="$(destination_for "$kind" "$name")"
    state_matches "$kind" "$destination" "$prior_type" "$prior_value" || die "destination changed during installation; retry: $destination"
  done <"$PLAN"
}

# Stage all new content before replacing any destination.
verify_all_snapshots
mkdir -p "$TARGET"
STAGE="$(mktemp -d "$TARGET/.claude-inc-stage.XXXXXX")"; ROLLBACK="$(mktemp -d "$TARGET/.claude-inc-rollback.XXXXXX")"; APPLIED="$ROLLBACK/journal.tsv"; : >"$APPLIED"
mkdir -p "$STAGE/skills" "$STAGE/agents" "$STAGE/commands" "$ROLLBACK/skills" "$ROLLBACK/agents" "$ROLLBACK/commands" "$ROLLBACK/cli" "$ROLLBACK/manifests"
while IFS=$'\t' read -r kind name desired_type desired_value prior_type prior_value; do
  [ "$desired_type" != "absent" ] || continue
  case "$kind" in
    skill) cp -Rp "$SRC/skills/$name" "$STAGE/skills/$name"; [ "$(fingerprint_directory "$STAGE/skills/$name")" = "$desired_value" ] || die "staged skill verification failed: $name" ;;
    agent) cp -p "$SRC/agents/$name" "$STAGE/agents/$name"; [ "$(fingerprint_file "$STAGE/agents/$name")" = "$desired_value" ] || die "staged agent verification failed: $name" ;;
    command) cp -p "$SRC/commands/$name" "$STAGE/commands/$name"; [ "$(fingerprint_file "$STAGE/commands/$name")" = "$desired_value" ] || die "staged command verification failed: $name" ;;
  esac
done <"$PLAN"
run_test_hook after-stage none none "$TARGET" "$ROLLBACK"
verify_all_snapshots

# Promote a verified remote candidate to a new immutable checkout only after preflight.
if [ "$REMOTE_MODE" = "yes" ]; then
  if [ -e "$REMOTE_FINAL" ]; then
    [ -d "$REMOTE_FINAL" ] && [ ! -L "$REMOTE_FINAL" ] || die "immutable checkout path is unsafe: $REMOTE_FINAL"
    runtime_payload_matches "$REMOTE_FINAL" "$REMOTE_CANDIDATE" || die "immutable checkout runtime payload was modified or is incomplete: $REMOTE_FINAL"
    remove_known_path "$REMOTE_CANDIDATE"; REMOTE_CANDIDATE=""
  else
    mkdir -p "$(dirname "$REMOTE_FINAL")"
    mkdir "$REMOTE_FINAL" 2>/dev/null || die "immutable checkout appeared during promotion: $REMOTE_FINAL"
    REMOTE_FINAL_WAS_NEW="yes"
    cp -Rp "$REMOTE_CANDIDATE"/. "$REMOTE_FINAL"/
    runtime_payload_matches "$REMOTE_FINAL" "$REMOTE_CANDIDATE" || die "promoted immutable checkout failed runtime verification: $REMOTE_FINAL"
    remove_known_path "$REMOTE_CANDIDATE"; REMOTE_CANDIDATE=""
  fi
  SRC="$REMOTE_FINAL"
fi

claim_file_no_clobber() {
  local staged="$1" destination="$2" kind="$3" name="$4" desired="$5" mode permissions mask mask_text
  mode="$(file_mode "$staged")" || die "cannot read staged mode for $kind/$name"
  case "$mode" in [0-7][0-7][0-7]) : ;; *) die "unsupported staged file mode for atomic claim: $mode ($staged)" ;; esac
  permissions=$((0$mode)); mask=$((0777 ^ permissions)); mask_text="$(printf '%03o' "$mask")"
  if ! (umask "$mask_text"; set -o noclobber; cat "$staged" >"$destination") 2>/dev/null; then
    die "destination appeared after backup; no overwrite performed: $destination"
  fi
  state_matches "$kind" "$destination" file "$desired" || die "claimed file failed verification; recovery data retained: $destination"
  remove_known_path "$staged" || die "installed file verified but staged copy could not be removed: $staged"
}

claim_directory_no_clobber() {
  local staged="$1" destination="$2" kind="$3" name="$4" desired="$5" mode
  mode="$(file_mode "$staged")" || die "cannot read staged directory mode for $kind/$name"
  case "$mode" in [0-7][0-7][0-7]) : ;; *) die "unsupported staged directory mode for atomic claim: $mode ($staged)" ;; esac
  mkdir -m "$mode" "$destination" 2>/dev/null || die "destination appeared after backup; no overwrite performed: $destination"
  cp -Rp "$staged"/. "$destination"/
  state_matches "$kind" "$destination" dir "$desired" || die "claimed directory failed verification; recovery data retained: $destination"
  remove_known_path "$staged" || die "installed directory verified but staged copy could not be removed: $staged"
}

claim_symlink_no_clobber() {
  local destination="$1"
  if [ -e "$destination" ] || [ -L "$destination" ]; then die "destination appeared after backup; no overwrite performed: $destination"; fi
  ln -s "$CLI_TARGET_DESIRED" "$destination" || die "destination appeared while claiming CLI symlink; no overwrite performed: $destination"
  state_matches cli "$destination" symlink "$CLI_TARGET_DESIRED" || die "claimed CLI symlink failed verification; recovery data retained: $destination"
}

apply_prepared_entry() {
  local kind="$1" name="$2" desired_type="$3" desired_value="$4" prior_type="$5" prior_value="$6" staged="${7:-}"
  local destination backup had_old="no"
  destination="$(destination_for "$kind" "$name")"; backup="$(backup_path_for "$kind" "$name")"
  run_test_hook before-entry "$kind" "$name" "$destination" "$backup"
  state_matches "$kind" "$destination" "$prior_type" "$prior_value" || die "destination changed immediately before apply; no overwrite performed: $destination"
  [ "$prior_type" = "absent" ] || had_old="yes"
  mkdir -p "$(dirname "$destination")" "$(dirname "$backup")"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$kind" "$name" "$had_old" "$prior_type" "$prior_value" "$desired_type" "$desired_value" >>"$APPLIED"
  run_test_hook after-journal "$kind" "$name" "$destination" "$backup"
  if [ "$had_old" = "yes" ]; then mv "$destination" "$backup"; fi
  if [ "$had_old" = "yes" ]; then state_matches "$kind" "$backup" "$prior_type" "$prior_value" || die "backup verification failed immediately after move; recovery data retained at $backup"; fi
  run_test_hook after-backup "$kind" "$name" "$destination" "$backup"
  if [ "$desired_type" = "absent" ]; then :
  elif [ "$kind" = "cli" ]; then claim_symlink_no_clobber "$destination"
  elif [ "$desired_type" = "dir" ]; then claim_directory_no_clobber "$staged" "$destination" "$kind" "$name" "$desired_value"
  else claim_file_no_clobber "$staged" "$destination" "$kind" "$name" "$desired_value"; fi
  run_test_hook after-entry "$kind" "$name" "$destination" "$backup"
}

while IFS=$'\t' read -r kind name desired_type desired_value prior_type prior_value; do
  [ -n "$kind" ] || continue
  staged=""; if [ "$desired_type" != "absent" ] && [ "$kind" != "cli" ]; then staged="$(stage_path_for "$kind" "$name")"; fi
  apply_prepared_entry "$kind" "$name" "$desired_type" "$desired_value" "$prior_type" "$prior_value" "$staged"
done <"$PLAN"

# Commit both ownership files last through the same recovery journal.
verify_manifest_snapshots
if [ "$MANIFEST_SNAPSHOT" = "absent" ]; then MAIN_PRIOR_TYPE="absent"; MAIN_PRIOR_VALUE="-"; else MAIN_PRIOR_TYPE="file"; MAIN_PRIOR_VALUE="${MANIFEST_SNAPSHOT#file:}"; fi
MANIFEST_TEMP="$(mktemp "$TARGET/$MANIFEST_NAME.tmp.XXXXXX")"; cp "$PROPOSED" "$MANIFEST_TEMP"; MAIN_NEW_HASH="$(fingerprint_file "$MANIFEST_TEMP")"
apply_prepared_entry meta-main manifest file "$MAIN_NEW_HASH" "$MAIN_PRIOR_TYPE" "$MAIN_PRIOR_VALUE" "$MANIFEST_TEMP"; MANIFEST_TEMP=""
if [ "$NO_BIN" = "no" ]; then
  mkdir -p "$HOME/.claude"
  if [ "$CLI_MANIFEST_SNAPSHOT" = "absent" ]; then CLI_PRIOR_TYPE="absent"; CLI_PRIOR_VALUE="-"; else CLI_PRIOR_TYPE="file"; CLI_PRIOR_VALUE="${CLI_MANIFEST_SNAPSHOT#file:}"; fi
  CLI_MANIFEST_TEMP="$(mktemp "$HOME/.claude/$CLI_MANIFEST_NAME.tmp.XXXXXX")"; cp "$CLI_PROPOSED" "$CLI_MANIFEST_TEMP"; CLI_NEW_HASH="$(fingerprint_file "$CLI_MANIFEST_TEMP")"
  apply_prepared_entry meta-cli manifest file "$CLI_NEW_HASH" "$CLI_PRIOR_TYPE" "$CLI_PRIOR_VALUE" "$CLI_MANIFEST_TEMP"; CLI_MANIFEST_TEMP=""
fi

COMMITTED="yes"
if ! remove_known_path "$ROLLBACK"; then say "warning: installation succeeded but temporary recovery data could not be removed: $ROLLBACK"; else ROLLBACK=""; fi
remove_known_path "$STAGE" || true; STAGE=""

if [ "$NO_BIN" = "no" ]; then case ":$PATH:" in *":$HOME/.local/bin:"*) : ;; *) say "note: add ~/.local/bin to your PATH to use 'company'" ;; esac; fi
echo; say "${G}hired ${n_agents} department heads and ${n_skills} employees${R} -> $TARGET"; echo
echo "  ${B}Next:${R}"
if [ "$NO_BIN" = "no" ]; then echo "    company roster                       # meet the team"; echo "    company brief \"launch my product\"    # brief the CEO"; fi
echo "    claude                               # skills + agents + /company are live in Claude Code"; echo
echo "  ${B}Claude Code plugin route (alternative):${R}"; echo "    /plugin marketplace add alebgl77/claude-inc"; echo "    /plugin install claude-inc@claude-inc"

defer_install_onboarding() {
  if [ "$NO_BIN" = "yes" ]; then if [ "$PROJECT" = "yes" ]; then echo "Onboarding deferred. Install the Claude Code plugin, then run: /onboard"; else echo "Onboarding deferred. Install the Claude Code plugin, then run: /onboard --global"; fi
  elif [ "$PROJECT" = "yes" ]; then echo "Onboarding deferred. Run: company onboard"; else echo "Onboarding deferred. Run: company onboard --global"; fi
}
if [ "$ONBOARD" = "yes" ]; then
  ENGINE="${CLAUDE_INC_ENGINE:-claude}"
  if [ "$NO_BIN" = "no" ] && [ -t 0 ] && [ -t 1 ] && command -v "$ENGINE" >/dev/null 2>&1 && [ -f "$SRC/bin/company" ]; then
    if [ "$PROJECT" = "yes" ]; then if ! bash "$SRC/bin/company" onboard; then say "onboarding did not complete"; defer_install_onboarding; fi
    else if ! bash "$SRC/bin/company" onboard --global; then say "onboarding did not complete"; defer_install_onboarding; fi; fi
  else defer_install_onboarding; fi
fi
