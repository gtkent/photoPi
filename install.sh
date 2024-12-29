#!/bin/bash
#Install dependencies
sudo apt-get update
sudo apt-get -y install python3-pip git
mkdir libs

#Download the Waveshare Libraries 
# Also https://files.waveshare.com/upload/7/71/E-Paper_code.zip
git clone -n --depth=1 --filter=tree:0 https://github.com/waveshare/e-Paper.git libs
cd libs
git sparse-checkout set --no-cone /RaspberryPi_JetsonNano/python/lib/waveshare_epd
git checkout
cd ..
#python3 -m venv venv
#source venv/bin/activate
pip3 install --break-system-packages -r requirements.txt
sudo touch /var/log/paperPi.log
sudo chmod a+rw /var/log/paperPi.log
#sudo cp paperPi.service /etc/systemd/system/
#sudo systemctl daemon-reload
