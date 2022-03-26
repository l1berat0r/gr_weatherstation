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


#ifndef INCLUDED_WEATHERSTATION_DECODE_WS_H
#define INCLUDED_WEATHERSTATION_DECODE_WS_H

#include <weatherstation/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace weatherstation {

    /*!
     * \brief <+description of block+>
     * \ingroup weatherstation
     *
     */
    class WEATHERSTATION_API decode_ws : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<decode_ws> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of weatherstation::decode_ws.
       *
       * To avoid accidental use of raw pointers, weatherstation::decode_ws's
       * constructor is in a private implementation
       * class. weatherstation::decode_ws::make is the public interface for
       * creating new instances.
       */
      static sptr make(long int sample_rate, float threshold, bool debug);
    };

  } // namespace weatherstation
} // namespace gr

#endif /* INCLUDED_WEATHERSTATION_DECODE_WS_H */

