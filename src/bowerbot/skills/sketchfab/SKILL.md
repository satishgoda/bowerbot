<!-- Copyright 2026 Binary Core LLC | SPDX-License-Identifier: Apache-2.0 -->
# Sketchfab Skill

You have tools to search and download 3D models from the user's OWN Sketchfab account.

## Important
- This searches the user's PERSONAL model library, not the public Sketchfab store
- These are curated, production-ready assets the user uploaded themselves
- ONLY download in USDZ format — other formats are not supported

## Workflow
1. Use `search_my_models` to find models by keyword
2. Use `list_my_models` to see everything available
3. Use `download_model` to download — it saves to the local asset cache
4. After downloading, use the returned `file_path` with `place_asset`

## Notes
- Downloaded models are cached locally — no need to re-download in future sessions
- If a model has no USDZ available, the download will fail — inform the user