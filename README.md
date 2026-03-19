<div align="center">

<img src="docs/mascot.png" alt="BowerBot" width="200">

# BowerBot

**AI-powered USD scene assembly, from your assets to production-ready .usdz.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![OpenUSD](https://img.shields.io/badge/OpenUSD-25.x-green)](https://openusd.org)
[![Built by Binary Core LLC](https://img.shields.io/badge/Built%20by-Binary%20Core%20LLC-black)](https://binarycore.us)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## 🐦 Meet BowerBot

In the rainforests of Australia and New Guinea lives one of nature's most remarkable architects: the **bowerbird**.

Unlike any other creature, the male bowerbird doesn't attract mates with flashy feathers. Instead, he spends weeks **collecting objects from across his entire environment** (feathers, shells, berries, bottle caps, glass fragments) and assembles them into an elaborate **3D structure** called a bower. Each object is curated deliberately. Each piece placed with intention.

**BowerBot does the same thing for your 3D pipeline.**

Point it at your Sketchfab account, your local asset cache, or any connected provider. BowerBot fetches what you need and assembles a production-ready **OpenUSD stage**. You focus on the creative decisions. BowerBot handles the pipeline.

---

## ✨ What It Does

```
$ bowerbot open coffee_shop

You: Search my Sketchfab for a round bistro table and download it
BowerBot: Found "Round Bistro Table". Downloaded to assets/Round_Bistro_Table.usdz

You: Place it at the center of the room
BowerBot: Placed at /Scene/Furniture/Round_Bistro_Table_01 (5.0, 0.0, 4.0)

You: Find an espresso cup in my local assets and place it on the table surface
BowerBot: Found espresso_cup.usdz. Table surface at Y=0.74.
         Placed at /Scene/Products/Espresso_Cup_01 (5.0, 0.74, 4.0)

You: Move the cup to the left side of the table
BowerBot: Moved to (4.7, 0.74, 4.0) — within table bounds.

You: Validate and package
BowerBot: All checks passed. Packaged to scenes/coffee_shop/scene.usdz
```

Open the `.usda` in Maya, usdview, or any USD viewer to fine-tune. Close the session, come back tomorrow, and pick up where you left off. Projects are persistent.

---

## ✨ Features

- 📦 **OpenUSD native** : references, defaultPrim, metersPerUnit, upAxis, all correct out of the box
- 🔌 **Pluggable skills** : Sketchfab, local asset cache, and easy to add more
- 🧩 **Automatic unit handling** : assets in cm, mm, or inches are scaled correctly at reference time
- 📐 **Geometry-aware** : uses bounding boxes to place objects on surfaces, not guesswork
- 🗣️ **Conversational assembly** : search, download, place, and adjust assets through chat
- 🧠 **Multi-LLM support** : OpenAI, Anthropic, and any provider via [litellm](https://docs.litellm.ai/)
- 📁 **Project-based workflow** : one folder per scene, resumable across sessions
- ✅ **Scene validation** : catches USD errors before they reach your DCC
- 📦 **USDZ packaging** : export for Apple Vision Pro, Omniverse, or any USD viewer
- 🏗️ **Onboarding wizard** : zero-config setup in 60 seconds
- 🎯 **SKILL.md system** : modular prompts, each skill teaches the LLM how to use it

---

## 🚀 Quick Start

Requires [uv](https://docs.astral.sh/uv/) (handles Python automatically).

```bash
# Clone
git clone https://github.com/binary-core-llc/bowerbot.git
cd bowerbot

# Install
uv sync

# First-time setup (creates ~/.bowerbot/config.json)
uv run bowerbot onboard

# Create a project and start building
uv run bowerbot new "Coffee Shop"
uv run bowerbot open coffee_shop
```

The onboard wizard asks for your LLM API key and optional Sketchfab token. Everything is stored in `~/.bowerbot/config.json`. One file, one place, no `.env`.

---

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `bowerbot new "name"` | Create a new project |
| `bowerbot open name` | Open a project and start chatting |
| `bowerbot list` | Show all projects with object counts |
| `bowerbot chat` | Auto-detect project in current directory |
| `bowerbot build "prompt"` | Single-shot build (auto-creates project) |
| `bowerbot skills` | List enabled skills and their tools |
| `bowerbot info` | Show current configuration |
| `bowerbot onboard` | First-time setup wizard |

---

## 📁 Projects

BowerBot uses a project-based workflow. Each project is a self-contained folder:

```
scenes/coffee_shop/
  project.json        # Metadata: name, created, updated, object count
  scene.usda          # The USD stage
  scene.usdz          # Packaged output
  assets/             # Assets used by this project
    mug.usdz
    table.usdz
```

Projects are resumable:

```
$ bowerbot open coffee_shop
# Project: Coffee Shop
# Scene: scene.usda (5 object(s))

You: Show me the scene structure
BowerBot: Scene has 5 objects...

You: Remove Table_03
BowerBot: Removed /Scene/Furniture/Table_03
```

---

## 🔌 Skills

Skills are pluggable tools the agent uses. Each skill has a Python module for execution and a `SKILL.md` file that teaches the LLM when and how to use it.

### Built-in Skills

**Assembly** (always active) : 9 tools for USD scene building

| Tool | Description |
|------|-------------|
| `create_stage` | Initialize a new USD scene with standard hierarchy |
| `place_asset` | Add an asset with position, rotation, and auto unit conversion |
| `move_asset` | Reposition an existing object without creating duplicates |
| `compute_grid_layout` | Calculate evenly spaced positions |
| `list_scene` | Show current scene with positions and bounding boxes |
| `rename_prim` | Move/rename objects in the hierarchy |
| `remove_prim` | Delete objects from the scene |
| `validate_scene` | Check for USD errors |
| `package_scene` | Bundle as `.usdz` |

**Local** : Searches previously downloaded assets on disk. Supports `.usd`, `.usda`, `.usdc`, `.usdz`.

**Sketchfab** : Searches and downloads models from your own Sketchfab account. Downloads in USDZ format only. These are your curated assets, not the public marketplace.

### Writing a Skill

Create a folder in `src/bower_bot/skills/` with:

```
my_provider/
  __init__.py
  my_provider.py      # Implements the Skill interface
  SKILL.md            # Natural language instructions for the LLM
```

The `SKILL.md` is injected into the system prompt when the skill is active. It teaches the agent when and how to use your tools. See `skills/sketchfab/SKILL.md` for an example.

---

## ⚙️ Configuration

All settings live in `~/.bowerbot/config.json`:

```json
{
  "llm": {
    "model": "gpt-4o",
    "api_key": "sk-...",
    "temperature": 0.1,
    "max_tokens": 4096
  },
  "scene_defaults": {
    "meters_per_unit": 1.0,
    "up_axis": "Y",
    "default_room_bounds": [10.0, 3.0, 8.0]
  },
  "skills": {
    "local": {
      "enabled": true,
      "config": { "paths": ["./assets"] }
    },
    "sketchfab": {
      "enabled": true,
      "config": { "token": "your-sketchfab-token" }
    }
  },
  "projects_dir": "./scenes"
}
```

Switch models by changing one line:

```json
{ "model": "gpt-4o" }
{ "model": "anthropic/claude-sonnet-4-20250514" }
{ "model": "deepseek/deepseek-chat" }
```

---

## 🏗️ Architecture

```
src/bower_bot/
  project.py              # Project management (create/load/resume)
  agent.py                # AgentRuntime, LLM tool-calling loop
  cli.py                  # Click CLI
  config.py               # Settings from ~/.bowerbot/config.json
  engine/
    stage_writer.py       # All USD/pxr operations (create, place, rename, remove)
    scene_graph.py        # Spatial math (grids, walls, collisions)
    validator.py          # USD validation (defaultPrim, metersPerUnit, upAxis, refs)
    packager.py           # USDZ packaging
  skills/
    base.py               # Skill interface + SKILL.md loading
    registry.py           # Tool discovery, routing, and prompt collection
    assembly/             # Scene building tools + SKILL.md
    local/                # Local asset search + SKILL.md
    sketchfab/            # Sketchfab API + SKILL.md
  schemas/
    models.py             # Pydantic data models
  gateway/                # Future: FastAPI + MCP server
```

Design principles:

- **Skills never touch USD** : all `pxr` calls live exclusively in `engine/`
- **User controls the workflow** : the agent follows instructions, not a hardcoded pipeline
- **SKILL.md per skill** : modular prompts, only injected when the skill is active
- **Project-based** : one folder per scene, resumable across sessions
- **One config file** : `~/.bowerbot/config.json`, no `.env`

---

## 📐 USD Compliance

Every scene BowerBot produces follows these rules:

- `metersPerUnit = 1.0`
- `upAxis = "Y"`
- Assets added as USD references (not copies)
- `defaultPrim` always set
- Standard hierarchy: `/Scene/Architecture`, `/Scene/Furniture`, `/Scene/Products`, `/Scene/Lighting`, `/Scene/Props`
- Validated before packaging
- Automatic unit conversion for assets with different `metersPerUnit`

---

## 🎨 The Mascot

<div align="center">
<img src="docs/mascot.png" alt="BowerBot Mascot" width="300">

*Meticulous. Obsessive about quality. Always collecting. Never done decorating.*
</div>

---

## 🗺️ Roadmap

- [x] Core USD engine (StageWriter, Validator, Packager)
- [x] CLI (chat, new, open, list, build, skills, info, onboard)
- [x] Sketchfab skill (search user's own models, USDZ download)
- [x] Local asset cache skill
- [x] Assembly skill (9 tools: create, place, move, grid, list, rename, remove, validate, package)
- [x] SKILL.md system (modular prompts per skill)
- [x] Project-based workflow with persistence
- [x] Multi-LLM support (OpenAI, Anthropic via litellm)
- [x] Automatic unit conversion (cm/mm/inches to meters)
- [x] Geometry-aware surface placement
- [x] Onboarding wizard
- [ ] Scene templates : JSON-driven scene assembly with asset resolution
- [ ] DCC exporter : tool to export scene layout as BowerBot JSON
- [ ] Error recovery : validator errors fed back to LLM for auto-retry
- [ ] Token management : conversation summarization for long sessions
- [ ] More skills : Fab, PolyHaven, Objaverse, CGTrader
- [ ] MCP Gateway : FastAPI server for web UI and external AI clients
- [ ] Web UI : chat panel + live 3D viewport
- [ ] BowerHub : community skill registry

---

## 🤝 Contributing

BowerBot is open source and welcomes contributions. The best way to start is writing a new **skill** for an asset provider you use.

```bash
git clone https://github.com/binary-core-llc/bowerbot.git
cd bowerbot
uv sync
uv run pytest tests/
```

---

## 📄 License

```
Copyright 2026 Binary Core LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

---

<div align="center">

Built with 🐦 by [Binary Core LLC](https://binarycore.io)

*"The bowerbird doesn't have the flashiest feathers. It just builds the most compelling world."*

</div>