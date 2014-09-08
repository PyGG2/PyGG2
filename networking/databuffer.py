from __future__ import division, print_function

import struct

class Buffer(object):
    def __init__(self, data=""):
        self.data = data
    
    def write(self, format, data):
        # If several arguments were passed, ie. data is a tuple, unpack it
        if type(data) == type((1, 2)):
            self.data += struct.pack(">"+format, *data)
        else:
            # If not, just pack that one element
            self.data += struct.pack(">"+format, data)
    
    def read(self, format):
        output = struct.unpack_from(">"+format, self.data)
        self.data = self.data[struct.calcsize(">"+format):]
        # FIXME: Unclean hack, dk how to do this properly
        if len(output) > 1:
            return output
        else:
            return output[0]
    
    def is_empty(self):
        if len(self.data) > 0:
            return False
        return True