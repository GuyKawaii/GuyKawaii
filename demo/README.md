# ASCII Art Demo

This folder contains a demo script to test the ASCII art conversion.

## What it does

The script (`ascii_demo.py`):
1. **Always displays the ASCII palette scale** showing how different brightness levels map to characters
2. **Converts an image to ASCII art** using one of these sources (in order):
   - Image path provided as command-line argument
   - Default image (`default.png`) in this folder
   - No image (just shows the scale)

## Usage

```powershell
# Use default image (default.png)
python ascii_demo.py

# Use a specific image
python ascii_demo.py path/to/image.png

# Use a specific image with custom width
python ascii_demo.py path/to/image.png 80
```

## Requirements

Make sure you've installed the project dependencies:

```powershell
pip install -r ../requirements.txt
```

The script imports from the parent `src/` folder.