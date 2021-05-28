import os
from pathlib import Path

import wx

from deeplabcut.gui.widgets import WidgetPanel, BaseFrame
from deeplabcut.utils import auxiliaryfunctions
from gui.dataset_generation import ContactDataset


class ContactModelGeneration(BaseFrame):
    def __init__(self, parent, CWD, title='Contact Model Generation', config=None):
        super(ContactModelGeneration, self).__init__(parent=parent, frame_title=title)

        self.panel = WidgetPanel(self)
        self.WIDTHOFINPUTS = 420
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Contact Model Generation")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # # Components definition:

        # 1. path picker to set the working directory
        targetVideosLbl = wx.StaticText(self.panel, -1, "Target videos path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # TODO: make default path find yaml in the current directory
        config_dlc = auxiliaryfunctions.read_config(self.config)
        self.targetVideos = wx.DirPickerCtrl(self.panel, -1)
        self.project_path = config_dlc['project_path']
        self.targetVideos.SetPath(os.path.join(self.project_path,'videos'))
        os.chdir(self.project_path)

        # 2. which input?
        listOrPathLbl = wx.StaticText(self.panel, -1, "Use list or path?")
        self.listOrPath = wx.Choice(self.panel, id=-1, choices=['target videos path', 'target videos list'])

        # 3. inputs to select model
        snapshotIndexLbl = wx.StaticText(self.panel, -1, "snapshot index:")
        self.snapshotIndex = wx.TextCtrl(self.panel, -1, "-1")
        snapshotIndex = self.snapshotIndex.GetSelection()
        self.snapshotIndex.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, snapshotIndex))

        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.TextCtrl(self.panel, -1, "1")
        shuffle = self.shuffle.GetSelection()
        self.shuffle.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, shuffle))

        # 4. format of video in path
        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type to search in videos path:")
        self.videoType = wx.TextCtrl(self.panel, -1, ".mp4")

        # 5. GPU configurations
        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices=['None'])  # +get_available_gpus()


        # 6. list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.panel, -1, "Target videos list:")
        self.videosList = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # datataset output path

        destfolderLbl = wx.StaticText(self.panel, -1, "Dataset Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)
        self.destfolder.SetPath(os.path.join(self.project_path,'training-datasets','iteration-'+ str(config_dlc['iteration'])))

        # # Button components..

        # buttons to add video
        bmp1 = wx.Image(os.path.join(CWD, "figures/iconplus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.panel, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image(os.path.join(CWD, "figures/iconMinus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonMinus = wx.BitmapButton(self.panel, -1, bmp2, pos=(10, 20))
        self.buttonMinus.Bind(wx.EVT_BUTTON, self.onRemoveVideo)

        # button to make manual corrections in the dataset
        correctionsButton = wx.Button(self.panel, label='Make Corrections')
        correctionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, ' make corrections'))

        # button to train contact model
        trainButton = wx.Button(self.panel, label='Train Model')
        trainButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'train model'))

        # button to make manual corrections in the dataset
        genDatasetButton = wx.Button(self.panel, label='Generate Dataset')
        genDatasetButton.Bind(wx.EVT_BUTTON, self.on_generate_dataset)

        # # Sizers definition
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
        line1.Add(snapshotIndexLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.snapshotIndex, 0, wx.EXPAND | wx.ALL, 2)
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
        buttonSizer.Add(genDatasetButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(correctionsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(trainButton, 0, wx.EXPAND | wx.ALL, 5)


        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(buttonSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # # Final adjustment
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or keycode == 8:
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value = edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and ('.' not in raw_value):
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()
    def onAddVideo(self, event):
        dialog = wx.FileDialog(None, "Choose input directory", self.project_path,
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

    def on_generate_dataset(self, event):
        print('Generate dataset....')


    def on_new_frame(self, event, frame_type):
        print('open new window: ', frame_type)
        if frame_type is None or len(frame_type) == 0:  # empty string:
            print('new frame not specified in button!! ')
            return
        # elif frame_type == 'make corrections':
        #     frame = FilterPredictions(self.GetParent(), config=self.config)
        # elif frame_type == 'train model':
        #     if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
        #         videos = self.targetVideos.GetPath()
        #     else:  # 'target videos list'
        #         videos = get_videos(self.videosList)
        #     print('Videos: ', videos)
        #     frame = PlotPredictions(self.GetParent(), config=self.config, videos=videos)
        # elif frame_type == 'label predictions':
        #     if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
        #         videos = self.targetVideos.GetPath()
        #     else:  # 'target videos list'
        #         videos = get_videos(self.videosList)
        #     print('Videos: ', videos)
        #     destfolder = None if len(self.destfolder.GetPath()) == 0 else self.destfolder.GetPath()
        #     frame = LabelPredictions(self.GetParent(), config=self.config, videos=videos, destfolder=destfolder)
        # elif frame_type == 'extract outliers':
        #     count = self.videosList.GetItemCount()
        #     if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
        #         videos = [str(self.targetVideos.GetPath())]
        #     else:  # 'target videos list'
        #         videos = get_videos(self.videosList)
        #     print('Videos: ', videos, type(videos), type(videos[0]))
        #     frame = ExtractOutliers(self.GetParent(), config=self.config, videos=videos)
        else:
            return
        frame.Show()


def show(config, startpath='.'):
    app = wx.App()
    frame = ContactModelGeneration(None, startpath, config=config).Show()
    app.MainLoop()



if __name__ == '__main__':
    config = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config, startpath)








