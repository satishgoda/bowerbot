# Local Asset Cache

You have tools to search previously downloaded 3D assets on disk.

## When to Use
- When the user asks for assets without specifying a source
- When you want to check if an asset was already downloaded
- Before searching cloud providers — local is faster and free

## Supported Formats
Only USD-family files: .usd, .usda, .usdc, .usdz

## Behavior
- Searches by keyword matching against filenames
- Includes assets downloaded by any cloud provider (Sketchfab, etc.)
- Returns file paths ready for use with `place_asset`