#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 l1berat0r.
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
import pmt
import math
import struct
import re
from gnuradio import gr

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QFontMetricsF
from PyQt5.QtCore import Qt as Qtc
from PyQt5.QtCore import QRect

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
        self.widget = wsQtPanel(self, *args, **kwds)

    
class wsQtPanel(QFrame):
    def __init__(self, blk, *args, **kwds):
        self.blk = blk
        QFrame.__init__(self)        
        self.setFrameShape(QFrame.Panel)
        self.layout = QGridLayout()

        self.label_1 = QLabel("Temp")
        self.label_2 = QLabel("Channel")
        self.label_3 = QLabel("Auto TX")        
        
        self.temp = QLineEdit("0.0")
        self.chn = QLineEdit("1")
        self.auto_tx = QLineEdit("1")        
        
        self.hack = QPushButton("HACK!")
        self.hack.clicked.connect(self.send_msg) 

        self.layout.addWidget(self.label_1, 0, 0)
        self.layout.addWidget(self.temp, 1, 0)

        self.layout.addWidget(self.label_2, 0, 1)
        self.layout.addWidget(self.chn, 1, 1)

        self.layout.addWidget(self.label_3, 0, 2)
        self.layout.addWidget(self.auto_tx, 1, 2)

        self.layout.addWidget(self.hack, 2, 0, 1, 3)

        self.setLayout(self.layout)

        self.__set_properties()
        self.__do_layout()

    def send_msg(self, e):
        temp = int(re.sub(r'\.', '', self.temp.text()))
        chn = int(self.chn.text())
        auto_tx = int(self.auto_tx.text())
        
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

        crc_b = wsQtPanel.gen_crc(data_b)
        data_b = data_b + crc_b
        
        meta = pmt.to_pmt(None)
        data = pmt.init_u8vector(4, [int(data_b[i:i+8],2) for i in range(0,len(data_b),8)])

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
        pass

    def __do_layout(self):
        pass      



