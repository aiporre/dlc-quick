import os
from pathlib import Path

import wx

import deeplabcut.utils
from gui.rat_choice_list import RatChoice
from gui.utils import parse_yaml
from gui.utils.parse_yaml import extractTrainingIndexShuffle
from gui.utils.snapshot_index import find_analyzed_data_generic
from main import MainPanel, parser_yaml


class RefineTracklets(wx.Frame):
    def __init__(self, parent, title='Refine', config=None, videos=[], shuffle='', track_method=None):
        assert len(videos)>0, 'No videos selected, please input which videos you want to analyze. Check videos_path and video type, or add videos to your video list'
        assert len(shuffle), "No shuffle selection as input, please check the configuration in the analyze_videos window"
        assert isinstance(track_method, str) and track_method in ['skeleton', 'box', 'ellipse'], f"Input track_method {track_method}must be an string in box, elipse or skeleton"
        super(RefineTracklets, self).__init__(parent, title=title, size=(640, 500))

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
        videoTypeLbl = wx.StaticText(self.panel, -1, "Video type:")
        self.videoType = wx.TextCtrl(self.panel, -1, "avi", style= wx.TE_PROCESS_ENTER)
        self.videoType.Bind(wx.EVT_TEXT_ENTER, self.onChangeVideoType)

        self.running_on_dir =  not isinstance(videos, list) and os.path.isdir(videos)
        self.video_path = videos if self.running_on_dir else None
        if self.running_on_dir:
            self.videos = deeplabcut.utils.GetVideoList("all", self.video_path,
                                                        self.videoType.GetValue())
            self.videos = list(filter(lambda x: "_full." not in x and "_labeled."  not in x, self.videos))
            self.videos = list(map(lambda x: os.path.join(self.video_path, x),self.videos))
        else:
            self.videos = videos

        videosChoiceLbl =  wx.StaticText(self.panel, -1, "Select video to process:")
        self.videosChoice = RatChoice(self.panel, -1, choices=[Path(v).name for v in self.videos])

        self.makeTracksInAllVideos = wx.CheckBox(self.panel, -1, "Create tracks all files:")
        self.makeTracksInAllVideos.SetValue(False)

        numberOfTracksLbl = wx.StaticText(self.panel, -1, "Number of track (individuals in video):")
        self.numberOfTracks = wx.TextCtrl(self.panel, -1, "8")
        self.numberOfTracks.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.numberOfTracks))

        # enables number of tracks which creates dummies ind1 and so on...(this has problems creating labeled_videos)
        def enable_number_of_tracks(event):
            self.numberOfTracks.Enable(self.enableNumberOfTracks.GetValue())
        self.enableNumberOfTracks = wx.CheckBox(self.panel, -1, "Enable number of tracks input")
        self.enableNumberOfTracks.SetValue(True)
        self.enableNumberOfTracks.Bind(wx.EVT_CHECKBOX, enable_number_of_tracks)

        minSwapHighlightLbl = wx.StaticText(self.panel, -1, "Min swap length to hightlight:")
        self.minSwapHighlight = wx.TextCtrl(self.panel, -1, "2")
        self.minSwapHighlight.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.minSwapHighlight))

        maxGapLbl = wx.StaticText(self.panel, -1, "Max gap size of missing to fill:")
        self.maxGap = wx.TextCtrl(self.panel, -1, "5")
        self.maxGap.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.maxGap))

        trailLengthLbl = wx.StaticText(self.panel, -1, "Trail length (gui visual):")
        self.trailLength = wx.TextCtrl(self.panel, -1, "25")
        self.trailLength.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.trailLength))

        windowLengthLbl = wx.StaticText(self.panel, -1, "window length:")
        self.windowLength = wx.TextCtrl(self.panel, -1, "5")
        self.windowLength.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.windowLength))

        saveAsCSVLbl = wx.StaticText(self.panel, -1, "Save as CSV:")
        self.saveAsCSV = wx.CheckBox(self.panel, -1, "")
        self.saveAsCSV.SetValue(False)



        filterTypeLbl = wx.StaticText(self.panel, -1, "Filter type:")
        self.filterType = wx.Choice(self.panel, id=-1, choices=['arima', 'median'])
        self.filterType.SetSelection(1)

        destfolderLbl = wx.StaticText(self.panel, -1, "Dest Folder (csv and h5 files will created there):", size=wx.Size(self.WIDTHOFINPUTS, 25))
        self.destfolder = wx.DirPickerCtrl(self.panel, -1)
        self.destfolder.Bind(wx.EVT_DIRPICKER_CHANGED, self.onChangeDestFolder)

        buttonTracks = wx.Button(self.panel, label="Create tracks")
        buttonTracks.Bind(wx.EVT_BUTTON, self.onCreateTracks)

        buttonRefine = wx.Button(self.panel, label="Refine Tracks")
        buttonRefine.Bind(wx.EVT_BUTTON, self.onRefine)

        buttonFilter = wx.Button(self.panel, label="Filter Tracks")
        buttonFilter.Bind(wx.EVT_BUTTON, self.onFilter)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

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

        # ---line (videos choice section)
        inputSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        inputSizer.Add(videosChoiceLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.videosChoice, 0, wx.EXPAND | wx.ALL, 2)

        # ---line (track calcualtion section)
        inputSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)


        inputSizer.Add(self.makeTracksInAllVideos, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(numberOfTracksLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.numberOfTracks, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.enableNumberOfTracks, 0, wx.EXPAND | wx.ALL, 2)

        # ---line (refine tracks section)
        inputSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        inputSizer.Add(minSwapHighlightLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.minSwapHighlight, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(maxGapLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.maxGap, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(trailLengthLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.trailLength, 0, wx.EXPAND | wx.ALL, 2)

        #  -- line (?? section)
        inputSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        inputSizer.Add(filterTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.filterType, 0, wx.EXPAND | wx.ALL, 2)
        # inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(windowLengthLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.windowLength, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(saveAsCSVLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.saveAsCSV, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(videoTypeLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.videoType, 0, wx.EXPAND | wx.ALL, 2)
        #  -- line (button section)
        inputSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        buttonSizer.Add(buttonTracks, 0, wx.CENTER | wx.ALL, 2)
        buttonSizer.Add(buttonRefine, 0, wx.CENTER | wx.ALL, 2)
        buttonSizer.Add(buttonFilter, 0, wx.CENTER | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        # contentSizer.Add(inputSizer2, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups

        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        mainSizer.Add(buttonSizer, 0, wx.TOP | wx.BOTTOM | wx.CENTER, 20)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

        # update list of videos to choice
        self.update_status_videos_choice()

    def onRefine(self, event):
        print('Refine videos: ')
        # get video from videos list (files with fullpath)
        video = self.videos[self.videosChoice.GetSelection()]
        # destfolder is where the h5 or pickle tracked is searched
        destfolder = str(Path(video).parents[0]) if self.destfolder.GetPath() == '' else self.destfolder.GetPath()

        print("Input video: ", video)
        print("destfolder: ", destfolder)
        import deeplabcut as d
        cfg = parse_yaml(self.config)
        xx = cfg["TrainingFraction"][int(self.trainIndex)]
        scorer, _ = d.auxiliaryfunctions.GetScorerName(cfg, trainFraction=xx, shuffle=self.shuffle)
        # try to find the datafile corresponing to the selectiect trakcing method
        videoname =  Path(video).stem
        datafile, scorer, suffix = find_analyzed_data_generic(destfolder,
                                                              videoname,
                                                              scorer,
                                                              filtered=False,
                                                              track_method=self.track_method,
                                                              type_file='pickle')

        print("filepath = ", datafile, " \n scorer= ", scorer,"\n suffix = ", suffix)


        self.manager, self.viz = deeplabcut.refine_tracklets(
            self.config,
            datafile.replace("pickle", "h5"),
            video,
            min_swap_len=int(self.minSwapHighlight.GetValue()),
            trail_len=int(self.trailLength.GetValue()),
            max_gap=int(self.maxGap.GetValue()))

        self.update_status_videos_choice()

    def update_status_videos_choice(self):
        import deeplabcut as d
        cfg = parse_yaml(self.config)
        xx = cfg["TrainingFraction"][int(self.trainIndex)]
        scorer, _ = d.auxiliaryfunctions.GetScorerName(cfg, trainFraction=xx, shuffle=self.shuffle)
        # destfolder is where the h5 or pickle tracked is searched
        for i,v in enumerate(self.videos):
            destfolder = str(Path(v).parents[0]) if self.destfolder.GetPath() == '' else self.destfolder.GetPath()
            videoname = Path(v).stem
            try:
                d.auxiliaryfunctions.find_analyzed_data(destfolder, videoname, scorer, track_method=self.track_method)
                self.videosChoice.make_rat(i)
            except:
                print(f'video {videoname} not processed')
    def onFilter(self, event):
        import deeplabcut as d
        shuffle = self.shuffle
        trainingsetindex = self.trainIndex
        tracker = self.track_method
        window_length = int(self.windowLength.GetValue())
        if window_length % 2 != 1:
            raise ValueError("Window length should be odd.")

        video = self.videos[self.videosChoice.GetSelection()]
        d.filterpredictions(
            self.config,
            [video],
            shuffle=shuffle,
            trainingsetindex=trainingsetindex,
            filtertype=self.filterType.GetStringSelection(),
            track_method=tracker,
            windowlength=window_length,
            save_as_csv=True,
        )
    def onChangeDestFolder(self, event):
        if os.path.exists(self.destfolder.GetPath()) and os.path.isdir(self.destfolder.GetPath()):
            self.update_status_videos_choice()

    def onCreateTracks(self, event):
        destfolder = None if self.destfolder.GetPath() == '' else self.destfolder.GetPath()
        n_tracks = int(self.numberOfTracks.GetValue()) if self.enableNumberOfTracks.GetValue() else None
        import deeplabcut as d
        videos_to_stitch = []
        if self.running_on_dir and self.makeTracksInAllVideos.GetValue():
            print('creating tracks from the video in sht epath:  ', self.video_path)
            videos_to_stitch = self.videos
        elif self.makeTracksInAllVideos.GetValue():
            print('creating tracks for videos : ', self.videos)
            videos_to_stitch = self.videos
        else:
            print('creating tracks for video ',  self.videosChoice.GetStringSelection())
            videos_to_stitch = [v for v in self.videos if self.videosChoice.GetStringSelection()[1:] in v]
        d.stitch_tracklets(self.config,
                           videos=videos_to_stitch,
                           shuffle=self.shuffle,
                           trainingsetindex=self.trainIndex,
                           videotype=self.videoType.GetValue(),
                           n_tracks=n_tracks,
                           track_method=self.track_method,
                           destfolder=destfolder)
        self.update_status_videos_choice()
    def onChangeVideoType(self, event):
        import deeplabcut as d
        print('changes video type:')
        if self.running_on_dir:
            videos = deeplabcut.utils.GetVideoList("all", self.video_path, self.videoType.GetValue())
            self.videos = list(filter( lambda x: "_full" not in x and "_labeled"  not in x, videos))
            self.videosChoice.SetItems([Path(v).name for v in self.videos])

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