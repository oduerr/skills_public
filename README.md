# skills

A collection of reusable AI agent skills for Claude and other LLM-powered CLIs.

Skills are self-contained directories with a `SKILL.md` that tells the agent what the skill does and when to use it.

## Available Skills

| Skill | Description |
|-------|-------------|
| [easy_chef](./easy_chef/) | Transforms any recipe into a structured, easy-to-follow format with emoji-numbered ingredients, mise en place notes, metric units, and a Samin Nosrat culinary critique |

## Installation

Clone the repo and run the install script to symlink all skills into the global skill folders for supported agents:

```bash
git clone https://github.com/oduerr/skills.git
cd skills
bash scripts/link_skills.sh
```

The script links each skill directory into the following locations:

| Agent | Skill folder |
|-------|-------------|
| Claude (claude.ai / Claude Code) | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Gemini | `~/.gemini/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Generic agents | `~/.agents/skills/` |

Symlinks mean updates via `git pull` are picked up automatically — no reinstall needed.

> **Note:** Restart your CLI after running the script for changes to take effect.

## Repo structure

```
skills/                  ← each skill is a subdirectory here
  easy_chef/
    SKILL.md
scripts/
  link_skills.sh         ← install script
README.md
```



## Adding a skill

1. Create a new directory under `skills/your_skill_name/`  
2. Add a `SKILL.md` with a YAML frontmatter block:

```markdown
---
name: your_skill_name
description: "When to trigger this skill and what it produces."
---

# Your Skill

Instructions for the agent...
```

3. Run `bash scripts/link_skills.sh` again to link the new skill.

## Contributing

Pull requests welcome! Please make sure each skill has a clear `description` in the frontmatter — this is what agents use to decide when to invoke the skill.
