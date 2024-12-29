import os, sys

from flask import Flask
from .jinjafilters import *
from .errorhandlers import *
from dotenv import load_dotenv
from logging_config import logger

def loadEnv():
    print(f"PWD is {os.getcwd()}")
    load_dotenv()
    sys.path.append('..')
    
    logger.info(f"PAPERPIROOT: {os.environ['PAPERPIROOT']}")
    logger.info(f"PAPERPIAPP: {os.environ['PAPERPIAPP']}")
    logger.info(f"PAPERPICONFIG: {os.environ['PAPERPICONFIG']}")
    logger.info(f"PAPERPIPICS: {os.environ['PAPERPIPICS']}")
        
    #for x in os.environ.keys():
    #    logger.info(f"{x}:{os.environ[x]}")
    '''if os.path.exists("../randomImage.py"):
        print("Appending")
        sys.path.append(os.path.dirname(os.path.realpath("../randomImage.py")))
    '''
    
    
def create_app():
    logger.info("Creating WebApp for PaperPi...")
    loadEnv()    
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ['SESSION_SECRET'],
    )    
    from . import bl_home
    app.register_blueprint(bl_home.bp)
    
    from . import bl_upload
    app.register_blueprint(bl_upload.bp)
    
    from . import bl_log
    app.register_blueprint(bl_log.bp)

    #Add other blueprints if needed
    from . import auth
    app.register_blueprint(auth.bp)

    #ADDS HANDLER FOR ERRORs
    app.register_error_handler(500, error_500)
    app.register_error_handler(404, error_404)

    #JINJA FILTERS
    app.jinja_env.filters['slugify'] = slugify
    app.jinja_env.filters['displayError'] = displayError 
    app.jinja_env.filters['displayMessage'] = displayMessage

    return app