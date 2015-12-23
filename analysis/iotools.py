# iotools.py
#
# A collection of tools that are useful for I/O from the "3G" file format used
# for data files produced by spt3g_software.
#
# Adam Anderson
# adama@fnal.gov
# 23 December 2015


class store_frame_value(object):
    """
    A generic class that will store arbitrary values from frames in a g3 file
    for manipulation. This pipeline module is initialized with a list of member
    functions that do the actual work of extracting the desired data from each
    frame. Being able to extract data frame-by-frame like this is particularly
    useful low-level data analysis and debugging, which often require looking at
    raw timestreams.

    Attributes
    ----------
    stored_data : dictionary of numpy arrays, indexed by variable name; data to
        store for retrieval later.
    access_functions : list of functions; functions used to access data from the
        frames (see below)
    jentry : integer; the number of entry that we are on in reading the data
    frame_type : core.G3FrameType.*; type of frame from which to retrieve data
    """
    def __init__(self, data_size, frame_type, access_functions, Output='store_frame_value'):
        self.jentry = 0
        self.data = dict()
        self.frame_type = frame_type
        self.access_functions = access_functions
        for func in self.access_functions:
            self.data[func.func_name] = np.zeros(data_size)
    def __call__(self, frame):
        if frame.type == self.frame_type and self.jentry < len(self.data[self.data.keys()[0]]):
            for func in self.access_functions:
                self.data[func.func_name][self.jentry] = func(frame)
