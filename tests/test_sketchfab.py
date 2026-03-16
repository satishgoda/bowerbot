"""Test Sketchfab skill — verify API authentication and endpoints."""

import asyncio

from bowerbot.config import load_settings
from bowerbot.skills.sketchfab import SketchfabSkill


async def test_auth_and_list():
    """Test 1: Verify API token works and list user's models."""
    settings = load_settings()
    sketchfab_config = settings.skills.get("sketchfab")

    if not sketchfab_config or not sketchfab_config.enabled:
        print("⏭️  Skipping — sketchfab not enabled in config.json")
        return

    token = sketchfab_config.config.get("token", "")
    if not token:
        print("⏭️  Skipping — no token in config.json")
        return

    skill = SketchfabSkill(token=token)

    # List all models (will be empty if no uploads yet)
    result = await skill.execute("list_my_models", {"max_results": 5})

    if not result.success:
        print(f"❌ API call failed: {result.error}")
        return

    model_count = len(result.data)
    print(f"✅ test_auth_and_list PASSED — API connected, {model_count} model(s) in your account")

    if model_count > 0:
        for m in result.data:
            print(f"   • {m['name']} (uid: {m['uid']}, verts: {m['vertex_count']})")
    else:
        print("   (No models uploaded yet — that's fine, connection works!)")


async def test_search_empty():
    """Test 2: Search for something — should return empty list gracefully."""
    settings = load_settings()
    sketchfab_config = settings.skills.get("sketchfab")

    if not sketchfab_config or not sketchfab_config.enabled:
        return

    token = sketchfab_config.config.get("token", "")
    skill = SketchfabSkill(token=token)

    result = await skill.execute("search_my_models", {"query": "table"})

    assert result.success, f"Search failed: {result.error}"
    print(f"✅ test_search_empty PASSED — search returned {len(result.data)} result(s)")


async def main():
    await test_auth_and_list()
    await test_search_empty()
    print("\n🎉 Sketchfab connection tests done!")


if __name__ == "__main__":
    asyncio.run(main())
