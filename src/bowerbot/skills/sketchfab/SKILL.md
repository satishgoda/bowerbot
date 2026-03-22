<!-- Copyright 2026 Binary Core LLC | SPDX-License-Identifier: Apache-2.0 -->
# Sketchfab Skill

You have tools to search and download 3D models from the user's OWN Sketchfab account.

## Important
- This searches the user's PERSONAL model library, not the public Sketchfab store
- These are curated, production-ready assets the user uploaded themselves
- ONLY download in USDZ format — other formats are not supported
- NEVER guess or fabricate a model UID — always get it from search or list results

## Workflow
1. Use `search_my_models` to find models by keyword
2. If search returns no results or poor matches, ALWAYS fall back to `list_my_models` and look through all assets by checking their name, description, and tags — do NOT give up after a failed search
3. Only consider models where `is_downloadable` is true
4. Evaluate each result's name, description, and tags to confirm it actually matches what the user asked for — do not assume the first result is correct
5. Use `download_model` to download — it saves to the local asset cache
6. After downloading, use the returned `file_path` with `place_asset`

## Notes
- Downloaded models are cached locally — no need to re-download in future sessions
- If a model has no USDZ available, the download will fail — inform the user