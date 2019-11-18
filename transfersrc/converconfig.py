import argparse, os
from getpass import getpass

from transfersrc import transfervideo, convertconfig
from transfersrc.transfer import transferprojects

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--path', metavar='path', type=str, default='analyzed_videos',
                    help='path to project transfer')
parser.add_argument('--ip', metavar='ip', type=str, default='127.0.0.1',
                    help='ip of remote ssh server')
parser.add_argument('--user', metavar='user', type=str, default='ariel',
                    help='user in the PPA of remote endpoint')
parser.add_argument('--task', metavar='task', type=str, default='ContrastBB-Ariel-2019-10-10',
                    help='task in the remote server.')
parser.add_argument('--send', metavar='send', type=str, default='y',
                    help='send data or receive data? y=send or n=receive (default)')


# parse args
args = parser.parse_args()
convertconfig(args)