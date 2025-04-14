# tests/test_hardware.py - Basic hardware test for Matrix Portal S3

import time
import board
import displayio
import terminalio
from adafruit_display_text.label import Label

print("Matrix Portal S3 Hardware Test")
print("-----------------------------")

# Initialize display
print("Initializing display...")
matrix = displayio.Display(board.DISPLAY)
print(f"Display dimensions: {matrix.width}x{matrix.height}")

# Create a display group
group = displayio.Group()
matrix.root_group = group

# Create a simple test pattern
print("Creating test pattern...")
bitmap = displayio.Bitmap(matrix.width, matrix.height, 3)
palette = displayio.Palette(3)
palette[0] = 0xFF0000  # Red
palette[1] = 0x00FF00  # Green
palette[2] = 0x0000FF  # Blue

# Fill the bitmap with color blocks
for x in range(matrix.width):
    for y in range(matrix.height):
        if x < matrix.width // 3:
            bitmap[x, y] = 0
        elif x < 2 * (matrix.width // 3):
            bitmap[x, y] = 1
        else:
            bitmap[x, y] = 2

# Create and add the TileGrid to the group
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
group.append(tile_grid)

print("Test pattern displayed. Waiting 3 seconds...")
time.sleep(3)

# Create and display a text label
print("Testing text display...")
text = "Matrix S3 OK!"
text_area = Label(terminalio.FONT, text=text, color=0xFFFFFF)
text_area.x = (matrix.width - text_area.width) // 2
text_area.y = matrix.height // 2
group.append(text_area)

print("Test complete!")
print("If you see colored bars and text on the matrix, your hardware is working correctly.")
print("This test will end in 10 seconds...")
time.sleep(10)

# Clear the display
group = displayio.Group()
matrix.root_group = group