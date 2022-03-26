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
import re
from gnuradio import gr

class wspanel_tx(gr.sync_block):
    """
    docstring for block wspanel_tx
    """
    def __init__(self, *args, **kwds):
        gr.sync_block.__init__(self,
            name="WS Panel TX",
            in_sig=None,
            out_sig=None)

        self.message_port_register_out(pmt.intern('out'))
        self.panel = wsWxPanel(self, *args, **kwds)


    
class wsWxPanel(wx.Panel):
    def __init__(self, blk, *args, **kwds):
        self.blk = blk

        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "Temp")
        self.label_2 = wx.StaticText(self, -1, "Channel")
        self.label_3 = wx.StaticText(self, -1, "Auto TX")        
        
        self.temp = wx.TextCtrl(self, -1, "0.0")
        self.chn = wx.TextCtrl(self, -1, "1")
        self.auto_tx = wx.TextCtrl(self, -1, "1")        
        
        self.hack = wx.Button(self, -1, "HACK!")
        self.hack.Bind(wx.EVT_BUTTON, self.send_msg) 

        self.__set_properties()
        self.__do_layout()

    def send_msg(self, e):
        temp = int(re.sub(r'\.', '', self.temp.GetValue()))
        chn = int(self.chn.GetValue())
        auto_tx = int(self.auto_tx.GetValue())
        
        unknown_b = "000011101"
        chn_b = "00"

        if chn == 1:
            chn_b = "00"
        elif chn == 2:
            chn_b = "01"
        elif chn == 3:
            chn_b = "10"

        auto_tx_b = "{0:01b}".format(auto_tx)
        temp_b = "{0:012b}".format(temp)        

        data_b = unknown_b + auto_tx_b + chn_b + temp_b

        crc_b = wsWxPanel.gen_crc(data_b)
        data_b = data_b + crc_b
        
        meta = pmt.to_pmt(None)
        data = pmt.init_u8vector(4, [int(data_b[i:i+8],2) for i in range(0,len(data_b),8)])
        #data = pmt.init_u8vector(4,[14,128,44,168])

        msg = pmt.cons(meta, data)
        self.blk.message_port_pub(pmt.intern('out'), msg)

    @staticmethod
    def gen_crc(data, div = '100110001'):    
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
        
        return "".join([str(c) for c in crc])

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
        sizer_1.Add(self.auto_tx, 0, flag, 20)
        sizer_0.Add(sizer_1, 1, wx.ALIGN_CENTER)


        sizer_2.Add(self.hack, 0, flag, 0)
        sizer_0.Add(sizer_2, 1, wx.ALIGN_CENTER)
        #sizer_0.Add(sizer_3, 0, wx.ALIGN_CENTER)
        #sizer_0.Add(sizer_4, 0, wx.ALIGN_CENTER)

        self.SetSizer(sizer_0)
        self.SetMinSize([700,75])           



