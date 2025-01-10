# photoPi

## Overview
This aim of this project is to build a Digital Picture Frame using a Raspberry Pi Zero and a color e-ink display. A Flask Based Web Application can be used to config the device and upload photos. Additionally, a Random Abstract Photo generation script utilizing the Python Pillow Library is provided. The project is meant to run on statup as a Linux Service
____
## Display
The specific display supported in this project is the [Waveshare 7.3 e-Paper F](https://www.waveshare.com/wiki/7.3inch_e-Paper_HAT_(F)_Manual#Overview)
The vendor library for this display is retrieved from the manufacturer github and placed in a libs directory in the root of the project by the _install.sh_ script
This library is utilized in _screen_handler.py_ to interface with the display. (Modifications to this handler would be need to support a different screen)
____
## Installation

To begin with it is assumed a Raspberry Pi OS Lite image is installed and configured to connect to your Wifi and allow SSH logon (there are numerous tutorials to help with this). To date only a Pi Zero W running the 32bit bookworm build has been used and tested.

1. Connect to the Zero via SSH
2. If you have a fresh install of the OS you will need to install and configure git to download and install this project
   ```
   $ sudo apt update
   $ sudo apt install git
   $ git config --global user.name "Your Name"
   $ git config --global user.email "youremail@yourdomain.com"
   ```
4. From the Directory you wish the project to live in run:
   ```
   $  git clone https://github.com/gtkent/photoPi.git
   ```
6. CD into the photoPi directory and run:
   ```
   $ cd photoPi
   $ ./install.sh
   ```
8. setup service.....
____
## Major Components
```
├── install.sh:
      Installation script that install needed dependencies and libraries

├── logging_config.py -

├── main.py - Test Main to run local flask webserver for testing

├── paperPi.service:
      systemd style service file to be placed in _/etc/systemd/system/_ to run this project as a service 

├── paperPi.sh:
      Bash script called by systemd service to start and stop _service.py_ the core of this project

├── randomImage.py:
      Python script that can be utilized to generate random abstract images using python Pillow image library

├── requirements.txt:
      A file of listed software requirements to be installed by PIP in _install.sh_

├── screen_handler.py:
      A screen handler class that provide the interface functionality between the screen driver and the application

├── service.py:
      The core service file for this application that starts the WebApp as a Gunicorn app, Monitors the Configuration file, and updates the displayed photo when time to do so

└── webApp:
      Directory containing the Python Flask WebApp to manage the PhotoPi
          ...
          ├── config
          │   └── config.json- Configuration File with settings for the PhotoPi
          ...
          ├── static
          │   ...
          │   ├── pics (directory containing photos that can be displayed)
          │   │   └── current.bmp - Current Photo being displayed 
```
## Configuration File
The configuration file for PhotoPi is named _**config.json**_ and is located under the _webApp/config_ directory.
In general the config allows you to choose to display an image Daily, Weekly, or in a user defined number of hours using either a randomly generated image or a random uploaded photo. Additionally, to immprove the life of the screen it can be refreshed on a Daily, Weekly or user defined nummber of hours. The schema below outlines the expected format. Note that the _lowPower_ and _offline_ fields are currently not immplemented.

```
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Schema for PaperPi",
  "type": "object",
  "properties": {
    "source": {
      "enum": ["Generate Random Image", "Use Uploaded Pictures"]
    },
    "changeFreq": {
      "enum": ["Daily", "Weekly", <USER_SUPPLIED_NUMBER>]
    },
    "screenRefreshFreq": {
      "enum": ["Daily", "Weekly", <USER_SUPPLIED_NUMBER>]
    },
    "lowPower": {
      "type": "boolean"
    },
    "offline": {
      "type": "boolean"
    }
  },
  "required": [
    "source",
    "changeFreq",
    "screenRefreshFreq",
    "lowPower",
    "offline"
  ]
}
```

## PhotoPi Web Application

### Home Page
Shows the current configuration the PhotoPi is running under. Provides a link to the configuration tab and a button to generate a random new picture and name it _current.bmp_

![PhotoPi-Homepage](https://github.com/user-attachments/assets/67a2e7df-4d85-49d3-b9e7-db08423da9af)

### Configuration Page
The configuration page allows the user to choose the source of the next photo (random generated art or random photo in pics directory), when they want the display to change photos, and how often to refresh the screen.
Currently the Low Power option is non-functional

![PhotoPi-ConfigurationPage](https://github.com/user-attachments/assets/d14e7c67-5e61-4ece-ab96-59fe27b0e85e)

### Upload and Download Page
This page provides an overview of the **_pics_** directory. The photos are listed and can be deleted or downloaded as Zip. Additionally, the user can upload new photos to be displayed.
To upload photos click **Choose Files** aand select valid photos or a 7z or Zip archive of photos, and then click **Upload Files**

![PhotoPi-UploadDownloadPage](https://github.com/user-attachments/assets/f1d2c7b7-d5f4-4aae-bf55-99f3c9405c40)

### Log Page
This page allows the user to click _**Display Logs**_ to view the PhotoPi's logfile. The _**Clear Log**_ button will erase the logfile

![PhotoPi-LogPage](https://github.com/user-attachments/assets/c3ee3952-f1de-4975-9c8a-68505939c554)
