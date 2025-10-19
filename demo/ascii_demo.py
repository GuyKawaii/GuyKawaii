"""
ASCII Art Demo Script
Usage: 
  python ascii_demo.py                    # Use default image (default.png)
  python ascii_demo.py image.png          # Use specified image
  python ascii_demo.py image.png 80       # Use specified image with custom width
"""
import sys
import os
from pathlib import Path
from PIL import Image

try:
    from src import get_ascii_char, image_to_ascii, DEFAULT_WIDTH
except ImportError:
    # Fallback if src is not in path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src import get_ascii_char, image_to_ascii, DEFAULT_WIDTH


def show_ascii_scale():
    """Always display the ASCII palette gradient"""
    print("\n" + "="*60)
    print("ASCII PALETTE SCALE")
    print("="*60)
    
    # Test with different brightness levels
    print("\nBrightness mapping:\n")
    
    for brightness in [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250]:
        pixel = (brightness, brightness, brightness)
        char = get_ascii_char(pixel)
        bar = char * 15
        print(f"  Brightness {brightness:3d}: [{bar}] '{char}'")
    
    print("\n" + "-"*60)
    print("Full gradient (dark -> light):")
    gradient = ""
    for brightness in range(0, 256, 4):
        pixel = (brightness, brightness, brightness)
        gradient += get_ascii_char(pixel)
    print(gradient)
    print("\n" + "="*60 + "\n")


def convert_image_to_ascii(image_path, width=DEFAULT_WIDTH):
    """Convert an image to ASCII art"""
    try:
        print(f"\nConverting image: {image_path}")
        print(f"Width: {width} characters\n")
        
        img = Image.open(image_path)
        ascii_art = image_to_ascii(img, width=width)
        
        print(ascii_art)
        print("\n" + "="*60)
        print("Done! ASCII art generated from image")
        print("="*60 + "\n")
        return True
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}\n")
        return False
    except Exception as e:
        print(f"Error processing image: {e}\n")
        return False


if __name__ == "__main__":
    # Always show the ASCII scale first
    show_ascii_scale()
    
    # Determine which image to use
    image_path = None
    width = DEFAULT_WIDTH
    
    if len(sys.argv) > 1:
        # Image path provided as argument
        image_path = sys.argv[1]
        if len(sys.argv) > 2:
            width = int(sys.argv[2])
    else:
        # Try default image in the same folder
        default_image = Path(__file__).parent / "default.png"
        if default_image.exists():
            image_path = str(default_image)
            print(f"No image provided. Using default: {default_image.name}\n")
        else:
            print("No image provided and no default image found.")
            print("Usage: python ascii_demo.py <image_path> [width]")
            print(f"Example: python ascii_demo.py photo.png {DEFAULT_WIDTH}\n")
    
    # Convert image if we have one
    if image_path:
        convert_image_to_ascii(image_path, width)
