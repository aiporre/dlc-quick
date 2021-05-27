import os
from pathlib import Path

import wx

from deeplabcut.gui.widgets import WidgetPanel, BasePanel, BaseFrame
from deeplabcut.utils import auxiliaryfunctions


class DetectWhiskers(BaseFrame):
    def __init__(self, parent, title='Detect Whiskers', config=None):
        super(DetectWhiskers, self).__init__(parent=parent, frame_title=title)
        self.panel = WidgetPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Detect whiskers ")
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
        recalculateLbl = wx.StaticText(self.panel, -1, "Force recalculate:")
        self.recalculate = wx.CheckBox(self.panel, -1, "");
        self.recalculate.SetValue(False)

        # check box to select automatic or manual selection
        outputPahtLbl = wx.StaticText(self.panel, -1, "Output path:", size=wx.Size(self.gui_size[0], 25))
        self.outputPath = wx.DirPickerCtrl(self.panel, -1)
        self.outputPath.SetPath(os.path.join(os.path.dirname(self.config),'whisker-detection'))

        # check box to mode of frames extraction (uniform or kmeans)
        selectionAlgoLbl = wx.StaticText(self.panel, -1, "Extraction algorithm:")
        self.selectionAlgo = wx.Choice(self.panel, id=-1, choices=['Whiski'])

        # button to create project
        buttonExtract = wx.Button(self.panel, label="Extract")
        buttonExtract.Bind(wx.EVT_BUTTON, self.onExtractButton)

        # create the main sizer that contains the context and input sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        inputSizer = wx.BoxSizer(wx.VERTICAL)

        # adding stuff to the inputsizer, i.e. buttons checkboxes.. etc.
        inputSizer.Add(recalculateLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.recalculate, 0, wx.EXPAND, 2)
        inputSizer.Add(selectionAlgoLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.selectionAlgo, 0, wx.EXPAND, 2)
        inputSizer.Add(outputPahtLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.outputPath, 0, wx.EXPAND, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        # contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonExtract, 0, wx.CENTER | wx.ALL, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onExtractButton(self, event):
        print('Extraction of the whiskers....')
        algo = self.selectionAlgo.GetString(self.selectionAlgo.GetCurrentSelection())

        print('importing whiskiwrap. ')
        import WhiskiWrap
        from multiprocessing import freeze_support
        from warnings import warn
        import shutil

        configDLC = auxiliaryfunctions.read_config(self.config)
        detectionsPath = self.outputPath.GetPath()
        if not os.path.exists(detectionsPath):
            warn('detectionsPath didn\'t exist creating output path ' + detectionsPath)
            os.mkdir(detectionsPath)

        print('video sets!! +++ > ')
        cnt = 0
        for input_video in configDLC['video_sets']:
            cnt += 1
            print(cnt ,') video => ', type(input_video))
            # get video name
            video_fname = os.path.basename(input_video)
            video_name = ''.join(video_fname.split('.')[:-1])
            # output_path has the same name of the video name plus whiki_
            output_path = os.path.join(detectionsPath, 'whiski_' + video_name)
            # creates output path if it doesn't exists
            if not os.path.exists(output_path):
                warn('out path didn\'t exist creating output path ' + output_path)
                os.mkdir(output_path)

            output_file = os.path.join(output_path, video_name + '.hdf5')
            freeze_support()
            input_video = os.path.expanduser(input_video)
            output_file = os.path.expanduser(output_file)
            print('input_video ', input_video)
            print('output_file', output_file)
            input_reader = WhiskiWrap.FFmpegReader(input_video)
            WhiskiWrap.interleaved_reading_and_tracing(input_reader, output_path, h5_filename=output_file, chunk_size=100)
            # WhiskiWrap.pipeline_trace(input_video, output_file, n_trace_processes=1, chunk_sz_frames=100)

        print('Extraction...')
        self.Close()



def show(config):
    app = wx.App()
    frame = DetectWhiskers(None, config=config).Show()
    app.MainLoop()



if __name__ == '__main__':
    config = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config)





