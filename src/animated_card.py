"""Render a small looping terminal card from aggregate profile statistics."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = '#0d1117'
PANEL = '#0f172a'
BORDER = '#334155'
TEAL = '#5eead4'
TEXT = '#e2e8f0'
MUTED = '#94a3b8'
CAT = r'''
       /\          /\
      /  \________/  \
     /                \
    /                  \
   |                    |
   |     E        E     |
 --|--       w       --|--
   |    ///     ///     |
    \                  /
     '----------------'
          |  (>)  |
     __   |       |
    /  \ /         \
   |   |/           \
   |   |             |
    \   \           /
     '.__|__|___|__|'
'''.strip('\n').splitlines()


def font(size):
    for path in (
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf',
        'C:/Windows/Fonts/consola.ttf',
        'consola.ttf',
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def fitted(text, size, width):
    face = font(size)
    while face.getlength(text) > width and size > 12:
        size -= 1
        face = font(size)
    return face


def wrapped(text, face, width):
    lines = []
    line = ''
    for word in text.split():
        candidate = f'{line} {word}'.strip()
        if line and face.getlength(candidate) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    return lines + ([line] if line else [])


def render_card(stats, config, output_dir='out'):
    username = str(stats['username'])
    stack = next((line.partition(':')[2].strip() for line in config.get('additional_info', '').splitlines()
                  if line.lower().startswith('stack:')), '')
    stack = stack.replace(' | ', ' / ')
    width, height = 1440, 800
    x, right = 575, 1360
    header = f'{username}@github.com'
    header_font = fitted(header, 36, right - x - 30)
    count = f"{stats['total_lines_of_code']:,}"
    count_font = fitted(count, 82, right - x)
    labels = {'public_repos': 'Public repos', 'total_stars': 'Stars', 'total_commits': 'Commits'}
    rows = config.get('card_stats', ['public_repos', 'total_stars', 'total_commits'])
    rows = [key for key in rows if key in stats and stats[key] is not None]
    footer_font = font(19)
    footer_lines = wrapped(stack, footer_font, right - x - 85)
    # Expand for configured rows or long stack descriptions rather than clipping them.
    divider_y = 445 + len(rows) * 53
    height = max(height, divider_y + 105 + len(footer_lines) * 27)
    frames = []
    for blink, cursor in [(False, True), (True, True), (False, False), (False, True)]:
        image = Image.new('RGB', (width, height), BG)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((24, 24, width - 25, height - 25), radius=18,
                               fill=PANEL, outline=BORDER, width=3)
        # The mascot is code-native ASCII, so it stays crisp at every frame.
        cat_font = font(25)
        for index, line in enumerate(CAT):
            line = line.replace('E', '-' if blink else '^')
            draw.text((65, 130 + index * 29), line, font=cat_font, fill=TEAL)
        prompt = f'{username.lower()}@dev:~$'
        prompt_font = fitted(prompt, 23, 435)
        draw.text((65, height - 104), prompt, font=prompt_font, fill=TEAL)
        if cursor:
            px = 72 + prompt_font.getlength(prompt)
            draw.rectangle((px, height - 99, px + 13, height - 77), fill=TEAL)
        draw.text((x, 85), header, font=header_font, fill=TEXT)
        if cursor:
            hx = x + header_font.getlength(header) + 12
            draw.rectangle((hx, 91, hx + 15, 121), fill=TEAL)
        draw.line((x, 157, right, 157), fill=BORDER, width=2)
        draw.text((x, 190), 'Repositories LOC', font=font(32), fill=MUTED)
        draw.text((x - 4, 235), count, font=count_font, fill=TEAL)
        draw.text((x, 345), 'Across public & private repositories', font=font(23), fill=MUTED)
        for index, key in enumerate(rows):
            y = 429 + index * 53
            label = labels.get(key, key.replace('_', ' ').title())
            value = stats[key]
            value = f'{value:,}' if type(value) is int else str(value)
            draw.text((x, y), label, font=fitted(label, 26, 350), fill=MUTED)
            draw.text((x + 390, y), value, font=fitted(value, 28, right - x - 390), fill=TEXT)
        draw.line((x, divider_y, right, divider_y), fill=BORDER, width=2)
        if stack:
            draw.text((x, divider_y + 33), 'Stack', font=font(21), fill=MUTED)
            for index, line in enumerate(footer_lines):
                draw.text((x + 85, divider_y + 34 + index * 27), line, font=footer_font, fill=TEXT)
        draw.text((x, height - 66), 'Aggregate stats / Updated daily', font=font(17), fill=MUTED)
        frames.append(image)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frames[0].save(output / 'fetch.png')
    # Share one palette so text colors remain identical across GIF frames.
    palette = frames[0].quantize(colors=256)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    frames[0].save(output / 'fetch.gif', save_all=True, append_images=frames[1:],
                   duration=[1800, 160, 900, 640], loop=0, disposal=2, optimize=True)
