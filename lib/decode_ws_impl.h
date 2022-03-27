/* -*- c++ -*- */
/*
 * Copyright 2022 l1berat0r.
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

#ifndef INCLUDED_WEATHERSTATION_DECODE_WS_IMPL_H
#define INCLUDED_WEATHERSTATION_DECODE_WS_IMPL_H

#include <weatherstation/decode_ws.h>

namespace gr {
  namespace weatherstation {

    class decode_ws_impl : public decode_ws
    {
     private:
      // Nothing to declare in this block.

     public:
      decode_ws_impl(long int sample_rate, float threshold, bool debug);
      ~decode_ws_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

      void reset_state();      
      void send_data();

      unsigned long captured_data;
      unsigned long signal_length;
      unsigned long pulse_length;
      unsigned long reference_pulse_length;
      unsigned long sample_rate;
      unsigned char current_state;
      unsigned char last_state;
      float threshold;
      int bits_captured;
      bool receiving;
      bool debug;
    };
  } // namespace weatherstation
} // namespace gr

#endif /* INCLUDED_WEATHERSTATION_DECODE_WS_IMPL_H */

