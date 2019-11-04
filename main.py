import wx
import wx.grid
from blockwindow import BlockWindow
import os
import yaml
from wx.lib.masked.numctrl import NumCtrl
import sys

# import deeplabcut as d
def get_videos(videosList):
    count = videosList.GetItemCount()
    videos = []
    for row in range(count):
        item = videosList.GetItem(itemIdx=row, col=1)
        videos.append(item.GetText())
    return videos

def find_yaml():
    '''
    Find the most likely yaml config file in the current directory
    :return:
    '''
    config_yamls = []
    yamls = []
    cwd = os.getcwd()
    for dirpath, dnames, fnames in os.walk(cwd):
        for f in fnames:
            if f.endswith("config.yaml"):
                config_yamls.append(os.path.join(dirpath, f))
            elif f.endswith(".yaml"):
                yamls.append(os.path.join(dirpath, f))
    print('Yaml options found:', yamls, ' or configs: ', config_yamls)
    config_yaml = ''
    if not len(config_yamls)==0:
        config_yaml = config_yamls[-1]
    elif len(config_yamls) == 0 and not len(yamls) == 0:
        config_yaml = yamls[-1]
    else:
        print('no config yaml found using empty string')
        config_yaml = ''
    print('using : ', config_yaml)
    return config_yaml

def parser_yaml(filepath):
    with open(filepath, 'r') as stream:
        try:
            print('Reading yaml file: ', filepath )
            content = yaml.safe_load(stream)
            print(type(content),'--', content)
            return content
        except yaml.YAMLError as exc:
            print(exc)

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def get_available_gpus():
    from tensorflow.python.client import device_lib
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']

def get_radiobutton_status(radiobuttons):
    status = {}
    for k in radiobuttons.keys():
        status[k]=radiobuttons[k].GetValue()

    if status['All']:
        return 'all'
    else:
        return [k for k, v in status.items() if v and not k=='All']

class CreateTrainingSet(wx.Frame):
    def __init__(self,parent,title='Create training set', config=None):
        super(ExtractFrames, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Create training set")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # input test to set the working directory
        configPathLbl = wx.StaticText(self.panel, -1, "Config path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        cwd = find_yaml()
        configPath = wx.FilePickerCtrl(self.panel, -1, cwd, wildcard='*.yaml')

        # check box to select automatic or manual selection
        modeLbl = wx.StaticText(self.panel, -1, "Automatic/Manual:")
        mode = wx.CheckBox(self.panel, -1, "");
        mode.SetValue(True)

        # check box to mode of frames extraction (uniform or kmeans)
        selectionAlgoLbl = wx.StaticText(self.panel, -1, "Uniform/Manual:")
        selectionAlgo = wx.CheckBox(self.panel, -1, "");
        selectionAlgo.SetValue(True)

        # button to remove video
        # button to create project
        buttonExtract = wx.Button(self.panel, label="Extract")
        # btn.Bind(wx.EVT_BUTTON, self.add_line)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)



        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(configPathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(configPath, 0, wx.EXPAND, 2)
        inputSizer.Add(modeLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(mode, 0, wx.EXPAND, 2)
        inputSizer.Add(selectionAlgoLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(selectionAlgo, 0, wx.EXPAND, 2)
        inputSizer.Add(buttonExtract)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        # contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

class ExtractFrames(wx.Frame):
    def __init__(self,parent,title='Extract frames',config=None):
        super(ExtractFrames, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Extract frames")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # input test to set the working directory
        # configPathLbl = wx.StaticText(self.panel, -1, "Config path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # cwd = find_yaml()
        # self.configPath = wx.FilePickerCtrl(self.panel, -1, cwd, wildcard='*.yaml')

        # # check box for user selection
        # userFeedbackLbl = wx.StaticText(self.panel, -1, "User feedback:")
        # self.userFeedback = wx.CheckBox(self.panel, -1, "");
        # self.userFeedback.SetValue(True)

        # check box to select cropping or not
        croppingLbl = wx.StaticText(self.panel, -1, "Use cropping:")
        self.cropping = wx.CheckBox(self.panel, -1, "");
        self.cropping.SetValue(False)

        # check box to select automatic or manual selection
        modeLbl = wx.StaticText(self.panel, -1, "Extraction mode:")
        self.mode = wx.Choice(self.panel, id=-1, choices=['automatic', 'manual'])


        # check box to mode of frames extraction (uniform or kmeans)
        selectionAlgoLbl = wx.StaticText(self.panel, -1, "Extraction algorithm:")
        self.selectionAlgo = wx.Choice(self.panel, id=-1, choices=['uniform', 'kmeans'])



        # button to create project
        buttonExtract = wx.Button(self.panel, label="Extract")
        buttonExtract.Bind(wx.EVT_BUTTON, self.onExtractButton)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)



        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        # inputSizer.Add(configPathLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(configPath, 0, wx.EXPAND, 2)
        # inputSizer.Add(userFeedbackLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.userFeedback, 0, wx.EXPAND, 2)
        inputSizer.Add(croppingLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.cropping, 0, wx.EXPAND, 2)
        inputSizer.Add(modeLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.mode, 0, wx.EXPAND, 2)
        inputSizer.Add(selectionAlgoLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.selectionAlgo, 0, wx.EXPAND, 2)


        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        # contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonExtract, 0 , wx.CENTER | wx.ALL, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)
    def onExtractButton(self, event):
        print('Extraction of the frames....')
        print('import dlc. '); import deeplabcut as d
        mode = self.mode.GetString(self.mode.GetCurrentSelection())
        algo = self.selectionAlgo.GetString(self.selectionAlgo.GetCurrentSelection())

        d.extract_frames(self.config, mode=mode, algo=algo, crop=self.cropping.GetValue(), userfeedback=False)
        print('Extraction...')
        self.Close()

class CreateTraining(wx.Frame):
    def __init__(self,parent,title='Create training set',config=None):
        super(CreateTraining, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Create training set")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # spin control to select the number of suffles
        nShuffleLbl = wx.StaticText(self.panel, -1, "Number of shuffles (number of sets):")
        self.nShuffle = wx.SpinCtrl(self.panel, id=-1, min=1, max=1000, initial=1)

        # button to create dataset or datasets
        buttonCreate = wx.Button(self.panel, label="Create")
        buttonCreate.Bind(wx.EVT_BUTTON, self.onCreateDataset)
        # btn.Bind(wx.EVT_BUTTON, self.add_line)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(nShuffleLbl, 0, wx.EXPAND|wx.ALL, 10)
        inputSizer.Add(self.nShuffle, 0, wx.CENTER, 2)
        inputSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        inputSizer.Add(buttonCreate, 0, wx.CENTER, 2)


        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onCreateDataset(self, event):
        import deeplabcut as d
        d.create_training_dataset(self.config, num_shuffles = self.nShuffle.GetValue())
        self.Close()

class AddNewVideos(wx.Frame):
    def __init__(self,parent,title='Add new videos',config=None):
        super(AddNewVideos, self).__init__(parent, title=title, size=(640, 500))
        self.addNewVideosFrame = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.addNewVideosFrame, -1, "Add New Videos")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # input test to set the working directory
        videosPathLbl = wx.StaticText(self.addNewVideosFrame, -1, "Path to videos:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # TODO: make default path find yaml in the current directory
        self.videosPath = wx.DirPickerCtrl(self.addNewVideosFrame,-1)

        # check box to select copy videos
        copyVideosLbl = wx.StaticText(self.addNewVideosFrame, -1, "Copy videos:")
        self.copyVideos = wx.CheckBox(self.addNewVideosFrame, -1, "");
        self.copyVideos.SetValue(True)

        listOrPathLbl = wx.StaticText(self.addNewVideosFrame, -1, "Use list or path?")
        self.listOrPath = wx.Choice(self.addNewVideosFrame, id=-1, choices=['target videos path', 'target videos list'])

        # list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.addNewVideosFrame, -1, "Videos:")
        self.videosList = wx.ListCtrl(self.addNewVideosFrame, -1, style=wx.LC_REPORT )
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # buttons to add video
        bmp1 = wx.Image("figures/iconplus.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.addNewVideosFrame, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image("figures/iconMinus.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonMinus = wx.BitmapButton(self.addNewVideosFrame, -1, bmp2, pos=(10, 20))
        self.buttonMinus.Bind(wx.EVT_BUTTON, self.onRemoveVideo)

        # button to create project
        buttonCreate = wx.Button(self.addNewVideosFrame, label="Add")
        buttonCreate.Bind(wx.EVT_BUTTON, self.onAddVideos)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.addNewVideosFrame), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)



        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(videosPathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosPath, 0, wx.EXPAND, 2)
        inputSizer.Add(videosListLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosList, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(copyVideosLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.copyVideos, 0, wx.EXPAND, 2)
        buttonSizer.Add(listOrPathLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.listOrPath, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.buttonPlus, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.buttonMinus, 0, wx.EXPAND, 2)
        buttonSizer.Add(buttonCreate, 0, wx.EXPAND, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.addNewVideosFrame.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onAddVideos(self,event):
        print('Adding new videos ...')
        import deeplabcut as d
        listOrPath = self.listOrPath.GetString(self.listOrPath.GetCurrentSelection())
        if listOrPath == 'target videos path':
            video_path = self.videosPath.GetPath()
            print('video path: ', video_path)
            videos = [os.path.join(video_path,v) for v in os.listdir(video_path) if v.endswith('.avi')]
            d.add_new_videos(self.config, videos=videos,copy_videos=self.copyVideos.GetValue())
        elif listOrPath  == 'target videos list':
            videos = get_videos(self.videosList)
            d.add_new_videos(self.config, videos=videos, copy_videos=self.copyVideos.GetValue())
        print('Done')
        self.Close()

    def onAddVideo(self,event):
        dialog = wx.FileDialog(None, "Choose input directory", "",
                           style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST) # wx.FD_FILE_MUST_EXIST
        if dialog.ShowModal() == wx.ID_OK:
            pathToFile = dialog.GetPath()
            print('Path to file: ', pathToFile)

        else:
            return
        dialog.Destroy()
        line = os.path.basename(pathToFile)

        self.videosList.InsertItem(self.listIndex, line)
        self.videosList.SetItem(self.listIndex, 1, pathToFile)
        self.listIndex += 1
    def onRemoveVideo(self,event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.videosList.GetFirstSelected(self)
        if item_id==-1:
            item_id = self.listIndex-1

        print("removing entry : ", item_id)
        self.videosList.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex-1

class NewProjectFrame(wx.Frame):
    def __init__(self,parent,title='New project',config=None):
        super(NewProjectFrame, self).__init__(parent, title=title, size=(640, 500))
        self.newProjectFrame = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.newProjectFrame, -1, "Create a new project")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # input text to put the name of the project
        nameLbl = wx.StaticText(self.newProjectFrame, -1, "Name:")
        self.name = wx.TextCtrl(self.newProjectFrame, -1, "");

        # input text to set experiemnter
        experimenterLbl = wx.StaticText(self.newProjectFrame, -1, "Experimenter:")
        self.experimenter = wx.TextCtrl(self.newProjectFrame, -1, "");

        # input test to set the working directory
        wdirLbl = wx.StaticText(self.newProjectFrame, -1, "Working directory:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # wdir = wx.TextCtrl(self.newProjectFrame, -1, "");
        # TODO: make default directory the current directory
        cwd = os.getcwd()
        self.wdir = wx.DirPickerCtrl(self.newProjectFrame,-1,cwd)

        # check box to select copy videos
        copyVideosLbl = wx.StaticText(self.newProjectFrame, -1, "Copy videos:")
        self.copyVideos = wx.CheckBox(self.newProjectFrame, -1, "");
        self.copyVideos.SetValue(True)

        # list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.newProjectFrame, -1, "Videos:")
        self.videosList = wx.ListCtrl(self.newProjectFrame, -1, style=wx.LC_REPORT )
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # buttons to add video
        bmp1 = wx.Image("figures/iconplus.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.newProjectFrame, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image("figures/iconMinus.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonMinus = wx.BitmapButton(self.newProjectFrame, -1, bmp2, pos=(10, 20))
        self.buttonMinus.Bind(wx.EVT_BUTTON, self.onRemoveVideo)

        # button to create project
        buttonCreate = wx.Button(self.newProjectFrame, label="Create")
        buttonCreate.Bind(wx.EVT_BUTTON, self.create_project)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.newProjectFrame), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)



        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(nameLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.name, 0, wx.EXPAND, 2)
        inputSizer.Add(experimenterLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.experimenter, 0, wx.EXPAND, 2)
        inputSizer.Add(wdirLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.wdir, 0, wx.EXPAND, 2)
        inputSizer.Add(videosListLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosList, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(copyVideosLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.copyVideos, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.buttonPlus, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.buttonMinus, 0, wx.EXPAND, 2)
        buttonSizer.Add(buttonCreate, 0, wx.EXPAND, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.newProjectFrame.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)
    def create_project(self, event):
        name = self.name.GetValue()
        experimenter = self.experimenter.GetValue()
        wdir = self.wdir.GetPath()
        copy_videos = self.copyVideos.GetValue()
        videos = get_videos(self.videosList)

        print('Importing deeplabcut....')
        import deeplabcut as d
        print('Done')

        config_path = d.create_new_project(project=name, experimenter=experimenter, videos=videos, working_directory=wdir, copy_videos=copy_videos)
        print('project create with config.yaml file:', config_path)
        self.Close()

    def onAddVideo(self,event):
        dialog = wx.FileDialog(None, "Choose input directory", "",
                           style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST) # wx.FD_FILE_MUST_EXIST
        if dialog.ShowModal() == wx.ID_OK:
            pathToFile = dialog.GetPath()
            print('Path to file: ', pathToFile)

        else:
            return
        dialog.Destroy()
        line = os.path.basename(pathToFile)

        self.videosList.InsertItem(self.listIndex, line)
        self.videosList.SetItem(self.listIndex, 1, pathToFile)
        self.listIndex += 1
    def onRemoveVideo(self,event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.videosList.GetFirstSelected(self)
        if item_id==-1:
            item_id = self.listIndex-1

        print("removing entry : ", item_id)
        self.videosList.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex-1

class TrainNetwork(wx.Frame):
    def __init__(self,parent,title='Train network',config=None):
        super(TrainNetwork, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Train network")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # choice iteration from configuration file
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        self.iteration = wx.Choice(self.panel, id=-1, choices=self.find_iterations())
        pose_config = self.read_fields()

        # default fields from the pose_cfg.yaml file:
        all_jointsLbl = wx.StaticText(self.panel, -1, "All joints")
        all_joints = BlockWindow(self.panel,-1,label=str(pose_config['all_joints']))

        all_jointsNamesLbl = wx.StaticText(self.panel, -1, "All joints names")
        all_jointsNames = BlockWindow(self.panel,-1,label=str(pose_config['all_joints_names']), size=(7*len(str(pose_config['all_joints_names'])),25))

        bottomheightLbl = wx.StaticText(self.panel, -1, "Bottom height")
        self.bottomheight = wx.TextCtrl(self.panel, -1, str(pose_config['bottomheight']))

        cropLbl = wx.StaticText(self.panel, -1, "Crop")
        self.crop = wx.CheckBox(self.panel, -1, "")
        self.crop.SetValue(pose_config['crop'])

        cropRatioLbl = wx.StaticText(self.panel, -1, "Crop ratio")
        self.cropRatio = wx.SpinCtrlDouble(self.panel, id=-1, min=0, max=1, initial=pose_config['cropratio'],inc=0.1)

        datasetLbl = wx.StaticText(self.panel,-1,"Dataset")
        self.dataset = wx.FilePickerCtrl(self.panel, -1, pose_config['dataset'], wildcard='*.mat')


        datasetTypeLbl = wx.StaticText(self.panel,-1,"Dataset type")
        self.datasetType = wx.TextCtrl(self.panel, -1, pose_config['dataset_type'])

        displayItersLbl = wx.StaticText(self.panel,-1,"Display iters")
        self.displayIters = wx.SpinCtrlDouble(self.panel, id=-1, min=1, max=10000, initial=pose_config['display_iters'],inc=1)

        max_itersLbl = wx.StaticText(self.panel, -1, "Max iters")
        self.max_iters = wx.SpinCtrlDouble(self.panel, id=-1, min=1, max=10000, initial=100,
                                              inc=1)
        # inputSizer.Add(max_itersLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.max_iters, 0, wx.EXPAND, 2)

        globalScaleLbl = wx.StaticText(self.panel, -1, "Global scale")
        self.globalScale = wx.SpinCtrlDouble(self.panel, id=-1, min=0, max=1, initial=pose_config['global_scale'],inc=0.1)

        initWeightsLbl = wx.StaticText(self.panel, -1, "Initial weights")
        self.initWeights = wx.TextCtrl(self.panel, -1, os.path.basename(pose_config['init_weights']))

        intermediateSupervisionLbl = wx.StaticText(self.panel, -1, "Intermediate supervision")
        self.intermediateSupervision = wx.CheckBox(self.panel, -1, "")
        self.intermediateSupervision.SetValue(pose_config['intermediate_supervision'])

        intermediate_supervision_layerLbl = wx.StaticText(self.panel, -1, "intermediate_supervision_layer")
        self.intermediate_supervision_layer = wx.SpinCtrl(self.panel, id=-1, min=0.1, max=1000, initial=pose_config['intermediate_supervision_layer'])


        leftwidthLbl = wx.StaticText(self.panel, -1, "left width")
        self.leftwidth = wx.TextCtrl(self.panel, -1, str(pose_config['leftwidth']))

        location_refinementLbl = wx.StaticText(self.panel, -1, "location_refinement")
        self.location_refinement = wx.CheckBox(self.panel, -1, "")
        self.location_refinement.SetValue(pose_config["location_refinement"])

        locref_huber_lossLbl = wx.StaticText(self.panel, -1, "locref_huber_loss")
        self.locref_huber_loss = wx.CheckBox(self.panel, -1, "")
        self.locref_huber_loss.SetValue(pose_config["locref_huber_loss"])

        locref_loss_weightLbl = wx.StaticText(self.panel, -1, "locref_loss_weight")
        self.locref_loss_weight = wx.SpinCtrlDouble(self.panel, id=-1, min=0.1, max=10000, initial=pose_config['display_iters'],inc=0.1)

        locref_stdevLbl = wx.StaticText(self.panel, -1, "locref_stdev")
        self.locref_stdev = wx.TextCtrl(self.panel, -1, str(pose_config['locref_stdev']))
        self.locref_stdev.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.locref_stdev))


        max_input_sizeLbl = wx.StaticText(self.panel, -1, "max_input_size")
        self.max_input_size = wx.TextCtrl(self.panel, -1, str(pose_config["max_input_size"]))
        self.max_input_size.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.max_input_size))


        metadatasetLbl = wx.StaticText(self.panel, -1, "metadataset")
        self.metadataset = BlockWindow(self.panel,-1,os.path.basename(pose_config['metadataset']),size=(3*len(str(pose_config['metadataset'])),25))

        min_input_sizeLbl = wx.StaticText(self.panel, -1, "min_input_size")
        self.min_input_size = wx.TextCtrl(self.panel,-1,str(pose_config['min_input_size']))
        self.min_input_size.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.min_input_size))

        minsizeLbl = wx.StaticText(self.panel, -1, "minsize")
        self.minsize = wx.TextCtrl(self.panel,-1, str(pose_config["minsize"]))
        self.minsize.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.minsize))

        mirrorLbl = wx.StaticText(self.panel, -1, "mirror")
        self.mirror = wx.CheckBox(self.panel, -1, "")
        self.mirror.SetValue(pose_config["mirror"])

        multi_stepLbl = wx.StaticText(self.panel, -1, "multi_step (reduction/steps)")
        self.multi_step_1 = wx.TextCtrl(self.panel,-1, str(pose_config['multi_step'][0][0])) # 'multi_step': [[0.001, 5]]
        self.multi_step_2 = wx.TextCtrl(self.panel, -1, str(pose_config['multi_step'][0][1]))
        self.multi_step_1.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.multi_step_1))
        self.multi_step_2.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.multi_step_2))

        net_typeLbl = wx.StaticText(self.panel, -1, "net_type")
        self.net_type = wx.TextCtrl(self.panel,-1,str(pose_config['net_type']))

        num_jointsLbl = wx.StaticText(self.panel, -1, "num_joints")
        self.num_joints = wx.TextCtrl(self.panel,-1,str(pose_config['num_joints']))
        self.num_joints.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.num_joints))

        pos_dist_threshLbl = wx.StaticText(self.panel, -1, "pos_dist_thresh")
        self.pos_dist_thresh = wx.TextCtrl(self.panel,-1,str(pose_config["pos_dist_thresh"]))
        self.pos_dist_thresh.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.pos_dist_thresh))

        rightwidthLbl = wx.StaticText(self.panel, -1, "rightwidth")
        self.rightwidth = wx.TextCtrl(self.panel,-1,str(pose_config['rightwidth']))
        self.rightwidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.rightwidth))

        save_itersLbl = wx.StaticText(self.panel, -1, "save_iters")
        self.save_iters = wx.SpinCtrl(self.panel, id=-1, min=1, max=1000, initial=pose_config['save_iters'])

        scale_jitter_loLbl = wx.StaticText(self.panel, -1, "scale_jitter_lo")
        self.scale_jitter_lo = wx.TextCtrl(self.panel,-1,str(pose_config["scale_jitter_lo"]))
        self.scale_jitter_lo.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.scale_jitter_lo))

        scale_jitter_upLbl = wx.StaticText(self.panel, -1, "scale_jitter_up")
        self.scale_jitter_up = wx.TextCtrl(self.panel,-1,str(pose_config["scale_jitter_up"]))
        self.scale_jitter_up.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.scale_jitter_up))

        topheightLbl = wx.StaticText(self.panel, -1, "topheight")
        self.topheight = wx.TextCtrl(self.panel,-1,str(pose_config['topheight']))
        self.topheight.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.topheight))


        # button to create dataset or datasets
        buttonTrain = wx.Button(self.panel, label="Train")
        buttonTrain.Bind(wx.EVT_BUTTON, self.onTrainNetwork)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        mainSizer.Add(iterationLbl, 0, wx.CENTER|wx.ALL, 2)
        mainSizer.Add(self.iteration, 0, wx.CENTER|wx.ALL, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizerRight = wx.BoxSizer(wx.VERTICAL)
        inputSizerCenter = wx.BoxSizer(wx.VERTICAL)

        # adding elements to the sizers
        inputSizer.Add(all_jointsLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(all_joints, 0, wx.EXPAND, 2)
        inputSizer.Add(all_jointsNamesLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(all_jointsNames, 0, wx.EXPAND, 2)
        inputSizer.Add(bottomheightLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.bottomheight, 0, wx.EXPAND, 2)
        inputSizer.Add(cropLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.crop, 0, wx.EXPAND, 2)
        inputSizer.Add(cropRatioLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.cropRatio, 0, wx.EXPAND, 2)
        inputSizer.Add(datasetLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.dataset, 0, wx.EXPAND, 2)
        inputSizer.Add(datasetTypeLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.datasetType, 0, wx.EXPAND, 2)
        inputSizer.Add(displayItersLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.displayIters, 0, wx.EXPAND, 2)
        inputSizer.Add(save_itersLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.save_iters, 0, wx.EXPAND, 2)
        inputSizer.Add(max_itersLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.max_iters, 0, wx.EXPAND, 2)

        inputSizer.Add(globalScaleLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.globalScale, 0, wx.EXPAND, 2)
        inputSizer.Add(initWeightsLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.initWeights, 0, wx.EXPAND, 2)
        inputSizer.Add(intermediateSupervisionLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.intermediateSupervision, 0, wx.EXPAND, 2)
        inputSizer.Add(intermediate_supervision_layerLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.intermediate_supervision_layer, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(leftwidthLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.leftwidth, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(location_refinementLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.location_refinement, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(locref_huber_lossLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.locref_huber_loss, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(locref_loss_weightLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.locref_loss_weight, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(locref_stdevLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.locref_stdev, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(max_input_sizeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.max_input_size, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(metadatasetLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.metadataset, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(min_input_sizeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.min_input_size, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(minsizeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.minsize, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(mirrorLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.mirror, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(multi_stepLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.multi_step_1, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.multi_step_2, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(net_typeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.net_type, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(num_jointsLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.num_joints, 0, wx.EXPAND, 2)
        inputSizerRight.Add(pos_dist_threshLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(self.pos_dist_thresh, 0, wx.EXPAND, 2)
        inputSizerRight.Add(rightwidthLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(self.rightwidth, 0, wx.EXPAND, 2)
        inputSizerRight.Add(scale_jitter_loLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(self.scale_jitter_lo, 0, wx.EXPAND, 2)
        inputSizerRight.Add(scale_jitter_upLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(self.scale_jitter_up, 0, wx.EXPAND, 2)
        inputSizerRight.Add(topheightLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(self.topheight, 0, wx.EXPAND, 2)
        #//////////////////////////////


        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizerCenter, 0, wx.ALL, 10)
        contentSizer.Add(inputSizerRight, 0 ,wx.ALL, 10)
        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        mainSizer.Add(buttonTrain, 0, wx.CENTER|wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)
    def onTrainNetwork(self,event):
        print('Training...')
        pose_config = self.read_fields()
        pose_config_file = self.read_fields(parse=False)
        pose_config['bottomheight'] = int(self.bottomheight.GetValue())
        pose_config['crop'] = self.crop.GetValue()
        pose_config['cropration'] = float(self.crop.GetValue())
        pose_config['dataset'] = self.dataset.GetPath()
        pose_config['dataset_type'] = self.datasetType.GetValue()
        pose_config['display_iters'] = int(self.displayIters.GetValue())
        pose_config['global_scale'] = float(self.displayIters.GetValue())
        if not self.initWeights.GetValue() == 'resnet_v1_50.ckpt':
            pose_config['init_weights'] = self.initWeights.GetValue()
        pose_config['intermediate_supervision'] = self.intermediateSupervision.GetValue()
        pose_config['intermediate_supervision_layer'] = int(self.intermediate_supervision_layer.GetValue())
        pose_config['leftwidth'] = int(self.leftwidth.GetValue())
        pose_config['location_refinement'] = self.location_refinement.GetValue()
        pose_config['locref_huber_loss'] = self.locref_huber_loss.GetValue()
        pose_config['locref_loss_weight'] = float(self.locref_loss_weight.GetValue())
        pose_config['locref_stdev'] = float(self.locref_stdev.GetValue())
        pose_config['max_input_size'] = int(self.max_input_size.GetValue())
        pose_config['min_input_size'] = int(self.min_input_size.GetValue())
        pose_config['minsize'] = int(self.minsize.GetValue())
        pose_config['mirror'] = self.mirror.GetValue()
        pose_config['multi_step'] = [self.multi_step_1.GetValue(), self.multi_step_2.GetValue()]
        pose_config['net_type'] = self.net_type.GetValue()
        pose_config['num_joints'] = int(self.num_joints.GetValue())
        pose_config['pos_dist_thresh'] = int(self.pos_dist_thresh.GetValue())
        pose_config['rightwidth'] = int(self.rightwidth.GetValue())
        pose_config['save_iters'] = int(self.save_iters.GetValue())
        pose_config['scale_jitter_lo'] = float(self.scale_jitter_lo.GetValue())
        pose_config['scale_jitter_up'] = float(self.scale_jitter_up.GetValue())
        pose_config['topheight'] = int(self.topheight.GetValue())
        config = parser_yaml(self.config)
        pose_config['project_path'] = pose_config['project_path']
        import deeplabcut as d
        d.auxiliaryfunctions.write_plainconfig(pose_config_file, pose_config)
        d.train_network(self.config, maxiters=int(self.max_iters.GetValue()), displayiters=pose_config['display_iters'],
                        saveiters=pose_config['save_iters'])
        self.Close()
        print('Training finished')
    def find_iterations(self):
        '''find the iterations given a config file.'''
        # import deeplabcut
        # cfg = deeplabcut.auxiliaryfunctions.read_config(self.config)
        config = parser_yaml(self.config)
        return os.listdir(os.path.join(config['project_path'],'dlc-models'))
    def read_fields(self, parse=True):
        iteration_selection_num = self.iteration.GetCurrentSelection()
        iteration_selection = self.iteration.GetString(iteration_selection_num)
        print('iteration_selection', iteration_selection)
        cfg = parser_yaml(self.config)
        posefile = os.path.join(cfg['project_path'], 'dlc-models',iteration_selection, cfg['Task']+cfg['date']+'-trainset'+str(int(cfg['TrainingFraction'][0]*100))+'shuffle'+str(1), 'train/pose_cfg.yaml')
        print('Pose file: ', posefile)
        if parse:
            return parser_yaml(posefile)
        else:
            return posefile

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit():
                # Valid alphanumeric character
                event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value =  edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.' not in raw_value:
                # Valid alphanumeric character
                event.Skip()

class EvaluaterNetwork(wx.Frame):
    def __init__(self,parent,title='Evaluate network',config=None):
        super(EvaluaterNetwork, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        config = parser_yaml(self.config)

        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Evaluate network")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # selection of iteration:
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        self.iteration = wx.Choice(self.panel, id=-1, choices=self.find_iterations())

        trainingIndexLbl = wx.StaticText(self.panel, -1, "Training index")
        self.trainingIndex = wx.Choice(self.panel, id=-1, choices=self.find_training_index())

        plottingLbl = wx.StaticText(self.panel, -1, "Plotting")
        self.plotting = wx.CheckBox(self.panel, -1, "")
        self.plotting.SetValue(True)

        showErrorLbl = wx.StaticText(self.panel, -1, "Show error")
        self.showError = wx.CheckBox(self.panel, -1, "")
        self.showError.SetValue(False)

        comparisionBodyPartsLbl = wx.StaticText(self.panel, -1, "Comparision body parts")

        comparisionBodyParts, items = self.MakeStaticBoxSizer(boxlabel='body parts',itemlabels=config['bodyparts']+['All'],type='checkBox')

        self.radioButtons = items
        self.radioButtonCurrentStatus = {}
        items['All'].SetValue(True)
        items['All'].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, 'All'))
        for k in items.keys():
            if not k == 'All':
                items[k].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, ''))

        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices= ['None']+get_available_gpus())

        rescaleLbl = wx.StaticText(self.panel, -1, "Rescale")
        self.rescale = wx.CheckBox(self.panel, -1, "")
        self.rescale.SetValue(False)

        # box of results:
        summaryLbl = wx.StaticText(self.panel, -1, "summaryLbl")
        self.summary = self.generate_summary()

        # button to evaluate netwrok
        buttonExtract = wx.Button(self.panel, label="Evaluate")
        buttonExtract.Bind(wx.EVT_BUTTON, self.evaluate_network)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)

        mainSizer.Add(iterationLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.iteration, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer3 = wx.BoxSizer(wx.VERTICAL)

        # inputSizer.Add(selectionAlgoLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(selectionAlgo, 0, wx.EXPAND, 2)
        inputSizer.Add(trainingIndexLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.trainingIndex, 0, wx.EXPAND, 2)
        inputSizer.Add(plottingLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.plotting, 0, wx.EXPAND, 2)
        inputSizer.Add(showErrorLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.showError, 0, wx.EXPAND, 2)

        inputSizer2.Add(comparisionBodyPartsLbl, 0, wx.EXPAND, 2)
        inputSizer2.Add(comparisionBodyParts, 0, wx.EXPAND, 2)

        inputSizer3.Add(gpusAvailableLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.gpusAvailable, 0, wx.EXPAND, 2)
        inputSizer3.Add(rescaleLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.rescale, 0, wx.EXPAND, 2)


        inputSizer2.Add(buttonExtract)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer3, 0, wx.ALL, 10)
        # contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(summaryLbl, 0, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add(self.summary, 0, wx.ALL, 2)
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)# Main window

    def evaluate_network(self, event):
        trainingIndex = float(self.trainingIndex.GetString(self.trainingIndex.GetCurrentSelection()))
        bodyParts = get_radiobutton_status(self.radioButtons)
        print(bodyParts)

        import deeplabcut as d
        d.evaluate_network(self.config, plotting=self.plotting.GetValue(),
                           show_errors=self.showError.GetValue(),comparisonbodyparts=bodyParts)
        self.Close()

    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150,25),type='block'):
        box = wx.StaticBox(self.panel, -1, boxlabel)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        items = {}
        for label in itemlabels:
            if type=='block':
                item = BlockWindow(self.panel, label=label, size=size)
            elif type=='button':
                item = wx.Button(self.panel, label=label)
            elif type=='radioButton':
                item = wx.RadioButton(self.panel, label=label, size=size)
            elif type=='checkBox':
                item = wx.CheckBox(self.panel, -1, label=label)
            else:
                item = BlockWindow(self.panel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items

    def find_iterations(self):
        '''find the iterations given a config file.'''
        # import deeplabcut
        # cfg = deeplabcut.auxiliaryfunctions.read_config(self.config)
        config = parser_yaml(self.config)
        print(" evaluation results: ", os.path.join(config['project_path'],'evaluation_results'))
        if os.path.exists(os.path.join(config['project_path'],'evaluation_results')):
            return os.listdir(os.path.join(config['project_path'],'evaluation_results'))
        else:
            return ['']
    def find_training_index(self):
        config = parser_yaml(self.config)
        trainingFractions = config['TrainingFraction']
        if len(trainingFractions)==0:
            return ['']
        print('trainingFractions: ',  trainingFractions, 'type: ', type(trainingFractions))
        return [str(c) for c in trainingFractions]

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)

    def generate_summary(self):
        # Create a wxGrid object
        grid = wx.grid.Grid(self.panel, -1)

        # Then we call CreateGrid to set the dimensions of the grid
        columns = ['Training iterations', '%Training dataset', 'Shuffle number', 'Train error(px)', 'Test error(px)',
                   'p-cutoff', 'used', 'Train error with p-cutoff', 'Test error with p-cutoff']
        grid.CreateGrid(1, len(columns))
        for i, c in enumerate(columns):
            grid.SetColLabelValue(i,c)
        grid.SetRowLabelSize(0)
        # READING VALUES:
        iteration_selection_num = self.iteration.GetCurrentSelection()
        iteration_selection = self.iteration.GetString(iteration_selection_num)
        cfg = parser_yaml(self.config)
        path_to_csv =  os.path.join(cfg['project_path'], 'dlc-models',iteration_selection, cfg['Task']+cfg['date']+'-trainset'+str(int(cfg['TrainingFraction'][0]*100))+'shuffle'+str(1), 'train/pose_cfg.yaml')


        # # And set grid cell contents as strings
        # grid.SetCellValue(0, 0, 'wxGrid is good')
        #
        # # We can specify that some cells are read.only
        # grid.SetCellValue(0, 3, 'This is read.only')
        # grid.SetReadOnly(0, 3)
        #
        # # Colours can be specified for grid cell contents
        # grid.SetCellValue(3, 3, 'green on grey')
        # grid.SetCellTextColour(3, 3, wx.GREEN)
        # grid.SetCellBackgroundColour(3, 3, wx.LIGHT_GREY)
        #
        # # We can specify the some cells will store numeric
        # # values rather than strings. Here we set grid column 5
        # # to hold floating point values displayed with width of 6
        # # and precision of 2
        # grid.SetColFormatFloat(5, 6, 2)
        # grid.SetCellValue(0, 6, '3.1415')
        # sizer = wx.BoxSizer(grid, wx.VERTICAL)
        # sizer.Add(grid, 1, wx.EXPAND, 2)
        grid.AutoSize()
        return grid

class FilterPredictions(wx.Frame):
    def __init__(self,parent,title='filter predictions',config=None):
        super(FilterPredictions, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        config = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Filter predictions")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # input test to set the working directory
        targetVideosLbl = wx.StaticText(self.panel, -1, "Video to filter:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.targetVideos = wx.FilePickerCtrl(self.panel,-1)

        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.TextCtrl(self.panel, -1, "1")
        self.shuffle.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffle))

        windowlengthLbl = wx.StaticText(self.panel, -1, "Window length:")
        self.windowlength = wx.TextCtrl(self.panel, -1, "5")
        self.windowlength.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.windowlength))

        p_boundLbl = wx.StaticText(self.panel, -1, "P-Bound:")
        self.p_bound = wx.TextCtrl(self.panel, -1, "0.001")
        self.p_bound.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.p_bound))

        ARdegreeLbl = wx.StaticText(self.panel, -1, "Autoregressive degree:")
        self.ARdegree = wx.TextCtrl(self.panel, -1, "3")
        self.ARdegree.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.ARdegree))

        MAdegreeLbl = wx.StaticText(self.panel, -1, "Moving Avarage degree:")
        self.MAdegree = wx.TextCtrl(self.panel, -1, "1")
        self.MAdegree.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.MAdegree))

        alphaLbl = wx.StaticText(self.panel, -1, "MEDIAN degree:")
        self.alpha = wx.TextCtrl(self.panel, -1, "0.5")
        self.alpha.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.alpha))


        saveAsCSVLbl = wx.StaticText(self.panel, -1, "Save as CSV:")
        self.saveAsCSV = wx.CheckBox(self.panel, -1, "");
        self.saveAsCSV.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, ".mp4")

        filterTypeLbl = wx.StaticText(self.panel, -1, "Filter type:")
        self.filterType = wx.Choice(self.panel, id=-1, choices=['arima', 'median'])

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        buttonFilter = wx.Button(self.panel, label="Filter")
        buttonFilter.Bind(wx.EVT_BUTTON, self.onFilter)


        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        mainSizer.Add(targetVideosLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.targetVideos, 0, wx.EXPAND, 2)
        mainSizer.Add(destfolderLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.destfolder, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(shuffleLbl, 0 , wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.shuffle, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(windowlengthLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.windowlength, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(p_boundLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.p_bound, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(ARdegreeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.ARdegree, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(filterTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.filterType, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer2.Add(MAdegreeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.MAdegree, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(alphaLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.alpha, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(saveAsCSVLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.saveAsCSV, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(videoTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.videoType, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(buttonFilter, 0, wx.EXPAND | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups

        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onFilter(self, event):
        filterType = self.filterType.GetString(self.filterType.GetCurrentSelection())
        destfolder = None if self.destfolder.GetPath()=='' else self.destfolder.GetPath()
        print("destfolder: ", destfolder)
        import deeplabcut as d
        d.filterpredictions(self.config, video=self.targetVideos.GetPath(), videotype=self.videoType.GetValue(),
                            shuffle=int(self.shuffle.GetValue()), filtertype=filterType,
                            windowlength=int(self.windowlength.GetValue()), p_bound=float(self.p_bound.GetValue()),
                            ARdegree=int(self.ARdegree.GetValue()), MAdegree=int(self.MAdegree.GetValue()),
                            alpha=float(self.alpha.GetValue()), save_as_csv=self.saveAsCSV.GetValue(),
                            destfolder=destfolder)
        self.Close()

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit():
                # Valid alphanumeric character
                event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value =  edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.' not in raw_value:
                # Valid alphanumeric character
                event.Skip()

class PlotPredictions(wx.Frame):
    def __init__(self,parent,title='Plot predictions',config=None, videos=[]):
        super(PlotPredictions, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        self.videos = videos
        config = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Plot predictions")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # shuffle
        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.TextCtrl(self.panel, -1, "1")
        self.shuffle.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffle))


        filteredLbl = wx.StaticText(self.panel, -1, "Filtered:")
        self.filtered = wx.CheckBox(self.panel, -1, "");
        self.filtered.SetValue(False)

        showFiguresLbl = wx.StaticText(self.panel, -1, "Show figures:")
        self.showFigures = wx.CheckBox(self.panel, -1, "");
        self.showFigures.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, ".mp4")

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        buttonPlot = wx.Button(self.panel, label="Plot")
        buttonPlot.Bind(wx.EVT_BUTTON, self.OnPlot)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        mainSizer.Add(destfolderLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.destfolder, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(shuffleLbl, 0 , wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.shuffle, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(filteredLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.filtered, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(showFiguresLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.showFigures, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(videoTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.videoType, 0, wx.EXPAND | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups

        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonPlot, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def OnPlot(self, event):
        if len(self.videos) == 0:
            print('ERROR: No videos specified.')
            return
        destfolder = None if self.destfolder.GetPath()=='' else self.destfolder.GetPath()
        print("destfolder: ", destfolder)
        import deeplabcut as d
        d.plot_trajectories(self.config, videos=self.videos, videotype=self.videoType.GetValue(),
                            shuffle=int(self.shuffle.GetValue()), filtered=self.filtered.GetValue(),
                            showfigures= self.showFigures.GetValue(),
                            destfolder=destfolder)
        self.Close()

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit():
                # Valid alphanumeric character
                event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value =  edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.' not in raw_value:
                # Valid alphanumeric character
                event.Skip()

class LabelPredictions(wx.Frame):
    def __init__(self,parent,title='Label predictions',config=None, videos=[]):
        super(LabelPredictions, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 600
        self.videos = videos
        config = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Label predictions")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # shuffle
        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.TextCtrl(self.panel, -1, "1")
        self.shuffle.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffle))

        # filtered
        filteredLbl = wx.StaticText(self.panel, -1, "Filtered:")
        self.filtered = wx.CheckBox(self.panel, -1, "");
        self.filtered.SetValue(False)

        # save frames
        saveFramesLbl = wx.StaticText(self.panel, -1, "Save frames:")
        self.saveFrames = wx.CheckBox(self.panel, -1, "");
        self.saveFrames.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, "avi")

        bodyPartsBox, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                              itemlabels=config['bodyparts']+['All'], type='checkBox')
        self.radioButtons = items
        self.radioButtonCurrentStatus = {}
        items['All'].SetValue(True)
        items['All'].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, 'All'))
        for k in items.keys():
            if not k == 'All':
                items[k].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, ''))
        # codec
        codecLbl = wx.StaticText(self.panel, -1, "Codec:")
        self.codec = wx.TextCtrl(self.panel, -1, ".mp4v")

        # Output Frame Rate
        outputFrameRateLbl = wx.StaticText(self.panel, -1, "Output Frame Rate:")
        self.outputFrameRate = wx.TextCtrl(self.panel, -1, "0")
        self.outputFrameRate.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.outputFrameRate))

        # draw skeleton
        drawSkeletonLbl = wx.StaticText(self.panel, -1, "Draw skeleton:")
        self.drawSkeleton = wx.CheckBox(self.panel, -1, "");
        self.drawSkeleton.SetValue(False)

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        # create labeeled video
        labelButton = wx.Button(self.panel, label="Create Labeled Video")
        labelButton.Bind(wx.EVT_BUTTON, self.onLabel)
        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        mainSizer.Add(destfolderLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.destfolder, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(shuffleLbl, 0 , wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.shuffle, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(filteredLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.filtered, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(saveFramesLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.saveFrames, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(videoTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.videoType, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(bodyPartsBox, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(codecLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.codec, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(outputFrameRateLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.outputFrameRate, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(drawSkeletonLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer2.Add(self.drawSkeleton, 0, wx.EXPAND | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups

        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 1)
        mainSizer.Add(labelButton, 0, wx.ALL | wx.CENTER , 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onLabel(self, event):
        import deeplabcut as d
        outputframerate = float(self.outputFrameRate.GetValue())
        if outputframerate < 1:
            outputframerate = None
        bodyParts = get_radiobutton_status(self.radioButtons)
        d.create_labeled_video(self.config, videos = self.videos, videotype=self.videoType.GetValue(), displayedbodyparts=bodyparts,
                               shuffle=int(self.shuffle), filtered=self.filtered.GetValue(), save_frames= self.saveFrames.GetValue(),
                               codec=self.codec.GetValue(), outputframerate=outputframerate, draw_skeleton=self.drawSkeleton.GetValue())
        self.Close()

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit():
                # Valid alphanumeric character
                event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value =  edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.' not in raw_value:
                # Valid alphanumeric character
                event.Skip()
    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150,25),type='block'):
        box = wx.StaticBox(self.panel, -1, boxlabel)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        items = {}
        for label in itemlabels:
            if type=='block':
                item = BlockWindow(self.panel, label=label, size=size)
            elif type=='button':
                item = wx.Button(self.panel, label=label)
            elif type=='radioButton':
                item = wx.RadioButton(self.panel, label=label, size=size)
            elif type=='checkBox':
                item = wx.CheckBox(self.panel, -1, label=label)
            else:
                item = BlockWindow(self.panel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)

class ExtractOutliers(wx.Frame):
    def __init__(self,parent,title='Extract outliers',config=None, videos=[]):
        super(ExtractOutliers, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.config = config
        self.videos = videos
        self.WIDTHOFINPUTS = 600
        config = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Extract outliers")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # shuffle
        videotypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videotype = wx.TextCtrl(self.panel, -1, "avi")

        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.TextCtrl(self.panel, -1, "1")
        self.shuffle.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffle))

        # extraction algorithm
        extractionAlgLbl = wx.StaticText(self.panel, -1, "Extraction algorithm")
        self.extractionAlg = wx.Choice(self.panel, id=-1, choices=['kmeans', 'uniform'])

        # outlier algorithm
        outlierAlgLbl = wx.StaticText(self.panel, -1, "Outlier algorithm")
        self.outlierAlg = wx.Choice(self.panel, id=-1, choices=['fitting', 'jump', 'uncertain', 'manual'])

        # epsilon...
        epsilonLbl = wx.StaticText(self.panel, -1, "Epsilon:")
        self.epsilon = wx.TextCtrl(self.panel, -1, "20.0")
        self.epsilon.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.epsilon))

        p_boundLbl = wx.StaticText(self.panel, -1, "P-Bound:")
        self.p_bound = wx.TextCtrl(self.panel, -1, "0.001")
        self.p_bound.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.p_bound))

        ARdegreeLbl = wx.StaticText(self.panel, -1, "Autoregressive degree:")
        self.ARdegree = wx.TextCtrl(self.panel, -1, "3")
        self.ARdegree.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.ARdegree))

        MAdegreeLbl = wx.StaticText(self.panel, -1, "Moving Avarage degree:")
        self.MAdegree = wx.TextCtrl(self.panel, -1, "1")
        self.MAdegree.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.MAdegree))

        alphaLbl = wx.StaticText(self.panel, -1, "Significance level for detecting outliers:")
        self.alpha = wx.TextCtrl(self.panel, -1, "0.01")
        self.alpha.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.alpha))

        # Cluster Color
        clusterColorLbl = wx.StaticText(self.panel, -1, "Cluster Color:")
        self.clusterColor = wx.CheckBox(self.panel, -1, "");
        self.clusterColor.SetValue(False)

        # Cluster resize width
        clusterResizeWidthLbl = wx.StaticText(self.panel, -1, "Cluster resize width:")
        self.clusterResizeWidth = wx.TextCtrl(self.panel, -1, "30")
        self.clusterResizeWidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.clusterResizeWidth))

        # automatic
        automaticLbl = wx.StaticText(self.panel, -1, "Automatic:")
        self.automatic = wx.CheckBox(self.panel, -1, "");
        self.automatic.SetValue(False)

        # Save Labeled
        saveLabeledLbl = wx.StaticText(self.panel, -1, "Save laveled:")
        self.saveLabeled = wx.CheckBox(self.panel, -1, "");
        self.saveLabeled.SetValue(True)

        bodyPartsBox, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                              itemlabels=config['bodyparts']+['All'], type='checkBox')
        self.radioButtons = items
        self.radioButtonCurrentStatus = {}
        items['All'].SetValue(True)
        items['All'].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, 'All'))
        for k in items.keys():
            if not k == 'All':
                items[k].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, ''))

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        # create labeeled video
        extractOutliersButton = wx.Button(self.panel, label="extract outliers")
        extractOutliersButton.Bind(wx.EVT_BUTTON, self.OnExtractOutliers)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        mainSizer.Add(destfolderLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.destfolder, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer3 = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(videotypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.videotype, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(shuffleLbl, 0 , wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.shuffle, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(clusterColorLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.clusterColor, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(clusterResizeWidthLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.clusterResizeWidth, 0, wx.EXPAND, 2)
        inputSizer.Add(automaticLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.automatic, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(saveLabeledLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.saveLabeled, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer2.Add(bodyPartsBox, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer3.Add(extractionAlgLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.extractionAlg, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(outlierAlgLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.outlierAlg, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer3.Add(epsilonLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.epsilon, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer3.Add(p_boundLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.p_bound, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(ARdegreeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.ARdegree, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(MAdegreeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.MAdegree, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(alphaLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.alpha, 0, wx.EXPAND | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer3, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups

        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 1)
        mainSizer.Add(extractOutliersButton, 0, wx.ALL | wx.CENTER , 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def OnExtractOutliers(self, event):
        import deeplabcut as d
        outlieralg = self.outlierAlg.GetString(self.outlierAlg.GetCurrentSelection())
        extractionAlg = self.extractionAlg.GetString(self.extractionAlg.GetCurrentSelection())
        bodyParts = get_radiobutton_status(self.radioButtons)
        d.extract_outlier_frames(config=self.config, videos=self.videos, videotype=self.videotype, shuffle=int(self.shuffle.GetValue()),
                                 outlieralgorithm=outlieralg, comparisonbodyparts=bodyParts, epsilon=float(self.epsilon.GetValue()),
                                 p_bound=float(self.p_bound.GetValue()), ARdegree=int(self.ARdegree.GetValue()),
                                 MAdegree=int(self.MAdegree.GetValue()), alpha=float(self.alpha.GetValue()), extractionalgorithm=extractionAlg,
                                 automatic=self.automatic.GetValue(), savelabeled=self.saveLabeled.GetValue())
        self.Close()

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit():
                # Valid alphanumeric character
                event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value =  edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.' not in raw_value:
                # Valid alphanumeric character
                event.Skip()
    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150,25),type='block'):
        box = wx.StaticBox(self.panel, -1, boxlabel)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        items = {}
        for label in itemlabels:
            if type=='block':
                item = BlockWindow(self.panel, label=label, size=size)
            elif type=='button':
                item = wx.Button(self.panel, label=label)
            elif type=='radioButton':
                item = wx.RadioButton(self.panel, label=label, size=size)
            elif type=='checkBox':
                item = wx.CheckBox(self.panel, -1, label=label)
            else:
                item = BlockWindow(self.panel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)

class AnalyzeVideos(wx.Frame):
    def __init__(self,parent,title='Analyze videos',config=None):
        super(AnalyzeVideos, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Analyze videos")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # input test to set the working directory
        targetVideosLbl = wx.StaticText(self.panel, -1, "Target videos path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # TODO: make default path find yaml in the current directory
        self.targetVideos = wx.DirPickerCtrl(self.panel,-1)

        listOrPathLbl = wx.StaticText(self.panel, -1, "Use list or path?")
        self.listOrPath = wx.Choice(self.panel, id=-1, choices=['target videos path','target videos list'])

        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.TextCtrl(self.panel, -1, "1")
        self.shuffle.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, shuffle))

        saveAsCSVLbl = wx.StaticText(self.panel, -1, "Save as CSV:")
        self.saveAsCSV = wx.CheckBox(self.panel, -1, "");
        self.saveAsCSV.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, ".mp4")

        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices=['None'])#+get_available_gpus()

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        # list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.panel, -1, "Target videos list:")
        self.videosList = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT )
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # buttons to add video
        bmp1 = wx.Image("figures/iconplus.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.panel, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image("figures/iconMinus.bmp", wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonMinus = wx.BitmapButton(self.panel, -1, bmp2, pos=(10, 20))
        self.buttonMinus.Bind(wx.EVT_BUTTON, self.onRemoveVideo)

        # button to filter predictions
        filterPredictionsButton = wx.Button(self.panel, label='Filter Predictions')
        filterPredictionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'filter predictions'))

        plotPredictionsButton = wx.Button(self.panel, label='Plot Predictions')
        plotPredictionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'plot predictions'))

        labelPredictionsButton = wx.Button(self.panel, label='Label Predictions')
        labelPredictionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'label predictions'))

        extractOutliersButton = wx.Button(self.panel, label='Extract Outliers')
        extractOutliersButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'extract outliers'))

        # button to create project
        buttonAnalyze = wx.Button(self.panel, label="Analyze")
        buttonAnalyze.Bind(wx.EVT_BUTTON, self.onEvaluate)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)



        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        # inputSizer.Add(configPathLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(configPath, 0, wx.EXPAND, 2)
        inputSizer.Add(targetVideosLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.targetVideos, 0, wx.EXPAND, 2)
        inputSizer.Add(videosListLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosList, 0, wx.EXPAND, 2)

        line1 = wx.BoxSizer(wx.HORIZONTAL)
        line1.Add(shuffleLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.shuffle, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(saveAsCSVLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.saveAsCSV, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(videoTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.videoType, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(gpusAvailableLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.gpusAvailable, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer.Add(line1, 0, wx.EXPAND, 2)
        inputSizer.Add(destfolderLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.destfolder, 0, wx.EXPAND, 2)
        inputSizer.Add(listOrPathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.listOrPath, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(self.buttonPlus, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(self.buttonMinus, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(buttonAnalyze, 0, wx.EXPAND | wx.ALL , 5)
        buttonSizer.Add(filterPredictionsButton, 0, wx.EXPAND | wx.ALL , 5)
        buttonSizer.Add(plotPredictionsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(labelPredictionsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(extractOutliersButton, 0, wx.EXPAND | wx.ALL, 5)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onEvaluate(self, event):
        if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
            videos = self.destfolder.GetPath()
        else: #'target videos list'
            videos = get_videos(self.videosList)
        if self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()) == 'None':
            gputouse = None
        else:
            gputouse = int(self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()))
        destfolder = self.destfolder.GetPath()
        if destfolder == '':
            destfolder = None

        import deeplabcut as d
        d.analyze_videos(self.config, videos=videos, videotype=self.videoType.GetValue(),
                         shuffle=self.shuffle.GetValue(), gputouse=gputouse, save_as_csv=self.saveAsCSV.GetValue(),
                         destfolder=destfolder)
        self.Close()

    def onAddVideo(self,event):
        dialog = wx.FileDialog(None, "Choose input directory", "",
                           style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST) # wx.FD_FILE_MUST_EXIST
        if dialog.ShowModal() == wx.ID_OK:
            pathToFile = dialog.GetPath()
            print('Path to file: ', pathToFile)
        else:
            return
        dialog.Destroy()
        line = os.path.basename(pathToFile)

        self.videosList.InsertItem(self.listIndex, line)
        self.videosList.SetItem(self.listIndex, 1, pathToFile)
        self.listIndex += 1

    def onRemoveVideo(self,event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.videosList.GetFirstSelected(self)
        if item_id==-1:
            item_id = self.listIndex-1

        print("removing entry : ", item_id)
        self.videosList.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex-1

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit():
                # Valid alphanumeric character
                event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value =  edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or chr(keycode)=='.' and '.' not in raw_value:
                # Valid alphanumeric character
                event.Skip()

    def on_new_frame(self, event,frame_type):
        if frame_type is None or len(frame_type)==0: # empty string:
            print('new frame not specified in button!! ')
            return
        elif frame_type == 'filter predictions':
            frame = FilterPredictions(self.GetParent(), config=self.config)
        elif frame_type == 'plot predictions':
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            frame = PlotPredictions(self.GetParent(), config=self.config, videos=videos)
        elif frame_type == 'label predictions':
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            frame = LabelPredictions(self.GetParent(), config=self.config, videos=videos)
        elif frame_type == 'extract outliers':
            count = self.videosList.GetItemCount()
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            frame = ExtractOutliers(self.GetParent(), config=self.config, videos=videos)
        else:
            return
        frame.Show()

class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        self.out.WriteText(string)
        wx.CallAfter(self.out.WriteText, string)

class Log(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Log")

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(panel, wx.ID_ANY, size=(300, 100),
                          style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)

        # redirect text here
        redir = RedirectText(log)
        sys.stdout = redir

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size = (640,500))
        self.mainPanel = MainPanel(self)
        topLbl = wx.StaticText(self.mainPanel, -1, "quick DLC")

        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # create main control elements
        # annotation
        box1, items = self.MakeStaticBoxSizer("Annotation",
                                       ['create new project', 'add new videos', 'extract frames', 'label frames','check annotations'],
                                       size=(200,25),
                                       type='button')
        items['create new project'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'create new project'))
        items['add new videos'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'add new videos'))
        items['extract frames'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'extract frames'))
        items['label frames'].Bind(wx.EVT_BUTTON, self.on_label_frames)
        items['check annotations'].Bind(wx.EVT_BUTTON, self.on_check_annotations)

        print(box1.GetChildren())

        # training
        box2, items = self.MakeStaticBoxSizer("Training",
                                       ['create training set','train network','evaluate network'],
                                       size=(200, 25),
                                       type='button')
        items['create training set'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'create training set'))
        items['train network'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'train network'))
        items['evaluate network'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'evaluate network'))

        # refinement
        box3, items = self.MakeStaticBoxSizer("Refinement",
                                       ['analyze videos', 'refine labels', 'merge datasets'],
                                       size=(200, 25),
                                       type='button')
        items['analyze videos'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'analyze videos'))
        items['refine labels'].Bind(wx.EVT_BUTTON, self.OnRefineLabels)
        items['merge datasets'].Bind(wx.EVT_BUTTON, self.OnMergeDataset)
        # config path selection:
        configPathLbl = wx.StaticText(self.mainPanel, -1, "Config path:", size=wx.Size(600, 25))
        cwd = find_yaml()
        self.configPath = wx.FilePickerCtrl(self.mainPanel, -1, cwd, wildcard='*.yaml')

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.mainPanel), 0,
                      wx.EXPAND | wx.TOP, 5)

        # create a button sizer
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(box1, 0, wx.ALL, 10)
        buttonSizer.Add(box2, 0, wx.ALL, 10)
        buttonSizer.Add(box3, 0, wx.ALL, 10)

        # add button sizer to the main sizer
        mainSizer.Add(buttonSizer, 0, wx.CENTER | wx.TOP, 10)
        mainSizer.Add(configPathLbl, 0, wx.EXPAND | wx.TOP, 10)
        mainSizer.Add(self.configPath, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.mainPanel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150,25),type='block'):
        box = wx.StaticBox(self.mainPanel, -1, boxlabel)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        items = {}
        for label in itemlabels:
            if type=='block':
                item = BlockWindow(self.mainPanel, label=label, size=size)
            elif type=='button':
                item = wx.Button(self.mainPanel, label=label    )
            else:
                item = BlockWindow(self.mainPanel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items

    def on_label_frames(self, event):
        print('create labels...')
        import deeplabcut as d
        config_path = self.configPath.GetPath()
        d.label_frames(config_path)
        print('Done')

    def on_check_annotations(self, event):
        print('check labels...')
        import deeplabcut as d
        config_path = self.configPath.GetPath()
        d.check_labels(config_path)
        print('Done')

    def on_new_frame(self, event,frame_type):
        if frame_type is None or len(frame_type)==0: # empty string:
            print('new frame not specified in button!! ')
            return
        elif frame_type == 'create new project':
            frame = NewProjectFrame(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'add new videos':
            frame = AddNewVideos(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'extract frames':
            frame = ExtractFrames(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'create training set':
            frame = CreateTraining(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'train network':
            frame = TrainNetwork(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'evaluate network':
            frame = EvaluaterNetwork(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'analyze videos':
            frame = AnalyzeVideos(self.GetParent(), config=self.configPath.GetPath())
        else:
            return
        frame.Show()

    def OnRefineLabels(self, event):
        import deeplabcut as d
        d.refine_labels(self.configPath.GetPath())

    def OnMergeDataset(self, event):
        import deeplabcut as d
        d.merge_datasets(self.configPath.GetPath())

class MainPanel(wx.Panel):
    def __init__(self, parent):
        super(MainPanel, self).__init__(parent)


# Object app
class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(parent=None, title='Quick DLC interface')
        self.frame.Show()
        # self.log = Log()
        # self.log.Show()
        return True

if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()




