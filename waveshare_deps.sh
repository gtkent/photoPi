#Install dependencies
sudo apt-get update
sudo apt-get -y install python3-pip python3-pil python3-numpy python3-spidev python3-gpiozero git git-lfs
mkdir libs pics

#Download the Waveshare Libraries 
# Also https://files.waveshare.com/upload/7/71/E-Paper_code.zip
git clone -n --depth=1 --filter=tree:0 https://github.com/waveshare/e-Paper.git libs
cd libs
git sparse-checkout set --no-cone /RaspberryPi_JetsonNano/python/lib/waveshare_epd
git checkout