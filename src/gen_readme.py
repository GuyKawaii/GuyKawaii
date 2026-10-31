import json, os, re 
from src.draw_ascii import generate_logo
from src.fetch_info import fetch_stats
from PIL import Image, ImageDraw, ImageFont
from github import Github

def stat_label(stat: str) -> str:
    if stat == "total_lines_of_code":
        return "Repositories LOC"
    return stat.replace("_", " ").title()


def format_stat(value) -> str:
    return f"{value:,}" if type(value) is int else str(value)


def generate_fetch(g:Github) -> str:
    with open("config.json", "r") as f:
        config = json.load(f)

    user = fetch_stats(g)
    pfp = generate_logo(g)


    stats = f"{user['username']}@github.com\n------------------------------\n"
    for stat in config['display_stats']:
        if stat in user:
            stats += f"{stat_label(stat)}: {format_stat(user[stat])}\n"
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
        "teal": (94, 234, 212, 255),
    }

    if color in color_map:
        return color_map[color]
    else:
        return color_map["lightblue"]



def gen_image(g: Github):
    from src.animated_card import render_card

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
    from src.canvas_portrait import portrait_frames
    frames = portrait_frames(g.get_user().avatar_url)
    render_card(fetch_stats(g), config, portrait_frames=frames)


def generate_readme(g: Github):
        gen_image(g)
        
        image_pattern = r'<div align=\'center\'>\s*<img src=\'out/fetch\.gif\' alt=\'Github Fetch\'>\s*</div>'
        image_content = "\n## Example Output\n<div align='center'>\n  <img src='out/fetch.gif' alt='Github Fetch'>\n</div>\n"
        
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()
                
            content = content.replace("src='out/fetch.png'", "src='out/fetch.gif'")

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