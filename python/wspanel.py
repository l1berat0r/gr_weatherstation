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
import time
from gnuradio import gr
from gnuradio import qtgui

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QFontMetricsF
from PyQt5.QtCore import Qt as Qtc
from PyQt5.QtCore import QRect

class DataEvent(object):
    msg_counter = 0
    last_received = round(time.time() * 1000)
    
    def __init__(self, data_b, meta_data_b):
        data = "".join(map(lambda n: "{0:08b}".format(n), data_b))

        self.data = data
        self.meta_data = meta_data_b

        temp = int(data[12:24], 2)
        if int(data[12]):
            temp = -1 * (math.pow(2,12) - temp)

        self.temp = str(temp / 10.0) 
        self.chn = "--"        

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

        self.widget = wsQtPanel(*args, **kwds)
        self.debug = debug
        

    def handle_msg(self, msg):
        if(pmt.is_pair(msg)):
            d = pmt.to_python(pmt.cdr(msg))
            md = pmt.to_python(pmt.car(msg))

            de = DataEvent(d, md)
            self.widget.display_data(de)
            del de
    
class wsQtPanel(QFrame):
    def __init__(self, *args, **kwds):
        QFrame.__init__(self)
        
        self.setFrameShape(QFrame.Panel)
        self.layout = QGridLayout()

        self.label_1 = QLabel("Temp")
        self.label_2 = QLabel("Channel")
        self.label_3 = QLabel("CRC")
        self.label_4 = QLabel("Auto TX")

        self.label_5 = QLabel("Signal length")
        self.label_6 = QLabel("Pulse length")
        self.label_7 = QLabel("Number of packets")
        
        self.temp = QLabel("-----")
        self.chn = QLabel("--")
        self.crc = QLabel("--")
        self.auto_tx = QLabel("--")

        self.signal_length = QLabel("----")
        self.pulse_length = QLabel("----")
        self.msg_counter = QLabel("----")

        self.layout.addWidget(self.label_1, 0, 0)
        self.layout.addWidget(self.temp, 1, 0)

        self.layout.addWidget(self.label_2, 0, 1)
        self.layout.addWidget(self.chn, 1, 1)

        self.layout.addWidget(self.label_3, 0, 2)
        self.layout.addWidget(self.crc, 1, 2)

        self.layout.addWidget(self.label_4, 0, 3)
        self.layout.addWidget(self.auto_tx, 1, 3)

        self.layout.addWidget(self.label_5, 2, 0)
        self.layout.addWidget(self.signal_length, 3, 0)

        self.layout.addWidget(self.label_6, 2, 1)
        self.layout.addWidget(self.pulse_length, 3, 1)

        self.layout.addWidget(self.label_7, 2, 2)
        self.layout.addWidget(self.msg_counter, 3, 2)

        self.setLayout(self.layout)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        pass        

    def display_data(self, event):
        self.temp.setText(event.temp)
        self.chn.setText(event.chn)
        self.crc.setText(event.crc)
        self.auto_tx.setText(event.auto_tx)

        self.signal_length.setText(event.signal_length_ms)
        self.pulse_length.setText(event.pulse_length_ms)
        self.msg_counter.setText(str(event.msg_counter))

    def clear_data(self):
        self.temp.setText("-----")

