# Overview
This is the fridge control and readout software for the SPT3G test cryostat. It consists of roughly three parts: readout of all the Lakeshore boxes and summary plots, a website that is hosted by a webserver, and a GUI for handling the fridge cycling and control. In the `legacy` directory, there is also some old code that was formerly used for the fridge readout and control, but this is now quite deprecated and should not be used.

# Main Components
Each subdirectory contains the code for different tasks:
* `control/` - contains GUI for running fridge cycle (GUI.py)
* `legacy/` - old logger scripts (deprecated); should ignore unless interested in archaeology
* `logger/` - contains the python script that writes log files from temperature data (fridge_logger.py)
* `website/` - files for the rudimentary website that displays the latest plot

The script `fridge_logger.py` outputs data to a file whose name you specify at startup. A duplicate file called `..._read.h5` is also produced so that other scripts, such as GUI.py, can simultaneously read the latest data without corrupting the file.

# Troubleshooting
Several problems can occur which are not due to bugs in the repository code, but due to interactions with dependencies. This section lists a few of these problems and known workarounds. Feel free to add more as you find them.

#### Cannot connect to serial ports after Ubuntu update
If the logger script throws an error after a system update about not being able to connect to port /dev/ttyrXX, the problem is most likely that the driver for the MOXA Nport needs to be recompiled. The MOXA driver links against the specific Linux kernel that is currently running, so changing the version will cause it to fail. To recompile the MOXA driver, simply do the following:
```bash
sudo ./moxa/kernel3.x/mxinst
```
For further reference, see the README file in `/moxa`.
