<!-- Copyright 2026 Binary Core LLC | SPDX-License-Identifier: Apache-2.0 -->
# Assembly Skill

You have tools to create and manipulate OpenUSD scenes.

## Workflow
1. ALWAYS call `create_stage` first before placing any assets
2. Place assets using `place_asset` with coordinates in meters
3. Use `move_asset` to reposition an existing object (do NOT call
   `place_asset` again — that creates a duplicate)
4. Use `compute_grid_layout` to plan evenly spaced arrangements
5. Use `list_scene` to show the user what's currently in the scene
6. Use `rename_prim` or `remove_prim` when the user wants to reorganize
7. ALWAYS call `validate_scene` before packaging
8. Call `package_scene` to produce the final .usdz

## USD Rules
- metersPerUnit = 1.0 (always, no exceptions)
- upAxis = "Y"
- Assets are added as USD references (not copies)
- Every stage has a defaultPrim set automatically

## Scene Hierarchy
Default groups: /Scene/Architecture, /Scene/Furniture, /Scene/Products, /Scene/Lighting, /Scene/Props
The user may request a custom hierarchy — use `rename_prim` to reorganize after placement.

## Spatial Reasoning
- Tables, chairs, shelves → floor (Y = 0)
- Ceiling lights, pendants → ceiling (Y = room height, typically 2.7)
- Wall-mounted items → against walls with 0.01m offset
- Maintain minimum 1.2m walkways between furniture groups

### Placing objects on surfaces
Do NOT guess surface heights or positions. ALWAYS call `list_scene`
first and use the `bounds` of the support object:
- `translate_y` = support `bounds.max.y` (surface height)
- `translate_x` must be between support `bounds.min.x` and
  `bounds.max.x` (stay within the surface)
- `translate_z` must be between support `bounds.min.z` and
  `bounds.max.z` (stay within the surface)

When arranging multiple objects on the same surface, also check
each object's own bounds to ensure they do not overlap or hang
off the edge.

## Room Defaults
- Width: 10m (X axis)
- Height: 3m (Y axis)
- Depth: 8m (Z axis)
- Origin (0,0,0) is back-left corner at floor level
- Center of room: (5.0, 0.0, 4.0)