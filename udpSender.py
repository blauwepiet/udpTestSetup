import socket
import sys
import numpy as np
import time
import threading
import struct
import argparse
import math
from matplotlib import pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Simple UDP frame sender. Repeatedly ends and image the same size as the depth image of a kinect (512x424) in fra
                                                    The package configuration is as follows: (double)frame time + (int)frame fragment id + (uint16[]) frame fragment content.""")
    parser.add_argument("-ip", "--host", help="Either the host name or ip of the server", required=True)
    parser.add_argument("-p", "--port", help="The port of the server", required=True, type=int)
    args = parser.parse_args()

    image_size = (512,424,3)

    HOST, PORT = socket.gethostbyname(args.host), args.port
    image = np.ones(image_size, np.dtype(np.uint16))
    display_image = np.zeros(image_size, np.dtype(np.uint16))+128
    data = image.data[:image.nbytes]

    # SOCK_DGRAM is the socket type to use for UDP sockets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    packet_size = 4096
    header_size = 8 + 4 + 4 # double for time frame integer for location and integer for padding (then 3x2 bytes per pixel is whole)
    content_size = packet_size - header_size

    print "Start sending to {} port {}".format(HOST, PORT)

    def sendData():
        while True:
            frame_time = time.time()
            header_frame_time = struct.pack('d',frame_time)
            for idx, a in enumerate([data[i:i + content_size] for i in xrange(0, len(data), content_size)]):  
                time.sleep(0.0001) # crude way to prevent congestion
                message = header_frame_time + struct.pack('i', idx) + a
                sock.sendto(message, (HOST,PORT))

    t1 = threading.Thread(target=sendData)
    t1.daemon = True
    t1.start()

    counter = 0

    startt = time.time()

    current_frame_time = 0
    prev_frame_time = 0

    fragment_count = 0

    number_of_fragments = math.ceil(len(data)/content_size)+1

    plt.ion()
    imgplotter = plt.imshow(display_image, interpolation='nearest')

    while True:
        received = sock.recv(packet_size)
        current_frame_time = struct.unpack('d',received[:8])[0]
        idx = struct.unpack('i',received[8:16])[0]
        write_offset = idx*content_size
        display_image.data[write_offset:write_offset + content_size] = received[16:packet_size]


        #print "Got fragment {} from frame {}".format(idx, current_frame_time)

        fragment_count += 1

        if current_frame_time != prev_frame_time:
            print "Got full frame in {} seconds and lost {} fragment".format(time.time()-startt, number_of_fragments-fragment_count)
            fragment_count = 0
            imgplotter.set_data(display_image)
            startt = time.time()

        prev_frame_time = current_frame_time




