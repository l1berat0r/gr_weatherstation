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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <iostream>
#include <string>

#include <gnuradio/io_signature.h>
#include "decode_ws_impl.h"

#define dout debug && std::cout

namespace gr {
  namespace weatherstation {

    decode_ws::sptr
    decode_ws::make(long int sample_rate, float threshold, bool debug)
    {
      return gnuradio::get_initial_sptr
        (new decode_ws_impl(sample_rate, threshold, debug));
    }

    /*
     * The private constructor
     */
    decode_ws_impl::decode_ws_impl(long int sample_rate, float threshold, bool debug)
      : gr::block("decode_ws",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(0,0,0)),
	    sample_rate(sample_rate),
      threshold(threshold),
      debug(debug)
    {
    	reset_state();
      current_state = 0;
      last_state = 0;

    	set_output_multiple(40); 
	    message_port_register_out(pmt::mp("out"));
    }

    /*
     * Our virtual destructor.
     */
    decode_ws_impl::~decode_ws_impl()
    {
    }

    void
    decode_ws_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    void
    decode_ws_impl::reset_state () {
      receiving = false;
      signal_length = 0;
      pulse_length = 0;
      reference_pulse_length = 0;
      captured_data = 0;
      bits_captured = 0;
    }

    void
    decode_ws_impl::send_data () {
      unsigned char dt[4];
      struct signal_metadata {
        unsigned long signal_length;
        unsigned long pulse_length;
        float signal_length_ms;
        float pulse_length_ms;
      };

      dt[0] = (captured_data >> 24) & 0xFF;
      dt[1] = (captured_data >> 16) & 0xFF;
      dt[2] = (captured_data >> 8) & 0xFF;
      dt[3] = captured_data & 0xFF;

      struct signal_metadata mdt = {
        signal_length,
        reference_pulse_length,
        (float) signal_length / (float) sample_rate,
        (float) reference_pulse_length / (float) sample_rate
      };

      dout << "WS: Message Captured - " << std::dec << (int)dt[0]
           << "," << std::dec << (int)dt[1]
           << "," << std::dec << (int)dt[2]
           << "," << std::dec << (int)dt[3]
           << " [" << std::dec << bits_captured << "]"<< std::endl;

      pmt::pmt_t data(pmt::make_blob(dt, 4));
	    pmt::pmt_t meta(pmt::make_blob(&mdt, sizeof(mdt)));

    	pmt::pmt_t pdu(pmt::cons(meta, data));
	    message_port_pub(pmt::mp("out"), pdu);
    }


    int
    decode_ws_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];

      for(int i=0; i<noutput_items; ++i, signal_length++) {
        current_state = in[i] > threshold;

        if(current_state != last_state) {
          last_state = current_state;
          if(!receiving && current_state == 1) {
            reset_state();
            receiving = true;  
            dout << "WS: Receiving started." << std::endl;
          } else {
            if(current_state == 1 && receiving) {
              if(pulse_length >= reference_pulse_length * 7 && pulse_length <= reference_pulse_length * 9) {
                captured_data <<= 1;
                captured_data |= 1;
                bits_captured++;
              }
              if(pulse_length >= reference_pulse_length * 3 && pulse_length <= reference_pulse_length * 5) {
                captured_data <<= 1;
                bits_captured++;
              }
              if(pulse_length >= reference_pulse_length * 0.5 && pulse_length <= reference_pulse_length * 2) {                                  
                if(bits_captured == 32) {
                  send_data();
                } else {
                  dout << "Captured data corrupted. Bits captured: " << std::dec << bits_captured << " - Reseting state." << std::endl;
                }
                reset_state();
              }
            } else {
              if(receiving && reference_pulse_length == 0) {
                reference_pulse_length = pulse_length;
              }
              pulse_length = 0;
            }
          }
        } else {
          pulse_length++;
        }

        if(signal_length > sample_rate) reset_state();
      }
      // Do <+signal processing+>
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace weatherstation */
} /* namespace gr */

