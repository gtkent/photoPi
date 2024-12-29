import flask, base64 
from time import sleep
from werkzeug.utils import secure_filename
from .layoutUtils import *
from .auth import *
import os, zipfile, psutil

LOG_FILE = '/var/log/paperPi.log'

bp = Blueprint('bl_log', __name__, url_prefix='/log')

@bp.route('/clearLogs')
@manage_cookie_policy
def clear_logs():
    if os.path.exists(LOG_FILE):
        f = open(LOG_FILE, 'r+')
        f.truncate(0)
    return redirect('/log')

@bp.route('/displayLogs')
@manage_cookie_policy
def display_Logs():
    def update():
        yield 'data: Prepare for log\n\n'
        with open(LOG_FILE) as f:
            data = f.read().encode("utf-8")
            yield f"data: {base64.urlsafe_b64encode(data).decode('utf-8')}\n\n"
        sleep(1)
        yield 'data: close\n\n'    
    return flask.Response(update(), mimetype='text/event-stream')

@bp.route('/',methods=['GET', 'POST'])
@manage_cookie_policy
def log():
    mc = set_menu("log")
    display_logs = False

    if flask.request.method == 'POST':
        if 'display_logs' in list(flask.request.form):
            display_logs = True

    return flask.render_template('home/log.html', mc=mc, display_logs=display_logs)
    
    