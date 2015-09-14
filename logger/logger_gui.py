# logger_gui.py
#
# A simple wxPython GUI to control the fridge logging code and (eventually) make
# diagnostic plots of the temperature readings.
#
# Adam Anderson
# adama@fnal.gov
# 14 September 2015

import wx

class LoggerWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, size=(350,200))

app = wx.App(redirect=True)
log_window = LoggerWindow("Hello World")
log_window.Show()
app.MainLoop()
