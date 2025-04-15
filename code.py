
import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import terminalio
import time
import os

# Release any displays
displayio.release_displays()

# --- Matrix Setup ---
WIDTH = 64
HEIGHT = 32
BIT_DEPTH = 4

matrix = rgbmatrix.RGBMatrix(
    width=WIDTH,
    height=HEIGHT,
    bit_depth=BIT_DEPTH,
    rgb_pins=[
        board.MTX_R1, board.MTX_G1, board.MTX_B1,
        board.MTX_R2, board.MTX_G2, board.MTX_B2,
    ],
    addr_pins=[
        board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)
display = framebufferio.FramebufferDisplay(matrix)

# Load font
try:
    font = bitmap_font.load_font("/fonts/font.bdf")
except Exception:
    font = terminalio.FONT

# === Static Game Data for Display ===
game_state = {
    "home_team": "ATL",
    "away_team": "NYM",
    "home_record": "48-30",
    "away_record": "37-41",
    "inning": "Top 4th",
    "balls": 1,
    "strikes": 2,
    "outs": 1,
    "score_home": 5,
    "score_away": 3,
    "bases": {"first": True, "second": False, "third": True}
}

# === Display Group ===
main_group = displayio.Group()

# --- Braves Logo ---
try:
    logo_bitmap = displayio.OnDiskBitmap("/images/ATL.bmp")
    logo_tilegrid = displayio.TileGrid(logo_bitmap, pixel_shader=logo_bitmap.pixel_shader, x=0, y=0)
    main_group.append(logo_tilegrid)
except Exception as e:
    print("Error loading logo:", e)

# --- Matchup Text (Top Right) ---
matchup_text = f"{game_state['home_team']} ({game_state['home_record']}) vs {game_state['away_team']} ({game_state['away_record']})"
matchup_label = label.Label(font, text=matchup_text, color=0xFFFFFF, x=24, y=0)
main_group.append(matchup_label)

# --- Inning and Bases ---
def get_base_status(first, second, third):
    return "{}{}{}".format(
        "⬤" if first else "⚪",
        "⬤" if second else "⚪",
        "⬤" if third else "⚪"
    )

inning_label = label.Label(font, text=game_state['inning'], color=0xFFFF00, x=26, y=8)
bases_str = get_base_status(**game_state["bases"])
bases_label = label.Label(font, text=bases_str, color=0xFFAA00, x=44, y=8)
main_group.append(inning_label)
main_group.append(bases_label)

# --- Count: Balls, Strikes, Outs ---
count_text = f"B:{game_state['balls']} S:{game_state['strikes']} O:{game_state['outs']}"
count_label = label.Label(font, text=count_text, color=0x00FFFF, x=26, y=16)
main_group.append(count_label)

# --- Score (Bottom Centered) ---
score_text = f"{game_state['home_team']} {game_state['score_home']} - {game_state['away_team']} {game_state['score_away']}"
score_label = label.Label(font, text=score_text, color=0x00FF00, x=10, y=26)
main_group.append(score_label)

# Show it all
display.root_group = main_group

# Idle loop
while True:
    time.sleep(1)
