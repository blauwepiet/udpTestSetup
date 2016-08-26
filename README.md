# UDP frame fragment repeater test setup

These 2 python are the UDP frame fragment streaming setup. The frames are the same size as the kinect depth images so this setup should represent the same network usage/bandwidth as the eventual unreal engine - kinect setup.

##udpRepeater.py
This is the server script which receives, processes and returns the frame fragments over UDP. For now the only thing it does is at random numbers to the fragment data.

##udpSender.py
This is the client side script which sends frame fragments over UDP to the server and then receives the processed fragments back. It keeps track of the frame times and the number of fragments lost in the process.

##Package information
The UDP packages (frame fragments) are 4096 bytes long and are configured as follows: (double)frame time + (int)frame fragment id + (uint16[]) frame fragment content.

##Dependencies
The only dependency it has is Numpy.

##Usage 
First start the server side for listening to client side packages:
python udpRepeater.py -ip {HOST} -p {PORT} (where HOST is the host name or IP of the server)

Then start the client side for sending UDP package to the server:
python udpSender.py -ip {HOST} -p {PORT} (where HOST is the host name or IP of the server)

