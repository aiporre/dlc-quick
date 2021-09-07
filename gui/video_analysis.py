import os

import wx

from blockwindow import BlockWindow
from gui.refine import RefineTracklets
from gui.utils import parse_yaml
from gui.utils.colors import TerminalColors
from gui.utils.parse_yaml import extractTrainingIndexShuffle
from gui.utils.snapshot_index import get_snapshots
from main import MainPanel, parser_yaml, get_radiobutton_status, get_available_gpus, CWD, get_videos


class FilterPredictions(wx.Frame):
    def __init__(self, parent, title='filter predictions', config=None, videos=[], shuffle='', track_method=None):
        assert len(videos)>0, 'No videos selected, please input which videos you want to analyze. Check videos_path and video type, or add videos to your video list'
        assert len(shuffle), "No shuffle selection as input, please check the configuration in the analyze_videos window"
        super(FilterPredictions, self).__init__(parent, title=title, size=(640, 500))

        self.panel = MainPanel(self)
        self.config = config
        self.trainIndex, self.shuffle = extractTrainingIndexShuffle(self.config, shuffle)
        self.track_method = track_method
        self.WIDTHOFINPUTS = 400
        config = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Filter predictions")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # input test to set the working directory
        self.targetVideos = videos if isinstance(videos, list) else [videos]

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
        self.saveAsCSV = wx.CheckBox(self.panel, -1, "")
        self.saveAsCSV.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, "avi")

        filterTypeLbl = wx.StaticText(self.panel, -1, "Filter type:")
        self.filterType = wx.Choice(self.panel, id=-1, choices=['arima', 'median'])
        self.filterType.SetSelection(1)

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder (csv and h5 files will created there):", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        buttonFilter = wx.Button(self.panel, label="Filter")
        buttonFilter.Bind(wx.EVT_BUTTON, self.onFilter)

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
        print('Filtering video(s): ')
        filterType = self.filterType.GetString(self.filterType.GetCurrentSelection())
        destfolder = None if self.destfolder.GetPath() == '' else self.destfolder.GetPath()
        print("Input video: ", self.targetVideos)
        print('video_type: ', self.videoType.GetValue())
        print("destfolder: ", destfolder)
        import deeplabcut as d
        cfg = parse_yaml(self.config)
        if cfg.get("multianimalproject", False):
            d.filterpredictions(self.config, self.targetVideos, videotype=self.videoType.GetValue(),
                                shuffle=self.shuffle, trainingsetindex=self.trainIndex, filtertype=filterType,
                                windowlength=int(self.windowlength.GetValue()), p_bound=float(self.p_bound.GetValue()),
                                ARdegree=int(self.ARdegree.GetValue()), MAdegree=int(self.MAdegree.GetValue()),
                                alpha=float(self.alpha.GetValue()), save_as_csv=self.saveAsCSV.GetValue(),
                                destfolder=destfolder, track_method=self.track_method)
        else:
            d.filterpredictions(self.config, self.targetVideos, videotype=self.videoType.GetValue(),
                                shuffle=self.shuffle, trainingsetindex=self.trainIndex, filtertype=filterType,
                                windowlength=int(self.windowlength.GetValue()), p_bound=float(self.p_bound.GetValue()),
                                ARdegree=int(self.ARdegree.GetValue()), MAdegree=int(self.MAdegree.GetValue()),
                                alpha=float(self.alpha.GetValue()), save_as_csv=self.saveAsCSV.GetValue(),
                                destfolder=destfolder)
        self.Close()

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
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and '.' not in raw_value:
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()


class PlotPredictions(wx.Frame):
    def __init__(self, parent, title='Plot predictions', config=None, videos=[], shuffle='', track_method=None):
        super(PlotPredictions, self).__init__(parent, title=title, size=(640, 500))
        assert len(shuffle)>0 , 'Shuffle selection is not defined as input, check your configuration in the analyze_videos window.'
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        self.videos = videos if isinstance(videos, list) else [videos]
        self.trainIndex, self.shuffle = extractTrainingIndexShuffle(self.config, shuffle)
        self.track_method = track_method
        cfg = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Plot predictions")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        filteredLbl = wx.StaticText(self.panel, -1, "Filtered:")
        self.filtered = wx.CheckBox(self.panel, -1, "")
        self.filtered.SetValue(False)

        showFiguresLbl = wx.StaticText(self.panel, -1, "Show figures:")
        self.showFigures = wx.CheckBox(self.panel, -1, "")
        self.showFigures.SetValue(False)
        if cfg.get('multianimalproject', False):
            self.showFigures.Disable()

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, ".avi")

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
        destfolder = None if self.destfolder.GetPath() == '' else self.destfolder.GetPath()
        print("destfolder: ", destfolder)
        import deeplabcut as d
        if self.track_method is None:

            d.plot_trajectories(self.config, videos=self.videos, videotype=self.videoType.GetValue(), shuffle=self.shuffle,
                                trainingsetindex=self.trainIndex, filtered=self.filtered.GetValue(),
                                showfigures=self.showFigures.GetValue(),
                                destfolder=destfolder)
        else:
            d.plot_trajectories(self.config, videos=self.videos, videotype=self.videoType.GetValue(),
                                shuffle=self.shuffle,
                                trainingsetindex=self.trainIndex, filtered=self.filtered.GetValue(),
                                showfigures=False,
                                destfolder=destfolder, track_method=self.track_method)
        self.Close()

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
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and '.' not in raw_value:
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()


class LabelPredictions(wx.Frame):
    def __init__(self, parent, title='Label predictions', config=None, videos=[], destfolder=None, shuffle=""):
        super(LabelPredictions, self).__init__(parent, title=title, size=(640, 500))
        assert len(shuffle)>0 , 'Shuffle selection is not defined as input, check your configuration in the analyze_videos window.'
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 600
        self.videos = videos if isinstance(videos, list) else [videos]
        self.trainIndex, self.shuffle = extractTrainingIndexShuffle(self.config, shuffle)
        self.destfolderParent = destfolder
        config = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Label predictions")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # filtered
        filteredLbl = wx.StaticText(self.panel, -1, "Filtered:")
        self.filtered = wx.CheckBox(self.panel, -1, "")
        self.filtered.SetValue(False)

        # save frames
        saveFramesLbl = wx.StaticText(self.panel, -1, "Save frames:")
        self.saveFrames = wx.CheckBox(self.panel, -1, "")
        self.saveFrames.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, "avi")

        cfg = parse_yaml(self.config)
        if cfg.get('multianimalproject', False):
            bodyPartsBox, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                          itemlabels=config['multianimalbodyparts'] + ['All'], type='checkBox')
        else:
            bodyPartsBox, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                      itemlabels=config['bodyparts'] + ['All'], type='checkBox')
        self.radioButtons = items
        self.radioButtonCurrentStatus = {}
        items['All'].SetValue(True)
        items['All'].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, 'All'))
        for k in items.keys():
            if not k == 'All':
                items[k].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, ''))
        # codec
        codecLbl = wx.StaticText(self.panel, -1, "Codec:")
        self.codec = wx.TextCtrl(self.panel, -1, "mp4v")

        # Output Frame Rate
        outputFrameRateLbl = wx.StaticText(self.panel, -1, "Output Frame Rate:")
        self.outputFrameRate = wx.TextCtrl(self.panel, -1, "0")
        self.outputFrameRate.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.outputFrameRate))

        # draw skeleton
        drawSkeletonLbl = wx.StaticText(self.panel, -1, "Draw skeleton:")
        self.drawSkeleton = wx.CheckBox(self.panel, -1, "")
        self.drawSkeleton.SetValue(False)

        # destination folder
        parent = '' if self.destfolderParent is None else self.destfolderParent
        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1, path=parent)
        # trail points only single-animal

        trailPointsLbl = wx.StaticText(self.panel, -1, "trail points to plot:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.trailPoints = wx.TextCtrl(self.panel, -1, "5")
        self.trailPoints.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.outputFrameRate))


        # color by (ma-projects)
        colorByLbl = wx.StaticText(self.panel, -1, "color code by:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.colorBy = wx.Choice(self.panel, -1, choices=['label individuals', 'label bodyparts'])
        self.colorBy.Disable() if not cfg.get('multianimalproject', False) else None
        self.colorBy.SetSelection(0)
        # track method
        trackMethodLbl = wx.StaticText(self.panel, -1, "track method:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.trackMethod = wx.Choice(self.panel, id=-1, choices=['skeleton', 'box', 'ellipse'])
        self.trackMethod.SetSelection(2)
        self.trackMethod.Disable() if not cfg.get('multianimalproject', False) else None

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
        inputSizer3 = wx.BoxSizer(wx.VERTICAL)
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
        inputSizer3.Add(trailPointsLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.trailPoints, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(colorByLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.colorBy, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(trackMethodLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer3.Add(self.trackMethod, 0, wx.EXPAND | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer3, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups

        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 1)
        mainSizer.Add(labelButton, 0, wx.ALL | wx.CENTER, 10)

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
        if len(self.destfolder.GetPath()) == 0:
            destfolder = self.destfolderParent
        else:
            destfolder = self.destfolder.GetPath()

        print('VIDEOS to be labeled: ', self.videos)
        if len(self.videos) == 0:
            print('No videos to label, please choose a folder or create a list of videos in \'analyze videos\' window')
            return

        cfg = parse_yaml(self.config)
        if cfg.get('multianimalproject', False):
            color_by = 'individual' if  self.colorBy.GetStringSelection() == 'label individuals' else 'bodypart'
            d.create_labeled_video(self.config,
                                   videos=self.videos,
                                   videotype=self.videoType.GetValue(),
                                   displayedbodyparts=bodyParts,
                                   shuffle=self.shuffle,
                                   trainingsetindex=self.trainIndex,
                                   filtered=self.filtered.GetValue(),
                                   save_frames=self.saveFrames.GetValue(),
                                   codec=self.codec.GetValue(),
                                   outputframerate=outputframerate,
                                   draw_skeleton=self.drawSkeleton.GetValue(),
                                   destfolder=destfolder,
                                   color_by=color_by,
                                   track_method=self.trackMethod.GetStringSelection(),
                                   trailpoints=int(self.trailPoints.GetValue()),
                                   )
        else:
            d.create_labeled_video(self.config,
                                   videos=self.videos,
                                   videotype=self.videoType.GetValue(),
                                   displayedbodyparts=bodyParts,
                                   shuffle=self.shuffle,
                                   trainingsetindex=self.trainIndex,
                                   filtered=self.filtered.GetValue(),
                                   save_frames=self.saveFrames.GetValue(),
                                   codec=self.codec.GetValue(),
                                   outputframerate=outputframerate,
                                   draw_skeleton=self.drawSkeleton.GetValue(),
                                   destfolder=destfolder,
                                   trailpoints=int(self.trailPoints.GetValue()))
        self.Close()

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
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and '.' not in raw_value:
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()

    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150, 25), type='block'):
        box = wx.StaticBox(self.panel, -1, boxlabel)

        h_sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        items = {}
        print(itemlabels)
        for i in range(len(itemlabels) // 10 + 1):
            # for groups of 10 items create a sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            for j in range(10):
                if 10 * i + j == len(itemlabels):
                    break
                label = itemlabels[10 * i + j]
                if type == 'block':
                    item = BlockWindow(self.panel, label=label, size=size)
                elif type == 'button':
                    item = wx.Button(self.panel, label=label)
                elif type == 'radioButton':
                    item = wx.RadioButton(self.panel, label=label, size=size)
                elif type == 'checkBox':
                    item = wx.CheckBox(self.panel, -1, label=label)
                else:
                    item = BlockWindow(self.panel, label=label, size=size)
                items[label] = item
                sizer.Add(item, 0, wx.EXPAND, 2)
            h_sizer.Add(sizer, 0, wx.EXPAND, 2)
        return h_sizer, items

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)


class ExtractOutliers(wx.Frame):
    def __init__(self, parent, title='Extract outliers', config=None, videos=[], shuffle=""):
        super(ExtractOutliers, self).__init__(parent, title=title, size=(640, 500))
        assert len(shuffle)>0 , 'Shuffle selection is not defined as input, check your configuration in the analyze_videos window.'

        self.panel = MainPanel(self)
        self.config = config
        self.videos = videos if isinstance(videos, list) else [videos]
        self.trainIndex, self.shuffle = extractTrainingIndexShuffle(self.config, shuffle)

        self.WIDTHOFINPUTS = 600
        cfg = parser_yaml(self.config)
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Extract outliers")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # shuffle
        videotypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videotype = wx.TextCtrl(self.panel, -1, "avi")

        # track method
        trackMethodLbl = wx.StaticText(self.panel, -1, "track method:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.trackMethod = wx.Choice(self.panel, id=-1, choices=['skeleton', 'box', 'ellipse'])
        self.trackMethod.SetSelection(2)
        self.trackMethod.Disable() if not cfg.get('multianimalproject', False) else None

        #
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
        self.clusterColor = wx.CheckBox(self.panel, -1, "")
        self.clusterColor.SetValue(False)

        # Cluster resize width
        clusterResizeWidthLbl = wx.StaticText(self.panel, -1, "Cluster resize width:")
        self.clusterResizeWidth = wx.TextCtrl(self.panel, -1, "30")
        self.clusterResizeWidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.clusterResizeWidth))

        # automatic
        automaticLbl = wx.StaticText(self.panel, -1, "Automatic:")
        self.automatic = wx.CheckBox(self.panel, -1, "")
        self.automatic.SetValue(False)

        # Save Labeled
        saveLabeledLbl = wx.StaticText(self.panel, -1, "Save laveled:")
        self.saveLabeled = wx.CheckBox(self.panel, -1, "")
        self.saveLabeled.SetValue(True)

        if cfg.get('multianimalproject', False):
            bodyPartsBox, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                          itemlabels=cfg['multianimalbodyparts'] + ['All'],
                                                          type='checkBox')
        else:
            bodyPartsBox, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                          itemlabels=cfg['bodyparts'] + ['All'], type='checkBox')

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
        inputSizer.Add(trackMethodLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.trackMethod, 0, wx.EXPAND | wx.ALL, 2)
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
        mainSizer.Add(extractOutliersButton, 0, wx.ALL | wx.CENTER, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def OnExtractOutliers(self, event):
        import deeplabcut as d
        outlieralg = self.outlierAlg.GetString(self.outlierAlg.GetCurrentSelection())
        extractionAlg = self.extractionAlg.GetString(self.extractionAlg.GetCurrentSelection())
        bodyParts = get_radiobutton_status(self.radioButtons)
        print('Videos: ', self.videos, type(self.videos), type(self.videos[0]))
        cfg = parser_yaml(self.config)

        track_method = self.trackMethod.GetStringSelection() if cfg.get('multianimalproject', False) else ""
        d.extract_outlier_frames(config=self.config, videos=self.videos, videotype=self.videotype.GetValue(),
                                 shuffle=self.shuffle,
                                 trainingsetindex=self.trainIndex,
                                 outlieralgorithm=outlieralg, comparisonbodyparts=bodyParts,
                                 epsilon=float(self.epsilon.GetValue()),
                                 p_bound=float(self.p_bound.GetValue()), ARdegree=int(self.ARdegree.GetValue()),
                                 MAdegree=int(self.MAdegree.GetValue()), alpha=float(self.alpha.GetValue()),
                                 extractionalgorithm=extractionAlg,
                                 automatic=self.automatic.GetValue(), savelabeled=self.saveLabeled.GetValue(),
                                 track_method=track_method)
        self.Close()

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
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and '.' not in raw_value:
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()

    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150, 25), type='block'):
        box = wx.StaticBox(self.panel, -1, boxlabel)

        h_sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        items = {}
        print(itemlabels)
        for i in range(len(itemlabels) // 10 + 1):
            # for groups of 10 items create a sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            for j in range(10):
                if 10 * i + j == len(itemlabels):
                    break
                label = itemlabels[10 * i + j]
                if type == 'block':
                    item = BlockWindow(self.panel, label=label, size=size)
                elif type == 'button':
                    item = wx.Button(self.panel, label=label)
                elif type == 'radioButton':
                    item = wx.RadioButton(self.panel, label=label, size=size)
                elif type == 'checkBox':
                    item = wx.CheckBox(self.panel, -1, label=label)
                else:
                    item = BlockWindow(self.panel, label=label, size=size)
                items[label] = item
                sizer.Add(item, 0, wx.EXPAND, 2)
            h_sizer.Add(sizer, 0, wx.EXPAND, 2)
        return h_sizer, items

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)


class AnalyzeVideos(wx.Frame):
    def __init__(self, parent, title='Analyze videos', config=None):
        super(AnalyzeVideos, self).__init__(parent, title=title, size=(640, 500))
        self.parent = parent
        self.panel = MainPanel(self)
        self.config = config
        self.WIDTHOFINPUTS = 400
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Analyze videos")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # input test to set the working directory
        targetVideosLbl = wx.StaticText(self.panel, -1, "Target videos path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        # TODO: make default path find yaml in the current directory
        config_dlc = parser_yaml(self.config)
        self.targetVideos = wx.DirPickerCtrl(self.panel, -1)
        self.project_path = config_dlc['project_path']
        self.targetVideos.SetPath(os.path.join(self.project_path,'videos'))
        os.chdir(self.project_path)

        listOrPathLbl = wx.StaticText(self.panel, -1, "Use list or path?")
        self.listOrPath = wx.Choice(self.panel, id=-1, choices=['target videos path', 'target videos list'])
        self.listOrPath.SetSelection(1)

        shuffleLbl = wx.StaticText(self.panel, -1, "Shuffle:")
        self.shuffle = wx.Choice(self.panel, -1, choices=self.find_shuffles())
        self.shuffle.SetSelection(0)
        self.shuffle.Bind(wx.EVT_CHOICE, self.onSelectShuffleNumber)

        snapshotLbl = wx.StaticText(self.panel, -1, "Snapshot:")
        self.snapshots = self.find_snapshots()
        self.snapshot = wx.Choice(self.panel, -1, choices=self.snapshots)
        self.snapshot.SetSelection(len(self.snapshots) - 1)

        saveAsCSVLbl = wx.StaticText(self.panel, -1, "Save as CSV:")
        self.saveAsCSV = wx.CheckBox(self.panel, -1, "")
        self.saveAsCSV.SetValue(False)

        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, ".avi")

        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices=['None']  + get_available_gpus())
        self.gpusAvailable.SetSelection(0)

        trackMethodLbl = wx.StaticText(self.panel, -1, "track method")
        self.trackMethod = wx.Choice(self.panel, id=-1, choices=['skeleton', 'box', 'ellipse'] )
        self.trackMethod.SetSelection(2)
        cfg = parse_yaml(self.config)
        if not cfg.get('multianimalproject', False):
            trackMethodLbl.Hide()
            self.trackMethod.Hide()

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)

        # list of videos to be processed.
        self.listIndex = 0
        videosListLbl = wx.StaticText(self.panel, -1, "Target videos list:")
        self.videosList = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
        self.videosList.InsertColumn(0, "file name", format=wx.LIST_FORMAT_CENTRE, width=-1)
        self.videosList.InsertColumn(1, "path", format=wx.LIST_FORMAT_CENTRE, width=self.WIDTHOFINPUTS)

        # buttons to add video
        bmp1 = wx.Image(os.path.join(CWD, "figures/iconplus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonPlus = wx.BitmapButton(self.panel, -1, bmp1, pos=(10, 20))
        self.buttonPlus.Bind(wx.EVT_BUTTON, self.onAddVideo)

        # button to remove video
        bmp2 = wx.Image(os.path.join(CWD, "figures/iconMinus.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        self.buttonMinus = wx.BitmapButton(self.panel, -1, bmp2, pos=(10, 20))
        self.buttonMinus.Bind(wx.EVT_BUTTON, self.onRemoveVideo)

        # button to filter predictions
        filterPredictionsButton = wx.Button(self.panel, label='Filter Predictions')
        filterPredictionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'filter predictions'))

        # button to refine tracklets
        refineTrackletsButton = wx.Button(self.panel, label='Refine Tracklets')
        refineTrackletsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'refine tracklets'))
        if not cfg.get('multianimalproject', False):
             refineTrackletsButton.Disable()

        # button to pose detection assesment
        poseAssesmentButton = wx.Button(self.panel, label='Video Assesment')
        poseAssesmentButton.Bind(wx.EVT_BUTTON, self.on_video_assesment)
        if not cfg.get('multianimalproject', False):
             poseAssesmentButton.Disable()

        plotPredictionsButton = wx.Button(self.panel, label='Plot Predictions')
        plotPredictionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'plot predictions'))
        # if cfg.get('multianimalproject', False):
        #     plotPredictionsButton.Disable()

        labelPredictionsButton = wx.Button(self.panel, label='Label Predictions')
        labelPredictionsButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'label predictions'))

        extractOutliersButton = wx.Button(self.panel, label='Extract Outliers')
        extractOutliersButton.Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'extract outliers'))

        # button to create project
        buttonAnalyze = wx.Button(self.panel, label="Analyze")
        buttonAnalyze.Bind(wx.EVT_BUTTON, self.onAnalyzeVideos)

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
        targetVideosSizer = wx.BoxSizer(wx.VERTICAL)


        targetVideosSizer.Add(targetVideosLbl, 0, wx.EXPAND, 2)
        targetVideosSizer.Add(self.targetVideos, 0, wx.EXPAND, 2)
        targetVideosSizer.Add(videoTypeLbl, 0, wx.LEFT | wx.ALL, 2)
        targetVideosSizer.Add(self.videoType, 0, wx.LEFT | wx.ALL, 2)

        inputSizer.Add(targetVideosSizer, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(videosListLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.videosList, 0, wx.EXPAND, 2)

        line1 = wx.BoxSizer(wx.HORIZONTAL)
        line1.Add(shuffleLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.shuffle, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(snapshotLbl, 0, wx.EXPAND | wx.ALL, 2)
        line1.Add(self.snapshot, 0, wx.EXPAND | wx.ALL, 2)

        line2 = wx.BoxSizer(wx.HORIZONTAL)

        line2.Add(saveAsCSVLbl, 0, wx.EXPAND | wx.ALL, 2)
        line2.Add(self.saveAsCSV, 0, wx.EXPAND | wx.ALL, 2)
        line2.Add(gpusAvailableLbl, 0, wx.EXPAND | wx.ALL, 2)
        line2.Add(self.gpusAvailable, 0, wx.EXPAND | wx.ALL, 2)
        line2.Add(trackMethodLbl, 0, wx.EXPAND | wx.ALL, 2)
        line2.Add(self.trackMethod, 0, wx.EXPAND | wx.ALL, 2)

        inputSizer.Add(line1, 0, wx.EXPAND, 2)
        inputSizer.Add(line2, 0, wx.EXPAND, 2)

        inputSizer.Add(destfolderLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.destfolder, 0, wx.EXPAND, 2)
        inputSizer.Add(listOrPathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.listOrPath, 0, wx.EXPAND, 2)

        # buttons (copy videos, add new video, remove video and run create project)
        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer.Add(self.buttonPlus, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(self.buttonMinus, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(buttonAnalyze, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(poseAssesmentButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(refineTrackletsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(filterPredictionsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(plotPredictionsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(labelPredictionsButton, 0, wx.EXPAND | wx.ALL, 5)
        buttonSizer.Add(extractOutliersButton, 0, wx.EXPAND | wx.ALL, 5)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(buttonSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)


    def find_shuffles(self):
        cfg = parse_yaml(self.config)
        iteration = 'iteration-' + str(cfg['iteration'])
        files = [f for f in os.listdir(os.path.join(cfg['project_path'], 'dlc-models', iteration)) if not f.startswith('.') and 'contact-model' not in f and 'whisking-model' not in f and 'motion-model' not in f and 'osc-model' not in f]
        print('files: ', files)
        return files

    def find_snapshots(self):
        training_index, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffle.GetStringSelection())
        return get_snapshots(self.config, shuffle_number, training_index).tolist() + ['latest', 'config.yaml']

    def onSelectShuffleNumber(self, event):
        self.snapshots = self.find_snapshots()
        self.snapshot.SetItems(self.snapshots)
        self.snapshot.SetSelection(len(self.snapshots)-1)

    def on_video_assesment(self, event):
        if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
            videos = [self.targetVideos.GetPath()]
        else:  # 'target videos list'
            videos = get_videos(self.videosList)
        if self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()) == 'None':
            gputouse = None
        else:
            gputouse = int(self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()))
        destfolder = self.destfolder.GetPath()
        if destfolder == '':
            destfolder = None
        track_method = self.trackMethod.GetStringSelection()
        if track_method == "ellipse":
            method = "el"
        elif track_method == "box":
            method = "bx"
        else:
            method = "sk"
        import deeplabcut as d
        print("Videos predictions analyzed for pose destection assesment: ", videos)
        trainindex, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffle.GetStringSelection())
        try:
            d.create_video_with_all_detections(
                self.config,
                videos,
                videotype=self.videoType.GetValue(),
                shuffle=shuffle_number,
                trainingsetindex=trainindex,
                destfolder=destfolder
            )
            # FIXME: there is a bug in DLC error reshape(-1,3) tracklets have now 4 values instead, duno why
            # cfg = parser_yaml(self.config)
            # trainFraction = cfg["TrainingFraction"][int(trainindex)]
            # scorer, _ = d.auxiliaryfunctions.GetScorerName(cfg, shuffle_number, trainFraction)
            #
            # for video in videos:
            #     videofolder = os.path.splitext(video)[0]
            #     video_name, ext = os.path.splitext(os.path.split(video)[1])
            #     outputname = f"{video_name + scorer}_{method}.mp4"
            #     if destfolder is None:
            #         track_pickle = os.path.join(videofolder + scorer + f"_{method}.pickle")
            #     else:
            #         d.auxiliaryfunctions.attempttomakefolder(destfolder)
            #         track_pickle = os.path.join(destfolder, str(Path(video).stem) + scorer + f"_{method}.pickle")
            #     d.utils.create_video_from_pickled_tracks(video, track_pickle, destfolder=destfolder, output_name=outputname, pcutoff=float(cfg['pcutoff']))
            wx.MessageDialog(self.parent, 'Check the videos ".._full.mp4" and make a decision: \n \t 1. Pose detection is fine, then continue with the refinement of animal tracking \n \t 2. Pose detection not so good. Relabel/Extract new frames/Extact outliers and retrain your model, maybe use other model.', 'Test', wx.OK | wx.ICON_INFORMATION).ShowModal()
        except FileNotFoundError as e:
            print(f"{TerminalColors.FAIL}Error: {e} {TerminalColors.ENDC}")
            print(f"{TerminalColors.WARNING}Maybe you need to run analyze_videos first. {TerminalColors.ENDC}")

    def onAnalyzeVideos(self, event):
        if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
            videos = [self.targetVideos.GetPath()]
        else:  # 'target videos list'
            videos = get_videos(self.videosList)
        if self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()) == 'None':
            gputouse = None
        else:
            gputouse = int(self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()))
        destfolder = self.destfolder.GetPath()
        if destfolder == '':
            destfolder = None

        import deeplabcut as d
        print("Videos to analyze: ", videos)
        trainindex, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffle.GetStringSelection())
        if self.snapshot.GetStringSelection() != "config.yaml":
            snapshotindex = self.snapshot.GetSelection()
            if self.snapshot.GetStringSelection() == 'latest':
                snapshotindex = -1
            d.auxiliaryfunctions.edit_config(self.config, {'snapshotindex': snapshotindex})

        try:
            d.analyze_videos(self.config, videos=videos, videotype=self.videoType.GetValue(),
                             shuffle=shuffle_number, trainingsetindex=trainindex, gputouse=gputouse, save_as_csv=self.saveAsCSV.GetValue(),
                             destfolder=destfolder)
        except IndexError as e:
            print(e)
            print('Snapshot index is not correct. Did you train your network? Select a correct Snapshot Index in the config.yaml or in the evaluation window in the main menu.')
        cfg = parse_yaml(self.config)
        if cfg.get('multianimalproject', False):
            identity_only = cfg.get('identity', False)
            d.convert_detections2tracklets(self.config, videos=videos, videotype=self.videoType.GetValue(),
                                           shuffle=shuffle_number, trainingsetindex=trainindex,
                                           track_method=self.trackMethod.GetStringSelection(),
                                           overwrite=True, identity_only=identity_only, destfolder=destfolder)

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

    def on_new_frame(self, event, frame_type):
        if frame_type is None or len(frame_type) == 0:  # empty string:
            print('new frame not specified in button!! ')
            return
        elif frame_type == 'refine tracklets':
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            frame = RefineTracklets(self.GetParent(), config=self.config, videos=videos, shuffle=self.shuffle.GetStringSelection(), track_method=self.trackMethod.GetStringSelection())
        elif frame_type == 'filter predictions':
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            cfg = parse_yaml(self.config)
            if cfg.get('multianimalproject', False):
                track_method = self.trackMethod.GetStringSelection()
            else:
                track_method = None
            frame = FilterPredictions(self.GetParent(), config=self.config, videos=videos, shuffle=self.shuffle.GetStringSelection(), track_method=track_method)
        elif frame_type == 'plot predictions':
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            cfg = parse_yaml(self.config)
            if cfg.get('multianimalproject', False):
                track_method = self.trackMethod.GetStringSelection()
            else:
                track_method = None
            frame = PlotPredictions(self.GetParent(), config=self.config, videos=videos, shuffle=self.shuffle.GetStringSelection(), track_method=track_method)
        elif frame_type == 'label predictions':
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = self.targetVideos.GetPath()
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos)
            destfolder = None if len(self.destfolder.GetPath()) == 0 else self.destfolder.GetPath()
            frame = LabelPredictions(self.GetParent(), config=self.config, videos=videos, destfolder=destfolder, shuffle=self.shuffle.GetStringSelection())
        elif frame_type == 'extract outliers':
            count = self.videosList.GetItemCount()
            if self.listOrPath.GetString(self.listOrPath.GetCurrentSelection()) == 'target videos path':
                videos = [str(self.targetVideos.GetPath())]
            else:  # 'target videos list'
                videos = get_videos(self.videosList)
            print('Videos: ', videos, type(videos), type(videos[0]))
            frame = ExtractOutliers(self.GetParent(), config=self.config, videos=videos,shuffle=self.shuffle.GetStringSelection())
        else:
            return
        frame.Show()