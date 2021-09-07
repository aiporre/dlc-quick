import wx

from deeplabcut.utils import skeleton
from gui.utils import parse_yaml
from main import MainPanel


class CreateTraining(wx.Frame):
    def __init__(self, parent, title='Create training set', config=None):
        super(CreateTraining, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config

        cfg = parse_yaml(self.config) # parse configuration
        self.is_multianimal = cfg.get('multianimalproject', False)

        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Create training set")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # spin control to select the number of shuffles (if you need to benchmark)
        # Widgets: configuration

        nShuffleLbl = wx.StaticText(self.panel, -1, "Shuffle index (something like shuffle id number):")
        self.nShuffle = wx.SpinCtrl(self.panel, id=-1, min=1, max=1000, initial=1)
        # feedback

        self.deleteFeedback = wx.CheckBox(self.panel,-1, "delete feedback in the console?")

        # training index
        self.listIndex = 0
        trainingIndexLbl = wx.StaticText(self.panel, -1 , " Define the splits of training sets:")
        self.trainingIndex = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
        self.trainingIndex.InsertColumn(0, "Training index", format=wx.LIST_FORMAT_CENTRE, width= 0.25 * self.WIDTHOFINPUTS)
        self.trainingIndex.InsertColumn(1, "Training fractions", format=wx.LIST_FORMAT_CENTRE,
                                    width=0.25 * self.WIDTHOFINPUTS)
        self.trainingFractions = cfg.get('TrainingFraction',[0.95])
        for trainingFraction in self.trainingFractions:
            self.trainingIndex.InsertItem(self.listIndex, str(self.listIndex))
            self.trainingIndex.SetItem(self.listIndex, 1, str(trainingFraction))
            self.listIndex +=1
        buttonAdd = wx.Button(self.panel, label="Add fraction")
        buttonAdd.Bind(wx.EVT_BUTTON, self.onAddStep)

        buttonRemove = wx.Button(self.panel, label="Remove fraction")
        buttonRemove.Bind(wx.EVT_BUTTON, self.onRemoveStep)

        addButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        addButtonSizer.Add(buttonAdd, 0, wx.CENTER|wx.ALL, 2)
        addButtonSizer.Add(buttonRemove, 0, wx.CENTER | wx.ALL, 2)


        # network architecture

        networkChoiceLbl = wx.StaticText(self.panel, -1, " Which network architecture to use? ")

        net_options = [
            "dlcrnet_ms5",
            "resnet_50",
            "resnet_101",
            "resnet_152",
            "mobilenet_v2_1.0",
            "mobilenet_v2_0.75",
            "mobilenet_v2_0.5",
            "mobilenet_v2_0.35",
            "efficientnet-b0",
            "efficientnet-b3",
            "efficientnet-b6",
        ]

        self.networkChoice = wx.ComboBox(self.panel, style=wx.CB_READONLY, value=net_options[0], choices=net_options)


        # cropping definition if multianimal project is selected
        cropSizer= None
        if self.is_multianimal:
            self.useCrop = wx.CheckBox(self.panel, -1, "Use crop")
            self.useCrop.SetValue(False)
            self.useCrop.Bind(wx.EVT_CHECKBOX, self.onCheckUseCrop)
            cropsWidthLbl = wx.StaticText(self.panel, -1, "Crops width")
            self.cropsWidth = wx.TextCtrl(self.panel, -1, "200")
            self.cropsWidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.cropWidth))
            self.cropsWidth.Enable(False)

            cropsHeightLbl = wx.StaticText(self.panel, -1, "Crops height")
            self.cropsHeight = wx.TextCtrl(self.panel, -1, "200")
            self.cropsHeight.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.cropLenght))
            self.cropsHeight.Enable(False)

            nCropsLbl = wx.StaticText(self.panel, -1, "Number of Crops per labeled images")
            self.nCrops = wx.TextCtrl(self.panel, -1, "10")
            self.nCrops.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.nCrops))
            self.nCrops.Enable(False)

            cropSizer = wx.BoxSizer(wx.VERTICAL)
            cropSizer.Add(self.useCrop, 0, wx.ALL, 2)
            cropSizer.Add(nCropsLbl, 0, wx.ALL, 2)
            cropSizer.Add(self.nCrops, 0, wx.ALL, 2)
            cropSizer.Add(cropsWidthLbl, 0, wx.ALL, 2)
            cropSizer.Add(self.cropsWidth, 0, wx.ALL, 2)
            cropSizer.Add(cropsHeightLbl, 0, wx.ALL, 2)
            cropSizer.Add(self.cropsHeight, 0, wx.ALL, 2)

        compareSizer = None
        if not self.is_multianimal:
            self.selectModelComparison = wx.CheckBox(self.panel, -1, "make model Comparison")
            self.selectModelComparison.SetValue(False)
            self.selectModelComparison.Bind(wx.EVT_CHECKBOX, self.onSelectModelComparision)
            compareNumShufflesLbl = wx.StaticText(self.panel, -1 , "Specify num of shuffles per comparison")
            self.compareNumShuffles = wx.SpinCtrl(self.panel, id=-1, min=1, max=1000, initial=1)
            compareTrainingIndexLbl = wx.StaticText(self.panel, -1, "Which training index for comparisons?")
            self.compareTrainingIndex = wx.SpinCtrl(self.panel, id=-1, min=0, max=999, initial=0)
            self.compareTrainingIndex.Enable(False)
            self.compareNetworkSelection = wx.CheckListBox(self.panel, -1, size= wx.Size(self.WIDTHOFINPUTS, -1), choices=net_options[1:], name="Select networks to compare: ")
            self.compareNumShuffles.Enable(False)
            self.compareNetworkSelection.Enable(False)

            compareSizer = wx.BoxSizer(wx.VERTICAL)
            compareSizer.Add(self.selectModelComparison, 0, wx.LEFT | wx.ALL, 2)
            compareSizer.Add(compareNumShufflesLbl, 0, wx.LEFT | wx.ALL, 2)
            compareSizer.Add(self.compareNumShuffles, 0, wx.LEFT | wx.ALL, 2)
            compareSizer.Add(compareTrainingIndexLbl, 0, wx.LEFT | wx.ALL, 2)
            compareSizer.Add(self.compareTrainingIndex, 0, wx.LEFT | wx.ALL, 2)
            compareSizer.Add(self.compareNetworkSelection, 0, wx.LEFT | wx.ALL, 2)

        # button to create dataset or datasets
        buttonCreate = wx.Button(self.panel, label="Create")
        buttonCreate.Bind(wx.EVT_BUTTON, self.onCreateDataset)
        buttonSkeleton = wx.Button(self.panel, label="Create Skeleton")
        buttonSkeleton.Bind(wx.EVT_BUTTON, self.build_skeleton)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer.Add(nShuffleLbl, 0, wx.EXPAND | wx.ALL, 10)
        inputSizer.Add(self.nShuffle, 0, wx.CENTER, 2)
        inputSizer.Add(trainingIndexLbl, 0, wx.EXPAND | wx.ALL, 10)
        inputSizer.Add(self.trainingIndex, 0, wx.CENTER, 2)
        inputSizer.Add(addButtonSizer, 0, wx.CENTER, 2)
        inputSizer.Add(networkChoiceLbl, 0, wx.CENTER, 2)
        inputSizer.Add(self.networkChoice, 0, wx.CENTER, 2)
        inputSizer.Add(self.deleteFeedback,0 , wx.CENTER, 2)

        if cropSizer:
            inputSizer.Add(wx.StaticLine(self.panel), 0,
                           wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
            inputSizer.Add(cropSizer, 0, wx.CENTER, 2)
        if compareSizer:
            inputSizer.Add(wx.StaticLine(self.panel), 0,
                           wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
            inputSizer.Add(compareSizer, 0, wx.CENTER, 2)

        inputSizer.Add(wx.StaticLine(self.panel), 0,
                       wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        buttonSizer.Add(buttonSkeleton, 0, wx.CENTER, 2)
        buttonSizer.Add(buttonCreate, 0, wx.CENTER, 2)
        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonSizer, 0, wx.TOP | wx.CENTER | wx.BOTTOM, 15)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onCreateDataset(self, event):
        import deeplabcut as d
        cfg = d.auxiliaryfunctions.read_config(self.config)

        if self.trainingIndex.GetItemCount()>0:
            trainingFractions = []
            for i in range(self.trainingIndex.GetItemCount()):
                trainingFractions.append(float(self.trainingIndex.GetItemText(i, col=1)))
        else:
            trainingFractions = [0.95]

        d.auxiliaryfunctions.edit_config(self.config, {'TrainingFraction': trainingFractions})

        if cfg.get("multianimalproject", False):
            num_shuffles = self.nShuffle.GetValue()

            if self.useCrop.GetValue():
                n_crops, height, width = [int(x.GetValue()) for x in [self.nCrops, self.cropsHeight, self.cropsWidth]]
                d.cropimagesandlabels(
                    self.config, n_crops, (height, width), userfeedback=self.deleteFeedback.GetValue()
                )
            print('Creating network with net_type: ', self.networkChoice.GetValue())
            d.create_multianimaltraining_dataset(
                self.config,
                num_shuffles,
                Shuffles=[self.nShuffle.GetValue()],
                net_type=self.networkChoice.GetValue(),
            )
        else:
            if not self.selectModelComparison.GetValue():
                num_shuffles = self.nShuffle.GetValue()

                d.create_training_dataset(
                    self.config,
                    num_shuffles,
                    Shuffles=[self.nShuffle.GetValue()],
                    userfeedback=self.deleteFeedback.GetValue(),
                    net_type=self.networkChoice.GetValue(),
                )
            if self.selectModelComparison.GetValue():
                compareNetworksList = list(self.compareNetworkSelection.GetCheckedStrings())
                num_shuffles = self.compareNumShuffles.GetValue()
                trainindex = self.compareTrainingIndex.GetValue()

                print('inputs: ')
                print('self.config: ', self.config)
                print('trainindex: ', trainindex)
                print('num_shuffles:', num_shuffles)
                print('userfeedback: ', self.deleteFeedback.GetValue())
                print('net_types: ', compareNetworksList)

                d.create_training_model_comparison(
                    self.config,
                    trainindex=trainindex,
                    num_shuffles=num_shuffles,
                    userfeedback=self.deleteFeedback.GetValue(),
                    net_types=compareNetworksList,
                )

    def build_skeleton(self, event):
        skeleton.SkeletonBuilder(self.config)

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


    def onCheckUseCrop(self, event):
       if self.is_multianimal:
           self.nCrops.Enable(self.useCrop.GetValue())
           self.cropsWidth.Enable(self.useCrop.GetValue())
           self.cropsHeight.Enable(self.useCrop.GetValue())
           self.nCrops.Enable(self.useCrop.GetValue())
           self.cropsWidth.Enable(self.useCrop.GetValue())
           self.cropsHeight.Enable(self.useCrop.GetValue())


    def onSelectModelComparision(self, event):
        if not self.is_multianimal:
            self.compareNumShuffles.Enable(self.selectModelComparison.GetValue())
            self.compareTrainingIndex.Enable(self.selectModelComparison.GetValue())
            self.compareNetworkSelection.Enable(self.selectModelComparison.GetValue())
            self.nShuffle.Enable(not self.selectModelComparison.GetValue())
            self.networkChoice.Enable(not self.selectModelComparison.GetValue())

    def onAddStep(self, event):
        def onOk(event, parent, frame):
            line = frame.fractionRate.GetValue()
            parent.trainingIndex.InsertItem(self.listIndex, str(parent.listIndex))
            parent.trainingIndex.SetItem(self.listIndex, 1, line)
            parent.listIndex += 1
            frame.Close()

        dialog = wx.Dialog(self, id=-1, title="Add new training fraction")
        dialog.Bind(wx.EVT_BUTTON, lambda event: onOk(event, self, dialog), id=wx.ID_OK)
        mainSizerDialog = wx.BoxSizer(wx.VERTICAL)
        field1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        lrLbl = wx.StaticText(dialog, -1, "training fraction rate")
        dialog.fractionRate = wx.TextCtrl(dialog, -1, '0.95')
        dialog.fractionRate.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, dialog.fractionRate))
        field1Sizer.Add(lrLbl, 2, wx.CENTER | wx.ALL, 2)
        field1Sizer.Add(dialog.fractionRate, 2, wx.CENTER | wx.ALL, 2)

        buttonsizer = dialog.CreateButtonSizer(wx.CANCEL | wx.OK)
        mainSizerDialog.Add(field1Sizer, 0, wx.CENTER | wx.ALL, 2)
        mainSizerDialog.Add(buttonsizer, 0, wx.CENTER | wx.ALL, 2)
        dialog.SetSizer(mainSizerDialog)
        dialog.ShowModal()
        dialog.Destroy()

    def onRemoveStep(self, event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.trainingIndex.GetFirstSelected(self)
        if item_id == -1:
            item_id = self.listIndex - 1

        print("removing entry : ", item_id)
        self.trainingIndex.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex - 1