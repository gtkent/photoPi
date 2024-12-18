#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pics')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'libs')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in3f
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

class Screen:
    def __init__(self):
        logging.info("New epd7in3f Screen")
        epd = epd7in3f.EPD()
        self.initialize()
        #newImage = Image.new('RGB', (epd.width, epd.height), epd.WHITE) 

    def initialize(self):
        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear()
    
    def sleep(self):
        self.epd.sleep() 

    def clear(self):
        self.epd.Clear() 

    def displayImage(self, image):
        self.epd.display(self.epd.getbuffer(image))

def main():
    try:
        # read Current Image file 
        logging.info("Reading current.gif file")
        sc = Screen()
        newImage = Image.open(os.path.join(picdir, 'current.gif'))
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
    main()