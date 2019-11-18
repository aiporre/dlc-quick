import subprocess
import os
from .utils import find_yaml, parser_yaml
from getpass import getpass





def transfervideo(args):
    '''
    copy video or video path between two computers via ssh
    args.path:path to video or videos
    args.user:user of the remote pc
    args.ip:ip of the remote pc
    :param args:
    :return:
    '''
    videopath = args.path
    assert os.path.exists(videopath), videopath+" doesn't exists."

    # password = getpass()
    if os.path.isfile(videopath):
        if args.send == 'y':
            subprocess.run(["scp", videopath, "{}@{}:dlc-projects/analyzed_videos/".format(args.user, args.ip)])
        else:
            subprocess.run(
                ["scp", "{}@{}:dlc-projects/analyzed_videos/{}".format(args.user, args.ip, videopath), 'imported/'+videopath])
    elif os.path.isdir(videopath):
        if args.send == 'y':
            subprocess.run(["scp", "-r", videopath, "{}@{}:dlc-projects/analyzed_videos/".format(args.user, args.ip)])
        else:
            subprocess.run(
                ["scp", "-r", "{}@{}:dlc-projects/analyzed_videos/{}".format(args.user, args.ip, videopath), 'imported/'+videopath])


def transferprojects(args):
    '''
    copy projects between two computers via ssh
    args.task:name of the project in the remote pc
    args.path:path to video or videos
    args.user:user of the remote pc
    args.ip:ip of the remote pc
    :param args:
    :return:
    '''
    projectpath = args.path
    assert os.path.exists(projectpath), projectpath+" doesn't exists."
    assert os.path.isdir(projectpath), projectpath+" is not a directory"
    # password = getpass()
    if args.send == 'y':
        subprocess.run(["scp","-r", projectpath, "{}@{}:dlc-projects/".format(args.user, args.ip)])
    else:
        subprocess.run(
            ["scp", "-r", "{}@{}:dlc-projects/{}".format(args.user, args.ip, args.task), 'imported/'+args.task])

def convertconfig(args):
    '''
    Rewrites the config.yaml of a project according to the location project supports local and remote pc
    args.task:name of the project in the remote pc
    args.projectpath:path of the project in the local pc
    args.send:flag to select changes in local=n or remote=y
    args.user:user of the remote pc
    args.ip:ip of the remote pc
    '''
    projectpath = args.path
    if args.send == 'n':
        config_path = find_yaml(wd=projectpath)
        print('Importing dlc:')
        import deeplabcut as d
        print('done')
        config = parser_yaml(config_path)
        config['project_path'] = projectpath
        d.auxiliaryfunctions.write_config(config_path, config)
    else:
        task = os.path.basename(projectpath)
        command = "'conda activate dlc-windowsGPU | python dlc-projects/quick-dlc/transfersrc/convertconfig.py " \
                  "--path dlc-projects/{}'".format(task)
        print(command)
        subprocess.run(
            ["ssh", "-t", "{}@{}".format(args.user, args.ip), command])

