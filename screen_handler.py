import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'webApp/static/pics')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs/RaspberryPi_JetsonNano/python/lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

picdir = os.getenv("PAPERPIPICS", picdir)

import logging
from waveshare_epd import epd7in3f
from PIL import Image, ImageOps


logging.basicConfig(level=logging.DEBUG)

class Screen:
    def __init__(self):
        logging.info("New epd7in3f Screen")
        self.epd = epd7in3f.EPD()
        self.initialize()
        
    def initialize(self):
        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear()
    
    def sleep(self):
        self.epd.sleep() 

    def clear(self):
        self.epd.Clear() 

    def prepImage(self, img):
        if img.height > img.width:
            img = img.rotate(270)
        if img.width != self.epd.width or img.height != self.epd.height:
            img = ImageOps.fit(img, (800, 480), Image.LANCZOS)

        return img

    def displayImage(self, image):
        self.epd.display(self.epd.getbuffer(image))

def test():
    testFile = os.path.join(picdir, 'current.bmp')
    print(f"{testFile} exists {os.path.exists(testFile)}")

def reset():
    sc = Screen()
    sc.clear()
    sc.sleep()
    
def main():
    try:
        # read Current Image file 
        logging.info("Reading current bmp file")
        sc = Screen()
        newImage = Image.open(os.path.join(picdir, 'current.bmp'))
        newImage = sc.prepImage(newImage)
        sc.displayImage(newImage)
       
        logging.info("Goto Sleep...")
        sc.sleep()
            
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in3f.epdconfig.module_exit(cleanup=True)
        exit()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset()
    else:
        main()
