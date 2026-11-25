"""The World in One Page — 25 November 2026.

A one-page broadsheet poster that sums up a day of world news in a
single image. The layout follows a classic newspaper front page: a dark
masthead with a letter-spaced nameplate, one big lead story with a drawn
graphic, a two-column grid of shorter stories, and a dark "also today"
band above the footer.

Pure Pillow, no network, no randomness: the same run always draws the
same 1024x1024 page. Run it from the repository root:

    python3 main.py

It writes entry.png next to this file.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------

PAGE = 1024                 # the poster is square, 1024 by 1024
FRAME = 0                   # thin dark border right at the page edge
MARGIN = 28                 # text margin on the left and right

HEADER_LEFT = 12            # masthead band runs almost full-bleed
HEADER_RIGHT = 1012
HEADER_BOTTOM = 119         # bottom of the dark green masthead band
GOLD_STRIP_TOP = 120        # gold rule under the masthead
GOLD_STRIP_BOTTOM = 126
ALSO_LEFT = 28              # "also today" band lines up with the grid
ALSO_RIGHT = 996
ALSO_TEXT_X = 46            # its text sits a little inside the band
LEAD_RULE_Y = 390           # gold rule under the lead story
GRID_TOP = 404              # top of the six-story grid
BOX_WIDTH = 472
BOX_HEIGHT = 148
BOX_GAP_X = 24              # gutter between the two columns
BOX_GAP_Y = 12              # gap between grid rows
ALSO_TOP = 886              # top of the dark "also today" band
ALSO_BOTTOM = 962
FOOTER_Y = 972              # footer dateline

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

PAPER = (248, 244, 236)     # warm off-white newsprint
INK = (18, 18, 18)          # near-black headline ink
GREY = (88, 88, 88)         # body copy grey
GREEN = (18, 44, 40)        # deep masthead green
GOLD = (228, 180, 34)       # masthead rule and "also today" label
RED = (192, 57, 43)         # kicker red and the chip rings
CHIP_BLUE = (31, 78, 121)   # the 5G chip
BOX_LINE = (170, 165, 150)  # hairline around the story boxes

# ---------------------------------------------------------------------------
# The stories: (tag, tag colour, headline, body)
# ---------------------------------------------------------------------------

STORIES = [
    ("UKRAINE", (33, 58, 102),
     "Abu Dhabi talks resume; 1,500-prisoner swap eyed",
     "US-mediated talks enter a second day as Kyiv faces a 27 November "
     "deadline; Zelenskyy calls the session constructive."),
    ("SPACE", (48, 92, 138),
     "Shenzhou-24 carries a Pakistani astronaut to orbit",
     "China launches its first foreign astronaut — a Pakistani payload "
     "specialist — to its space station."),
    ("MIDDLE EAST", (124, 76, 34),
     "Houthis strike Riyadh; US warns Americans",
     "A fresh Houthi attack on the Saudi capital prompts Washington to "
     "warn of a heightened threat in the region."),
    ("TECH", (16, 126, 109),
     "Nvidia's Huang apologises; says he is in 'therapy'",
     "The Nvidia chief faces staff after a bruising week as a US Senate "
     "leader accuses him of breaking export law."),
    ("SPORT", (93, 60, 144),
     "Senegal regain Africa Cup title after CAS ruling",
     "Ten months after a chaotic final, CAS overturns the decision that "
     "had handed the trophy to Morocco."),
    ("CHESS", (48, 127, 52),
     "Gukesh holds Sindarov in world title match",
     "The Indian champion weathers time pressure to draw and keep the "
     "championship match level."),
]

LEAD_DECK = (
    "A US jury convicts the Chinese tech giant of conspiracy to steal "
    "trade secrets and bank fraud, ending a years-long case over its "
    "Iran business. Beijing calls the verdict political; Washington "
    "hails it as a win for export controls."
)

ALSO_TODAY = (
    "Shein to pay $100m over US trade claims • China opens corruption "
    "probe into a Politburo member • CIA and spy chief's office hit "
    "by cyber breach • India urges human oversight of AI in warfare"
)


# ---------------------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------------------

def load_font(bold, serif, size):
    """Find a Liberation font, fall back to DejaVu if it is missing."""
    family = "Serif" if serif else "Sans"
    weight = "Bold" if bold else "Regular"
    candidates = [
        "/usr/share/fonts/truetype/liberation/Liberation%s-%s.ttf" % (family, weight),
        "/usr/share/fonts/truetype/dejavu/DejaVu%s%s.ttf" % (family, "-Bold" if bold else ""),
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    """Split text into lines that fit max_width, word by word."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_tracked(draw, text, font, x, y, tracking, fill, space_width=None):
    """Draw text with extra space between the letters, like a nameplate.

    A space can be given its own advance: the nameplate's word gap is
    tighter than the font's own space, so it is set by hand.
    """
    for letter in text:
        draw.text((x, y), letter, font=font, fill=fill)
        if letter == " " and space_width is not None:
            x += space_width
        else:
            x += draw.textlength(letter, font=font) + tracking


def draw_chip(draw, cx, cy):
    """The lead-story graphic: a 5G chip inside a double red ring."""
    # Two concentric red rings.
    draw.ellipse([cx - 86, cy - 86, cx + 86, cy + 86], outline=RED, width=5)
    draw.ellipse([cx - 74, cy - 74, cx + 74, cy + 74], outline=RED, width=2)
    # The chip body, with a row of pins on each side.
    draw.rounded_rectangle([cx - 55, cy - 55, cx + 55, cy + 55], radius=12, fill=CHIP_BLUE)
    for i in range(4):
        step = -33 + i * 22
        draw.rectangle([cx + step - 5, cy - 69, cx + step + 5, cy - 55], fill=CHIP_BLUE)
        draw.rectangle([cx + step - 5, cy + 55, cx + step + 5, cy + 69], fill=CHIP_BLUE)
        draw.rectangle([cx - 69, cy + step - 5, cx - 55, cy + step + 5], fill=CHIP_BLUE)
        draw.rectangle([cx + 55, cy + step - 5, cx + 69, cy + step + 5], fill=CHIP_BLUE)
    # The 5G label in the middle of the chip.
    label = load_font(True, False, 38)
    draw.text((cx, cy), "5G", font=label, fill="white", anchor="mm")


def draw_story(draw, x, y, colour, tag, headline, body):
    """One of the six boxes in the two-column grid below the lead."""
    # White face, then a hairline border and a solid colour bar on top.
    draw.rectangle([x, y, x + BOX_WIDTH, y + BOX_HEIGHT], fill="white")
    draw.rectangle([x, y, x + BOX_WIDTH, y + BOX_HEIGHT], outline=BOX_LINE, width=1)
    draw.rectangle([x, y, x + BOX_WIDTH, y + 6], fill=colour)
    # The section tag: a small rounded label in the section colour.
    tag_font = load_font(True, False, 17)
    tag_width = draw.textlength(tag, font=tag_font) + 20
    draw.rounded_rectangle([x + 14, y + 16, x + 14 + tag_width, y + 42],
                           radius=5, fill=colour)
    draw.text((x + 24, y + 29), tag, font=tag_font, fill="white", anchor="lm")
    # Headline in bold serif, wrapped to two lines.
    head_font = load_font(True, True, 27)
    text_y = y + 51
    for line in wrap(draw, headline, head_font, BOX_WIDTH - 28)[:2]:
        draw.text((x + 14, text_y), line, font=head_font, fill=INK)
        text_y += 28
    # Body copy in grey serif, two lines.
    body_font = load_font(False, True, 17)
    text_y = y + 107
    for line in wrap(draw, body, body_font, BOX_WIDTH - 28)[:2]:
        draw.text((x + 14, text_y), line, font=body_font, fill=GREY)
        text_y += 19


# ---------------------------------------------------------------------------
# The page, top to bottom
# ---------------------------------------------------------------------------

def draw_masthead(draw):
    """Dark green band: the nameplate on the left, the date on the right."""
    draw.rectangle([HEADER_LEFT, FRAME, HEADER_RIGHT, HEADER_BOTTOM], fill=GREEN)
    title_font = load_font(True, True, 80)
    draw_tracked(draw, "THE WORLD", title_font, MARGIN, 12, -3, "white",
                 space_width=17)
    gold_font = load_font(True, False, 17)
    draw.text((MARGIN - 2, 95), "IN ONE PAGE", font=gold_font, fill=GOLD)
    date_font = load_font(True, False, 22)
    small_font = load_font(False, False, 17)
    right = PAGE - 30
    draw.text((right, 30), "WEDNESDAY 25 NOVEMBER 2026",
              font=date_font, fill="white", anchor="ra")
    draw.text((right, 60), "ONE DAY  •  ONE IMAGE",
              font=small_font, fill="white", anchor="ra")
    draw.text((right, 88), "WORLD NEWS  •  25 NOV 2026",
              font=small_font, fill="white", anchor="ra")
    draw.rectangle([HEADER_LEFT, GOLD_STRIP_TOP, HEADER_RIGHT, GOLD_STRIP_BOTTOM],
                   fill=GOLD)


def draw_lead(draw):
    """The Huawei verdict: kicker, two-line headline, deck, chip."""
    kicker_font = load_font(True, False, 22)
    draw.text((MARGIN, 145), "TECH  •  US v HUAWEI, NEW YORK",
              font=kicker_font, fill=RED)
    head_font = load_font(True, True, 58)
    draw.text((MARGIN, 166), "HUAWEI FOUND", font=head_font, fill=INK)
    draw.text((MARGIN, 228), "GUILTY IN US TRIAL", font=head_font, fill=INK)
    deck_font = load_font(False, True, 21)
    text_y = 296
    for line in wrap(draw, LEAD_DECK, deck_font, 620):
        draw.text((MARGIN, text_y), line, font=deck_font, fill=GREY)
        text_y += 25
    draw_chip(draw, 852, 252)
    guilty_font = load_font(True, False, 30)
    draw.text((852, 350), "GUILTY", font=guilty_font, fill=RED, anchor="ma")
    draw.rectangle([MARGIN, LEAD_RULE_Y, PAGE - MARGIN, LEAD_RULE_Y + 1],
                   fill=GOLD)


def draw_grid(draw):
    """Six stories in two columns and three rows."""
    for i, (tag, colour, headline, body) in enumerate(STORIES):
        x = MARGIN + (i % 2) * (BOX_WIDTH + BOX_GAP_X)
        y = GRID_TOP + (i // 2) * (BOX_HEIGHT + BOX_GAP_Y)
        draw_story(draw, x, y, colour, tag, headline, body)


def draw_also_today(draw):
    """Dark band with the rest of the day's headlines."""
    draw.rectangle([ALSO_LEFT, ALSO_TOP, ALSO_RIGHT, ALSO_BOTTOM], fill=GREEN)
    label_font = load_font(True, False, 19)
    draw.text((ALSO_TEXT_X, ALSO_TOP + 13), "ALSO TODAY", font=label_font, fill=GOLD)
    body_font = load_font(False, True, 18)
    text_y = ALSO_TOP + 38
    for line in wrap(draw, ALSO_TODAY, body_font, 900):
        draw.text((ALSO_TEXT_X, text_y), line, font=body_font, fill="white")
        text_y += 16


def draw_footer(draw):
    """Dateline on the left, paper name on the right, sources below."""
    foot_font = load_font(True, False, 19)
    draw.text((MARGIN, FOOTER_Y),
              "Headlines as reported on Wednesday 25 November 2026",
              font=foot_font, fill=INK)
    draw.text((PAGE - MARGIN, FOOTER_Y), "THE WORLD IN ONE PAGE",
              font=foot_font, fill=INK, anchor="ra")
    source_font = load_font(False, False, 14)
    draw.text((MARGIN, FOOTER_Y + 23), "Sources: BBC, Reuters, The Hindu, AP, AFP",
              font=source_font, fill=GREY)


def main():
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)

    # Thin dark border right at the edge of the page.
    draw.rectangle([FRAME, FRAME, PAGE - 1, PAGE - 1],
                   outline=INK, width=2)

    draw_masthead(draw)
    draw_lead(draw)
    draw_grid(draw)
    draw_also_today(draw)
    draw_footer(draw)

    here = os.path.dirname(os.path.abspath(__file__))
    page.save(os.path.join(here, "entry.png"))
    print("Wrote entry.png", page.size)


if __name__ == "__main__":
    main()
