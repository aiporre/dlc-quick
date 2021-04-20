import argparse
from transfersrc import transfervideo

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--path', metavar='path', type=str, default='analyzed_videos',
                    help='video path to video to analyze or directory containing .avi videos (default analyzed_videos)')
parser.add_argument('--ip', metavar='ip', type=str, default='127.0.0.1',
                    help='ip of remote ssh server')
parser.add_argument('--user', metavar='user', type=str, default='ariel',
                    help='user in the PPA of remote endpoint')
parser.add_argument('--send', metavar='send', type=str, default='y',
                    help='send data or receive data? y=send or n=receive (default)')
args = parser.parse_args()

transfervideo(args)
