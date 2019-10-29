import wx
from blockwindow import BlockWindow
import os


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


class CreateTrainingSet(wx.Frame):
    def __init__(self,parent,title='Create training set'):
        super(ExtractFrames, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
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
    def __init__(self,parent,title='Extract frames'):
        super(ExtractFrames, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Extract frames")
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





class AddNewVideos(wx.Frame):
    def __init__(self,parent,title='Add new videos'):
        super(AddNewVideos, self).__init__(parent, title=title, size=(640, 500))
        self.addNewVideosFrame = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.addNewVideosFrame, -1, "Add New Videos")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))


        # input test to set the working directory
        configPathLbl = wx.StaticText(self.addNewVideosFrame, -1, "Config path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # TODO: make default path find yaml in the current directory
        cwd = find_yaml()
        configPath = wx.FilePickerCtrl(self.addNewVideosFrame,-1,cwd,wildcard='*.yaml')

        # check box to select copy videos
        copyVideosLbl = wx.StaticText(self.addNewVideosFrame, -1, "Copy videos:")
        copyVideos = wx.CheckBox(self.addNewVideosFrame, -1, "");
        copyVideos.SetValue(True)

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
        # btn.Bind(wx.EVT_BUTTON, self.add_line)

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
        inputSizer.Add(configPathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(configPath, 0, wx.EXPAND, 2)
        inputSizer.Add(videosListLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosList, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(copyVideosLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(copyVideos, 0, wx.EXPAND, 2)
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
    def __init__(self,parent,title='New project'):
        super(NewProjectFrame, self).__init__(parent, title=title, size=(640, 500))
        self.newProjectFrame = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.newProjectFrame, -1, "Create a new project")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # input text to put the name of the project
        nameLbl = wx.StaticText(self.newProjectFrame, -1, "Name:")
        name = wx.TextCtrl(self.newProjectFrame, -1, "");

        # input text to set experiemnter
        experimenterLbl = wx.StaticText(self.newProjectFrame, -1, "Experimenter:")
        experimenter = wx.TextCtrl(self.newProjectFrame, -1, "");

        # input test to set the working directory
        wdirLbl = wx.StaticText(self.newProjectFrame, -1, "Working directory:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # wdir = wx.TextCtrl(self.newProjectFrame, -1, "");
        # TODO: make default directory the current directory
        cwd = os.getcwd()
        wdir = wx.DirPickerCtrl(self.newProjectFrame,-1,cwd)

        # check box to select copy videos
        copyVideosLbl = wx.StaticText(self.newProjectFrame, -1, "Copy videos:")
        copyVideos = wx.CheckBox(self.newProjectFrame, -1, "");
        copyVideos.SetValue(True)

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
        # btn.Bind(wx.EVT_BUTTON, self.add_line)

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
        inputSizer.Add(name, 0, wx.EXPAND, 2)
        inputSizer.Add(experimenterLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(experimenter, 0, wx.EXPAND, 2)
        inputSizer.Add(wdirLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(wdir, 0, wx.EXPAND, 2)
        inputSizer.Add(videosListLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosList, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(copyVideosLbl, 0, wx.EXPAND, 2)
        buttonSizer.Add(copyVideos, 0, wx.EXPAND, 2)
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

# Main window
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

        print(box1.GetChildren())

        # training
        box2, items = self.MakeStaticBoxSizer("Training",
                                       ['create training set','train network','evaluate'],
                                       size=(200, 25),
                                       type='button')
        # refinement
        box3, items = self.MakeStaticBoxSizer("Refinement",
                                       ['Analyze videos', 'outliers', 'merge datasets'],
                                       size=(200, 25),
                                       type='button')
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
        mainSizer.Add(buttonSizer, 0, wx.EXPAND | wx.TOP, 10)

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
                item = wx.Button(self.mainPanel, label=label)
            else:
                item = BlockWindow(self.mainPanel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items
    def on_new_frame(self, event,frame_type):
        if frame_type is None or len(frame_type)==0: # empty string:
            print('new frame not specified in button!! ')
            return
        elif frame_type == 'create new project':
            frame = NewProjectFrame(self.GetParent())
        elif frame_type == 'add new videos':
            frame = ExtractFrames(self.GetParent())
        elif frame_type == 'extract frames':
            frame = ExtractFrames(self.GetParent())
        else:
            return
        frame.Show()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super(MainPanel, self).__init__(parent)


# Object app
class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(parent=None, title='Quick DLC interface')
        self.frame.Show()
        return True

if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()




