/* -*- c++ -*- */
/* 
 * Copyright 2020 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_WEATHERSTATION_ENCODE_WS_IMPL_H
#define INCLUDED_WEATHERSTATION_ENCODE_WS_IMPL_H

#include <weatherstation/encode_ws.h>

namespace gr {
  namespace weatherstation {

    class encode_ws_impl : public encode_ws
    {
     private:
      // Nothing to declare in this block.

     public:
      encode_ws_impl(long int sample_rate, float pulse_length_ms, bool debug);
      ~encode_ws_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);

      void message_in(pmt::pmt_t msg);
      void reset_state();
      void msg_end();
      void start_transmit(uint8_t *data);
      int get_current_bit();
      unsigned long tx_bit_length();

      float pulse_length_ms;
      unsigned long pulse_length;
      unsigned long sample_rate;
      unsigned long transmition_counter;
      int tx_bit;
      int tx_pulse;
      int repeat_number;
      int repeated_count;
      int bits_transmited;
      bool transmiting;
      bool tx_pause;
      bool debug;      
      uint8_t *data_to_transmit;
    };            
  } // namespace weatherstation
} // namespace gr

#endif /* INCLUDED_WEATHERSTATION_ENCODE_WS_IMPL_H */

