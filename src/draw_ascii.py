from PIL import Image
from io import BytesIO

# Shared default width for ASCII rendering
DEFAULT_WIDTH: int = 50

def get_ascii_char(pixel):
    """
    Converts a pixel to an ASCII character based on brightness.
    Uses luminance formula for more accurate brightness perception.
    Soft palette: dark to light with spaces as background.
    """
    # Soft gradient palette: dark (dense) to light (sparse/space)
    # Each character represents a different density level
    ascii_chars = '.:-=+. ##@'
    
    # Luminance formula: weights colors by human eye sensitivity
    # Green appears brighter to humans than red or blue
    r, g, b = pixel
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    
    # Map brightness (0-255) to character index (0 to len-1)
    char_index = int(brightness / 255 * (len(ascii_chars) - 1))
    
    # Clamp to valid range (defensive programming)
    char_index = max(0, min(char_index, len(ascii_chars) - 1))
    
    return ascii_chars[char_index]

def image_to_ascii(image, width: int = DEFAULT_WIDTH) -> str:
    aspect_ratio = image.width / image.height
    height = int((width*aspect_ratio)*0.5)

    image = image.resize((width, height))
    image = image.convert('RGB')
    ascii_str = ""

    for y in range(height): 
        for x in range(width):
            pixel = image.getpixel((x,y))
            ascii_str += get_ascii_char(pixel)
        ascii_str += "\n"

    return ascii_str

def generate_logo(g) -> str:
    """Generate ASCII logo from GitHub user avatar.
    
    Note: This function imports requests and Github lazily to avoid
    loading heavy dependencies when only using basic ASCII functions.
    """
    import requests
    from github import Github
    
    user_pfp = g.get_user().avatar_url
    response = requests.get(user_pfp)
    img = Image.open(BytesIO(response.content))

    return image_to_ascii(img)
