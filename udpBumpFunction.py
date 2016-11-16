import SocketServer
import numpy as np
import time
import random
import struct
import argparse
import socket

packet_size = 8192 
header_size = 4 + 4  # double for time frame integer for location + padding
content_size = packet_size - header_size

image_size = (180, 512,424,4)
sinImage = np.zeros(image_size)
amplitude = 10
numberOfPeriods = 3

for t in range(len(sinImage)):
    for x in range(len(sinImage[t])):
        for y in range(len(sinImage[t][x])):
            sinImage[t][x][y] = np.abs(((np.sin((x/512.0)*2.0*np.pi*numberOfPeriods+(t*np.pi/180.0))*amplitude))) + abs(((np.sin((y/424.0)*2.0*np.pi*(424.0/512.0)*numberOfPeriods+(t*np.pi/180.0))*(424.0/512.0)*amplitude)))

print "prepped the bump image"

sinImage.shape = (len(sinImage), sinImage[0].size)
sinImageSize = len(sinImage[0])
sinImage = sinImage.astype(np.uint8)

class MyUDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0]

        frame_time = struct.unpack('f',data[:4])
        idx = struct.unpack('i',data[4:8])
        if idx[0] == 0: 
			print 'Server received frame {}, idx {}, package size {}'.format(frame_time, idx, np.frombuffer(data[header_size:header_size+16], np.dtype(np.uint8)))

        socket = self.request[1]
        sinImageOffset = idx[0]*content_size
	
	if (sinImageOffset + content_size)>sinImageSize:
		residue = sinImageSize - sinImageOffset
		image = np.frombuffer(data[header_size:header_size+residue], np.dtype(np.uint8)) + sinImage[(int)((frame_time%1)*180)][sinImageOffset:sinImageOffset + residue]	
	else:	
	        image = np.frombuffer(data[header_size:header_size+content_size], np.dtype(np.uint8)) + sinImage[(int)((frame_time%1)*180)][sinImageOffset:sinImageOffset + content_size]
        socket.sendto(data[0:header_size] + image.data[:image.nbytes], self.client_address)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Simple frame fragment editor server that receives udp packages, edits the content and sends it back to the client. 
                                                    The package configuration is as follows: (double)frame time + (int)frame fragment id + (uint16[]) frame fragment content.""")
    parser.add_argument("-ip", "--host", help="Either the host name or ip of the server", required=True)
    parser.add_argument("-p", "--port", help="The port of this server", required=True, type=int)
    args = parser.parse_args()

    HOST = socket.gethostbyname(args.host)
    server = SocketServer.UDPServer((HOST, args.port), MyUDPHandler)
    server.serve_forever()
