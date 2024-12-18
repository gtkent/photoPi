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

#Download the Waveshare repo also at wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
git clone -n --depth=1 --filter=tree:0 https://github.com/waveshare/e-Paper.git libs
#cd e-Paper/RaspberryPi_JetsonNano/

#Run the demo
# Make sure it's in e-Paper/RaspberryPi_JetsonNano/
#cd python/examples/
#python3 epd_7in3f_test.py
