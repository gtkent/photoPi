from flask import (
    Blueprint, render_template, url_for, request, flash, current_app, send_file
)
from werkzeug.utils import secure_filename
from .layoutUtils import *
from .auth import *
import os, zipfile, psutil

ALLOWED_EXTENSIONS = {'.zip', '.7z', '.png', '.jpg', '.jpeg', '.gif', '.bmp'}
PICS_DIR = os.path.join(os.getcwd(), 'webApp/static/pics')
PICS_DIR = os.getenv("PAPERPIPICS", PICS_DIR)

def handleNewFiles(newFiles):
    for file in newFiles:
        filename = secure_filename(file.filename)
        filePath = os.path.join(PICS_DIR, filename)
        root, extension = os.path.splitext(filename.lower())
        if extension in ALLOWED_EXTENSIONS:
            if extension == '.zip' or extension == '.7z':
                file.save(filePath)
                with zipfile.ZipFile(filePath, 'r') as zip_ref:
                    zip_ref.extractall(PICS_DIR)
                os.remove(filePath)
            else:
                file.save(filePath)
                print("Saving: {}".format(filePath))
        else:
            flash("wrongImage")

def get_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def calcDiskUsage():
    sd_card_mount_point = ""
    partitions = psutil.disk_partitions()

    # Find SD card mount point
    for partition in partitions:
        if partition.mountpoint.startswith('/mnt/'):
            sd_card_mount_point = partition.mountpoint
            break
    
    if sd_card_mount_point:
        disk_usage = psutil.disk_usage(sd_card_mount_point)
        return disk_usage.percent
    
    return False

bp = Blueprint('bl_upload', __name__, url_prefix='/upload')

@bp.route('/',methods=['GET'])
@manage_cookie_policy
def upload():
    print("Set PICS_DIR to: {}".format(PICS_DIR))
    context = {
        "mc" : set_menu("upload"),
        "files" : [],
        "numFiles" : 0,
        "diskUsage" : 0,
    }
    context['files'] = get_files(PICS_DIR)
    context['numFiles'] = len(context['files'])
    context["diskUsage"] = calcDiskUsage()
    return render_template('home/upload.html', **context)

@bp.route('/',methods=['POST'])
@manage_cookie_policy
def upload_files():
    if 'file' in request.files:
        handleNewFiles(request.files.getlist('file'))
    return redirect(request.url)

@bp.route('/delete')
@manage_cookie_policy
def delete_files():
    for file in os.listdir(PICS_DIR):
        if file != 'current.bmp':
            os.remove(os.path.join(PICS_DIR, file))
    return redirect('/upload')

@bp.route('/download')
@manage_cookie_policy
def download_files():
    zipFile = os.path.join(PICS_DIR, "pictures.zip")
    files = os.listdir(PICS_DIR)
    with zipfile.ZipFile(zipFile, 'a') as zip_obj:
        for file in files:
            print("Adding file: {}".format(file))
            zip_obj.write(os.path.join(PICS_DIR, file), file)
    zip_obj.close()
    
    try:
        print(zipFile)
        print(os.path.join(PICS_DIR, zipFile))
        return send_file(zipFile, as_attachment=True)
    except Exception as e:
        return str(e)
    
    