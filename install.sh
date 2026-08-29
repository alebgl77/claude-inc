#!/usr/bin/env bash
# Claude, Inc. installer: puts 8 departments and 50 employees on your payroll.
#   curl -fsSL https://raw.githubusercontent.com/alebgl77/claude-inc/main/install.sh | bash
# Requires Bash and standard macOS/Linux tools. Git is required only when the
# installer is not running from a local checkout.
# Flags:
#   --project   install into ./.claude (current project) instead of ~/.claude
#   --no-bin    skip installing the 'company' CLI into ~/.local/bin
#   --onboard   optionally configure an active team after installation
set -euo pipefail

REPO_URL="${CLAUDE_INC_REPO_URL:-https://github.com/alebgl77/claude-inc}"
: "${HOME:?HOME must be set}"
CLONE_DIR="${CLAUDE_INC_HOME:-$HOME/.claude-inc}"

die() { printf 'claude-inc: %s\n' "$*" >&2; exit 1; }
need_command() { command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"; }

PROJECT="no"; NO_BIN="no"; ONBOARD="no"
for a in "$@"; do
  case "$a" in
    --project) PROJECT="yes" ;;
    --no-bin)  NO_BIN="yes" ;;
    --onboard) ONBOARD="yes" ;;
    *) echo "unknown flag: $a" >&2; exit 1 ;;
  esac
done

for command in dirname mkdir cp rm basename; do need_command "$command"; done
if [ "$NO_BIN" = "no" ]; then
  need_command ln
  need_command chmod
fi

if [ -t 1 ]; then B=$'\033[1m'; OR=$'\033[38;5;208m'; G=$'\033[32m'; R=$'\033[0m'; else B=""; OR=""; G=""; R=""; fi
say() { printf '%s\n' "${OR}${B}claude-inc${R} $*"; }

# --- locate source: already inside the repo, or clone/update it -------------
SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"
SCRIPT_DIR=""
if [ -n "$SCRIPT_SOURCE" ] && [ -f "$SCRIPT_SOURCE" ]; then
  SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_SOURCE")" >/dev/null 2>&1 && pwd || true)"
fi
if [ -n "$SCRIPT_DIR" ] \
  && [ -d "$SCRIPT_DIR/skills" ] \
  && [ -d "$SCRIPT_DIR/agents" ] \
  && { [ -f "$SCRIPT_DIR/bin/company" ] || [ "$NO_BIN" = "yes" ]; } \
  && [ -f "$SCRIPT_DIR/.claude-plugin/plugin.json" ]; then
  SRC="$SCRIPT_DIR"
  say "installing from local checkout: $SRC"
else
  need_command git
  if [ -d "$CLONE_DIR/.git" ]; then
    say "updating $CLONE_DIR"
    git -C "$CLONE_DIR" pull --ff-only >/dev/null
  else
    [ ! -e "$CLONE_DIR" ] || die "cache path exists but is not a git checkout: $CLONE_DIR"
    say "cloning $REPO_URL -> $CLONE_DIR"
    git clone --depth 1 "$REPO_URL" "$CLONE_DIR" >/dev/null
  fi
  SRC="$CLONE_DIR"
fi

# --- target ------------------------------------------------------------------
if [ "$PROJECT" = "yes" ]; then TARGET="$(pwd)/.claude"; else TARGET="$HOME/.claude"; fi
mkdir -p "$TARGET/skills" "$TARGET/agents"

# --- hire everyone -----------------------------------------------------------
n_skills=0
for d in "$SRC"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "$TARGET/skills/$name"
  cp -R "$d" "$TARGET/skills/$name"
  n_skills=$((n_skills + 1))
done

n_agents=0
for f in "$SRC"/agents/*.md; do
  cp "$f" "$TARGET/agents/$(basename "$f")"
  n_agents=$((n_agents + 1))
done

# CEO manual: only meaningful per-project
if [ "$PROJECT" = "yes" ] && [ ! -f "$(pwd)/CLAUDE.md" ]; then
  cp "$SRC/CLAUDE.md" "$(pwd)/CLAUDE.md"
  say "CEO manual installed as ./CLAUDE.md"
fi

# --- the company CLI ---------------------------------------------------------
if [ "$NO_BIN" = "no" ]; then
  [ -f "$SRC/bin/company" ] || die "company CLI not found in source: $SRC/bin/company"
  mkdir -p "$HOME/.local/bin"
  ln -sf "$SRC/bin/company" "$HOME/.local/bin/company"
  chmod +x "$SRC/bin/company"
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) : ;;
    *) say "note: add ~/.local/bin to your PATH to use 'company'" ;;
  esac
fi

echo
say "${G}hired ${n_agents} department heads and ${n_skills} employees${R} -> $TARGET"
echo
echo "  ${B}Next:${R}"
if [ "$NO_BIN" = "no" ]; then
  echo "    company roster                       # meet the team"
  echo "    company brief \"launch my product\"    # brief the CEO"
fi
echo "    claude                               # skills + agents are live in Claude Code"
echo
echo "  ${B}Claude Code plugin route (alternative):${R}"
echo "    /plugin marketplace add alebgl77/claude-inc"
echo "    /plugin install claude-inc@claude-inc"

defer_install_onboarding() {
  local scope_flag=""
  [ "$PROJECT" = "yes" ] || scope_flag=" --global"
  if [ "$NO_BIN" = "yes" ] && [ -f "$SRC/bin/company" ]; then
    echo "Onboarding deferred. Run: bash \"$SRC/bin/company\" onboard${scope_flag}"
  elif [ "$NO_BIN" = "yes" ]; then
    if [ "$PROJECT" = "yes" ]; then
      echo "Onboarding deferred. Install the Claude Code plugin, then run: /onboard"
    else
      echo "Onboarding deferred. Install the Claude Code plugin, then run: /onboard --global"
    fi
  elif [ "$PROJECT" = "yes" ]; then
    echo "Onboarding deferred. Run: company onboard"
  else
    echo "Onboarding deferred. Run: company onboard --global"
  fi
}

if [ "$ONBOARD" = "yes" ]; then
  ENGINE="${CLAUDE_INC_ENGINE:-claude}"
  if [ -t 0 ] && [ -t 1 ] && command -v "$ENGINE" >/dev/null 2>&1 && [ -f "$SRC/bin/company" ]; then
    if [ "$PROJECT" = "yes" ]; then
      if ! bash "$SRC/bin/company" onboard; then
        say "onboarding did not complete"
        defer_install_onboarding
      fi
    else
      if ! bash "$SRC/bin/company" onboard --global; then
        say "onboarding did not complete"
        defer_install_onboarding
      fi
    fi
  else
    defer_install_onboarding
  fi
fi
