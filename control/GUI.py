# GUI.py
#
# Main control panel for a "He10" fridge. With the exception of the fridge cycle
# code, this script is basic, standalone wxPython. Since the fridge cycle is a
# long running process, it is handled as a separate thread and code is located
# in the autocycle module. In order to keep the UI responsive and to update the
# log during the cycle, the thread must be non-blocking, which is implemented
# using threading events and wxPython events.
#
# Adam Anderson
# adama@fnal.gov

import wx
import wx.lib.newevent
import os
import time
import datetime
import threading
import autocycle
import powersupply

LoggingEvent, EVT_LOGGING = wx.lib.newevent.NewEvent()

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        # event object which lets the user kill the autocycle
        self.abortcycle = threading.Event()
        self.abortcycle.set()

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(400, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # bind logging event to function that updates the log
        self.Bind(EVT_LOGGING, self.logging_action)

        # text box to set the data file path
        self.dataFileBoxLabel = wx.StaticText(self, -1, "Fridge log file:")
        self.dataFileBox = wx.TextCtrl(self, -1, "none selected", size=(200, 30), style=wx.TE_READONLY)
        self.dataFileButton = wx.Button(self, -1, 'choose file')

        # make log box
        self.logBox = wx.TextCtrl(self, -1,'', wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)
        self.logBox.SetEditable(False)

        # bind file selector button to function
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.dataFileButton)

        # text box and buttons for controlling pump voltages
        self.he4icpumptext = wx.StaticText(self, label='4He IC Pump \n [-25V - 0V]')
        self.he4IC_voltage_scroll = wx.TextCtrl(self, -1, "0.00", size=(60,50))
        self.he4icsetvolt = wx.Button(self, -1, "Set Voltage")
        self.he3icpumptext = wx.StaticText(self,label='3He IC Pump \n [0V - 25V]')
        self.he3IC_voltage_scroll =  wx.TextCtrl(self, -1, "0.00", size=(60,50))
        self.he3icsetvolt = wx.Button(self, -1, "Set Voltage")
        self.he3ucpumptext = wx.StaticText(self,label='3He UC Pump \n [-25V - 0V]')
        self.he3UC_voltage_scroll =  wx.TextCtrl(self, -1, "0.00",size =(60,50))
        self.he3ucsetvolt = wx.Button(self, -1, "Set Voltage")
        # binds pump voltage buttons to function
        self.Bind(wx.EVT_BUTTON, self.he4icsetvolt_action, self.he4icsetvolt)
        self.Bind(wx.EVT_BUTTON, self.he3icsetvolt_action, self.he3icsetvolt)
        self.Bind(wx.EVT_BUTTON, self.he3ucsetvolt_action, self.he3ucsetvolt)

        # buttons for the stage switches
        self.he4ICswitch_button = wx.ToggleButton(self, -1, label="4He IC switch", size=(120,50))
        self.he3ICswitch_button = wx.ToggleButton(self, -1, label="3He IC switch", size=(120,50))
        self.he3UCswitch_button = wx.ToggleButton(self, -1, label="3He UC switch", size=(120,50))
        # binds switches buttons to function
        self.Bind(wx.EVT_TOGGLEBUTTON, self.he4icswitch_action, self.he4ICswitch_button)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.he3icswitch_action, self.he3ICswitch_button)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.he3ucswitch_action, self.he3UCswitch_button)

        # button to get current voltages
        self.voltagebutton = wx.Button(self, -1, label="Get Voltages", size=(100,40))
        self.Bind(wx.EVT_BUTTON, self.voltagebutton_action, self.voltagebutton)

        # pump/switch heater voltages
        self.heatervoltagetext = [wx.StaticText(self, label=name) for name in powersupply.heaternames]

        self.autocyclestart = wx.Button(self,-1,label="Start")
        self.autocyclestop = wx.Button(self, -1, label="Stop")
        self.Bind(wx.EVT_BUTTON, self.startcycle_action, self.autocyclestart)
        self.Bind(wx.EVT_BUTTON, self.stopcycle_action, self.autocyclestop)

        # sizer for the file field
        self.file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.file_sizer.Add(self.dataFileBoxLabel, 0, wx.ALL|wx.CENTER)
        self.file_sizer.Add(self.dataFileBox, 0, wx.ALL|wx.CENTER|wx.EXPAND)
        self.file_sizer.Add(self.dataFileButton, 0, wx.ALL|wx.CENTER)

        # sizer for pump text box and button
        self.he4IC_sizer = wx.BoxSizer(wx.VERTICAL)
        self.he4IC_sizer.Add(self.he4icpumptext, 0, wx.ALL|wx.CENTER)
        self.he4IC_sizer.Add(self.he4IC_voltage_scroll, 1, wx.ALL|wx.CENTER)
        self.he4IC_sizer.Add(self.he4icsetvolt,1,wx.ALL|wx.CENTER)

        self.he3IC_sizer = wx.BoxSizer(wx.VERTICAL)
        self.he3IC_sizer.Add(self.he3icpumptext,0,wx.ALL|wx.CENTER)
        self.he3IC_sizer.Add(self.he3IC_voltage_scroll, 1, wx.ALL|wx.CENTER)
        self.he3IC_sizer.Add(self.he3icsetvolt,1,wx.ALL|wx.CENTER)

        self.he3UC_sizer = wx.BoxSizer(wx.VERTICAL)
        self.he3UC_sizer.Add(self.he3ucpumptext, 0, wx.ALL|wx.CENTER)
        self.he3UC_sizer.Add(self.he3UC_voltage_scroll, 1, wx.ALL|wx.CENTER)
        self.he3UC_sizer.Add(self.he3ucsetvolt,1,wx.ALL|wx.CENTER)

        self.setswitchsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.setswitchsizer.Add(self.he4ICswitch_button,1,wx.ALL|wx.CENTER)
        self.setswitchsizer.Add(self.he3ICswitch_button,1,wx.ALL|wx.CENTER)
        self.setswitchsizer.Add(self.he3UCswitch_button,1,wx.ALL|wx.CENTER)

        self.pumpsizer = wx.BoxSizer(wx.VERTICAL)
        for text in self.heatervoltagetext:
            if 'pump' in text.Label:
                self.pumpsizer.Add(text, 1, wx.ALL|wx.CENTER, 10)

        self.switchsizer = wx.BoxSizer(wx.VERTICAL)
        for text in self.heatervoltagetext:
            if 'switch' in text.Label:
                self.switchsizer.Add(text, 1, wx.ALL|wx.CENTER, 10)

        self.voltagesizer = wx.BoxSizer(wx.HORIZONTAL)
        self.voltagesizer.Add(self.pumpsizer, 1,wx.ALL)
        self.voltagesizer.Add(self.switchsizer, 1, wx.ALL)

        self.autocyclesizer = wx.BoxSizer(wx.HORIZONTAL)
        self.autocyclesizer.Add(self.autocyclestart,1,wx.ALL|wx.CENTER)
        self.autocyclesizer.Add(self.autocyclestop,1,wx.ALL|wx.CENTER)

        self.fridge_control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fridge_control_sizer.Add(self.he4IC_sizer, 1, wx.ALL) # wx.EXPAND vs. wx.SHAPED
        self.fridge_control_sizer.Add(self.he3IC_sizer, 1, wx.ALL)
        self.fridge_control_sizer.Add(self.he3UC_sizer, 1, wx.ALL)


        # master sizer for the full vertical stack
        self.master_sizer = wx.BoxSizer(wx.VERTICAL)
        self.master_sizer.Add(self.file_sizer, 0, wx.ALL|wx.CENTER|wx.EXPAND)
        self.master_sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.CENTER|wx.EXPAND,10)
        self.master_sizer.Add(wx.StaticText(self,label='Set Pump Voltages'),0,wx.CENTER|wx.ALL|wx.EXPAND,10)
        self.master_sizer.Add(self.fridge_control_sizer, 0, wx.CENTER)
        self.master_sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.CENTER|wx.EXPAND,10)
        self.master_sizer.Add(wx.StaticText(self,label='Turn the Switches On/Off'),0,wx.CENTER|wx.ALL|wx.EXPAND,10)
        self.master_sizer.Add(self.setswitchsizer,0,wx.CENTER)
        self.master_sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.CENTER|wx.EXPAND,10)
        self.master_sizer.Add(wx.StaticText(self, label='Current Voltages'),0,wx.CENTER|wx.ALL|wx.EXPAND,10)
        self.master_sizer.Add(self.voltagesizer, 0, wx.ALL|wx.EXPAND)
        self.master_sizer.Add(self.voltagebutton, 0, wx.ALL|wx.CENTER)
        self.master_sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.CENTER|wx.EXPAND,10)
        self.master_sizer.Add(wx.StaticText(self,label='Start/Stop the Automatic Fridge Cycle'),0,wx.CENTER|wx.ALL|wx.EXPAND,10)
        self.master_sizer.Add(self.autocyclesizer,0,wx.CENTER)
        self.master_sizer.Add(self.logBox, 1, wx.ALL|wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.master_sizer)    # tell the frame to use this sizer
        self.SetAutoLayout(1)               # ?
        self.Show(True)

    #function to get current time for the log
    def Gettime(self):
        ts=time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return st

    def he4icsetvolt_action(self, event):
        powersupply.set_voltage('4He IC pump', float(self.he4IC_voltage_scroll.GetValue().strip()))
    def he3icsetvolt_action(self, event):
        powersupply.set_voltage('3He IC pump', float(self.he3IC_voltage_scroll.GetValue().strip()))
    def he3ucsetvolt_action(self, event):
        powersupply.set_voltage('3He UC pump', float(self.he3UC_voltage_scroll.GetValue().strip()))

    def switch_action(self, event, switchname):
        obj = event.GetEventObject()
        if obj.GetValue(): #if the button is pressed, the switch turns on
            powersupply.set_voltage(switchname, 5.0)
            self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned ON \r')
        else: #if the button is not pressed, then the switch turns off
            powersupply.set_voltage(switchname, 0.0)
            self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned OFF \r')
    def he4icswitch_action(self, event):
        self.switch_action(event, '4He IC switch')
    def he3icswitch_action(self, event):
        self.switch_action(event, '3He IC switch')
    def he3ucswitch_action(self, event):
        self.switch_action(event, '3He UC switch')

    import time
    def voltagebutton_action(self, event):
        for name in powersupply.heaternames:
            current_voltage = powersupply.read_voltage(name)
            for text in self.heatervoltagetext:
                if name in text.Label:
                    text.SetLabel('%s: %.2f' % (name, current_voltage))

    def ErrorMessage(self):
        wx.MessageBox('Inputed voltage is out of range \r voltage remains unchanged', 'Error', wx.OK | wx.ICON_ERROR)

    def startcycle_action(self, event):
        if self.abortcycle.is_set() == True:
            # check that a valid data file has been entered
            if os.path.isfile(self.dataFileBox.GetValue()) == False:
                wx.MessageBox('Please enter a valid fridge data file!', 'Error', wx.OK | wx.ICON_ERROR)
                return
            else:
                h5filename = self.dataFileBox.GetValue()
                cyclethread = threading.Thread(name='autocycle', target=autocycle.run, args=(h5filename, self, LoggingEvent, self.abortcycle))
                cyclethread.start()
            self.abortcycle.clear()
        else:
            self.logBox.AppendText('Fridge cycle is already running, ignoring request to start. \n')

    def stopcycle_action(self, event):
        if self.abortcycle.is_set() == False:
            self.abortcycle.set()
            self.logBox.AppendText('Terminating fridge cycle. \n')
            self.logBox.AppendText('Zeroing all pump heaters and switches. \n')
            powersupply.set_voltage('4He IC pump', 0.0)
            powersupply.set_voltage('3He IC pump', 0.0)
            powersupply.set_voltage('3He UC pump', 0.0)
            powersupply.set_voltage('4He IC switch', 0.0)
            powersupply.set_voltage('3He IC switch', 0.0)
            powersupply.set_voltage('3He UC switch', 0.0)
            self.logBox.AppendText('Fridge cycle terminated. \n')
        else:
            self.logBox.AppendText('Fridge cycle not running, ignoring request to stop. \n')

    def logging_action(self, event):
        self.logBox.AppendText('%s\n' % event.message)

    def OnExit(self, event):
        self.Close(True)  # Close the frame.

    def OnOpen(self, event):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.dataFileBox.SetValue(dlg.GetPath())
        dlg.Destroy()



app = wx.App(False)
frame = MainWindow(None, "Fridge Control")
app.MainLoop()
