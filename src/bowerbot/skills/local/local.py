# Copyright 2026 Binary Core LLC
# SPDX-License-Identifier: Apache-2.0

"""Local filesystem skill — searches for USD assets on disk."""

from pathlib import Path
from typing import Any

from bowerbot.skills.base import Skill, SkillCategory, Tool, ToolResult


class LocalSkill(Skill):
    """Searches local directories for 3D assets.

    This is the simplest skill — no API keys needed. Just point
    it at directories containing .usd/.usda/.usdc/.usdz/.fbx/.glb files.
    """

    name = "local"
    category = SkillCategory.ASSET_PROVIDER

    SUPPORTED_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}

    def __init__(self, paths: list[str] | None = None) -> None:
        self.search_paths = [Path(p) for p in (paths or [])]

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="search_assets",
                description="Search local directories for 3D assets by keyword.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search keyword to match against filenames.",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="list_assets",
                description="List all available 3D assets in local directories.",
                parameters={"type": "object", "properties": {}},
            ),
        ]

    async def execute(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        try:
            match tool_name:
                case "search_assets":
                    return self._search(params.get("query", ""))
                case "list_assets":
                    return self._list_all()
                case _:
                    return ToolResult(success=False, error=f"Unknown tool: {tool_name}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _search(self, query: str) -> ToolResult:
        query_lower = query.lower()
        results = []
        for path in self.search_paths:
            if not path.exists():
                continue
            for f in path.rglob("*"):
                if f.suffix.lower() in self.SUPPORTED_EXTENSIONS and query_lower in f.stem.lower():
                    results.append({"name": f.stem, "path": str(f), "format": f.suffix})
        return ToolResult(success=True, data=results)

    def _list_all(self) -> ToolResult:
        results = []
        for path in self.search_paths:
            if not path.exists():
                continue
            for f in path.rglob("*"):
                if f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    results.append({"name": f.stem, "path": str(f), "format": f.suffix})
        return ToolResult(success=True, data=results)

    def validate_config(self) -> bool:
        return len(self.search_paths) > 0
