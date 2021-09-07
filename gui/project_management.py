import glob
import os

import wx

from main import MainPanel, CWD
from gui.utils.generic import get_videos


class AddNewVideos(wx.Frame):
    def __init__(self, parent, title='Add new videos', config=None):
        super(AddNewVideos, self).__init__(parent, title=title, size=(640, 500))
        self.addNewVideosFrame = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.addNewVideosFrame, -1, "Add New Videos")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # input test to set the working directory
        videosPathLbl = wx.StaticText(self.addNewVideosFrame, -1, "Path to videos:",
                                      size=wx.Size(self.WIDTHOFINPUTS, 25))
        # TODO: make default path find yaml in the current directory
        self.videosPath = wx.DirPickerCtrl(self.addNewVideosFrame, -1)

        # check box to select copy videos
        copyVideosLbl = wx.StaticText(self.addNewVideosFrame, -1, "Copy videos:")
        self.copyVideos = wx.CheckBox(self.addNewVideosFrame, -1, "")
        self.copyVideos.SetValue(True)

        listOrPathLbl = wx.StaticText(self.addNewVideosFrame, -1, "Use list or path?")
        self.listOrPath = wx.Choice(self.addNewVideosFrame, id=-1, choices=['target videos path', 'target videos list'])

        # list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.addNewVideosFrame, -1, "Videos:")
        self.videosList = wx.ListCtrl(self.addNewVideosFrame, -1, style=wx.LC_REPORT)
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # buttons to add video
        bmp1 = wx.Image(os.path.join(CWD, "figures/iconplus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.addNewVideosFrame, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image(os.path.join(CWD, "figures/iconMinus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
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
        contentSizer.Add(buttonSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.addNewVideosFrame.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onAddVideos(self, event):
        print('Adding new videos ...')
        import deeplabcut as d
        listOrPath = self.listOrPath.GetString(self.listOrPath.GetCurrentSelection())
        if listOrPath == 'target videos path':
            video_path = self.videosPath.GetPath()
            print('video path: ', video_path)
            videos = [v for v in glob.glob(os.path.join(video_path, "**"), recursive=True) if v.endswith('.avi')]
            print('NEW VIDEOS FOUND:')
            for v in videos:
                print(v)
            d.add_new_videos(self.config, videos=videos, copy_videos=self.copyVideos.GetValue())
        elif listOrPath == 'target videos list':
            videos = get_videos(self.videosList)
            d.add_new_videos(self.config, videos=videos, copy_videos=self.copyVideos.GetValue())
        print('Done')
        self.Close()

    def onAddVideo(self, event):
        dialog = wx.FileDialog(None, "Choose input directory", "",
                               style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST)  # wx.FD_FILE_MUST_EXIST
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

    def onRemoveVideo(self, event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.videosList.GetFirstSelected(self)
        if item_id == -1:
            item_id = self.listIndex - 1

        print("removing entry : ", item_id)
        self.videosList.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex - 1


class NewProjectFrame(wx.Frame):
    def __init__(self, parent, mainFrame, title='New project', config=None):
        super(NewProjectFrame, self).__init__(parent, title=title, size=(640, 500))
        self.mainFrame = mainFrame
        self.newProjectFrame = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.newProjectFrame, -1, "Create a new project")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # input text to put the name of the project
        nameLbl = wx.StaticText(self.newProjectFrame, -1, "Name:")
        self.name = wx.TextCtrl(self.newProjectFrame, -1, "")

        # input text to set experiemnter
        experimenterLbl = wx.StaticText(self.newProjectFrame, -1, "Experimenter:")
        self.experimenter = wx.TextCtrl(self.newProjectFrame, -1, "")

        # input test to set the working directory
        wdirLbl = wx.StaticText(self.newProjectFrame, -1, "Working directory:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # wdir = wx.TextCtrl(self.newProjectFrame, -1, "")
        # TODO: make default directory the current directory
        cwd = os.getcwd()
        self.wdir = wx.DirPickerCtrl(self.newProjectFrame, -1, cwd)

        # choice box with to select type of quick-DLC Project
        projectTypeLbl = wx.StaticText(self.newProjectFrame, -1, "Type of quick-DLC")
        self.projectType = wx.Choice(self.newProjectFrame, -1, choices=['contact', 'motion', 'whisking'])

        # check box to select copy videos
        copyVideosLbl = wx.StaticText(self.newProjectFrame, -1, "Copy videos:")
        self.copyVideos = wx.CheckBox(self.newProjectFrame, -1, "")
        self.copyVideos.SetValue(True)

        # check box to make project multi animal
        multiAnimalLbl = wx.StaticText(self.newProjectFrame, -1, "Make multi-animal project:")
        self.multiAnimal = wx.CheckBox(self.newProjectFrame, -1, "")
        self.multiAnimal.SetValue(False)


        # list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.newProjectFrame, -1, "Videos:")
        self.videosList = wx.ListCtrl(self.newProjectFrame, -1, style=wx.LC_REPORT)
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # buttons to add video
        bmp1 = wx.Image(os.path.join(CWD, "figures/iconplus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.newProjectFrame, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image(os.path.join(CWD, "figures/iconMinus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
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
        inputSizer.Add(projectTypeLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.projectType, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(copyVideosLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.copyVideos, 0, wx.EXPAND, 2)
        buttonSizer.Add(multiAnimalLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.multiAnimal, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.buttonPlus, 0, wx.EXPAND, 2)
        buttonSizer.Add(self.buttonMinus, 0, wx.EXPAND, 2)
        buttonSizer.Add(buttonCreate, 0, wx.EXPAND, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(buttonSizer, 0, wx.ALL, 10)

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
        multi_animal = self.multiAnimal.GetValue()
        videos = get_videos(self.videosList)
        print('Importing deeplabcut....')
        import deeplabcut as d
        config_path = d.create_new_project(project=name, experimenter=experimenter, videos=videos,
                                           working_directory=wdir, copy_videos=copy_videos, multianimal=multi_animal)
        project_type = self.projectType.GetStringSelection()
        d.auxiliaryfunctions.edit_config(config_path, {"project_type": project_type})
        if project_type=='contact' and not multi_animal:
            d.auxiliaryfunctions.edit_config(config_path, {"bodyparts": ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9',
                                                                         'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9',
                                                                         'nose']})
        elif project_type=='contact' and multi_animal:
            d.auxiliaryfunctions.edit_config(config_path,
                                             {"multianimalbodyparts": ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9'],
                                              "individuals":['wU1','wD1'],
                                              'uniquebodyparts':'[nose]'})
        elif (project_type=='whisking' or project_type=='motion') and multi_animal:
            d.auxiliaryfunctions.edit_config(config_path,
                                             {"multianimalbodyparts": ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7','a8', 'a9'],
                                              "individuals": ['wR1', 'wR2', 'wR3', 'wR4', 'wL1', 'wL2', 'wL3', 'wL4'],
                                              'uniquebodyparts': '[nose]'})
        else:
            print(f"WARNING: projec_type={project_type} is not compatible with multianimal = {multi_animal}. Analysis and Simplified modeles may not work")
        print('project create with config.yaml file:', config_path)

        self.mainFrame.configPath.SetPath(config_path)
        self.Close()

    def onAddVideo(self, event):
        dialog = wx.FileDialog(None, "Choose input directory", "",
                               style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST)  # wx.FD_FILE_MUST_EXIST
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

    def onRemoveVideo(self, event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.videosList.GetFirstSelected(self)
        if item_id == -1:
            item_id = self.listIndex - 1

        print("removing entry : ", item_id)
        self.videosList.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex - 1