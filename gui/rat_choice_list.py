#!/usr/bin/pythonw

import wx
import wx.grid

from gui.main_panel import MainPanel


class RatChoice(wx.Choice):
    CIRCLE_EMOJI = "\u274C"
    RAT_EMOJI = "\U0001F401"
    def __init__(self, parent, id, choices, *args, **kwargs):
        self.choices_strings = choices
        self.choices_unicode = [self.CIRCLE_EMOJI + c for c in self.choices_strings]
        super(RatChoice, self).__init__(parent, id, choices=self.choices_unicode, *args, **kwargs)

    def make_rat(self, choice_index):
        if choice_index > len(self.choices_unicode)-1:
            raise IndexError(f'Index out of range list of choices has {len(self.choices_unicode)} elemnent')
        self.choices_unicode[choice_index] = self.RAT_EMOJI + self.choices_strings[choice_index]
        selection = self.GetSelection()
        self.SetItems(self.choices_unicode)
        self.SetSelection(selection)

    def make_circle(self, choice_index):
        if choice_index > len(self.choices_unicode)-1:
            raise IndexError(f'Index out of range list of choices has {len(self.choices_unicode)} elemnent')
        self.choices_unicode[choice_index] = self.CIRCLE_EMOJI + self.choices_strings[choice_index]
        selection = self.GetSelection()
        self.SetItems(self.choices_unicode)
        self.SetSelection(selection)


class ChoiceList(wx.Frame):
    def __init__(self, parent, title='choice check box'):
        super(ChoiceList, self).__init__(parent, title=title, size=(640,500))
        self.panel = MainPanel(self)
        # self.panel = ImagePanel(window, config, self.gui_size)
        topLbl = wx.StaticText(self.panel, -1, "Extract frames")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        ratChoiceLbl = wx.StaticText(self.panel, -1, "Select a rat video to process:")
        self.ratChoice = RatChoice(self.panel, 1, choices=['a', 'b', 'c'])

        # button to create project
        buttonProcess = wx.Button(self.panel, label="Extract")
        buttonProcess.Bind(wx.EVT_BUTTON, self.onUpdate)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # horizontal sizer inside the main sizer
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND | wx.TOP, 5)

        # inputs sizer:
        inputSizer = wx.BoxSizer(wx.VERTICAL)

        inputSizer.Add(ratChoiceLbl, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(self.ratChoice, 0, wx.EXPAND | wx.ALL, 2)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonProcess, 0, wx.CENTER | wx.ALL, 15)

        # finally set sizer and configure window behavior
        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def onUpdate(self, event):
        index =self.ratChoice.GetSelection()
        self.ratChoice.make_rat(index)


def show(config, startpath='.'):
    app = wx.App()
    frame = ChoiceList(None)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    show(None)
