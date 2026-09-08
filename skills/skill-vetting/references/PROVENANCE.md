# NVIDIA Skill Inspector reference

Source attribution: NVIDIA and the SkillSpector contributors, [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector).
Retrieved and reviewed 2026-09-08 at immutable commit
`704bc9544260c2f41222dc0f92982521709496ab`.

| Local file | Unchanged upstream file | SHA-256 |
|---|---|---|
| `nvidia-skill-inspector.md` | [`skills/skill-inspector/SKILL.md`](https://github.com/NVIDIA/SkillSpector/blob/704bc9544260c2f41222dc0f92982521709496ab/skills/skill-inspector/SKILL.md) | `89ab1550769752ffbad782ee63fee3c345d546bded672adaac5fd03d2941aa84` |
| `LICENSE.nvidia` | [`LICENSE`](https://github.com/NVIDIA/SkillSpector/blob/704bc9544260c2f41222dc0f92982521709496ab/LICENSE) | `9f8785b47596b2993a17a3fa8d747ae63126a2c5e80a9e77195a907273d71839` |

The copied manual and license are byte-for-byte upstream files. The upstream
root has no `NOTICE` file at this commit. Its
[THIRD_PARTY_NOTICES.md](https://github.com/NVIDIA/SkillSpector/blob/704bc9544260c2f41222dc0f92982521709496ab/THIRD_PARTY_NOTICES.md)
lists scanner runtime dependencies; none of that software is bundled here.
The reference retains Apache-2.0, independently of the repository's first-party MIT content.

Use the parent `skill-vetting` manual as the local wrapper. Its permissions,
quarantine/data boundaries, evidence statuses, and output format take precedence
over reference suggestions. The reference does not authorize acquisition,
execution, extra access, a report style change, or tool installation.

The optional scanner at this snapshot is SkillSpector 2.11.1 and requires
Python >=3.12,<3.15, as recorded in its [pyproject.toml](https://github.com/NVIDIA/SkillSpector/blob/704bc9544260c2f41222dc0f92982521709496ab/pyproject.toml);
the company project helper still requires only Python 3.9+.
No scanner, dependencies, credentials, model calls, or live benchmark are included.
This is source provenance, not NVIDIA certification or automatic update tracking.
Review a changed upstream snapshot before replacing these files and hashes.
