from flask import (
    Blueprint, render_template, request, send_from_directory, flash
)
from .layoutUtils import *
from .auth import *
from datetime import datetime
import json, os
import randomImage

CONFIG_FILE = 'webApp/config/config.json'
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
    art = randomImage.RandomImage()
    seed = int(datetime.now().timestamp())
    art.myRandom = art.MyRandom(seed, art.numColors)
    art.genImage(art.shape)
    fileName = datetime.now().strftime("%m.%d.%Y-%H.%M.%S")+".bmp"
    print("Pic Dir in Random: {}".format(PICS_DIR))
    art.image.save(os.path.join(PICS_DIR,fileName))
    art.image.save(os.path.join(PICS_DIR, "current.bmp"))
    print("\nCreated: {} and copied it as {} \n".format(fileName, "current.bmp"))

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
    print("Flashing")
    flash("Msg1")
    return redirect('/')

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
