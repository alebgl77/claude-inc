#!/usr/bin/env bash
# Claude, Inc. installer — puts 7 departments and 42 employees on your payroll.
#   curl -fsSL https://raw.githubusercontent.com/alebgl77/claude-inc/main/install.sh | bash
# Flags:
#   --project   install into ./.claude (current project) instead of ~/.claude
#   --no-bin    skip installing the 'company' CLI into ~/.local/bin
set -euo pipefail

REPO_URL="https://github.com/alebgl77/claude-inc"
CLONE_DIR="${CLAUDE_INC_HOME:-$HOME/.claude-inc}"

PROJECT="no"; NO_BIN="no"
for a in "$@"; do
  case "$a" in
    --project) PROJECT="yes" ;;
    --no-bin)  NO_BIN="yes" ;;
    *) echo "unknown flag: $a" >&2; exit 1 ;;
  esac
done

if [ -t 1 ]; then B=$'\033[1m'; OR=$'\033[38;5;208m'; G=$'\033[32m'; R=$'\033[0m'; else B=""; OR=""; G=""; R=""; fi
say() { printf '%s\n' "${OR}${B}claude-inc${R} $*"; }

# --- locate source: already inside the repo, or clone/update it -------------
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd || true)"
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills" ] && [ -d "$SCRIPT_DIR/agents" ]; then
  SRC="$SCRIPT_DIR"
  say "installing from local checkout: $SRC"
else
  if [ -d "$CLONE_DIR/.git" ]; then
    say "updating $CLONE_DIR"
    git -C "$CLONE_DIR" pull --ff-only >/dev/null
  else
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
echo "    company roster                       # meet the team"
echo "    company brief \"launch my product\"    # brief the CEO"
echo "    claude                               # skills + agents are live in Claude Code"
echo
echo "  ${B}Claude Code plugin route (alternative):${R}"
echo "    /plugin marketplace add alebgl77/claude-inc"
echo "    /plugin install claude-inc@claude-inc"
