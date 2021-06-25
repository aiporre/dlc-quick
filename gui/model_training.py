import os
from pathlib import Path

import wx

from deeplabcut.gui.widgets import WidgetPanel, BaseFrame
from deeplabcut.utils import auxiliaryfunctions

from gui.utils import parse_yaml
from gui.utils.parse_yaml import write_whisking_config

from whisker_touch_pred.touch.touch import Trainer
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
        self.training_config_path = os.path.join(self.project_path, 'dlc-models', self.iterations[self.iteration.GetSelection()],'contact-model', 'contact.yaml')
        # Read the training config. If the program doesn't exists it creates a default
        self.training_cfg = WhiskerModelTraining.read_config(self.training_config_path)

        # CheckBox activate eager mode
        enableEagerLbl = wx.StaticText(self.panel, -1, "Enable Eager")
        self.enableEager = wx.CheckBox(self.panel, -1, "")
        self.enableEager.SetValue(self.training_cfg['enable_eager'])

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

        # The shuffle to create random batches
        shuffleBufferLbl = wx.StaticText(self.panel, -1, "Size of buffer to make shuffle after each epoch:")
        self.shuffleBuffer = wx.TextCtrl(self.panel, -1, str(self.training_cfg["shuffle_buffer"]))
        self.shuffleBuffer.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffleBuffer))

        # Text control to define number of epoch to train.
        epochNumberLbl = wx.StaticText(self.panel, -1, "Number of epochs to train:")
        self.epochNumber = wx.TextCtrl(self.panel, -1, '10')
        self.epochNumber.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffleBuffer))

        # Check-Box to activate caching samples to improve training speed
        cacheLbl = wx.StaticText(self.panel, -1, "Enable cache of dataset while reading? ")
        self.cache = wx.CheckBox(self.panel, -1, "")
        self.cache.SetValue(self.training_cfg['cache'])

        # define a SpinControl define training/test rate between 10% and 90%
        splitRateLbl = wx.StaticText(self.panel, -1, "Training vs Test split rate")
        self.splitRate = wx.SpinCtrlDouble(self.panel, id=-1, min=0.1, max=0.9,
                                                          initial=self.training_cfg['split_rate'], inc=0.05)

        # Path to the init-weights. Initial path if formed in the training_config_path with the name of the training
        # config.
        initialWeigthsLbl = wx.StaticText(self.panel, -1, "Initial weigths path:", size=wx.Size(self.gui_size[0], 25))
        self.initialWeigths = wx.FilePickerCtrl(self.panel, -1)
        initial_weights_path =os.path.join(os.path.dirname(self.training_config_path), self.training_cfg['init_weights'])
        if not os.path.exists(initial_weights_path):
            initial_weights_path = ''
        self.initialWeigths.SetPath(initial_weights_path)

        # Initial datapath calculation, same as the training, it taked form the training config file or
        # form the one in training datasets, at the given iteration.
        # training_config_file overrides this initial value calculated.
        datapathLbl = wx.StaticText(self.panel, -1, "Dataset path:", size=wx.Size(self.gui_size[0], 25))
        self.datapath = wx.DirPickerCtrl(self.panel, -1)
        datapath_initial = os.path.join(self.project_path, 'training-datasets', self.iterations[self.iteration.GetSelection()],'contact-dataset')

        if len(self.training_cfg['datapath']) == 0  and os.path.exists(datapath_initial):
            self.datapath.SetPath(datapath_initial)
            self.training_cfg['datapath'] = datapath_initial
            write_whisking_config(self.training_config_path, self.training_cfg)
        else:
            self.datapath.SetPath(self.training_cfg['datapath'])

        # button to create dataset object in the trainer, also saves the training config with the given parameters.
        self.buttonSaveConfig = wx.Button(self.panel, label="Save Configuration")
        self.buttonSaveConfig.Bind(wx.EVT_BUTTON, self.onSaveConfig)

        # button to plot 16 images of the datatset, batchsize has no influence in that
        self.buttonShowBatch = wx.Button(self.panel, label="Show Batch")
        self.buttonShowBatch.Bind(wx.EVT_BUTTON, self.onShowBatch)

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
        inputSizer = wx.BoxSizer(wx.VERTICAL)

        # adding stuff to the inputsizer, i.e. buttons checkboxes.. etc.
        inputSizer.Add(iterationLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.iteration, 0, wx.EXPAND, 2)

        inputSizer.Add(datapathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.datapath, 0, wx.EXPAND, 2)

        inputSizer.Add(enableEagerLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.enableEager, 0, wx.EXPAND, 2)

        inputSizer.Add(imageDimHeightLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.imageDimHeight, 0, wx.EXPAND, 2)

        inputSizer.Add(imageDimWidthLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.imageDimWidth, 0, wx.EXPAND, 2)

        inputSizer.Add(batchSizeLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.batchSize, 0, wx.EXPAND, 2)

        inputSizer.Add(cacheLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.cache, 0, wx.EXPAND, 2)

        inputSizer.Add(shuffleBufferLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.shuffleBuffer, 0, wx.EXPAND, 2)

        inputSizer.Add(splitRateLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.splitRate, 0, wx.EXPAND, 2)

        inputSizer.Add(initialWeigthsLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.initialWeigths, 0, wx.EXPAND, 2)

        inputSizer.Add(epochNumberLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.epochNumber, 0, wx.EXPAND, 2)

        # adding buttons

        buttonSizer.Add(self.buttonSaveConfig, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonShowBatch, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonTrainModel, 0, wx.CENTER | wx.ALL, 15)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonSizer, 0, wx.CENTER, 15)
        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

        self.buttonShowBatch.Enable(False)
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
        tf.enable_eager_execution()
        model_output_path = Path(self.training_config_path).parent.resolve().absolute()
        self.model_trainer = Trainer(self.training_cfg['datapath'],
                enable_eager=self.training_cfg['enable_eager'],
                img_height=self.training_cfg['image_dim_height'],
                img_width=self.training_cfg['image_dim_width'],
                batch_size=self.training_cfg['batch_size'],
                learning_rate=self.training_cfg['learning_rate'],
                output_path=model_output_path)
        self.model_trainer.create_dataset()
        self.model_trainer.prepare_for_training(
                cache=self.training_cfg['cache'],
                shuffle_buffer_size=self.training_cfg['shuffle_buffer']).\
            split_training(
                rate=self.training_cfg['split_rate']).\
            create_model(init_weights=
                self.initialWeigths.GetPath())
        # enabling buttons:
        self.buttonShowBatch.Enable(True)
        self.buttonTrainModel.Enable(True)

    def onShowBatch(self, event):
        print('show batch: :) ')
        if not hasattr(self, 'model_trainer'):
            return
        print('plot bactch')
        self.model_trainer.show_batch()

    def onTrainModel(self, event):
        print('train model: :) ')
        if not hasattr(self, 'model_trainer'):
            return
        self.model_trainer.EPOCHS = int(self.epochNumber.GetValue())
        self.model_trainer.train_model()
        self.model_trainer.score()

    @staticmethod
    def read_config(configpath):
        if os.path.exists(configpath):
            config = parse_yaml(configpath)
        else:
            config = {}
            config['datapath'] = ''
            config['enable_eager'] = True
            config['image_dim_width'] = 100
            config['image_dim_height'] = 100
            config['batch_size'] = 32
            config['learning_rate'] = 0.01
            config['display_iter'] = 5
            config['cache'] = True
            config['shuffle_buffer'] = 1000
            config['split_rate'] = 0.9
            config['init_weights']='bw_best.h5'
            parent = Path(configpath).parent.resolve().absolute()
            if not os.path.exists(parent):
                os.makedirs(parent)
            write_whisking_config(configpath, config)
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





def show(config, startpath='.'):
    app = wx.App()
    frame = WhiskerModelTraining(None, config=config).Show()
    app.MainLoop()



if __name__ == '__main__':
    config = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config, startpath)