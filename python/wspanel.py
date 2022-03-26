#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2020 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
import wx
import pmt
import math
import struct
import time
from gnuradio import gr

wxDATA_EVENT = wx.NewEventType()
def EVT_DATA_EVENT(win, func):
    win.Connect(-1, -1, wxDATA_EVENT, func)

class DataEvent(wx.PyEvent):
    msg_counter = 0
    last_received = round(time.time() * 1000)
    
    def __init__(self, data_b, meta_data_b):
        wx.PyEvent.__init__(self)
        data = "".join(map(lambda n: "{0:08b}".format(n), data_b))

        self.SetEventType (wxDATA_EVENT)
        self.data = data
        self.meta_data = meta_data_b

        temp = int(data[12:24], 2)
        if int(data[12]):
            temp = -1 * (math.pow(2,12) - temp)

        self.temp = str(temp / 10.0) 
        self.chn = "--"        
        print(data)
        if data[10:12] == "00":
            self.chn = "1"
        elif data[10:12] == "01" :
            self.chn = "2"
        elif data[10:12] == "10":
            self.chn = "3"

        if DataEvent.check_crc(data[0:24], data[24:32]):
            self.crc = "OK"
        else:
            self.crc = "BAD"

        if data[9] == "0":
            self.auto_tx = 'Yes'
        else:
            self.auto_tx = 'No'

        if meta_data_b is not None and len(meta_data_b) == 24:
            self.signal_length = "%d" % struct.unpack('L', meta_data_b[0:8])
            self.pulse_length = "%d" % struct.unpack('L', meta_data_b[8:16])
            self.signal_length_ms = "%.3f ms" % (struct.unpack('f', meta_data_b[16:20])[0] * 1000.0)
            self.pulse_length_ms = "%.3f ms" % (struct.unpack('f', meta_data_b[20:24])[0] * 1000.0)
        else:
            self.signal_length = "--"
            self.pulse_length = "--"
            self.signal_length_ms = "--"
            self.pulse_length_ms = "--"

        if DataEvent.last_received < (round(time.time() * 1000) - 1000):
            DataEvent.msg_counter = 1
        else:
            DataEvent.msg_counter += 1

        DataEvent.last_received = (round(time.time() * 1000))

    @staticmethod
    def check_crc(data, crc_check, div = '100110001'):    
        i=0
        crc=[0] * 8  
        
        data_a = [int(c) for c in data] + ['0'] * 8        
        
        while i<len(data_a):        
            while i<len(data_a) and data_a[i] == 0:
                i+=1                        
                
            if i < len(data_a):
                for j in range(len(div)):
                    if i+j < len(data_a):
                        data_a[i+j] = int(div[j]) ^ int(data_a[i+j])
                    else:                    
                        crc[(i+j) - len(data_a)] = int(div[j]) ^ int(crc[(i+j) - len(data_a)])
                    
            i+=1
        
        return "".join([str(c) for c in crc]) == crc_check

    def Clone (self):
        self.__class__ (self.GetId())

class wspanel(gr.sync_block):
    """
    docstring for block wspanel
    """
    def __init__(self, debug, *args, **kwds):
        gr.sync_block.__init__(self,
            name="WS panel",
            in_sig=None,
            out_sig=None)
        
        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

        self.panel = wsWxPanel(*args, **kwds)
        self.debug = debug

    def handle_msg(self, msg):
        if(pmt.is_pair(msg)):
            d = pmt.to_python(pmt.cdr(msg))
            md = pmt.to_python(pmt.car(msg))

            de = DataEvent(d, md)
            wx.PostEvent(self.panel, de)
            del de
    
class wsWxPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "Temp")
        self.label_2 = wx.StaticText(self, -1, "Channel")
        self.label_3 = wx.StaticText(self, -1, "CRC")
        self.label_4 = wx.StaticText(self, -1, "Auto TX")

        self.label_5 = wx.StaticText(self, -1, "Signal length")
        self.label_6 = wx.StaticText(self, -1, "Pulse length")
        self.label_7 = wx.StaticText(self, -1, "Number of packets")
        
        self.temp = wx.StaticText(self, -1, "-----")
        self.chn = wx.StaticText(self, -1, "--")
        self.crc = wx.StaticText(self, -1, "--", size=[60,20])
        self.auto_tx = wx.StaticText(self, -1, "--", size=[60,20])

        self.signal_length = wx.StaticText(self, -1, "----", size=[40,20])
        self.pulse_length = wx.StaticText(self, -1, "----", size=[40,20])
        self.msg_counter = wx.StaticText(self, -1, "----", size=[40,20])


        self.__set_properties()
        self.__do_layout()

        EVT_DATA_EVENT (self, self.display_data)

    def __set_properties(self):
        font_bold = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "")
        font_normal = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "")
        font_small = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "")

        self.temp.SetFont(font_small)

    def __do_layout(self):
        sizer_0 = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)

        flag = wx.ALIGN_CENTER_VERTICAL|wx.LEFT

        # arguments: window, proportion, flag, border
        sizer_1.Add(self.label_1, 0, flag)
        sizer_1.Add(self.temp, 0, flag, 20)

        sizer_1.Add(self.label_2, 0, flag, 100)
        sizer_1.Add(self.chn, 0, flag, 20)

        sizer_1.Add(self.label_3, 0, flag, 100)
        sizer_1.Add(self.crc, 0, flag, 20)

        sizer_1.Add(self.label_4, 0, flag, 100)
        sizer_1.Add(self.auto_tx, 0, flag, 20)
        sizer_0.Add(sizer_1, 1, wx.ALIGN_CENTER)

        sizer_2.Add(self.label_5, 0, flag, 0)
        sizer_2.Add(self.signal_length, 0, flag, 20)

        sizer_2.Add(self.label_6, 0, flag, 60)
        sizer_2.Add(self.pulse_length, 0, flag, 20)

        sizer_2.Add(self.label_7, 0, flag, 60)
        sizer_2.Add(self.msg_counter, 0, flag, 20)
        sizer_0.Add(sizer_2, 1, wx.ALIGN_CENTER)
        #sizer_0.Add(sizer_3, 0, wx.ALIGN_CENTER)
        #sizer_0.Add(sizer_4, 0, wx.ALIGN_CENTER)

        self.SetSizer(sizer_0)
        self.SetMinSize([200,50])

    def display_data(self, event):
        self.temp.SetLabel(event.temp)
        self.chn.SetLabel(event.chn)
        self.crc.SetLabel(event.crc)
        self.auto_tx.SetLabel(event.auto_tx)

        self.signal_length.SetLabel(event.signal_length_ms)
        self.pulse_length.SetLabel(event.pulse_length_ms)
        self.msg_counter.SetLabel(str(event.msg_counter))

        self.Layout()

    def clear_data(self):
        self.temp.SetLabel("-----")

