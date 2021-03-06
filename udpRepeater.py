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

class MyUDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0]

        frame_time = struct.unpack('f',data[:4])
        idx = struct.unpack('i',data[4:8])
        if idx[0] == 0: 
			print 'Server received frame {}, idx {}, package size {}'.format(frame_time, idx, np.frombuffer(data[header_size:header_size+16], np.dtype(np.uint8)))

        socket = self.request[1]
        image = np.negative(np.frombuffer(data[header_size:header_size+content_size], np.dtype(np.uint8)))
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
