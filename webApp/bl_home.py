from flask import (
    Blueprint, render_template, request, send_from_directory, flash
)
from .layoutUtils import *
from .auth import *
from datetime import datetime
from logging_config import logger
import json, os
#from service import PaperPiService, resetScreen #, screen_handler

CONFIG_FILE = os.path.join(os.getcwd(),'webApp/config/config.json')
CONFIG_FILE = os.getenv("PAPERPICONFIG", CONFIG_FILE)

PICS_DIR = os.path.join(os.getcwd(), 'webApp/static/pics')
PICS_DIR = os.getenv("PAPERPIPICS", PICS_DIR)

def read_config():    
    with open(CONFIG_FILE, 'r') as file:
        data = json.load(file)
    return data

def write_config(newConfig):    
    with open(CONFIG_FILE, 'r+') as file:
        data = json.load(file)
        data['source'] = newConfig['source']        
        data['changeFreq'] = newConfig['other_imageFreq'] if newConfig['changeFreq'] == 'other' else newConfig['changeFreq']
        data['screenRefreshFreq'] = newConfig['other_refreshFreq'] if newConfig['screenRefreshFreq'] == 'other' else newConfig['screenRefreshFreq']
        if 'lowPower' in newConfig:
            data['lowPower'] = newConfig['lowPower']
        else:
            data['lowPower'] = "False"
        file.seek(0)
        file.truncate(0)
        json.dump(data, file)

def create_random_image():
    fileName = datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".bmp"
    args = {"fileName": fileName, "directory": PICS_DIR}
    randomImage.createRandomImage(**args)
    origFile = os.path.join(PICS_DIR,fileName)
    copyFile = os.path.join(PICS_DIR,'current.bmp')
    os.system(f'cp {origFile} {copyFile}')
    logger.info(f"Created: {fileName} and copied as current.bmp")

    '''pps = service.PaperPiService()
    pps.create_random_image()
    pps.displayPic(True)'''

bp = Blueprint('bl_home', __name__)

@bp.route('/', methods=('GET', 'POST'))
@manage_cookie_policy
def index():
    print("Picture Directory: {}".format(PICS_DIR))
    config = read_config()
    mc = set_menu("home")
    return render_template('home/index.html', mc=mc, config=config)

@bp.route('/config', methods=('GET', 'POST'))
@manage_cookie_policy
def config():
    if request.method == 'POST':
        print("Form Data: {}".format(request.form))
        write_config(request.form)
        return redirect('/')   
    mc = set_menu("config")
    return render_template('home/config.html', mc=mc)

@bp.route('/random')
@manage_cookie_policy
def new_random():
    create_random_image()
    flash("newImageMsg")
    return redirect('/')

"""
@bp.route('/clear')
@manage_cookie_policy
def clear_screen():
    #service.resetScreen()
    os.system("python screen_handler.py reset")
    flash("cleanScreenMsg")
    return redirect('/')
"""

@bp.route('/privacy-notice',methods=('GET', 'POST'))
def privacy():
    mc = set_menu("")
    return render_template('home/privacy-notice.html', mc=mc)

@bp.route('/terms-of-service',methods=('GET', 'POST'))
def termsofservice():
    mc = set_menu("")
    return render_template('home/terms-of-service.html', mc=mc)

#MANAGE sitemap and robots calls 
#These files are usually in root, but for Flask projects must
#be in the static folder
@bp.route('/robots.txt')
@bp.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])

