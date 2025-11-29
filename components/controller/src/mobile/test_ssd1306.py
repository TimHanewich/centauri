import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Initialize OLED display dimensions
WIDTH = 128
HEIGHT = 64

# Set up I2C communication with the OLED display
i2c = board.I2C()  # Utilizes board's SCL and SDA pins
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

# Clear the OLED display
oled.fill(0)
oled.show()

# Create a new image with 1-bit color for drawing
image = Image.new("1", (oled.width, oled.height))

# Obtain a drawing object to manipulate the image
draw = ImageDraw.Draw(image)

# Draw a filled white rectangle as the background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Define border size for an inner rectangle
BORDER = 5
# Draw a smaller black rectangle inside the larger one
draw.rectangle(
    (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    outline=0,
    fill=0,
)

# Load the default font for text
font = ImageFont.load_default()

def getfontsize(font, text):
    # Calculate the size of the text in pixels
    left, top, right, bottom = font.getbbox(text)
    return right - left, bottom - top

# Define the text to be displayed
text = "Hello World!"
# Get the width and height of the text in pixels
(font_width, font_height) = getfontsize(font, text)
# Draw the text, centered on the display
draw.text(
    (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
    text,
    font=font,
    fill=255,
)

# Send the image to the OLED display
oled.image(image)
oled.show()