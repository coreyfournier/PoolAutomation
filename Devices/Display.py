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
import os

class Display:
    def __init__(self, width, height) -> None:
        self._width = width
        self._height = height
        self._font = ImageFont.load_default()
        

    def _getImage(self, text:"list[str]"):
        image = Image.new("1", (self._width, self._height))
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        (font_width, font_height) = self._font.getsize(text[0])

        lineNumber:int = 1
        for row in text:
            draw.text(
                (0, 
                (font_height + 2) * lineNumber),
                row,
                font=self._font,
                fill=255
            )
            lineNumber +=1
        return image

class DisplayStub(Display):
    def __init__(self, saveToDirectory:str) -> None:
        super().__init__(128,64)

        self._saveTo = saveToDirectory

    def write(self, text:"list[str]"):
        image = self._getImage(text)
        image.save(self._saveTo)


#d = DisplaySSD1306(oled)
class DisplaySSD1306(Display):
    def __init__(self, oled) -> None:
        super().__init__(oled.width, oled.height)

        self._oled = oled                

    def write(self, text:"list[str]"):
        # Clear display.
        self._oled.fill(0)
        self._oled.show()    

        image = self._getImage(text)

        # Display image
        self._oled.image(image)
        self._oled.show()