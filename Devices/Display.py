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
    def __init__(self, width, height, fontDirectory:str) -> None:
        self._width = width
        self._height = height
        self._font = ImageFont.truetype(os.path.join(fontDirectory,"Anonymous Pro.ttf"), 10)
        #self._font = ImageFont.load_default()        
        self._color = 255

    def _getImage(self, text:"list[str]"):
        image = Image.new("1", (self._width, self._height))
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)
        
        bbox = self._font.getbbox(text[0])
        font_width = bbox[2] - bbox[0]
        font_height = bbox[3] - bbox[1]
        

        lineNumber:int = 0
        for row in text:
            if(lineNumber == 0):
                position = font_height * lineNumber
            else:
                position = (font_height * lineNumber)  + 3
            
            textPosition = (0, position)

            draw.text(textPosition, row, font=self._font, fill = self._color)
            lineNumber +=1
            
        return image

    def write(self, text:"list[str]"):
        """Writes the text out to the display

        Args:
            text (list[str]): Expects the first row of text to the be header. All other lines written out to the display
        """
        pass

class DisplayStub(Display):
    def __init__(self, saveToDirectory:str, fontPath:str) -> None:
        super().__init__(128,64, fontPath)

        self._saveTo = saveToDirectory

    def write(self, text:"list[str]"):
        image = self._getImage(text)
        image.save(self._saveTo)


class DisplaySSD1306(Display):
    def __init__(self, oled, fontPath:str) -> None:
        super().__init__(oled.width, oled.height, fontPath)

        self._oled = oled                

    def write(self, text:"list[str]"):
        # Clear display.
        self._oled.fill(0)
        self._oled.show()    

        image = self._getImage(text)

        # Display image
        self._oled.image(image)
        self._oled.show()