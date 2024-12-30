import json, os, sys, time, random
import subprocess, signal, threading
import randomImage, screen_handler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_MODIFIED
from logging_config import logger
from datetime import datetime
from PIL import Image
from queue import Queue, Full, Empty

SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR
SECONDS_IN_WEEK = 7 * SECONDS_IN_DAY
q = Queue(maxsize=1)

#Setup default local environment variables
CONFIG_FILE = os.path.join(os.getcwd(), 'webApp/config/config.json')
PICS_DIR = os.path.join(os.getcwd(), 'webApp/static/pics')

class ConfigChangeHandler(FileSystemEventHandler):    
    def on_modified(self, event):
        if event.event_type == EVENT_TYPE_MODIFIED:
            if event.src_path == CONFIG_FILE:
                logger.info(f"File {event.src_path} has been modified!")
                try:
                    q.put(True, block=False)
                except Full:
                    pass
                
class PaperPiService():   
    def __init__(self, currConfig=False, webService=False, wdConfigThread=False, picFreqTimer=False, screenFreqTimer=False, lowPower=False):
        self.currConfig = currConfig
        self.webService = webService
        self.wdConfigThread = wdConfigThread
        self.picFreqTimer = picFreqTimer
        self.screenFreqTimer = screenFreqTimer
        self.lowPower = lowPower
    
    def runObserver(self):
        path = CONFIG_FILE
        event_handler = ConfigChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, path)
        logger.info("Observer Thread Starting")
        observer.start()
    
    def configWatchdog(self):
        # Create and start the watchdog thread
        logger.info('Configuring watchdog thread...')
        self.wdConfigThread = threading.Thread(target=self.runObserver, args=())
        self.wdConfigThread.daemon = True 
        logger.info('Starting watchdog thread')
        self.wdConfigThread.start()
        
    def handleConfigMod(self):
        newConfig = self.read_config()
        if self.currConfig['changeFreq'] != newConfig['changeFreq']:
            self.setPicFreq(newConfig['changeFreq'])
        if self.currConfig['screenRefreshFreq'] != newConfig['screenRefreshFreq']:
            self.setScreenRefresh(newConfig['screenRefreshFreq'])
        if self.currConfig['lowPower'] != newConfig['lowPower']:
            self.setPower(newConfig['lowPower'])
        self.currConfig = newConfig
    
    def setPicFreq(self, newPicFreq):
        logger.info(f"Setting new image change timer event: {newPicFreq}")
        if newPicFreq == 'Daily':
            self.picFreqTimer = threading.Timer(SECONDS_IN_DAY, self.changePic_on_event)
        elif newPicFreq == 'Weekly':
            self.picFreqTimer = threading.Timer(SECONDS_IN_WEEK, self.changePic_on_event)
        else:
            self.picFreqTimer = threading.Timer(float(newPicFreq) * SECONDS_IN_HOUR, self.changePic_on_event)            
        self.picFreqTimer.start()
        
    def setScreenRefresh(self, newScreenFreq):
        logger.info(f"Setting new screen refresh timer event: {newScreenFreq}")
        if newScreenFreq == 'Daily':
            self.screenFreqTimer = threading.Timer(SECONDS_IN_DAY, self.refreshScreen_on_event)
        elif newScreenFreq == 'Weekly':
            self.screenFreqTimer = threading.Timer(SECONDS_IN_WEEK, self.refreshScreen_on_event)
        else:
            self.screenFreqTimer = threading.Timer(float(newScreenFreq) * SECONDS_IN_HOUR, self.refreshScreen_on_event)           
        self.screenFreqTimer.start()

    def setPower(self, newPower):
        logger.info(f"Changing low power to {newPower}")
        self.lowPower = newPower
        return

    def changePic_on_event(self):
        logger.info("Picture Change Event Triggered")
        self.displayPic()
        self.create_random_image()
        self.setPicFreq(self.currConfig['changeFreq'])
        
    def refreshScreen_on_event(self):
        logger.info("Screen Refresh Event Triggered")
        #Change also refreshes and have to restore picture anyway so...
        self.displayPic(same=True)
        self.setScreenRefresh(self.currConfig['screenRefreshFreq'])

    def displayPic(self, same=False):
        sc = screen_handler.Screen()
        if same:
            logger.info("Displaying the same image")
            screen_handler.main()
        elif self.currConfig['source'] == "Generate Random Image":
            self.create_random_image()     
            logger.info("Display a new random image")
            screen_handler.main()
        else:
            randomFile = self.choose_random_image()
            newImage = Image.open(os.path.join(PICS_DIR, randomFile))
            newImage = sc.prepImage(newImage)
            logger.info("Choosing image to display")
            sc.displayImage(newImage)
            sc.sleep()  
        
    def create_random_image(self):
        fileName = datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".bmp"
        args = {"fileName": fileName, "directory": PICS_DIR}
        randomImage.createRandomImage(**args)
        origFile = os.path.join(PICS_DIR,fileName)
        copyFile = os.path.join(PICS_DIR,'current.bmp')
        os.system(f'cp {origFile} {copyFile}')
        logger.info(f"Created: {fileName} and copied as current.bmp")

    def choose_random_image(self):
        logger.info("Trying to choose and image to display...")
        ALLOWED_EXTENSIONS = {'.zip', '.7z', '.png', '.jpg', '.jpeg', '.gif', '.bmp'}

        files = [os.path.join(path, filename) for path, dirs, files in os.walk(PICS_DIR) 
            for filename in files if os.path.splitext(filename)[1] in ALLOWED_EXTENSIONS]

        return random.choice(files)

    def set_exit_handler(self, func):
        logger.info("Exit handler setup")
        signal.signal(signal.SIGTERM, func)
        
    def on_exit(self, sig, func=None):
        logger.info("Exit handler triggered")
        os.killpg(os.getpgid(self.webService.pid), signal.SIGTERM)
        self.stop()
        sys.exit(1)

    def read_config(self):    
        with open(CONFIG_FILE, 'r') as file:
            data = json.load(file)
        return data

    def setup(self):
        global CONFIG_FILE
        global PICS_DIR
        
        #Read in environment variables and config
        CONFIG_FILE = os.getenv("PAPERPICONFIG", CONFIG_FILE)
        PICS_DIR = os.getenv("PAPERPIPICS", PICS_DIR)

        logger.info('Setup PaperPi service')
        logger.info(f"Using Configuration file: {CONFIG_FILE}")
        logger.info(f"Using Picture Directory file: {PICS_DIR}")
        self.currConfig = self.read_config() 
        logger.info(f"Current Configuration is: {self.currConfig}")
        self.setPicFreq(self.currConfig['changeFreq'])
        self.setScreenRefresh(self.currConfig['screenRefreshFreq'])
                
    def gunicorn(self):
        gunicorn_args = ["/home/user/.local/bin/gunicorn", "--bind=0.0.0.0:8080", "--timeout", "600", "webApp:create_app()" ]
        return subprocess.Popen(gunicorn_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    """
    def gunicorn(self):
        gunicorn_args = ["venv/bin/gunicorn", "--bind=0.0.0.0:8080", "--timeout", "600", "--access-logfile", "/var/log/paperPi.log","webApp:create_app()" ]
        return subprocess.Popen(gunicorn_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    """
    def wait(self):
        logger.info("Wait loop started to monitor config changes")
        while True:
            time.sleep(60)
            try:
                changed = q.get(False)
            except Empty:
                pass
            else:
                if changed:
                    self.handleConfigMod()
  
    def startWebApp(self):
        self.webService = self.gunicorn()
        
        if self.webService:
            logger.info('PaperPi Web service started')
        else:
            logger.info('PaperPi Web service failed')
            sys.exit(1)

    def start(self):
        logger.info('Starting PaperPi service...')
        self.setup()
        self.startWebApp()
        self.configWatchdog()

    def stop(self):
        # Your cleanup logic goes here
        logger.info('Stopping PaperPi service...')
        self.wdConfigThread.stop()
        screen_handler.reset()

if __name__ == '__main__':
    logger.info('----------------------------------------------------------')
    pps = PaperPiService()
    pps.set_exit_handler(pps.on_exit)
    pps.start()
    pps.wait()
