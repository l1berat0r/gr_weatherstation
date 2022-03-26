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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "encode_ws_impl.h"

#define dout debug && std::cout

namespace gr {
  namespace weatherstation {

    encode_ws::sptr
    encode_ws::make(long int sample_rate, float pulse_length_ms, bool debug)
    {
      return gnuradio::get_initial_sptr
        (new encode_ws_impl(sample_rate, pulse_length_ms, debug));
    }

    /*
     * The private constructor
     */
    encode_ws_impl::encode_ws_impl(long int sample_rate, float pulse_length_ms, bool debug)
      : gr::sync_block("encode_ws",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 1, sizeof(float))),
          sample_rate(sample_rate),
          pulse_length_ms(pulse_length_ms),
          debug(debug)
    {
      pulse_length = (unsigned long) ((sample_rate * pulse_length_ms) / 1000);
      data_to_transmit = (uint8_t*) malloc(4);
      dout << "PULZ: " << pulse_length << std::endl;
      
      dout << "LET's ROCK" << std::endl;
      message_port_register_in(pmt::mp("in"));
	    set_msg_handler(pmt::mp("in"), boost::bind(&encode_ws_impl::message_in, this, _1));

      reset_state();
    }

    /*
     * Our virtual destructor.
     */
    encode_ws_impl::~encode_ws_impl()
    {
    }

    void
    encode_ws_impl::reset_state () {
      tx_bit = 0;
      bits_transmited = 0;
      transmition_counter = 0;
      tx_pulse = 0;
      tx_pause = 0;      
      repeated_count = 0;
      transmiting = false;
      memset(data_to_transmit, 0, 4);
    }

    void
    encode_ws_impl::msg_end () {
      if(++repeated_count < repeat_number) {
        tx_pause = 1;
        tx_bit = 0;
        bits_transmited = 0;
        transmition_counter = 0;
        tx_pulse = true;
      } else {
        reset_state();
      }
    }

    int
    encode_ws_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      float *out = (float *) output_items[0];
      float out_v = 0;

      // Do <+signal processing+>
    
      for(int i=0;i<noutput_items;++i,++transmition_counter) {
        if(!transmiting) {
          out_v = 0;
        } else {
          if(tx_pause) {
            out_v = 0;
            if(transmition_counter > pulse_length * 18) {
              tx_pause = false;
              transmition_counter = 0;
            }
          } else {
            if(tx_pulse) {
              out_v = 1;
              if(transmition_counter > pulse_length) {
                transmition_counter = 0;
                tx_bit = get_current_bit();
                tx_pulse = false;
              }
            } else {
              out_v = 0;
              if(transmition_counter > tx_bit_length()) {
                transmition_counter = 0;
                tx_pulse = true;
                bits_transmited++;
              }
            }
          }
        }
        out[i]=out_v;
      }

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

    unsigned long
    encode_ws_impl::tx_bit_length()
    {
      if(bits_transmited > 32) {
        msg_end();
        return -1;
      }      
      return (bits_transmited >= 32) ? pulse_length :  (tx_bit ? (pulse_length * 8) : (pulse_length * 4));
    }

    int 
    encode_ws_impl::get_current_bit()
    {
      dout << ((data_to_transmit[bits_transmited / 8] & (0x1 << 7 - (bits_transmited % 8))) >> 7 - (bits_transmited % 8)) << std::endl;
      return ((data_to_transmit[bits_transmited / 8] & (0x1 << 7 - (bits_transmited % 8))) >> 7 - (bits_transmited % 8)) & 0x1;
    }

    void encode_ws_impl::start_transmit(uint8_t *data)
    {      
      bits_transmited = 0;
      transmition_counter = 0;
      tx_pulse = 1;
      repeat_number = 7;

      memcpy(data_to_transmit, data, 4);
      tx_bit = get_current_bit();
      transmiting = true;
    }

    void encode_ws_impl::message_in(pmt::pmt_t msg) 
    {
      dout << "GOT MSG" << std::endl;
      if(pmt::is_pair(msg) && !transmiting) {
        uint8_t *data = (uint8_t*) pmt::blob_data(pmt::cdr(msg));
        start_transmit(data);
        dout << "DATAZ: " << data[0] << data[1] << data[2] << data[3] << std::endl;
        dout << "RAZCWIETALI JABŁONI I GRUSZY" << std::endl;
      }
    }

  } /* namespace weatherstation */
} /* namespace gr */

