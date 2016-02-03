# Overview
This is the fridge control and readout software for the SPT3G test cryostat. It consists of roughly three parts: readout of all the Lakeshore boxes and summary plots, a website that is hosted by a webserver, and a GUI for handling the fridge cycling and control. Each subdirectory contains the code for different tasks:
* `analysis/' - python modules that for reading log files
* `control/` - contains GUI for running fridge cycle (GUI.py)
* `logger/` - contains the python script that writes log files from temperature data (fridge_logger.py)
* `website/` - files for the rudimentary website that displays the latest data

# Logging
The script `fridge_logger.py` outputs data to a file whose name you specify at startup. This script writes the data to a pytables (hdf5) file and then produces a continuously-updated plot which is saved to the `website/' directory. The hdf5 files can be read with the usual pytables tools, the GUI app vitables, or some higher-level python interface functions in the `analysis/' directory. A duplicate file called `..._read.h5` is also produced so that other scripts, such as GUI.py, can simultaneously read the latest data without conflicting with write operations.

For each fridge system, there is some necessary configuration of the IP addresses and serial ports for communicating with the Lakeshore boxes that handle the thermometry. The network interface and the names of each thermometer must be specified. To set this, look at the first few lines of fridge_logger.py, which contain this information and a short description of how to modify it.

# Fridge Control
The python script `control/GUI.py' provides a rudimentary graphical interface for controlling the heater and switch voltages on the He10 fridge. It also can perform an automatic fridge cycle. Please note that the GUI is sometimes slow to respond to user commands because of some weirdness in the way that wxPython plays with functions that take a long time to run (such as the code that does the autocycling). Much of this code should probably be streamlined or rewritten in the future if anyone outside of Fermilab starts relying heavily on this tool.

# Website
The files for a rudimentary website are located in `website/'. At present, this basically just displays a plot with the latest fridge data. If you set up a web server on the machine running this code, you can make this page visible to the outside world, which is particularly useful for checking temperatures remotely.

# Troubleshooting
Several problems can occur which are not due to bugs in the repository code, but due to interactions with dependencies. This section lists a few of these problems and known workarounds. Feel free to add more as you find them.

#### Cannot connect to serial ports after Ubuntu update
If the logger script throws an error after a system update about not being able to connect to port /dev/ttyrXX, the problem is most likely that the driver for the MOXA Nport needs to be recompiled. The MOXA driver links against the specific Linux kernel that is currently running, so changing the version will cause it to fail. To recompile the MOXA driver, simply do the following:
```bash
sudo ./moxa/kernel3.x/mxinst
```
For further reference, see the README file in `/moxa`.
