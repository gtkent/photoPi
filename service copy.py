import json, os, sys, time, random
import subprocess, signal, threading
import watchdog.observers
import watchdog.events
import randomImage #, screen_handler
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_MODIFIED
from logging_config import logger
from datetime import datetime
from PIL import Image


SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR
SECONDS_IN_WEEK = 7 * SECONDS_IN_DAY

#Setup default local environment variables
CONFIG_FILE = os.path.join(os.getcwd(), 'webApp/config/config.json')
PICS_DIR = os.path.join(os.getcwd(), 'webApp/static/pics')

#webService = ""
#currConfig = ""
#wdConfigThread = ""

class ConfigChangeHandler(FileSystemEventHandler):    
    def on_modified(self, event):
        if event.event_type == EVENT_TYPE_MODIFIED:
            if event.src_path == CONFIG_FILE:
                logger.info(f"File {event.src_path} has been modified!")
                PaperPiService.handleConfigMod()
        
class ConfigWatchdogThread(threading.Thread):
    def __init__(self, directory):
        super().__init__()
        self.event_handler = ConfigChangeHandler()
        self.directory = directory
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self.event_handler, self.directory)
        self.observer.start()

    '''def run(self):
        logger.info('In watchdog thread run')
        while True:
            # Monitor file events
            event = self.observer.wait_for_events(timeout=1.0)  # adjust timeout as needed
            if event:
                # Handle the event
                print(f"Event: {event.event_type} - {event.src_path}")
            else:
                # No events, sleep for a bit
                time.sleep(0.1)
    '''
    def stop(self):
        self.observer.stop()
        self.observer.join()

class PaperPiService():   
    def __init__(self, currConfig=False, webService=False, wdConfigThread=False, picFreqTimer=False, screenFreqTimer=False, lowPower=False):
        self.currConfig = currConfig
        self.webService = webService
        self.wdConfigThread = wdConfigThread
        self.picFreqTimer = picFreqTimer
        self.screenFreqTimer = screenFreqTimer
        self.lowPower = lowPower
    
    def configWatchdog(self):
        # Create and start the watchdog thread
        logger.info('Configuring watchdog thread...')
        self.wdConfigThread = ConfigWatchdogThread(CONFIG_FILE)
        self.wdConfigThread.daemon = True  # set as daemon thread
        logger.info('Starting watchdog thread')
        self.wdConfigThread.start()
        
    def handleConfigMod(self):
        newConfig = self.read_config()
        if currConfig['changeFreq'] != newConfig['changeFreq']:
            self.setPicFreq(newConfig['changeFreq'])
        if currConfig['screenRefreshFreq'] != newConfig['screenRefreshFreq']:
            self.setScreenRefresh(newConfig['screenRefreshFreq'])
        if currConfig['lowPower'] != newConfig['lowPower']:
            self.setPower(newConfig['lowPower'])
        currConfig = newConfig
    
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
        #self.displayPic()
        self.setPicFreq(self.currConfig['changeFreq'])
        
    def refreshScreen_on_event(self):
        logger.info("Screen Refresh Event Triggered")
        #Change also refreshes and have to restore picture anyway so...
        #self.displayPic(same=True)
        self.setScreenRefresh(self.currConfig['screenRefreshFreq'])

    """ def displayPic(self, same=False):
        sc = screen_handler.Screen()
        if same:
            sc.main()
        elif self.currConfig['source'] == "Generate Random Image":
            self.create_random_image()     
            sc.main()
        else:
            randomFile = self.choose_random_image()
            newImage = Image.open(os.path.join(PICS_DIR, randomFile))
            newImage = sc.prepImage(newImage)
            sc.displayImage(newImage)
            sc.sleep() """
        
    def create_random_image(self):
        art = randomImage.RandomImage()
        seed = int(datetime.now().timestamp())
        art.myRandom = art.MyRandom(seed, art.numColors)
        art.genImage(art.shape)
        fileName = datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".bmp"
        art.image.save(os.path.join(PICS_DIR,fileName))
        art.image.save(os.path.join(PICS_DIR, "current.bmp"))
        logger.info("\nCreated: {} and copied it as {} \n".format(fileName, "current.bmp"))

    def choose_random_image(self):
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
        #print(f"CWD: {os.getcwd()}")
        self.setPicFreq(self.currConfig['changeFreq'])
        self.setScreenRefresh(self.currConfig['screenRefreshFreq'])
                
    def gunicorn(self):
        gunicorn_args = ["venv/bin/gunicorn", "--bind=0.0.0.0", "--timeout", "600", "--access-logfile", "/var/log/paperPi.log","webApp:create_app()" ]
        return subprocess.Popen(gunicorn_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def wait(self):
        while True:
            time.sleep(60) 

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
        #screen_handler.reset()
        

if __name__ == '__main__':
    logger.info('----------------------------------------------------------')
    pps = PaperPiService()
    pps.set_exit_handler(pps.on_exit)
    pps.start()
    #pps.wait()
    '''
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        start()
    elif len(sys.argv) > 1 and sys.argv[1] == 'stop':
        stop()
    else:
        print('Usage: python service.py [start|stop]')
        sys.exit(1)    
    '''