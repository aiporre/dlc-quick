import wx

from gui.utils.main_panel import MainPanel


class ExtractFrames(wx.Frame):
    def __init__(self, parent, title='Extract frames', config=None):
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
        # self.userFeedback = wx.CheckBox(self.panel, -1, "")
        # self.userFeedback.SetValue(True)

        # check box to select cropping or not
        croppingLbl = wx.StaticText(self.panel, -1, "Use cropping:")
        self.cropping = wx.Choice(self.panel, -1, choices=['no crop', 'use from file', 'pick in gui'])

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
        mainSizer.Add(buttonExtract, 0, wx.CENTER | wx.ALL, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onExtractButton(self, event):
        print('Extraction of the frames....')
        print('import dlc. ')
        import deeplabcut as d
        mode = self.mode.GetString(self.mode.GetCurrentSelection())
        algo = self.selectionAlgo.GetString(self.selectionAlgo.GetCurrentSelection())
        crop_options = {'no crop': False, 'use from file': True, 'pick in gui':'GUI'}
        d.extract_frames(self.config, mode=mode, algo=algo, crop=crop_options[self.cropping.GetStringSelection()], userfeedback=False, opencv=True)
        print('Extraction...')
        self.Close()