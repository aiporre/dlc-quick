import subprocess
import webbrowser

from deeplabcut.utils import skeleton
from pathlib import Path

import pandas as pd
import wx
import wx.grid
from blockwindow import BlockWindow
import os
import yaml
from wx.lib.masked.numctrl import NumCtrl
import sys
import matplotlib
import glob

from gui.model_generation import ContactModelGeneration
from gui.utils import parse_yaml
from gui.utils.parse_yaml import extractTrainingIndexShuffle
from gui.utils.snapshot_index import get_snapshots
from gui.whisker_detection import DetectWhiskers
from gui.whisker_label_toolbox import LabelWhiskersFrame
from gui.multi_whisker_label_toolbox import LabelWhiskersFrame as MultiLabelWhiskersFrame


print('importing deeplab cut..')

print('Done')

CWD = os.getcwd()


def get_videos(videosList):
    count = videosList.GetItemCount()
    videos = []
    for row in range(count):
        item = videosList.GetItem(itemIdx=row, col=1)
        videos.append(item.GetText())
    return videos


def find_yaml(wd=None):
    '''
    Find the most likely yaml config file in the current directory
    wd:working directory to search for the yaml
    :return:
    '''
    config_yamls = []
    yamls = []
    cwd = os.getcwd() if wd is None else wd
    for dirpath, dnames, fnames in os.walk(cwd):
        for f in fnames:
            if f.endswith("config.yaml"):
                config_yamls.append(os.path.join(dirpath, f))
            elif f.endswith(".yaml"):
                yamls.append(os.path.join(dirpath, f))
    print('Yaml options found:', yamls, ' or configs: ', config_yamls)
    config_yaml = ''
    if not len(config_yamls) == 0:
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
            print('Reading yaml file: ', filepath)
            content = yaml.safe_load(stream)
            print(type(content), '--', content)
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
        status[k] = radiobuttons[k].GetValue()

    if status['All']:
        return 'all'
    else:
        return [k for k, v in status.items() if v and not k == 'All']

def paco():
    e

class CreateTrainingSet(wx.Frame):
    def __init__(self, parent, title='Create training set', config=None, *args, **kw):
        super(CreateTrainingSet, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Create training set")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # input test to set the working directory
        configPathLbl = wx.StaticText(self.panel, -1, "Config path:", size=wx.Size(self.WIDTHOFINPUTS, 25))
        cwd = find_yaml()
        os.chdir(cwd)
        configPath = wx.FilePickerCtrl(self.panel, -1, cwd, wildcard='*.yaml')

        # check box to select automatic or manual selection
        modeLbl = wx.StaticText(self.panel, -1, "Automatic/Manual:")
        mode = wx.CheckBox(self.panel, -1, "")
        mode.SetValue(True)

        # check box to mode of frames extraction (uniform or kmeans)
        selectionAlgoLbl = wx.StaticText(self.panel, -1, "Uniform/Manual:")
        selectionAlgo = wx.CheckBox(self.panel, -1, "")
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
        d.auxiliaryfunctions.edit_config(config_path, {"project_type": self.projectType.GetStringSelection()})
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


class TrainNetwork(wx.Frame):
    def __init__(self, parent, title='Train network', config=None):
        super(TrainNetwork, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Train network")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # choice iteration from configuration file
        cfg = parser_yaml(self.config)
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        current_iteration = 'iteration-' + str(cfg['iteration'])
        iterations = [current_iteration]
        iterations.extend([it for it in self.find_iterations() if it not in iterations])
        self.iteration = wx.Choice(self.panel, id=-1, choices=iterations)
        self.iteration.SetSelection(0)
        shuffleNumberLbl = wx.StaticText(self.panel, -1, "Shuffles")
        self.shuffleNumber = wx.Choice(self.panel, id=-1, choices=self.find_shuffles())
        self.shuffleNumber.SetSelection(0)
        pose_config = self.read_fields()
        self.iteration.Bind(wx.EVT_CHOICE, self.onSelectIteration)
        self.shuffleNumber.Bind(wx.EVT_CHOICE, self.onSelectShuffle)
        # # default fields from the pose_cfg.yaml file:
        # all_jointsLbl = wx.StaticText(self.panel, -1, "All joints")
        # all_joints = BlockWindow(self.panel,-1,label=str(pose_config['all_joints']))
        #
        # all_jointsNamesLbl = wx.StaticText(self.panel, -1, "All joints names")
        # all_jointsNames = BlockWindow(self.panel,-1,label=str(pose_config['all_joints_names']), size=(7*len(str(pose_config['all_joints_names'])),25))

        # leftwidthLbl = wx.StaticText(self.panel, -1, "left width")
        # print('pose_config fields: ', pose_config.keys())
        # self.leftwidth = wx.TextCtrl(self.panel, -1, str(pose_config['leftwidth']))

        # minsizeLbl = wx.StaticText(self.panel, -1, "minsize")
        # self.minsize = wx.TextCtrl(self.panel, -1, str(pose_config["minsize"]))
        # self.minsize.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.minsize))

        # rightwidthLbl = wx.StaticText(self.panel, -1, "rightwidth")
        # self.rightwidth = wx.TextCtrl(self.panel, -1, str(pose_config['rightwidth']))
        # self.rightwidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.rightwidth))

        # topheightLbl = wx.StaticText(self.panel, -1, "topheight")
        # self.topheight = wx.TextCtrl(self.panel, -1, str(pose_config['topheight']))
        # self.topheight.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.topheight))

        # bottomheightLbl = wx.StaticText(self.panel, -1, "Bottom height")
        # self.bottomheight = wx.TextCtrl(self.panel, -1, str(pose_config['bottomheight']))

        # cropLbl = wx.StaticText(self.panel, -1, "Crop")
        # self.crop = wx.CheckBox(self.panel, -1, "")
        # self.crop.SetValue(pose_config['crop'])

        cropRatioLbl = wx.StaticText(self.panel, -1, "Crop ratio")
        self.cropRatio = wx.SpinCtrlDouble(self.panel, id=-1, min=0, max=1, initial=pose_config['cropratio'], inc=0.1)

        # datasetLbl = wx.StaticText(self.panel,-1,"Dataset")
        # self.dataset = wx.FilePickerCtrl(self.panel, -1, pose_config['dataset'], wildcard='*.mat')

        # datasetTypeLbl = wx.StaticText(self.panel,-1,"Dataset type")
        # self.datasetType = wx.TextCtrl(self.panel, -1, pose_config['dataset_type'])

        displayItersLbl = wx.StaticText(self.panel, -1, "Display iters")
        self.displayIters = wx.SpinCtrlDouble(self.panel, id=-1, min=1, max=sys.maxsize,
                                              initial=pose_config['display_iters'], inc=1)

        max_itersLbl = wx.StaticText(self.panel, -1, "Max iters")
        self.max_iters = wx.SpinCtrlDouble(self.panel, id=-1, min=1, max=sys.maxsize, initial=5000,
                                           inc=1)
        save_itersLbl = wx.StaticText(self.panel, -1, "save_iters")
        self.save_iters = wx.SpinCtrlDouble(self.panel, id=-1, min=1, max=sys.maxsize,
                                            initial=pose_config['save_iters'], inc=1)

        # inputSizer.Add(max_itersLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.max_iters, 0, wx.EXPAND, 2)

        globalScaleLbl = wx.StaticText(self.panel, -1, "Global scale")
        self.globalScale = wx.SpinCtrlDouble(self.panel, id=-1, min=0, max=1, initial=pose_config['global_scale'],
                                             inc=0.1)

        initWeightsLbl = wx.StaticText(self.panel, -1, "Initial weights")
        self.initWeights = wx.TextCtrl(self.panel, -1, pose_config['init_weights'])

        intermediateSupervisionLbl = wx.StaticText(self.panel, -1, "Intermediate supervision")
        self.intermediateSupervision = wx.CheckBox(self.panel, -1, "")
        self.intermediateSupervision.SetValue(pose_config['intermediate_supervision'])

        intermediate_supervision_layerLbl = wx.StaticText(self.panel, -1, "intermediate_supervision_layer")
        self.intermediate_supervision_layer = wx.SpinCtrl(self.panel, id=-1, min=0.1, max=1000,
                                                          initial=pose_config['intermediate_supervision_layer'])

        self.listIndex = 0
        multistepLbl = wx.StaticText(self.panel, -1, "Multi step:")
        self.multistep = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
        self.multistep.InsertColumn(0, "Learning Rate", format=wx.LIST_FORMAT_CENTRE, width=0.25 * self.WIDTHOFINPUTS)
        self.multistep.InsertColumn(1, "Up to iteration...", format=wx.LIST_FORMAT_CENTRE,
                                    width=0.25 * self.WIDTHOFINPUTS)


        multisteps = pose_config.get('multi_step', [['0.002', '10000']])
        for lr, upToIter in multisteps:
            self.multistep.InsertItem(self.listIndex, str(lr))
            self.multistep.SetItem(self.listIndex, 1, str(upToIter))
            self.listIndex += 1
        # location_refinementLbl = wx.StaticText(self.panel, -1, "location_refinement")
        # self.location_refinement = wx.CheckBox(self.panel, -1, "")
        # self.location_refinement.SetValue(pose_config["location_refinement"])

        # locref_huber_lossLbl = wx.StaticText(self.panel, -1, "locref_huber_loss")
        # self.locref_huber_loss = wx.CheckBox(self.panel, -1, "")
        # self.locref_huber_loss.SetValue(pose_config["locref_huber_loss"])

        # locref_loss_weightLbl = wx.StaticText(self.panel, -1, "locref_loss_weight")
        # self.locref_loss_weight = wx.SpinCtrlDouble(self.panel, id=-1, min=0.1, max=10000, initial=pose_config['display_iters'],inc=0.1)

        # locref_stdevLbl = wx.StaticText(self.panel, -1, "locref_stdev")
        # self.locref_stdev = wx.TextCtrl(self.panel, -1, str(pose_config['locref_stdev']))
        # self.locref_stdev.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.locref_stdev))

        max_input_sizeLbl = wx.StaticText(self.panel, -1, "max_input_size")
        self.max_input_size = wx.TextCtrl(self.panel, -1, str(pose_config["max_input_size"]))
        self.max_input_size.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.max_input_size))

        #
        # metadatasetLbl = wx.StaticText(self.panel, -1, "metadataset")
        # self.metadataset = BlockWindow(self.panel,-1,os.path.basename(pose_config['metadataset']),size=(3*len(str(pose_config['metadataset'])),25))

        min_input_sizeLbl = wx.StaticText(self.panel, -1, "min_input_size")
        self.min_input_size = wx.TextCtrl(self.panel, -1, str(pose_config['min_input_size']))
        self.min_input_size.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.min_input_size))

        mirrorLbl = wx.StaticText(self.panel, -1, "mirror")
        self.mirror = wx.CheckBox(self.panel, -1, "")
        self.mirror.SetValue(pose_config["mirror"])

        # multi_stepLbl = wx.StaticText(self.panel, -1, "multi_step (reduction/steps)")
        # self.multi_step_1 = wx.TextCtrl(self.panel,-1, str(pose_config['multi_step'][0][0])) # 'multi_step': [[0.001, 5]]
        # self.multi_step_2 = wx.TextCtrl(self.panel, -1, str(pose_config['multi_step'][0][1]))
        # self.multi_step_1.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.multi_step_1))
        # self.multi_step_2.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.multi_step_2))

        net_typeLbl = wx.StaticText(self.panel, -1, "net_type")
        self.net_type = wx.TextCtrl(self.panel, -1, str(pose_config['net_type']))

        # num_jointsLbl = wx.StaticText(self.panel, -1, "num_joints")
        # self.num_joints = wx.TextCtrl(self.panel,-1,str(pose_config['num_joints']))
        # self.num_joints.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.num_joints))

        pos_dist_threshLbl = wx.StaticText(self.panel, -1, "pos_dist_thresh")
        self.pos_dist_thresh = wx.TextCtrl(self.panel, -1, str(pose_config["pos_dist_thresh"]))
        self.pos_dist_thresh.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.pos_dist_thresh))

        scale_jitter_loLbl = wx.StaticText(self.panel, -1, "scale_jitter_lo")
        self.scale_jitter_lo = wx.TextCtrl(self.panel, -1, str(pose_config["scale_jitter_lo"]))
        self.scale_jitter_lo.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.scale_jitter_lo))

        scale_jitter_upLbl = wx.StaticText(self.panel, -1, "scale_jitter_up")
        self.scale_jitter_up = wx.TextCtrl(self.panel, -1, str(pose_config["scale_jitter_up"]))
        self.scale_jitter_up.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.scale_jitter_up))

        # button to create dataset or datasets
        buttonTrain = wx.Button(self.panel, label="Train")
        buttonTrain.Bind(wx.EVT_BUTTON, self.onTrainNetwork)

        buttonAdd = wx.Button(self.panel, label="Add step")
        buttonAdd.Bind(wx.EVT_BUTTON, self.onAddStep)

        buttonRemove = wx.Button(self.panel, label="Remove step")
        buttonRemove.Bind(wx.EVT_BUTTON, self.onRemoveStep)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        mainSizer.Add(iterationLbl, 0, wx.CENTER | wx.ALL, 2)
        mainSizer.Add(self.iteration, 0, wx.CENTER | wx.ALL, 2)
        mainSizer.Add(shuffleNumberLbl, 0, wx.CENTER | wx.ALL, 2)
        mainSizer.Add(self.shuffleNumber, 0, wx.CENTER | wx.ALL, 2)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizerRight = wx.BoxSizer(wx.VERTICAL)
        inputSizerCenter = wx.BoxSizer(wx.VERTICAL)

        # adding elements to the sizers
        # inputSizer.Add(all_jointsLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(all_joints, 0, wx.EXPAND, 2)
        # inputSizer.Add(all_jointsNamesLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(all_jointsNames, 0, wx.EXPAND, 2)

        # Cropping image part of aug.
        # inputSizer.Add(cropLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.crop, 0, wx.EXPAND, 2)
        inputSizer.Add(cropRatioLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.cropRatio, 0, wx.EXPAND, 2)
        # inputSizer.Add(minsizeLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.minsize, 0, wx.EXPAND, 2)
        # inputSizer.Add(leftwidthLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.leftwidth, 0, wx.EXPAND, 2)
        # inputSizer.Add(rightwidthLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.rightwidth, 0, wx.EXPAND, 2)
        # inputSizer.Add(bottomheightLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.bottomheight, 0, wx.EXPAND, 2)
        # inputSizer.Add(topheightLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(self.topheight, 0, wx.EXPAND, 2)

        inputSizer.Add(globalScaleLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.globalScale, 0, wx.EXPAND, 2)
        inputSizer.Add(pos_dist_threshLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.pos_dist_thresh, 0, wx.EXPAND, 2)
        inputSizer.Add(scale_jitter_loLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.scale_jitter_lo, 0, wx.EXPAND, 2)
        inputSizer.Add(scale_jitter_upLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.scale_jitter_up, 0, wx.EXPAND, 2)
        inputSizer.Add(mirrorLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.mirror, 0, wx.EXPAND, 2)

        # training configurations..
        inputSizerCenter.Add(displayItersLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.displayIters, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(save_itersLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.save_iters, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(max_itersLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.max_iters, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(net_typeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.net_type, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(initWeightsLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.initWeights, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(intermediateSupervisionLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.intermediateSupervision, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(intermediate_supervision_layerLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.intermediate_supervision_layer, 0, wx.EXPAND, 2)

        # inputSizerCenter.Add(datasetLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.dataset, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(datasetTypeLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.datasetType, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(location_refinementLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.location_refinement, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(locref_huber_lossLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.locref_huber_loss, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(locref_loss_weightLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.locref_loss_weight, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(locref_stdevLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.locref_stdev, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(max_input_sizeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.max_input_size, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(metadatasetLbl, 0, wx.EXPAND, 2)
        # inputSizerCenter.Add(self.metadataset, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(min_input_sizeLbl, 0, wx.EXPAND, 2)
        inputSizerCenter.Add(self.min_input_size, 0, wx.EXPAND, 2)
        # inputSizerRight.Add(multi_stepLbl, 0, wx.EXPAND, 2)
        # inputSizerRight.Add(self.multi_step_1, 0, wx.EXPAND, 2)
        # inputSizerRight.Add(self.multi_step_2, 0, wx.EXPAND, 2)

        # inputSizerRight.Add(num_jointsLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(multistepLbl, 0, wx.EXPAND, 2)
        inputSizerRight.Add(self.multistep, 0, wx.EXPAND, 2)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(buttonAdd)
        buttonSizer.Add(buttonRemove)
        inputSizerRight.Add(buttonSizer, 0, wx.EXPAND, 2)

        # //////////////////////////////
        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizerCenter, 0, wx.ALL, 10)
        contentSizer.Add(inputSizerRight, 0, wx.ALL, 10)
        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        mainSizer.Add(buttonTrain, 0, wx.CENTER | wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onSelectIteration(self, event):
        self.shuffleNumber.SetItems(self.find_shuffles())
        self.shuffleNumber.SetSelection(0)
        self.reloadFields()

    def onSelectShuffle(self, event):
        self.reloadFields()


    def reloadFields(self):
        pose_config = self.read_fields()

        self.cropRatio.SetValue(str(pose_config['cropratio']))
        self.globalScale.SetValue(str(pose_config['global_scale']))
        self.initWeights.SetValue(str(pose_config['init_weights']))
        self.intermediateSupervision.SetValue(pose_config['intermediate_supervision'])
        self.intermediate_supervision_layer.SetValue(pose_config['intermediate_supervision_layer'])
        self.max_input_size.SetValue(str(pose_config['max_input_size']))
        self.min_input_size.SetValue(str(pose_config['min_input_size']))
        self.mirror.SetValue(pose_config['mirror'])
        self.net_type.SetValue(pose_config['net_type'])
        self.pos_dist_thresh.SetValue(str(pose_config['pos_dist_thresh']))
        self.scale_jitter_lo.SetValue(str(pose_config['scale_jitter_lo']))
        self.scale_jitter_up.SetValue(str(pose_config['scale_jitter_up']))



    def onTrainNetwork(self, event):
        print('Training...')
        pose_config = self.read_fields()
        pose_config_file = self.read_fields(parse=False)
        # pose_config['bottomheight'] = int(self.bottomheight.GetValue())
        # pose_config['crop'] = self.crop.GetValue()
        pose_config['cropratio'] = float(self.cropRatio.GetValue())
        pose_config['display_iters'] = int(self.displayIters.GetValue())
        pose_config['global_scale'] = float(self.displayIters.GetValue())
        pose_config['init_weights'] = self.initWeights.GetValue()
        pose_config['intermediate_supervision'] = self.intermediateSupervision.GetValue()
        pose_config['intermediate_supervision_layer'] = int(self.intermediate_supervision_layer.GetValue())
        # pose_config['leftwidth'] = int(self.leftwidth.GetValue())
        pose_config['max_input_size'] = int(self.max_input_size.GetValue())
        pose_config['min_input_size'] = int(self.min_input_size.GetValue())
        # pose_config['minsize'] = int(self.minsize.GetValue())
        pose_config['mirror'] = self.mirror.GetValue()

        count = self.multistep.GetItemCount()
        learning_rates = [self.multistep.GetItem(itemIdx=e, col=0).GetText() for e in range(count)]
        iterations = [self.multistep.GetItem(itemIdx=e, col=1).GetText() for e in range(count)]
        pose_config['multi_step'] = [[float(lr), int(it)] for lr, it in zip(learning_rates, iterations)]

        pose_config['net_type'] = self.net_type.GetValue()
        pose_config['pos_dist_thresh'] = int(self.pos_dist_thresh.GetValue())
        # pose_config['rightwidth'] = int(self.rightwidth.GetValue())
        pose_config['save_iters'] = int(self.save_iters.GetValue())
        pose_config['scale_jitter_lo'] = float(self.scale_jitter_lo.GetValue())
        pose_config['scale_jitter_up'] = float(self.scale_jitter_up.GetValue())
        # pose_config['topheight'] = int(self.topheight.GetValue())
        config = parser_yaml(self.config)
        pose_config['project_path'] = config['project_path']
        print('CONFIG POSE:')
        print(pose_config)
        import deeplabcut as d
        d.auxiliaryfunctions.write_plainconfig(pose_config_file, pose_config)
        trainingIndex, shuffle = extractTrainingIndexShuffle(self.config, self.shuffleNumber.GetStringSelection())
        iterationNum = int(self.iteration.GetStringSelection().split('-')[-1])

        if config['iteration'] != iterationNum:
            print(f'\e[32m Atention! Iteration is being set back to iteration-{iterationNum}\e[0m')
            d.auxiliaryfunctions.write_config(self.config, {'iteration': iterationNum})
        print('trainingIndex: ', trainingIndex)
        print('shuffle: ', shuffle)
        d.train_network(self.config, shuffle=shuffle, trainingsetindex=trainingIndex, maxiters=int(self.max_iters.GetValue()), displayiters=pose_config['display_iters'],
                        saveiters=pose_config['save_iters'])
        print('Training finished')

    def find_iterations(self):
        '''find the iterations given a config file.'''
        # import deeplabcut
        # cfg = deeplabcut.auxiliaryfunctions.read_config(self.config)
        config = parser_yaml(self.config)
        return [f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models')) if not f.startswith('.')]


    def find_shuffles(self):
        config = parser_yaml(self.config)
        numbers = []
        iteration_selection = self.iteration.GetStringSelection()
        files = [ f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models', iteration_selection)) if not f.startswith('.') and 'contact-model' not in f and 'whisking-model' not in f and 'motion-model' not in f]
        return files

    def read_fields(self, parse=True):
        iteration_selection = self.iteration.GetStringSelection()
        print('iteration_selection', iteration_selection)
        cfg = parser_yaml(self.config)
        posefile = os.path.join(cfg['project_path'], 'dlc-models', iteration_selection, self.shuffleNumber.GetStringSelection(), 'train', 'pose_cfg.yaml')
        if not os.path.exists(posefile):
            raise FileNotFoundError(posefile)
        print('Pose file: ', posefile)
        if parse:
            return parser_yaml(posefile)
        else:
            return posefile

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

    def onAddStep(self, event):
        def onOk(event, parent, frame):
            line = frame.lr.GetValue()
            parent.multistep.InsertItem(self.listIndex, line)
            parent.multistep.SetItem(self.listIndex, 1, frame.iteration.GetValue())
            parent.listIndex += 1
            frame.Close()

        dialog = wx.Dialog(self, id=-1, title="Add new step")
        dialog.Bind(wx.EVT_BUTTON, lambda event: onOk(event, self, dialog), id=wx.ID_OK)
        mainSizerDialog = wx.BoxSizer(wx.VERTICAL)
        field1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        lrLbl = wx.StaticText(dialog, -1, "learning rate")
        dialog.lr = wx.TextCtrl(dialog, -1, '0.001')
        dialog.lr.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, dialog.lr))
        field1Sizer.Add(lrLbl, 2, wx.CENTER | wx.ALL, 2)
        field1Sizer.Add(dialog.lr, 2, wx.CENTER | wx.ALL, 2)

        field2Sizer = wx.BoxSizer(wx.HORIZONTAL)
        iterationLbl = wx.StaticText(dialog, -1, "learning rate")
        dialog.iteration = wx.TextCtrl(dialog, -1, '10000')
        dialog.iteration.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, dialog.iteration))
        field2Sizer.Add(iterationLbl, 2, wx.CENTER | wx.ALL, 2)
        field2Sizer.Add(dialog.iteration, 2, wx.CENTER | wx.ALL, 2)

        buttonsizer = dialog.CreateButtonSizer(wx.CANCEL | wx.OK)
        mainSizerDialog.Add(field1Sizer, 0, wx.CENTER | wx.ALL, 2)
        mainSizerDialog.Add(field2Sizer, 0, wx.CENTER | wx.ALL, 2)
        mainSizerDialog.Add(buttonsizer, 0, wx.CENTER | wx.ALL, 2)
        dialog.SetSizer(mainSizerDialog)
        dialog.ShowModal()
        dialog.Destroy()

    def onRemoveStep(self, event):
        if self.listIndex == 0:
            print('Nothing to remove')
            return
        item_id = self.multistep.GetFirstSelected(self)
        if item_id == -1:
            item_id = self.listIndex - 1

        print("removing entry : ", item_id)
        self.multistep.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex - 1


class EvaluaterNetwork(wx.Frame):
    def __init__(self, parent, title='Evaluate network', config=None):
        super(EvaluaterNetwork, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        config = parser_yaml(self.config)

        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Evaluate network")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # selection of iteration:
        cfg = parser_yaml(self.config)
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        current_iteration = 'iteration-' + str(cfg['iteration'])
        iterations = [current_iteration]
        iterations.extend([it for it in self.find_iterations() if it not in iterations])
        self.iteration = wx.Choice(self.panel, id=-1, choices=iterations)
        self.iteration.SetSelection(0)
        shuffleNumberLbl = wx.StaticText(self.panel, -1, "Shuffles")
        self.shuffleNumber = wx.Choice(self.panel, id=-1, choices=self.find_shuffles())
        self.shuffleNumber.SetSelection(0)
        self.iteration.Bind(wx.EVT_CHOICE, self.onSelectIteration)
        self.shuffleNumber.Bind(wx.EVT_CHOICE, self.onSelectShuffleNumber)


        plottingLbl = wx.StaticText(self.panel, -1, "Plotting")
        self.plotting = wx.CheckBox(self.panel, -1, "")
        self.plotting.SetValue(True)

        showErrorLbl = wx.StaticText(self.panel, -1, "Show error")
        self.showError = wx.CheckBox(self.panel, -1, "")
        self.showError.SetValue(False)

        comparisionBodyPartsLbl = wx.StaticText(self.panel, -1, "Comparision body parts")
        print(config['bodyparts'])
        print(len(config['bodyparts']))
        if config.get("multianimalproject", False):
            bodyparts = config["multianimalbodyparts"]
        else:
            bodyparts = config["bodyparts"]
        comparisionBodyParts, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                              itemlabels=bodyparts + ['All'], type='checkBox')

        self.radioButtons = items
        self.radioButtonCurrentStatus = {}
        items['All'].SetValue(True)
        items['All'].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, 'All'))
        for k in items.keys():
            if not k == 'All':
                items[k].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, ''))

        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices=['None'] + get_available_gpus())

        rescaleLbl = wx.StaticText(self.panel, -1, "Rescale")
        self.rescale = wx.CheckBox(self.panel, -1, "")
        self.rescale.SetValue(False)

        snapshotindexLbl = wx.StaticText(self.panel, -1, "Select best snapshot")

        self.snapshots = self.find_snapshots()
        self.snapshotindex = wx.Choice(self.panel, -1, choices=self.snapshots)

        # box of results:
        summaryLbl = wx.StaticText(self.panel, -1, "summaryLbl")
        self.summary = self.generate_summary()

        # button to evaluate netwrok
        buttonEvaluate = wx.Button(self.panel, label="Evaluate")
        buttonEvaluate.Bind(wx.EVT_BUTTON, self.evaluate_network)
        buttonCollect = wx.Button(self.panel, label="Collect results all")
        buttonCollect.Bind(wx.EVT_BUTTON, self.generate_collected_summary_csv)

        buttonConfig = wx.Button(self.panel, label="Write snapshot to config.yaml")
        buttonConfig.Bind(wx.EVT_BUTTON, self.onConfigSnapshot)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)

        mainSizer.Add(iterationLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.iteration, 0, wx.EXPAND, 2)
        mainSizer.Add(shuffleNumberLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.shuffleNumber, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer3 = wx.BoxSizer(wx.VERTICAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # inputSizer.Add(selectionAlgoLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(selectionAlgo, 0, wx.EXPAND, 2)
        inputSizer.Add(plottingLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.plotting, 0, wx.EXPAND, 2)
        inputSizer.Add(showErrorLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.showError, 0, wx.EXPAND, 2)

        inputSizer2.Add(comparisionBodyPartsLbl, 0, wx.EXPAND, 2)
        inputSizer2.Add(comparisionBodyParts, 0, wx.EXPAND, 2)
        inputSizer2.Add(snapshotindexLbl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        inputSizer2.Add(self.snapshotindex, 0, wx.ALIGN_LEFT | wx.ALL, 2)

        inputSizer3.Add(gpusAvailableLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.gpusAvailable, 0, wx.EXPAND, 2)
        inputSizer3.Add(rescaleLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.rescale, 0, wx.EXPAND, 2)

        buttonSizer.Add(buttonEvaluate, 0, wx.CENTER | wx.ALL, 4)
        buttonSizer.Add(buttonCollect, 0, wx.CENTER | wx.ALL, 4)
        buttonSizer.Add(buttonConfig, 0, wx.CENTER |  wx.ALL, 4)
        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer3, 0, wx.ALL, 10)

        # contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(summaryLbl, 0, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add(self.summary, 0, wx.ALL, 2)
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonSizer, 0, wx.BOTTOM | wx.CENTER, 15)

        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)  # Main window

    def evaluate_network(self, event):
        bodyParts = get_radiobutton_status(self.radioButtons)
        print(bodyParts)

        import deeplabcut as d
        gputouse = None if self.gpusAvailable.GetStringSelection() == 'None' else self.gpusAvailable.GetSelection()
        shuffleNumString = self.shuffleNumber.GetStringSelection()
        trainingIndex, shuffleNum = extractTrainingIndexShuffle(self.config, shuffleNumString )

        d.evaluate_network(self.config, trainingsetindex=trainingIndex, Shuffles=[shuffleNum] ,plotting=self.plotting.GetValue(),
                           show_errors=self.showError.GetValue(), comparisonbodyparts=bodyParts, gputouse=gputouse,
                           rescale=self.rescale.GetValue())
        self.Close()

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

    def find_iterations(self):
        '''find the iterations given a config file.'''
        config = parse_yaml(self.config)
        print(" evaluation results: ", os.path.join(config['project_path'], 'evaluation_results'))
        if os.path.exists(os.path.join(config['project_path'], 'evaluation_results')):
            return os.listdir(os.path.join(config['project_path'], 'evaluation_results'))
        else:
            return ['']

    def find_shuffles(self):
        config = parse_yaml(self.config)
        iteration_selection = self.iteration.GetStringSelection()
        files = [ f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models', iteration_selection))if not f.startswith('.') and 'contact-model' not in f and 'whisking-model' not in f and 'motion-model' not in f]
        return files

    def find_snapshots(self):
        training_index, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffleNumber.GetStringSelection())
        return get_snapshots(self.config, shuffle_number, training_index).tolist() + ['latest']


    def onSelectIteration(self, event):
        self.shuffleNumber.SetItems(self.find_shuffles())
        self.shuffleNumber.SetSelection(0)
        self.onSelectShuffleNumber(None)

    def onSelectShuffleNumber(self, event):
        self.snapshots = self.find_snapshots()
        self.snapshotindex.SetItems(self.snapshots)
        self.snapshotindex.SetSelection(0)

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)
    def onConfigSnapshot(self, event):
        import deeplabcut as dlc
        snapshotindex = self.snapshotindex.GetSelection()
        if self.snapshotindex.GetStringSelection() == 'latest':
            snapshotindex = -1
        dlc.auxiliaryfunctions.edit_config(self.config, {'snapshotindex': snapshotindex})

    def generate_collected_summary_csv(self, event):
        cfg = parse_yaml(self.config)
        path_to_csv = os.path.join(cfg['project_path'], 'evaluation-results',
                                       'summary-all-results.csv')
        summary = None
        for f in Path(os.path.join(cfg['project_path'], 'evaluation-results')).rglob('DLC*.csv'):
            fname = f.name
            net_type = fname.split('_')[1]
            snapshot = fname.split('_')[-1]
            snapshot = snapshot[:snapshot.index('-results')]
            results = pd.read_csv(f.resolve().absolute(), index_col=0)
            results['net_type'] = [net_type] * len(results.index)
            results['snapshot'] = ['snapshot-' + snapshot] * len(results.index)
            results['iteration'] = [f.parent.parent.name] * len(results.index)


            if summary is None:
                summary = results
            else:
                summary = summary.append(results, ignore_index=True)
        summary.to_csv(path_to_csv)
        print('Summary of all files generated in :', path_to_csv,'\n \[\033[32m\]USE THIS SUMMARY TO CONFIGURE YOUR CONFIG.YAML\[\033[m\]')

    def generate_summary(self):

        # READING VALUES:
        cfg = parse_yaml(self.config)
        iteration_selection = self.iteration.GetStringSelection()
        # for example: "[proj-path]/evaluation-results/iteration-0/CombinedEvaluation-results.csv"
        try:
            path_to_csv = os.path.join(cfg['project_path'], 'evaluation-results', iteration_selection, 'CombinedEvaluation-results.csv')
            results = pd.read_csv(path_to_csv, index_col=0)
            columns = results.columns
        except FileNotFoundError as e:
            print(e)
            print('Making empty results table')
            columns = ['Training iterations', '%Training dataset', 'Shuffle number', 'Train error(px)',
                       'Test error(px)',
                       'p-cutoff', 'used', 'Train error with p-cutoff', 'Test error with p-cutoff']
            results = None
        # Create a wxGrid object
        grid = wx.grid.Grid(self.panel, -1)

        # Then we call CreateGrid to set the dimensions of the grid

        grid.CreateGrid(1, len(columns))
        for i, c in enumerate(columns):
            grid.SetColLabelValue(i, c)
        grid.SetRowLabelSize(0)

        if results is not None:
            print('results.ndim = ', results.ndim)
            for j, row in results.iterrows():
                for i, c in enumerate(columns):
                    try:
                        float(str(row[c]))
                        grid.SetColFormatFloat(j, i, 2)
                    except:
                        pass
                    grid.SetCellValue(j, i, str(row[c]))
                    grid.SetReadOnly(j,i)
                print('grid.GetNumberRows() = ', grid.GetNumberRows())
                if j+1 == grid.GetNumberRows() and j+1< len(results):
                    grid.AppendRows()



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
        self.colorBy = wx.Choice(self.panel, -1, choices=['animal color', 'body color'])
        self.colorBy.Disable() if not cfg.get('multianimalproject', False) else None
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
                                   color_by=self.colorBy.GetStringSelection(),
                                   track_method=self.trackMethod.GetStringSelection(),
                                   trailpoints=int(self.trailPoints.GetValue()))
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
        self.listOrPath.SetSelection(0)

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
        files = [f for f in os.listdir(os.path.join(cfg['project_path'], 'dlc-models', iteration)) if not f.startswith('.') and 'contact-model' not in f and 'whisking-model' not in f and 'motion-model' not in f]
        print('files: ', files)
        return files

    def find_snapshots(self):
        training_index, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffle.GetStringSelection())
        return get_snapshots(self.config, shuffle_number, training_index).tolist() + ['latest', 'config.yaml']

    def onSelectShuffleNumber(self, event):
        self.snapshots = self.find_snapshots()
        self.snapshot.SetItems(self.snapshots)
        self.snapshot.SetSelection(len(self.snapshots)-1)

    def onEvaluate(self, event):
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
            d.convert_detections2tracklets(self.config, videos=videos, videotype=self.videoType.GetValue(),
                                           shuffle=shuffle_number, trainingsetindex=trainindex,
                                           track_method=self.trackMethod.GetStringSelection(), overwrite=True)

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
        super(MainFrame, self).__init__(parent, title=title, size=(640, 500))
        self.mainPanel = MainPanel(self)
        topLbl = wx.StaticText(self.mainPanel, -1, "quick DLC")

        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # create main control elements
        # annotation
        box1, items = self.MakeStaticBoxSizer("Annotation",
                                              ['create new project',
                                               'add new videos',
                                               'extract frames',
                                               'detect whiskers',
                                               'label frames',
                                               'label whiskers',
                                               'check annotations'],
                                              size=(200, 25),
                                              type='button')
        items['create new project'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'create new project'))
        items['add new videos'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'add new videos'))
        items['extract frames'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'extract frames'))
        items['detect whiskers'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'detect whiskers'))
        items['label whiskers'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'label whiskers'))

        items['label frames'].Bind(wx.EVT_BUTTON, self.on_label_frames)
        items['check annotations'].Bind(wx.EVT_BUTTON, self.on_check_annotations)

        print(box1.GetChildren())

        # training
        box2, items = self.MakeStaticBoxSizer("Training",
                                              ['create training set', 'train network', 'evaluate network'],
                                              size=(200, 25),
                                              type='button')
        items['create training set'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'create training set'))
        items['train network'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'train network'))
        items['evaluate network'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'evaluate network'))

        # refinement
        box3, items = self.MakeStaticBoxSizer("Refinement",
                                              ['analyze videos', 'refine labels', 'merge datasets', 'create whisking model'],
                                              size=(200, 25),
                                              type='button')
        items['analyze videos'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'analyze videos'))
        items['refine labels'].Bind(wx.EVT_BUTTON, self.OnRefineLabels)
        items['merge datasets'].Bind(wx.EVT_BUTTON, self.OnMergeDataset)
        items['create whisking model'].Bind(wx.EVT_BUTTON, self.onCreateWhiskingModel)
        # config path selection:
        configPathLbl = wx.StaticText(self.mainPanel, -1, "Config path:", size=wx.Size(600, 25))
        cwd = find_yaml()
        self.configPath = wx.FilePickerCtrl(self.mainPanel, -1, cwd, wildcard='*.yaml')
        self.configPath.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_config_path_picked)
        self.startpath = os.getcwd()
        os.chdir(Path(cwd).parent.absolute())

        self.openConfigButton = wx.Button(self.mainPanel, -1, "open config")
        self.openConfigButton.Bind(wx.EVT_BUTTON, self.on_open_config)

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
        openConfigSizer = wx.BoxSizer(wx.HORIZONTAL)
        openConfigSizer.Add(self.openConfigButton)
        mainSizer.Add(openConfigSizer, 0, wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, 10)


        self.mainPanel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150, 25), type='block'):
        box = wx.StaticBox(self.mainPanel, -1, boxlabel)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        items = {}
        for label in itemlabels:
            if type == 'block':
                item = BlockWindow(self.mainPanel, label=label, size=size)
            elif type == 'button':
                item = wx.Button(self.mainPanel, label=label)
            else:
                item = BlockWindow(self.mainPanel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items

    def on_open_config(self, event):
        config_path = self.configPath.GetPath()
        if config_path != "" and os.path.exists(config_path) and config_path.endswith(".yaml"):
            # For mac compatibility
            import platform
            if platform.system() == "Darwin":
                self.file_open_bool = subprocess.call(["open", config_path])
                self.file_open_bool = True
            else:
                self.file_open_bool = webbrowser.open(config_path)

            if self.file_open_bool:
                pass
            else:
                raise FileNotFoundError("Error while opening config.yaml file: " + str(config_path))

    def on_label_frames(self, event):
        print('opening dlc labeling tool box...')
        import deeplabcut as d
        config_path = self.configPath.GetPath()
        d.label_frames(config_path)
        print('Done')

    def on_check_annotations(self, event):
        print('check labels...')
        import deeplabcut as d
        config_path = self.configPath.GetPath()
        config = d.auxiliaryfunctions.read_config(config_path)
        if config.get('multianimalproject', False):
            d.check_labels(config_path, visualizeindividuals=True)
        d.check_labels(config_path, visualizeindividuals=False)
        print('Done')

    def on_new_frame(self, event, frame_type):
        if frame_type is None or len(frame_type) == 0:  # empty string:
            print('new frame not specified in button!! ')
            return
        elif frame_type == 'create new project':
            frame = NewProjectFrame(self.GetParent(), self, config=self.configPath.GetPath())
        elif frame_type == 'add new videos':
            frame = AddNewVideos(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'extract frames':
            frame = ExtractFrames(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'detect whiskers':
            frame = DetectWhiskers(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'create training set':
            frame = CreateTraining(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'train network':
            frame = TrainNetwork(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'evaluate network':
            frame = EvaluaterNetwork(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'analyze videos':
            frame = AnalyzeVideos(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'label whiskers':
            config = parse_yaml(self.configPath.GetPath())
            if config.get('multianimalproject',False):
                frame = MultiLabelWhiskersFrame(self.GetParent(), config=self.configPath.GetPath(),config3d=None, sourceCam=None)
            else:
                frame = LabelWhiskersFrame(self.GetParent(), config=self.configPath.GetPath(), imtypes=["*.png"], config3d=None, sourceCam=None)



        else:
            return
        frame.Show()

    def OnRefineLabels(self, event):
        import deeplabcut as d
        d.refine_labels(self.configPath.GetPath())

    def OnMergeDataset(self, event):
        import deeplabcut as d
        d.merge_datasets(self.configPath.GetPath())

    def onCreateWhiskingModel(self, event):
        frame = ContactModelGeneration(self.Parent, self.startpath, config=self.configPath.GetPath())
        frame.Show()

    def on_config_path_picked(self, event):
        print('===> on config path picked!! ')
        wd = Path(self.configPath.GetPath()).resolve().parents[0]
        os.chdir(str(wd))


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
