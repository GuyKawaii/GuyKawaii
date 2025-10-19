"""
ASCII Art Test Script - Unified tester for palette and images
Usage: 
  python test_ascii.py                    # Show palette gradient only
  python test_ascii.py image.png          # Convert image to ASCII
  python test_ascii.py image.png 80       # Convert with custom width
"""
import sys
try:
    from src.draw_ascii import DEFAULT_WIDTH
except Exception:
    DEFAULT_WIDTH = 50  # Fallback if module import fails

def show_palette():
    """Display the ASCII palette gradient without needing an image"""
    print("\n" + "="*60)
    print("ASCII PALETTE VISUALIZER")
    print("="*60)
    
    # Import the actual palette from the project
    try:
        from src.draw_ascii import get_ascii_char

        # Test with different brightness levels
        print("\nCurrent palette brightness mapping:\n")

        for brightness in [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250]:
            # Create test pixel (grayscale)
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

        print("\nBackground (bright pixels) will render as spaces")
        print("="*60 + "\n")

    except ImportError:
        print("Error: Could not import from src.draw_ascii")
        print("Make sure you're running from the project root directory")

def test_ascii_local(image_path, width=DEFAULT_WIDTH):
    """Test ASCII conversion with a local image"""
    try:
        from PIL import Image
        from src.draw_ascii import get_ascii_char
        
        img = Image.open(image_path)
        
        # Resize image
        aspect_ratio = img.width / img.height
        height = int((width * aspect_ratio) * 0.5)
        
        img = img.resize((width, height))
        img = img.convert('RGB')
        
        # Generate ASCII
        ascii_str = ""
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                ascii_str += get_ascii_char(pixel)
            ascii_str += "\n"
        
        print(ascii_str)
        return ascii_str
    
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        print("Please provide a valid image path")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ASCII ART TESTER")
    print("="*60)
    
    # Check for command-line argument
    if len(sys.argv) > 1:
        # Image path provided as argument
        image_path = sys.argv[1]
        width = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_WIDTH

        print(f"\nConverting image: {image_path}")
        print(f"   Width: {width} characters\n")

        test_ascii_local(image_path, width)

        print("\n" + "="*60)
        print("Done! ASCII art generated from image")
        print("="*60 + "\n")
    else:
        # No argument provided - show palette only
        print("\nNo image provided - showing palette visualization")
        print("   Usage: python test_ascii.py <image_path> [width]")
        print(f"   Example: python test_ascii.py photo.png {DEFAULT_WIDTH}")

        show_palette()

        print("\nTIP: To test with an image, run:")
        print("   python test_ascii.py image.png")
        print("\n" + "="*60 + "\n")
