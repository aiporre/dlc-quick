import glob
import os

import wx

from main import MainPanel, CWD, get_videos


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