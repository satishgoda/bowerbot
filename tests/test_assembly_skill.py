"""Test the AssemblySkill tools directly — no LLM involved."""

import asyncio
import tempfile
from pathlib import Path

from pxr import Usd, UsdGeom

from bowerbot.project import Project
from bowerbot.skills.assembly import AssemblySkill


def create_test_asset(directory: Path, name: str) -> Path:
    """Create a simple USD asset for testing."""
    path = directory / f"{name}.usda"
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    root = stage.DefinePrim(f"/{name}", "Xform")
    stage.SetDefaultPrim(root)
    cube = UsdGeom.Cube.Define(stage, f"/{name}/Mesh")
    cube.GetSizeAttr().Set(1.0)
    stage.Save()
    return path


def make_skill_with_project(tmp_path: Path, project_name: str = "test") -> tuple[AssemblySkill, Project]:
    """Create an AssemblySkill bound to a temp project."""
    project = Project.create(tmp_path, project_name)
    skill = AssemblySkill()
    skill.set_project(project)
    return skill, project


def test_create_stage():
    """Test 1: create_stage produces a valid USD file."""
    with tempfile.TemporaryDirectory() as tmp:
        skill, project = make_skill_with_project(Path(tmp))
        result = asyncio.run(skill.execute("create_stage", {"filename": "my_store"}))

        assert result.success, f"Failed: {result.error}"
        assert project.scene_path.exists(), "Stage file not on disk"

        stage = Usd.Stage.Open(str(project.scene_path))
        assert stage.GetDefaultPrim().IsValid()

        print("✅ test_create_stage PASSED")


def test_place_asset():
    """Test 2: place_asset adds a referenced prim with correct transform."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        asset_path = create_test_asset(tmp_path, "table")

        skill, project = make_skill_with_project(tmp_path, "place_test")
        asyncio.run(skill.execute("create_stage", {"filename": "test_scene"}))

        result = asyncio.run(skill.execute("place_asset", {
            "asset_file_path": str(asset_path),
            "asset_name": "DisplayTable",
            "group": "Furniture",
            "translate_x": 3.0,
            "translate_y": 0.0,
            "translate_z": 4.0,
            "rotate_y": 90.0,
        }))

        assert result.success, f"Failed: {result.error}"
        prim_path = result.data["prim_path"]
        assert prim_path.startswith("/Scene/Furniture/")

        stage = Usd.Stage.Open(str(project.scene_path))
        prim = stage.GetPrimAtPath(prim_path)
        assert prim.IsValid(), f"Prim not found: {prim_path}"

        xformable = UsdGeom.Xformable(prim)
        local_xform = xformable.GetLocalTransformation()
        translate = local_xform.ExtractTranslation()
        assert abs(translate[0] - 3.0) < 0.01
        assert abs(translate[1] - 0.0) < 0.01
        assert abs(translate[2] - 4.0) < 0.01

        print(f"✅ test_place_asset PASSED — placed at {prim_path}")


def test_place_multiple_assets():
    """Test 3: Place several assets and verify unique prim paths."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        table_path = create_test_asset(tmp_path, "table")
        chair_path = create_test_asset(tmp_path, "chair")

        skill, project = make_skill_with_project(tmp_path, "multi_test")
        asyncio.run(skill.execute("create_stage", {"filename": "multi_test"}))

        prim_paths = []
        for asset, name, x, z in [
            (table_path, "Table", 3.0, 4.0),
            (table_path, "Table", 5.0, 4.0),
            (chair_path, "Chair", 3.0, 2.0),
            (chair_path, "Chair", 5.0, 2.0),
        ]:
            result = asyncio.run(skill.execute("place_asset", {
                "asset_file_path": str(asset),
                "asset_name": name,
                "group": "Furniture",
                "translate_x": x,
                "translate_y": 0.0,
                "translate_z": z,
            }))
            assert result.success, f"Failed: {result.error}"
            prim_paths.append(result.data["prim_path"])

        assert len(set(prim_paths)) == 4, f"Duplicate prim paths: {prim_paths}"

        print(f"✅ test_place_multiple_assets PASSED — {prim_paths}")


def test_compute_grid_layout():
    """Test 4: Grid layout returns correct number of positions."""
    skill = AssemblySkill()
    result = asyncio.run(skill.execute("compute_grid_layout", {
        "count": 6,
        "spacing": 2.5,
    }))

    assert result.success
    assert len(result.data["positions"]) == 6

    print(f"✅ test_compute_grid_layout PASSED — {result.data['positions']}")


def test_validate_scene():
    """Test 5: Validator approves a well-formed scene."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        asset_path = create_test_asset(tmp_path, "item")

        skill, project = make_skill_with_project(tmp_path, "valid_test")
        asyncio.run(skill.execute("create_stage", {"filename": "valid_test"}))
        asyncio.run(skill.execute("place_asset", {
            "asset_file_path": str(asset_path),
            "asset_name": "Item",
            "group": "Props",
            "translate_x": 1.0,
            "translate_y": 0.0,
            "translate_z": 1.0,
        }))

        result = asyncio.run(skill.execute("validate_scene", {}))

        assert result.success
        assert result.data["is_valid"], f"Validation failed: {result.data['issues']}"

        print("✅ test_validate_scene PASSED")


def test_package_scene():
    """Test 6: Package produces a .usdz file."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        asset_path = create_test_asset(tmp_path, "item")

        skill, project = make_skill_with_project(tmp_path, "package_test")
        asyncio.run(skill.execute("create_stage", {"filename": "package_test"}))
        asyncio.run(skill.execute("place_asset", {
            "asset_file_path": str(asset_path),
            "asset_name": "Item",
            "group": "Props",
            "translate_x": 1.0,
            "translate_y": 0.0,
            "translate_z": 1.0,
        }))

        result = asyncio.run(skill.execute("package_scene", {}))

        assert result.success, f"Failed: {result.error}"
        usdz_path = Path(result.data["usdz_path"])
        assert usdz_path.exists()
        assert usdz_path.suffix == ".usdz"
        assert usdz_path.stat().st_size > 0

        print(f"✅ test_package_scene PASSED — {usdz_path.name} ({usdz_path.stat().st_size} bytes)")


def test_full_pipeline():
    """Test 7: Full pipeline — create → place → validate → package."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        table = create_test_asset(tmp_path, "table")
        chair = create_test_asset(tmp_path, "chair")
        light = create_test_asset(tmp_path, "pendant")

        skill, project = make_skill_with_project(tmp_path, "full_pipeline")
        r = asyncio.run(skill.execute("create_stage", {"filename": "full_pipeline"}))
        assert r.success

        r = asyncio.run(skill.execute("compute_grid_layout", {"count": 4, "spacing": 2.0}))
        assert r.success
        positions = r.data["positions"]

        for pos in positions:
            r = asyncio.run(skill.execute("place_asset", {
                "asset_file_path": str(table),
                "asset_name": "Table",
                "group": "Furniture",
                "translate_x": pos["x"],
                "translate_y": 0.0,
                "translate_z": pos["z"],
            }))
            assert r.success

        r = asyncio.run(skill.execute("place_asset", {
            "asset_file_path": str(light),
            "asset_name": "CeilingLight",
            "group": "Lighting",
            "translate_x": 5.0,
            "translate_y": 2.7,
            "translate_z": 4.0,
        }))
        assert r.success

        r = asyncio.run(skill.execute("validate_scene", {}))
        assert r.success
        assert r.data["is_valid"], f"Validation errors: {r.data['issues']}"

        r = asyncio.run(skill.execute("package_scene", {}))
        assert r.success
        usdz_path = Path(r.data["usdz_path"])
        assert usdz_path.exists()

        print(f"✅ test_full_pipeline PASSED")
        print(f"   4 tables + 1 ceiling light → {usdz_path.name} ({usdz_path.stat().st_size} bytes)")


if __name__ == "__main__":
    test_create_stage()
    test_place_asset()
    test_place_multiple_assets()
    test_compute_grid_layout()
    test_validate_scene()
    test_package_scene()
    test_full_pipeline()
    print("\n🎉 All assembly skill tests passed!")
