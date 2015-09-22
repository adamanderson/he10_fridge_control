import time as sleeptime
import wx
import os
import voltages
import time
import datetime
import threading
class MainWindow(wx.Frame):
    from autocycle import autocycle
    def __init__(self, parent, title):

        self.canstartcycle = 1
        self.abortcycle = 0

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(400, 800))
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # text box to set the data file path
        self.dataFileBoxLabel = wx.StaticText(self, -1, "Fridge log file:")
        self.dataFileBox = wx.TextCtrl(self, -1, "none selected", size=(200, 30), style=wx.TE_READONLY)
        self.dataFileButton = wx.Button(self, -1, 'choose file')

#       make log box
        self.logBox = wx.TextCtrl(self, -1,'', wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)
        self.logBox.SetEditable(False)

#       text box and buttons for controlling pump voltages
        self.he4icpumptext = wx.StaticText(self, label='4He IC Pump \n [-25V - 0V]')
        self.he4IC_voltage_scroll = wx.TextCtrl(self, -1, "0.00", size=(60,50))
        self.he4icsetvolt = wx.Button(self, -1, "Set Voltage")
        self.he3icpumptext = wx.StaticText(self,label='3He IC Pump \n [0V - 25V]')
        self.he3IC_voltage_scroll =  wx.TextCtrl(self, -1, "0.00", size=(60,50))
        self.he3icsetvolt = wx.Button(self, -1, "Set Voltage")
        self.he3ucpumptext = wx.StaticText(self,label='3He UC Pump \n [-25V - 0V]')
        self.he3UC_voltage_scroll =  wx.TextCtrl(self, -1, "0.00",size =(60,50))
        self.he3ucsetvolt = wx.Button(self, -1, "Set Voltage")

        # bind file selector button to function
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.dataFileButton)

#       binds pump voltage buttons to function
        self.Bind(wx.EVT_BUTTON, self.SetVoltage, self.he4icsetvolt)
        self.Bind(wx.EVT_BUTTON, self.SetVoltage, self.he3icsetvolt)
        self.Bind(wx.EVT_BUTTON, self.SetVoltage, self.he3ucsetvolt)

#        buttons for the stage switches
        self.he4IC_switch_button = wx.ToggleButton(self, -1, label="4He IC switch", size=(120,50))
        self.he3IC_switch_button = wx.ToggleButton(self, -1, label="3He IC switch", size=(120,50))
        self.he3UC_switch_button = wx.ToggleButton(self, -1, label="3He UC switch", size=(120,50))
#       binds switches buttons to function
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleSwitch, self.he4IC_switch_button)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleSwitch, self.he3IC_switch_button)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleSwitch, self.he3UC_switch_button)

#       button to get current voltages
        self.voltagebutton = wx.Button(self, -1, label="Current Voltages", size=(125,50))
        self.Bind(wx.EVT_BUTTON, self.GetVoltages, self.voltagebutton)

        self.he4icpumpvolt=wx.StaticText(self, label='4He IC Pump:')
        self.he3icpumpvolt=wx.StaticText(self, label='3He IC Pump: ')
        self.he3ucpumpvolt=wx.StaticText(self, label='3He UC Pump: ')

        self.he4icswitchvolt=wx.StaticText(self, label='4He IC Switch: ')
        self.he3icswitchvolt=wx.StaticText(self, label='3He IC Switch: ')
        self.he3ucswitchvolt=wx.StaticText(self, label='3He UC Switch: ')

        self.autocyclestart = wx.Button(self,-1,label="Start")
        self.autocyclestop = wx.Button(self, -1, label="Stop")
        self.Bind(wx.EVT_BUTTON, self.checkcycle , self.autocyclestart)
        self.Bind(wx.EVT_BUTTON, self.stopcycle , self.autocyclestop)

        # sizer for the file field
        self.file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.file_sizer.Add(self.dataFileBoxLabel, 0, wx.ALL|wx.CENTER)
        self.file_sizer.Add(self.dataFileBox, 0, wx.ALL|wx.CENTER|wx.EXPAND)
        self.file_sizer.Add(self.dataFileButton, 0, wx.ALL|wx.CENTER)

#       sizer for pump text box and button
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
        self.setswitchsizer.Add(self.he4IC_switch_button,1,wx.ALL|wx.CENTER)
        self.setswitchsizer.Add(self.he3IC_switch_button,1,wx.ALL|wx.CENTER)
        self.setswitchsizer.Add(self.he3UC_switch_button,1,wx.ALL|wx.CENTER)

        self.pumpsizer = wx.BoxSizer(wx.VERTICAL)
        self.pumpsizer.Add(self.he4icpumpvolt, 1,wx.ALL|wx.CENTER,10)
        self.pumpsizer.Add(self.he3icpumpvolt, 1,wx.ALL|wx.CENTER,10)
        self.pumpsizer.Add(self.he3ucpumpvolt, 1,wx.ALL|wx.CENTER,10)

        self.switchsizer = wx.BoxSizer(wx.VERTICAL)
        self.switchsizer.Add(self.he4icswitchvolt, 1,wx.ALL|wx.CENTER,10)
        self.switchsizer.Add(self.he3icswitchvolt, 1,wx.ALL|wx.CENTER,10)
        self.switchsizer.Add(self.he3ucswitchvolt, 1,wx.ALL|wx.CENTER,10)

        self.voltagesizer = wx.BoxSizer(wx.HORIZONTAL)
        self.voltagesizer.Add(self.pumpsizer, 1,wx.ALL|wx.CENTER,5)
        self.voltagesizer.Add(self.switchsizer, 1, wx.ALL|wx.CENTER,5)
        self.voltagesizer.Add(self.voltagebutton, 1, wx.ALL|wx.CENTER,5)

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
        self.master_sizer.Add(wx.StaticText(self, label='Check Current Voltages'),0,wx.CENTER|wx.ALL|wx.EXPAND,10)
        self.master_sizer.Add(self.voltagesizer, 0, wx.ALL)
        self.master_sizer.Add(wx.StaticLine(self),0,wx.ALL|wx.CENTER|wx.EXPAND,10)
        self.master_sizer.Add(wx.StaticText(self,label='Start/Stop the Automatic Fridge Cycle'),0,wx.CENTER|wx.ALL|wx.EXPAND,10)
        self.master_sizer.Add(self.autocyclesizer,0,wx.CENTER)
        self.master_sizer.Add(self.logBox, 1, wx.ALL|wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.master_sizer)    # tell the frame to use this sizer
        self.SetAutoLayout(1)               # ?
        # self.fridge_control_sizer.Fit(self)           # calculate initial size and positions of all elements
        self.Show(True)

    #function to get current time for the log
    def Gettime(self):
        ts=time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return st

    #function to set pump voltage
    def SetVoltage(self, e):
        obj=e.GetEventObject() #gets the particular button that was pressed
        if obj==self.he4icsetvolt:
            if  float(self.he4IC_voltage_scroll.GetValue().strip())>=-25 and float(self.he4IC_voltage_scroll.GetValue().strip())<=0: #checks if voltages are in range
                voltages.ser3.write('APPL N25V, '+str(self.he4IC_voltage_scroll.GetValue().strip())+ ' \r\n') #sends inputted voltage to Aligent
                self.logBox.AppendText(self.Gettime() +' 4He IC Pump has been changed to '+str(self.he4IC_voltage_scroll.GetValue().strip())+'V \r')
            else:
                self.logBox.AppendText(self.Gettime() +' Set 4He IC Pump voltage is out of range \r')
                self.ErrorMessage()

        if obj==self.he3icsetvolt:
            if float(self.he3IC_voltage_scroll.GetValue().strip())>=0 and float(self.he3IC_voltage_scroll.GetValue().strip())<=25:
                voltages.ser3.write('APPL P25V, '+str(self.he3IC_voltage_scroll.GetValue().strip())+ ' \r\n')
                self.logBox.AppendText(self.Gettime() +' 3He IC Pump has been changed to '+str(self.he3IC_voltage_scroll.GetValue().strip())+ 'V \r')
            else:
                self.logBox.AppendText(self.Gettime() +' Set 3He IC Pump voltage is out of range \r')
                self.ErrorMessage()

        if obj==self.he3ucsetvolt:
            if float(self.he3UC_voltage_scroll.GetValue().strip())>=-25 and float(self.he3UC_voltage_scroll.GetValue().strip())<=0:
                voltages.ser2.write('APPL N25V, '+str(self.he3UC_voltage_scroll.GetValue().strip())+ ' \r\n')
                self.logBox.AppendText(self.Gettime()+' 3He UC Pump has been changed to '+str(self.he3UC_voltage_scroll.GetValue().strip())+ 'V \r')
            else:
                self.logBox.AppendText(self.Gettime() +' Set 3He IUC Pump voltage is out of range \r')
                self.ErrorMessage()

    #function to toggle the switches
    def OnToggleSwitch(self, e):
        obj=e.GetEventObject() #gets the particular button that was pressed
        isPressed=obj.GetValue() #checks to see if the button is in the pressed or unpressed state
#        self.logBox.AppendText('asdfh \n')
        if obj==self.he4IC_switch_button:
            if isPressed: #if the button is pressed, the switch turns on
                voltages.ser3.write('APPL P6V, 5 \r\n')
                self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned ON \r')
#                sleeptime.sleep(1)
            else: #if the button is not pressed, then the switch turns off
                voltages.ser3.write('APPL P6V, 0 \r\n')
                self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned OFF \r')
#                sleeptime.sleep(1)
        if obj==self.he3IC_switch_button:
            if isPressed:
                voltages.ser2.write('APPL P25V, 5 \r\n')
                self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned ON \r')
#                sleeptime.sleep(1)
            else:
                voltages.ser2.write('APPL P25V, 0 \r\n')
                self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned OFF \r')
#                sleeptime.sleep(1)
        if obj==self.he3UC_switch_button:
            if isPressed:
                voltages.ser2.write('APPL P6V, 5 \r\n')
                self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned ON \r')
#                sleeptime.sleep(1)
            else:
                voltages.ser2.write('APPL P6V, 0 \r\n')
                self.logBox.AppendText(self.Gettime() +' '+ obj.GetLabelText() + ' has been turned OFF \r')
#                sleeptime.sleep(1)

    #function that gets voltages
    def GetVoltages(self, e):
        currentvolts = voltages.getvoltages() #grabs voltages using the function defined in voltages.py
        self.he4icpumpvolt.SetLabel('4He IC Pump: '+ str(currentvolts[0]))
        self.he3icpumpvolt.SetLabel('3He IC Pump: '+ str(currentvolts[1]))
        self.he3ucpumpvolt.SetLabel('3He UC Pump: '+ str(currentvolts[2]))

        self.he4icswitchvolt.SetLabel('4He IC Switch: '+ str(currentvolts[3]))
        self.he3icswitchvolt.SetLabel('3He IC Switch: '+ str(currentvolts[4]))
        self.he3ucswitchvolt.SetLabel('3He UC Switch: '+ str(currentvolts[5]))

    def ErrorMessage(self):
        wx.MessageBox('Inputted Voltage is out of range \r Voltage remains unchanged', 'Error', wx.OK | wx.ICON_ERROR)

    def checkcycle(self,e):
        if self.canstartcycle:
            self.logBox.AppendText('Starting Automatic Fridge Cycle \n')
            self.canstartcycle=0
            t = threading.Thread(name='autocycle', target=self.autocycle, args=self.dataFileBox.GetValue())
            t.start()
        else:
            self.logBox.AppendText('Automatic Fridge Cycle is already running \n')

    def stopcycle(self, e):
        if self.canstartcycle==0:
            self.logBox.AppendText('Trying to stop Automatic Fridge Cycle \n')
            self.abortcycle = 1
        else:
            self.logBox.AppendText('Automatic Fridge Cycle is Currently not running \n')

    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.dataFileBox.SetValue(dlg.GetPath())
        dlg.Destroy()



app = wx.App(False)
frame = MainWindow(None, "Fridge Control")
app.MainLoop()
