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


BG='#050910'
PANEL='#080d18'
CYAN='#43eddf'
PINK='#f16ab7'
WHITE='#e1edf4'
MUTED='#8da5b7'


def layout(portrait,index,stats,config):
    image=Image.new('RGB',(1920,1200),BG)
    draw=ImageDraw.Draw(image)
    points=[(30,62),(62,30),(1858,30),(1890,62),(1890,1138),(1858,1170),(62,1170),(30,1138)]
    draw.polygon(points,fill=PANEL,outline='#25354b',width=2)
    draw.line([(30,156),(30,62),(62,30),(208,30)],fill=CYAN,width=4)
    draw.line([(1712,1170),(1858,1170),(1890,1138),(1890,1044)],fill=PINK,width=4)
    draw.text((90,84),f"[ {stats['username'].upper()} / PROFILE ]",font=font(24),fill=CYAN)
    draw.text((1455,84),'NEOFETCH / GITHUB',font=font(23),fill=MUTED)
    image.paste(portrait,(88,224))
    draw.line((850,205,850,1030),fill='#233449',width=2)
    draw.text((910,208),str(stats['username']),font=font(46),fill=WHITE)
    name_width=font(46).getlength(str(stats['username']))
    draw.text((910+name_width,208),'@github',font=font(46),fill=PINK)
    draw.text((910,275),'------------------------------',font=font(28),fill='#345268')
    rows=list(config.get('profile_info', [])) + [('', '')]
    info_count=len(rows)
    labels={'total_lines_of_code':'Repositories LOC','public_repos':'Public repos','total_stars':'Stars','total_commits':'Commits'}
    for key in ['total_lines_of_code'] + config.get('card_stats', ['public_repos','total_stars','total_commits']):
        if key in stats:
            value=stats[key]
            rows.append((labels.get(key,key.replace('_',' ').title()), f'{value:,}' if type(value) is int else str(value)))
    for row,(label,value) in enumerate(rows):
        y=352+row*min(55, 570/max(1,len(rows)-1))
        draw.text((910,y),label,font=font(27),fill=CYAN if row<info_count else PINK)
        draw.text((1225,y),value,font=fitted(value,28,600),fill=WHITE)
    for n,color in enumerate(['#26364b','#2c81af','#43eddf','#71b6e9','#b9aaa0','#704a29','#f16ab7','#e1edf4']):
        draw.rectangle((910+n*48,963,950+n*48,994),fill=color)
    draw.text((90,1000),f"{stats['username'].lower()}@dev:~$",font=font(29),fill=CYAN)
    if index%16<8:draw.rectangle((366,1009,380,1037),fill=CYAN)
    draw.line((90,1080,1830,1080),fill='#233449',width=2)
    draw.text((90,1107),'AGGREGATE STATS / UPDATED DAILY',font=font(22),fill=MUTED)
    draw.text((1140,1107),'LOC INCLUDES PUBLIC + PRIVATE REPOS',font=font(22),fill=MUTED)
    return image



def render_card(stats, config, output_dir='out', portrait_frames=None):
    if not portrait_frames:
        raise ValueError('Canvas portrait frames are required')
    frames=[layout(portrait,index,stats,config) for index,portrait in enumerate(portrait_frames)]
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    frames[0].save(output/'fetch.png')
    swatches=Image.new('RGB',(480,300*len(frames)))
    for index,frame in enumerate(frames):
        swatches.paste(frame.resize((480,300)),(0,index*300))
    palette=swatches.quantize(colors=256)
    frames=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
    frames[0].save(output/'fetch.gif',save_all=True,append_images=frames[1:],
                   duration=[120 if index%2==0 else 130 for index in range(len(frames))],
                   loop=0,disposal=2,optimize=True)
