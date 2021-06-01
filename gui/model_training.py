import os
from pathlib import Path

import wx

from deeplabcut.gui.widgets import WidgetPanel, BasePanel, BaseFrame
from deeplabcut.utils import auxiliaryfunctions

from gui.utils import parse_yaml
from gui.utils.parse_yaml import write_whisking_config


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
        try:
            self.iteration.SetSelection(self.iterations.index(current_iteration))
        except ValueError as e:
            print('Error' + str(e))
            self.iteration.SetSelection(0)

        # reading training config for autofill:
        self.project_path = cfg['project_path']
        training_config_path = os.path.join(self.project_path, 'dlc-models', self.iterations[self.iteration.GetSelection()],'contact-model', 'contact.yaml')
        training_cfg = WhiskerModelTraining.read_config(training_config_path)

        enableEagerLbl = wx.StaticText(self.panel, -1, "Enable Eager")
        self.enableEager = wx.CheckBox(self.panel, -1, "")
        self.enableEager.SetValue(training_cfg['enable_eager'])


        enableLastChannelLbl = wx.StaticText(self.panel, -1, "Enable Last Channel")
        self.enableLastChannel = wx.CheckBox(self.panel, -1, "")
        self.enableLastChannel.SetValue(training_cfg['enable_last_channel'])

        imageDimWidthLbl = wx.StaticText(self.panel, -1, "Image width input to the network")
        self.imageDimWidth = wx.TextCtrl(self.panel, -1, str(training_cfg["image_dim_width"]))
        self.imageDimWidth.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.imageDimWidth))

        imageDimHeightLbl = wx.StaticText(self.panel, -1, "Image height input to the network")
        self.imageDimHeight = wx.TextCtrl(self.panel, -1, str(training_cfg["image_dim_height"]))
        self.imageDimHeight.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.imageDimHeight))

        batchSizeLbl = wx.StaticText(self.panel, -1, "Batch size")
        self.batchSize = wx.TextCtrl(self.panel, -1, str(training_cfg["batch_size"]))
        self.batchSize.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.batchSize))

        shuffleBufferLbl = wx.StaticText(self.panel, -1, "Size of buffer to make shuffle after each epoch:")
        self.shuffleBuffer = wx.TextCtrl(self.panel, -1, str(training_cfg["shuffle_buffer"]))
        self.shuffleBuffer.Bind(wx.EVT_CHAR, lambda event: self.force_numeric_int(event, self.shuffleBuffer))


        cacheLbl = wx.StaticText(self.panel, -1, "Enable cache of dataset while reading? ")
        self.cache = wx.CheckBox(self.panel, -1, "")
        self.cache.SetValue(training_cfg['cache'])

        splitRateLbl = wx.StaticText(self.panel, -1, "Training vs Test split rate")
        self.splitRate = wx.SpinCtrlDouble(self.panel, id=-1, min=0.1, max=0.9,
                                                          initial=training_cfg['split_rate'], inc=0.05)

        # check box to select automatic or manual selection
        initialWeigthsLbl = wx.StaticText(self.panel, -1, "Initial weigths path:", size=wx.Size(self.gui_size[0], 25))
        self.initialWeigths = wx.FilePickerCtrl(self.panel, -1)
        self.initialWeigths.SetPath(os.path.join(os.path.dirname(training_config_path), training_cfg['init_weights']))

        # button to create dataset object in the trainer
        buttonSaveConfig = wx.Button(self.panel, label="Save Configuration")
        buttonSaveConfig.Bind(wx.EVT_BUTTON, self.onSaveConfig)

        # button to plot 16 images of the datatset, batchsize has no influence in that
        buttonShowBatch = wx.Button(self.panel, label="Show Batch")
        buttonShowBatch.Bind(wx.EVT_BUTTON, self.onShowBatch)

        # button to train model
        buttonTrainModel = wx.Button(self.panel, label="Train Model")
        buttonTrainModel.Bind(wx.EVT_BUTTON, self.onTrainModel)


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

        inputSizer.Add(enableEagerLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.enableEager, 0, wx.EXPAND, 2)

        inputSizer.Add(enableLastChannelLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.enableLastChannel, 0, wx.EXPAND, 2)

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

        # adding buttons

        buttonSizer.Add(buttonShowBatch, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(buttonSaveConfig, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(buttonTrainModel, 0, wx.CENTER | wx.ALL, 15)

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

    def find_iterations(self):
        '''find the iterations given a config file.'''
        # import deeplabcut
        # cfg = deeplabcut.auxiliaryfunctions.read_config(self.config)
        config = parse_yaml(self.config)
        iterations = [ f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models')) if 'iteration' in f]
        return iterations

    def onSaveConfig(self, event):
        print('saving config dataset: :) ')
        # from whisking_detection.touch import Trainer
        # self.model_trainer = Trainer(self.training_cfg['datatapath'],
        #         enable_eager=self.training_cfg['enable_eager'],
        #         enable_channel_last=self.training_cfg['enable_channel_last'],
        #         img_height=self.training_cfg['image_dim_height'],
        #         img_width=self.training_cfg['image_dim_width'],
        #         batch_size=self.training_cfg['batch_size'])
        self.model_trainer = None


    def onShowBatch(self, event):
        print('show batch: :) ')

    def onTrainModel(self, event):
        print('train model: :) ')


    @staticmethod
    def read_config(configpath):
        if os.path.exists(configpath):
            config = parse_yaml(configpath)
        else:
            config = {}
            config['enable_eager'] = True
            config['enable_last_channel'] = True
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