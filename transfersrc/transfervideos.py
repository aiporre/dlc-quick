import subprocess
import argparse
import os
from getpass import getpass

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--video', metavar='video', type=str, default='analyzed_videos',
                    help='video path to video to analyze or directory containing .avi videos (default analyzed_videos)')
parser.add_argument('--ip', metavar='ip', type=str, default='127.0.0.1',
                    help='ip of remote ssh server')
parser.add_argument('--user', metavar='user', type=str, default='ariel',
                    help='user in the PPA of remote endpoint')

args = parser.parse_args()
videopath = args.video
assert os.path.exists(videopath), videopath + " doesn't exists."


password = getpass()
if os.path.isfile(videopath):
    subprocess.run(["scp", videopath,"{}@{}:analyzed_videos/".format(args.user,args.ip)])
elif os.path.isdir(videopath):
    subprocess.run(["scp", "-r", videopath,"{}@{}:analyzed_videos/".format(args.user,args.ip)])
