import json, os, re 
from src.draw_ascii import generate_logo
from src.fetch_info import fetch_stats
from PIL import Image, ImageDraw, ImageFont
from github import Github

def generate_fetch(g:Github) -> str:
    with open("config.json", "r") as f:
        config = json.load(f)

    user = fetch_stats(g)
    pfp = generate_logo(g)


    stats = f"{user['username']}@github.com\n------------------------------\n"
    for stat in config['display_stats']:
        if stat in user:
            stats += f"{stat.replace('_', ' ').title()}: {user[stat]}\n"
    stats += f"\n{config['additional_info']}\n"

    pfp_lines = pfp.split("\n")
    stats_lines = stats.split("\n")

    max_lines = max(len(pfp_lines), len(stats_lines))
    pfp_lines += [""] * (max_lines - len(pfp_lines))
    stats_lines += [""] * (max_lines - len(stats_lines))

    combined = "\n".join(f"{pfp_line:<50} {stats_line}" for pfp_line, stats_line in zip(pfp_lines, stats_lines))
    
    return combined

def return_preffered_color() -> tuple:
    with open("config.json", "r") as f:
        config = json.load(f)
    
    color = config['preferred_color']
    color_map = {
        "red": (255, 0, 0, 255),
        "green": (0, 128, 0, 255),
        "blue": (0, 0, 255, 255),
        "yellow": (255, 255, 0, 255),
        "purple": (128, 0, 128, 255),
        "orange": (255, 165, 0, 255),
        "pink": (255, 192, 203, 255),
        "white": (255, 255, 255, 255),
        "lightblue": (173, 216, 230, 255),
    }

    if color in color_map:
        return color_map[color]
    else:
        return color_map["lightblue"]



def calculate_content_height(config, user_stats, font, ascii_lines, line_spacing, box_margin, content_padding, ascii_width, text_margin, width):
    """Calculate the total height needed for all content without drawing."""
    y_offset = box_margin + content_padding
    x_text = ascii_width + text_margin
    max_text_width = width - ascii_width - (text_margin * 2)
    
    # Account for ASCII art height
    ascii_height = len(ascii_lines) * line_spacing
    
    # Calculate text section height
    text_y = box_margin + content_padding
    
    # Header + separator
    text_y += line_spacing * 2
    
    # Stats
    for stat in config['display_stats']:
        if stat in user_stats and user_stats[stat] is not None:
            value = str(user_stats[stat]).replace("//", "\n - //")
            title = f"{stat.replace('_', ' ').title()}:"
            title_width = font.getlength(title)
            remaining_width = max_text_width - title_width - 5
            
            if '\n' in value:
                value_lines = value.split('\n')
                for i, line in enumerate(value_lines):
                    if i == 0 and line.strip():
                        text_y += line_spacing
                    elif line.strip():
                        text_y += line_spacing
                    elif i == 0:
                        text_y += line_spacing
            else:
                words = value.split()
                if not words:
                    text_y += line_spacing
                    continue
                    
                line = []
                for word in words:
                    test_line = ' '.join(line + [word])
                    text_width = font.getlength(test_line)
                    if text_width <= remaining_width:
                        line.append(word)
                    else:
                        if line:
                            text_y += line_spacing
                            line = [word]
                        else:
                            text_y += line_spacing
                if line:
                    text_y += line_spacing
    
    # Additional info
    if config['additional_info']:
        additional_lines = config['additional_info'].split('\n')
        for line in additional_lines:
            if line.strip():
                text_y += line_spacing
    
    # Return max of ASCII height and text height, plus bottom padding
    return max(ascii_height, text_y) + box_margin + content_padding


def gen_image(g: Github):
    width = 1200
    ascii_width = 450
    text_margin = 60
    
    # Transparent background (RGBA, alpha=0)
    bg_color = (0, 0, 0, 0)
    value_color = return_preffered_color()
    text_color = (255, 255, 255, 255)  # RGBA format
    font_size = 16

    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
        "monospace",
        "consola.ttf"
    ]
    
    # Get ASCII art and user stats separately instead of using combined fetch
    from src.draw_ascii import generate_logo
    ascii_art = generate_logo(g)
    user_stats = fetch_stats(g)
    
    with open("config.json", "r") as f:
        config = json.load(f)
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except IOError:
            continue
    
    if font is None:
        print("No suitable fonts found. Aborting!")
        return
    
    # Calculate dimensions
    ascii_lines = ascii_art.split("\n")
    box_margin = 5
    content_padding = 10
    line_spacing = font_size + 4
    
    # Calculate required height
    required_height = calculate_content_height(
        config, user_stats, font, ascii_lines, line_spacing,
        box_margin, content_padding, ascii_width, text_margin, width
    )
    
    # Create image at the correct size from the start
    final_height = max(550, required_height + 20)
    image = Image.new("RGBA", (width, final_height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Draw black box with colored outline as background
    draw.rectangle(
        [(box_margin, box_margin), (width - box_margin - 1, final_height - box_margin - 1)],
        fill=(0, 0, 0, 200),
        outline=value_color,
        width=3
    )
    
    # Draw ASCII art on the left
    y_offset = box_margin + content_padding
    x_ascii = box_margin + content_padding
    for ascii_line in ascii_lines:
        draw.text((x_ascii, y_offset), ascii_line, fill=value_color, font=font)
        y_offset += line_spacing

    # Draw user info on the right
    y_offset = box_margin + content_padding
    x_text = ascii_width + text_margin
    max_text_width = width - ascii_width - (text_margin * 2)
    
    # Draw header
    header = f"{user_stats['username']}@github.com"
    draw.text((x_text, y_offset), header, fill=value_color, font=font)
    y_offset += line_spacing
    
    separator = "------------------------------"
    draw.text((x_text, y_offset), separator, fill=value_color, font=font)
    y_offset += line_spacing
    
    # Draw stats
    for stat in config['display_stats']:
        if stat in user_stats and user_stats[stat] is not None:
            title = f"{stat.replace('_', ' ').title()}:"
            value = str(user_stats[stat]).replace("//", "\n - //")
            
            title_width = font.getlength(title)
            draw.text((x_text, y_offset), title, fill=value_color, font=font)
            
            x_value = x_text + title_width + 5
            remaining_width = max_text_width - title_width - 5
            
            # Handle text wrapping for long values
            if '\n' in value:  # Handle multi-line values like languages
                value_lines = value.split('\n')
                for i, line in enumerate(value_lines):
                    if i == 0 and line.strip():  # First line goes next to title
                        draw.text((x_value, y_offset), line.strip(), fill=text_color, font=font)
                        y_offset += line_spacing
                    elif line.strip():  # Subsequent lines with small indent
                        draw.text((x_text + 10, y_offset), line.strip(), fill=text_color, font=font)
                        y_offset += line_spacing
                    elif i == 0:  # Empty first line, just move to next line
                        y_offset += line_spacing
            else:
                # Single line value with word wrapping
                words = value.split()
                line = []
                x_current = x_value
                
                for word in words:
                    test_line = ' '.join(line + [word])
                    text_width = font.getlength(test_line)
                    
                    if text_width <= remaining_width:
                        line.append(word)
                    else:
                        if line:
                            draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                            y_offset += line_spacing
                            line = [word]
                            x_current = x_text + text_margin
                        else:
                            draw.text((x_current, y_offset), word, fill=text_color, font=font)
                            y_offset += line_spacing
                if line:
                    draw.text((x_current, y_offset), ' '.join(line), fill=text_color, font=font)
                    y_offset += line_spacing
    
    # Add additional_info
    if config['additional_info']:
        additional_lines = config['additional_info'].split('\n')
        for line in additional_lines:
            if line.strip():
                # Split on first colon to separate label from value
                if ':' in line:
                    parts = line.split(':', 1)
                    label = parts[0] + ':'
                    value = parts[1].strip()
                    
                    label_width = font.getlength(label)
                    draw.text((x_text, y_offset), label, fill=value_color, font=font)
                    draw.text((x_text + label_width + 5, y_offset), value, fill=text_color, font=font)
                else:
                    # No colon, just draw as colored text
                    draw.text((x_text, y_offset), line.strip(), fill=value_color, font=font)
                y_offset += line_spacing

    os.makedirs("out", exist_ok=True)
    image.save("out/fetch.png")

def generate_readme(g: Github):
        gen_image(g)
        
        image_pattern = r'<div align=\'center\'>\s*<img src=\'out/fetch\.png\' alt=\'Github Fetch\'>\s*</div>'
        image_content = "\n## Example Output\n<div align='center'>\n  <img src='out/fetch.png' alt='Github Fetch'>\n</div>\n"
        
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()
                
            start_comment = "<!--- START OF DELETION --->"
            end_comment = "<!--- END OF DELETION --->"
            pattern = re.compile(f"{start_comment}.*?{end_comment}", re.DOTALL)
            content = re.sub(pattern, "", content)
            
            with open("config.json", "r") as f:
                config = json.load(f)
            append_automatic = config.get("append_automatic", True)
            
            if append_automatic and not re.search(image_pattern, content):
                content = content.rstrip() + "\n\n" + image_content
        except FileNotFoundError:
            content = image_content
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)