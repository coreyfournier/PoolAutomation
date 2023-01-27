#I followed this site: https://learn.adafruit.com/monochrome-oled-breakouts/python-usage-2
#Requires installing the following before or after pillow:
#sudo apt-get install libjpeg-dev -y
#sudo apt-get install zlib1g-dev -y
#sudo apt-get install libfreetype6-dev -y
#sudo apt-get install liblcms1-dev -y
#sudo apt-get install libopenjp2-7 -y
#sudo apt-get install libtiff5 -y
#
from PIL import Image, ImageDraw, ImageFont

class Display:
    pass
#d = DisplaySSD1306(oled)
class DisplaySSD1306(Display):
    def __init__(self, oled) -> None:
        self._oled = oled
        self._image = Image.new("1", (oled.width, oled.height))
        self._font = ImageFont.load_default()

    def write(self, text:"list[str]"):
        # Clear display.
        self._oled.fill(0)
        self._oled.show()

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(self._image)

        # Draw Some Text
        text = "Hello World!"

        (font_width, font_height) = self._font.getsize(text)
        lineNumber:int = 1
        for row in text:
            draw.text(
                (self._oled.width // 2 - font_width // 2, 
                font_height + 2 * lineNumber),
                row,
                font=self._font,
                fill=255
            )

            lineNumber +=1

        # Display image
        self._oled.image(self._image)
        self._oled.show()