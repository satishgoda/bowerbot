# Copyright 2026 Binary Core LLC
# SPDX-License-Identifier: Apache-2.0

"""StageWriter — creates and writes USD stages.

Handles all direct USD API calls: creating stages, adding references,
setting transforms, managing composition arcs.
"""

from pathlib import Path

from bowerbot.schemas import SceneObject


class StageWriter:
    """Writes USD stages using the pxr API.

    All USD file operations are centralized here so the rest of
    BowerBot never touches pxr directly.
    """

    def __init__(self, meters_per_unit: float = 1.0, up_axis: str = "Y") -> None:
        self.meters_per_unit = meters_per_unit
        self.up_axis = up_axis
        self._stage = None

    def create_stage(self, path: str | Path) -> None:
        """Create a new USD stage with BowerBot defaults."""
        from pxr import Kind, Usd, UsdGeom

        path = str(path)
        self._stage = Usd.Stage.CreateNew(path)

        # Set stage metadata
        UsdGeom.SetStageMetersPerUnit(self._stage, self.meters_per_unit)
        UsdGeom.SetStageUpAxis(
            self._stage,
            UsdGeom.Tokens.y if self.up_axis == "Y" else UsdGeom.Tokens.z,
        )

        # Create root prim and set as default
        root = self._stage.DefinePrim("/Scene", "Xform")
        self._stage.SetDefaultPrim(root)
        Usd.ModelAPI(root).SetKind(Kind.Tokens.assembly)

        # Create standard hierarchy
        for group in ["Architecture", "Furniture", "Products", "Lighting", "Props"]:
            self._stage.DefinePrim(f"/Scene/{group}", "Xform")

        self._stage.Save()

    def add_reference(self, scene_object: SceneObject) -> None:
        """Add a referenced asset to the stage at the given prim path."""
        from pxr import Gf, Sdf, UsdGeom

        if self._stage is None:
            msg = "No stage open. Call create_stage() first."
            raise RuntimeError(msg)

        # Define the prim and add reference
        prim = self._stage.DefinePrim(scene_object.prim_path, "Xform")
        asset_path = scene_object.asset.file_path or scene_object.asset.source_id
        prim.GetReferences().AddReference(asset_path)

        # Set transform
        xformable = UsdGeom.Xformable(prim)
        xformable.ClearXformOpOrder()

        tx, ty, tz = scene_object.translate
        xformable.AddTranslateOp().Set(Gf.Vec3d(tx, ty, tz))

        rx, ry, rz = scene_object.rotate
        if any(v != 0.0 for v in (rx, ry, rz)):
            xformable.AddRotateXYZOp().Set(Gf.Vec3f(rx, ry, rz))

        sx, sy, sz = scene_object.scale
        if any(v != 1.0 for v in (sx, sy, sz)):
            xformable.AddScaleOp().Set(Gf.Vec3f(sx, sy, sz))

    def save(self) -> None:
        """Save the current stage to disk."""
        if self._stage is None:
            msg = "No stage open."
            raise RuntimeError(msg)
        self._stage.Save()
    
    def list_prims(self) -> list[dict]:
        """List all placed objects (prims with references) in the stage."""
        from pxr import UsdGeom

        if self._stage is None:
            return []

        objects = []
        for prim in self._stage.Traverse():
            refs = prim.GetMetadata("references")
            if refs is None:
                continue

            position = None
            xformable = UsdGeom.Xformable(prim)
            if xformable:
                local_xform = xformable.GetLocalTransformation()
                t = local_xform.ExtractTranslation()
                position = {"x": round(t[0], 2), "y": round(t[1], 2), "z": round(t[2], 2)}

            asset_path = None
            for ref_list in [refs.prependedItems, refs.appendedItems, refs.explicitItems]:
                if ref_list:
                    for ref in ref_list:
                        asset_path = ref.assetPath
                        break

            objects.append({
                "prim_path": str(prim.GetPath()),
                "asset": asset_path,
                "position": position,
            })

        return objects

    def rename_prim(self, old_path: str, new_path: str) -> bool:
        """Move/rename a prim to a new path in the hierarchy."""
        from pxr import Sdf, Usd

        if self._stage is None:
            msg = "No stage open."
            raise RuntimeError(msg)

        old_prim = self._stage.GetPrimAtPath(old_path)
        if not old_prim.IsValid():
            msg = f"Prim not found: {old_path}"
            raise ValueError(msg)

        # Ensure parent hierarchy exists
        parent_path = str(Sdf.Path(new_path).GetParentPath())
        if parent_path and parent_path != "/":
            parent_prim = self._stage.GetPrimAtPath(parent_path)
            if not parent_prim.IsValid():
                self._stage.DefinePrim(parent_path, "Xform")

        layer = self._stage.GetRootLayer()
        edit = Sdf.BatchNamespaceEdit()
        edit.Add(old_path, new_path)
        success = layer.Apply(edit)

        if success:
            self._stage.Save()
            # Reload stage to pick up namespace changes
            self._stage = Usd.Stage.Open(str(self._stage.GetRootLayer().realPath))

        return success

    def remove_prim(self, prim_path: str) -> bool:
        """Remove a prim from the stage."""
        from pxr import Usd

        if self._stage is None:
            msg = "No stage open."
            raise RuntimeError(msg)

        prim = self._stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            msg = f"Prim not found: {prim_path}"
            raise ValueError(msg)

        result = self._stage.RemovePrim(prim_path)
        if result:
            self._stage.Save()

        return result

    def open_stage(self, path: str | Path) -> None:
        """Open an existing USD stage from disk."""
        from pxr import Usd
        self._stage = Usd.Stage.Open(str(path))

    @property
    def stage(self):  # noqa: ANN201
        """Access the underlying Usd.Stage (for validator, etc.)."""
        return self._stage
