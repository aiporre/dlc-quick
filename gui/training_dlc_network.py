import os
import sys

import wx

from gui.utils.parse_yaml import extractTrainingIndexShuffle
from gui.utils.main_panel import MainPanel
from gui.utils.generic import parser_yaml, get_available_gpus


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
        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices=['None'] + get_available_gpus())
        self.gpusAvailable.SetSelection(0)

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
        inputSizerCenter.Add(gpusAvailableLbl,0,wx.EXPAND, 2)
        inputSizerCenter.Add(self.gpusAvailable, 0, wx.EXPAND,2 )
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
        if self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()) == 'None':
            gputouse = None
        else:
            gputouse = int(self.gpusAvailable.GetStringSelection())

        d.train_network(self.config, shuffle=shuffle, trainingsetindex=trainingIndex, maxiters=int(self.max_iters.GetValue()), displayiters=pose_config['display_iters'],
                        saveiters=pose_config['save_iters'], gputouse=gputouse)
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
        files = [ f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models', iteration_selection)) if not f.startswith('.') and 'contact-model' not in f and 'whisking-model' not in f and 'motion-model' not in f and 'osc-model' not in f]
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