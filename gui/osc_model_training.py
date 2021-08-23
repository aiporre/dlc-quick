import os
from pathlib import Path

import wx

from deeplabcut.gui.widgets import WidgetPanel, BaseFrame
from deeplabcut.utils import auxiliaryfunctions

from gui.utils import parse_yaml
from gui.utils.parse_yaml import write_whisking_config

from whisker_osc_pred.osc.oscillation import Trainer
import tensorflow as tf


class WhiskerModelTraining(BaseFrame):
    def __init__(self, parent, title='Training Whisker Model', config=None):
        super(WhiskerModelTraining, self).__init__(parent=parent, frame_title=title)
        self.panel = WidgetPanel(self)
        self.WIDTHOFINPUTS = 100
        self.config = config

        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Training Whisker Model")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # choice iteration from configuration file
        cfg = parse_yaml(self.config)
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        current_iteration = 'iteration-' + str(cfg['iteration'])
        self.iterations = self.find_iterations()
        assert len(self.iterations) > 0, "Couldn't find an iteration, you must train a dlc-model first."

        self.iteration = wx.Choice(self.panel, id=-1, choices=self.iterations)
        # sets the current interation from the config.yaml file.
        try:
            self.iteration.SetSelection(self.iterations.index(current_iteration))
        except ValueError as e:
            print('Error' + str(e))
            self.iteration.SetSelection(0)

        # Reading training config for autofill:
        self.project_path = cfg['project_path']
        # the training config file, named "contact.yaml" is saved on the dlc-models/itertiation../contact-model
        self.training_config_path = os.path.join(self.project_path, 'dlc-models', self.iterations[self.iteration.GetSelection()],'osc-model', 'osc.yaml')
        # Read the training config. If the program doesn't exists it creates a default
        self.training_cfg = WhiskerModelTraining.read_config(self.training_config_path)

        # text control to set num of frames to crop or fill in the dataset configuraiton
        numFramesLbl = wx.StaticText(self.panel, -1, "Num Frames")
        self.numFrames = wx.TextCtrl(self.panel, -1, str(self.training_cfg['num_frames']))
        self.numFrames.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.numFrames))


        # define dimenstion of the of input to the image
        imageDimWidthLbl = wx.StaticText(self.panel, -1, "Image width input to the network")
        self.imageDimWidth = wx.TextCtrl(self.panel, -1, str(self.training_cfg["image_dim_width"]))
        self.imageDimWidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.imageDimWidth))

        imageDimHeightLbl = wx.StaticText(self.panel, -1, "Image height input to the network")
        self.imageDimHeight = wx.TextCtrl(self.panel, -1, str(self.training_cfg["image_dim_height"]))
        self.imageDimHeight.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.imageDimHeight))

        # text control to change batch size
        batchSizeLbl = wx.StaticText(self.panel, -1, "Batch size")
        self.batchSize = wx.TextCtrl(self.panel, -1, str(self.training_cfg["batch_size"]))
        self.batchSize.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.batchSize))

        # text control to change learning rate
        learningRateLbl = wx.StaticText(self.panel, -1, "Learning Rate")
        self.learningRate = wx.TextCtrl(self.panel, -1, str(self.training_cfg["learning_rate"]))
        self.learningRate.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_float(event, self.learningRate))

        # The shuffle to create random batches
        shuffleBufferLbl = wx.StaticText(self.panel, -1, "Size of buffer to make shuffle after each epoch:")
        self.shuffleBuffer = wx.TextCtrl(self.panel, -1, str(self.training_cfg["shuffle_buffer"]))
        self.shuffleBuffer.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffleBuffer))

        # num of parallel calls for reading the dataset fast
        numParallelCallsLbl = wx.StaticText(self.panel, -1, "number of threads while reading the dataset (-1 = autotune):")
        self.numParallelCalls = wx.SpinCtrl(self.panel, min=-1, max=1000, initial = self.training_cfg["num_parallel_calls"])

        # Text control to define number of epoch to train.
        epochNumberLbl = wx.StaticText(self.panel, -1, "Number of epochs to train:")
        self.epochNumber = wx.TextCtrl(self.panel, -1, '10')
        self.epochNumber.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffleBuffer))

        # Check-Box to activate caching samples to improve training speed
        cacheLbl = wx.StaticText(self.panel, -1, "Enable cache of dataset while reading? ")
        self.cache = wx.CheckBox(self.panel, -1, "")
        self.cache.SetValue(self.training_cfg['cache'])

        randomCropLbl = wx.StaticText(self.panel, -1, "Random crop images or resize? ")
        self.randomCrop = wx.CheckBox(self.panel, -1, "")
        self.randomCrop.SetValue(self.training_cfg['random_crop'])

        # define a SpinControl define training/test rate between 10% and 90%
        splitRateLbl = wx.StaticText(self.panel, -1, "Training vs Test split rate")
        self.splitRate = wx.SpinCtrlDouble(self.panel, id=-1, min=0.1, max=0.9,
                                                          initial=self.training_cfg['split_ratio'], inc=0.05)

        # fc_layers configuration

        self.listIndex = 0
        fcLayersLbl = wx.StaticText(self.panel, -1,
                                     "FC layers configuration before output layer and after the LSTM:")
        self.fcLayers = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
        self.fcLayers.InsertColumn(0, "index", format=wx.LIST_FORMAT_CENTRE, width=0.25 * self.gui_size[0])
        self.fcLayers.InsertColumn(1, "units", format=wx.LIST_FORMAT_CENTRE,
                                    width=0.25 * self.gui_size[0])

        fcLayers = self.training_cfg.get('multi_step', [['0', '4096'], ['1', '4096']])
        for index, fclayer in fcLayers:
            self.fcLayers.InsertItem(self.listIndex, str(index))
            self.fcLayers.SetItem(self.listIndex, 1, str(fclayer))
            self.listIndex += 1

        buttonAdd = wx.Button(self.panel, label="Add step")
        buttonAdd.Bind(wx.EVT_BUTTON, self.onAddStep)

        buttonRemove = wx.Button(self.panel, label="Remove step")
        buttonRemove.Bind(wx.EVT_BUTTON, self.onRemoveStep)

        # LSTM units configuration
        lstmUnitssLbl = wx.StaticText(self.panel, -1, "Number of lstm units:")
        self.lstmUnits = wx.TextCtrl(self.panel, -1, str(self.training_cfg["lstm_units"]))
        self.lstmUnits.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.lstmUnits))

        # base net
        baseNetLbl = wx.StaticText(self.panel, -1, "choice to feature extraction network:")
        self.baseNet = wx.Choice(self.panel, -1, choices=['alexnet', 'vgg16', 'resnet50'])
        self.baseNet.SetSelection(0)

        # net_id associated with metastate that will load the best weights from there
        netIdsLbl = wx.StaticText(self.panel, -1, "Net_id to load weights:", size=wx.Size(int(0.3*self.gui_size[0]), 25))
        self.net_ids = self.get_model_ids() + ['auto', 'custom']
        self.netIdsChoice = wx.Choice(self.panel, -1, choices = self.net_ids)
        self.netIdsChoice.SetSelection(0)

        customNetIdLbl = wx.StaticText(self.panel, -1 , "Define a new name for you model save weights")
        self.customNetId = wx.TextCtrl(self.panel, -1, "", size=wx.Size(int(0.3*self.gui_size[0]), 25))
        self.customNetId.Bind(wx.EVT_CHAR, lambda event: self.force_alpha_numeric(event, self.customNetId))

        # Initial datapath calculation, same as the training, it took from the training config file or
        # form the one in training datasets, at the given iteration.
        # training_config_file overrides this initial value calculated.
        datapathLbl = wx.StaticText(self.panel, -1, "Dataset path:", size=wx.Size(int(0.8*self.gui_size[0]), 25))
        self.datapath = wx.DirPickerCtrl(self.panel, -1)
        datapath_initial = os.path.join(self.project_path, 'training-datasets', self.iterations[self.iteration.GetSelection()],'osc-dataset')

        if len(self.training_cfg['datapath']) == 0  and os.path.exists(datapath_initial):
            self.datapath.SetPath(datapath_initial)
            self.training_cfg['datapath'] = datapath_initial
            write_whisking_config(self.training_config_path, self.training_cfg, project_type='osc')
        else:
            self.datapath.SetPath(self.training_cfg['datapath'])

        # button to create dataset object in the trainer, also saves the training config with the given parameters.
        self.buttonSaveConfig = wx.Button(self.panel, label="Save Configuration")
        self.buttonSaveConfig.Bind(wx.EVT_BUTTON, self.onSaveConfig)


        # button to train model
        self.buttonTrainModel = wx.Button(self.panel, label="Train Model")
        self.buttonTrainModel.Bind(wx.EVT_BUTTON, self.onTrainModel)

        # create the main sizer that contains the context and input sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer= wx.BoxSizer(wx.HORIZONTAL)
        inputRightSizer = wx.BoxSizer(wx.VERTICAL)
        inputLeftSizer = wx.BoxSizer(wx.VERTICAL)

        # adding stuff to the inputsizer, i.e. buttons checkboxes.. etc.
        mainSizer.Add(iterationLbl, 0, wx.ALIGN_CENTER | wx.ALL, 2)
        mainSizer.Add(self.iteration, 0, wx.ALIGN_CENTER | wx.ALL, 2)

        mainSizer.Add(datapathLbl, 0, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add(self.datapath, 0, wx.EXPAND | wx.ALL, 2)

        inputRightSizer.Add(numFramesLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.numFrames, 0, wx.EXPAND, 2)

        inputRightSizer.Add(imageDimHeightLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.imageDimHeight, 0, wx.EXPAND, 2)

        inputRightSizer.Add(imageDimWidthLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.imageDimWidth, 0, wx.EXPAND, 2)

        inputRightSizer.Add(batchSizeLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.batchSize, 0, wx.EXPAND, 2)

        inputRightSizer.Add(learningRateLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.learningRate, 0, wx.EXPAND, 2)

        inputRightSizer.Add(cacheLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.cache, 0, wx.EXPAND, 2)

        inputRightSizer.Add(shuffleBufferLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.shuffleBuffer, 0, wx.EXPAND, 2)

        inputRightSizer.Add(splitRateLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.splitRate, 0, wx.EXPAND, 2)

        inputRightSizer.Add(epochNumberLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.epochNumber, 0, wx.EXPAND, 2)

        inputRightSizer.Add(randomCropLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.randomCrop, 0, wx.EXPAND, 2)

        inputRightSizer.Add(numParallelCallsLbl, 0, wx.EXPAND, 2)
        inputRightSizer.Add(self.numParallelCalls, 0, wx.EXPAND, 2)

        inputLeftSizer.Add(fcLayersLbl, 0, wx.EXPAND, 2)
        inputLeftSizer.Add(self.fcLayers, 0, wx.EXPAND, 2)

        fcLayersSizer = wx.BoxSizer(wx.HORIZONTAL)
        fcLayersSizer.Add(buttonAdd, 0, wx.EXPAND | wx.ALIGN_CENTER, 2)
        fcLayersSizer.Add(buttonRemove, 0, wx.EXPAND | wx.ALIGN_CENTER, 2)
        inputLeftSizer.Add(fcLayersSizer, 0, wx.LEFT, 2 )

        inputLeftSizer.Add(lstmUnitssLbl, 0, wx.LEFT, 2)
        inputLeftSizer.Add(self.lstmUnits, 0, wx.LEFT, 2)

        inputLeftSizer.Add(baseNetLbl, 0, wx.LEFT, 2)
        inputLeftSizer.Add(self.baseNet, 0, wx.LEFT, 2)

        inputLeftSizer.Add(netIdsLbl, 0, wx.LEFT, 2)
        inputLeftSizer.Add(self.netIdsChoice, 0, wx.LEFT, 2)

        inputLeftSizer.Add(customNetIdLbl, 0, wx.LEFT, 2)
        inputLeftSizer.Add(self.customNetId, 0, wx.LEFT, 2)
        # adding buttons

        buttonSizer.Add(self.buttonSaveConfig, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonTrainModel, 0, wx.CENTER | wx.ALL, 15)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputRightSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputLeftSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonSizer, 0, wx.CENTER, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

        self.buttonTrainModel.Enable(False)

    def find_iterations(self):
        '''find the iterations given a config file.'''
        # import deeplabcut
        # cfg = deeplabcut.auxiliaryfunctions.read_config(self.config)
        config = parse_yaml(self.config)
        iterations = [f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models')) if 'iteration' in f]
        return iterations

    def onSaveConfig(self, event):
        print('saving config dataset: :) ')
        # the model_output_path is where the weights and logs are saved
        model_output_path = Path(self.training_config_path).parent.resolve().absolute()
        # applies configurations
        self.training_cfg['datapath'] = self.datapath.GetPath()
        self.training_cfg['num_frames'] = int(self.numFrames.GetValue())
        self.training_cfg['image_dim_height'] = int(self.imageDimHeight.GetValue())
        self.training_cfg['image_dim_width'] = int(self.imageDimWidth.GetValue())
        self.training_cfg['batch_size'] = int(self.batchSize.GetValue())
        self.training_cfg['learning_rate'] = float(self.learningRate.GetValue())
        self.training_cfg['fc_layers'] = self.get_fc_layers()
        self.training_cfg['base_net'] = self.baseNet.GetStringSelection()
        self.training_cfg['lstm_units'] = int(self.lstmUnits.GetValue())
        self.training_cfg['epochs'] = int(self.epochNumber.GetValue())
        self.training_cfg['split_ratio'] = self.splitRate.GetValue()
        self.training_cfg['random_crop'] = self.randomCrop.GetValue()
        self.training_cfg['num_parallel_calls' ] = self.numParallelCalls.GetValue()
        self.training_cfg['cache'] = self.cache.GetValue()
        self.training_cfg['shuffle_buffer'] = int(self.shuffleBuffer.GetValue())
        write_whisking_config(self.training_config_path, self.training_cfg, project_type='osc')
        self.model_trainer = Trainer(self.training_cfg['datapath'],
                                     output_path=model_output_path,
                                     num_frames=self.training_cfg['num_frames'],
                                     img_height=self.training_cfg['image_dim_height'],
                                     img_width=self.training_cfg['image_dim_width'],
                                     batch_size=self.training_cfg['batch_size'],
                                     learning_rate=self.training_cfg['learning_rate'],
                                     epochs=self.training_cfg['epochs'],
                                     split_ratio=self.training_cfg['split_ratio']
                                     )
        self.model_trainer.create_dataset(random_crop=self.training_cfg['random_crop'],
                                          num_parallel_calls=self.training_cfg['num_parallel_calls'])
        self.model_trainer.prepare_for_training(
                cache=self.training_cfg['cache'],
                shuffle_buffer_size=self.training_cfg['shuffle_buffer'])
        model_id, date = self.get_model_id() # gets model id from selection
        self.model_trainer.create_model(model_id=model_id, date= date, fc_layers=self.training_cfg['fc_layers'] + [2],
                                        lstm_units=self.training_cfg['lstm_units'], base_net=self.training_cfg['base_net'])
        # enabling buttons:
        self.buttonTrainModel.Enable(True)

    def get_model_id(self):
        def get_date_from_model_id(model_id):
            return '-'.join(model_id.split('-')[-6:])

        def get_net_id(model_id, date):
            return model_id[:model_id.index(date) - 1]

        if self.netIdsChoice.GetStringSelection() == 'auto':
            net_id = ''
            date = None
        elif self.netIdsChoice.GetStringSelection() == 'custom':
            # custom enables a field to write what you want valid path stuff restritect
            net_id = self.customNetId.GetValue()
            date = None
        else:
            model_id = self.netIdsChoice.GetStringSelection()
            date = get_date_from_model_id(model_id)
            net_id = get_net_id(model_id, date)
        return net_id, date

    def get_fc_layers(self):
        fc_layers = []
        for row in range(self.fcLayers.GetItemCount()):
            try:
                item = int(self.fcLayers.GetItemText(row,col=1))
                fc_layers.append(item)
            except ValueError as e:
                print('Error parsing the fc layers: ', e)
        if len(fc_layers) == 0:
            raise Exception('fc layers failed to parse. Check the values, must be int')

        return fc_layers

    def get_model_ids(self):
        model_saved_path = Path(self.training_config_path).parent.joinpath('models').resolve().absolute()
        model_ids_available = [ os.path.splitext(f)[0][len('model_'):] for f in os.listdir(model_saved_path) if f.startswith('model_')]
        # def get_date_from_model_id(model_id):
        #     return  '-'.join(model_id.split('-')[-6:])
        # def get_net_id(model_id, date):
        #     return model_id[:model_id.index(date)-1]
        # dates = [ get_date_from_model_id(model_id) for model_id in model_ids_available]
        # net_ids = [get_net_id(model_id, date) for model_id, date in zip(model_ids_available, dates)]
        return model_ids_available

    def onShowBatch(self, event):
        print('Not implemented')
        # if not hasattr(self, 'model_trainer'):
        #     return
        # print('plot bactch')
        # self.model_trainer.show_batch()

    def onTrainModel(self, event):
        print('train model: :) ')
        if not hasattr(self, 'model_trainer'):
            return
        self.model_trainer.train_model()
        self.model_trainer.score()

    @staticmethod
    def read_config(configpath):
        if os.path.exists(configpath):
            config = parse_yaml(configpath)
        else:
            config = {}
            config['datapath'] = ''
            config['num_frames'] = 60
            config['image_dim_width'] = 224
            config['image_dim_height'] = 224
            config['batch_size'] = 32
            config['learning_rate'] = 0.01
            config['display_iter'] = 5
            config['cache'] = True
            config['shuffle_buffer'] = 1000
            config['split_ratio'] = 0.9
            config['init_weights']='auto'
            config['epochs'] = 100
            config['split_ratio'] = 0.9
            config['random_crop'] = True
            config['num_parallel_calls'] = -1
            config['fc_layers'] = [4096, 4096]
            config['lstm_units'] = 32
            config['base_net'] = 'alexnet'

            parent = Path(configpath).parent.resolve().absolute()
            if not os.path.exists(parent):
                os.makedirs(parent)
            write_whisking_config(configpath, config, project_type='osc')
        return  config

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

    def force_alpha_numeric(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isalnum() or keycode == 8 or chr(keycode) == '_' or chr(keycode) == '-':
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()

    def onAddStep(self, event):
        def onOk(event, parent, frame):
            parent.fcLayers.InsertItem(parent.listIndex, str(parent.listIndex))
            parent.fcLayers.SetItem(parent.listIndex, 1, frame.units.GetValue())
            parent.listIndex += 1
            frame.Close()

        dialog = wx.Dialog(self, id=-1, title="Add new layer")
        dialog.Bind(wx.EVT_BUTTON, lambda event: onOk(event, self, dialog), id=wx.ID_OK)
        mainSizerDialog = wx.BoxSizer(wx.VERTICAL)
        field1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        unitsLbl = wx.StaticText(dialog, -1, "fc layer units")
        dialog.units = wx.TextCtrl(dialog, -1, '4096')
        dialog.units.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, dialog.units))
        field1Sizer.Add(unitsLbl, 2, wx.CENTER | wx.ALL, 2)
        field1Sizer.Add(dialog.units, 2, wx.CENTER | wx.ALL, 2)

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
        item_id = self.fcLayers.GetFirstSelected(self)
        if item_id == -1:
            item_id = self.listIndex - 1

        print("removing entry : ", item_id)
        self.fcLayers.DeleteItem(item_id)
        # update listIndex
        self.listIndex = self.listIndex - 1






def show(config, startpath='.'):
    app = wx.App()
    frame = WhiskerModelTraining(None, config=config).Show()
    app.MainLoop()



if __name__ == '__main__':
    config = r'D:\behaviorVids\projects-whisker\wtfree5ma-dlc2\wtfree5ma-agkuner-2021-06-25\config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config, startpath)