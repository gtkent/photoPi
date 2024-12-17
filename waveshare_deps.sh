#Install the function library
sudo apt-get update
sudo apt-get -y install python3-pip python3-pil python3-numpy python3-spidev

# Install function library (python2)
#sudo apt-get update
#sudo apt-get install python-pip python-pil python-numpy
#sudo pip install spidev

#Install gpiozero library (it is installed in the system by default, if not, you can install it by following the commands below)
sudo apt-get update
# python3
sudo apt -y install python3-gpiozero
# python2
#sudo apt install python-gpiozero


#Install git
sudo apt-get -y install git git-lfs

#Download the demo via GitHub (You can skip this step if you have downloaded it.)
git clone https://github.com/waveshare/e-Paper.git
#cd e-Paper/RaspberryPi_JetsonNano/

#Download the demo from web (You can skip this step if you have downloaded it.)
#wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
#unzip E-Paper_code.zip -d e-Paper
#cd e-Paper/RaspberryPi_JetsonNano/

#Run the demo
# Make sure it's in e-Paper/RaspberryPi_JetsonNano/
#cd python/examples/
#python3 epd_7in3f_test.py
