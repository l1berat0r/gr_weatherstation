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

#ifndef INCLUDED_WEATHERSTATION_ENCODE_WS_H
#define INCLUDED_WEATHERSTATION_ENCODE_WS_H

#include <weatherstation/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace weatherstation {

    /*!
     * \brief <+description of block+>
     * \ingroup weatherstation
     *
     */
    class WEATHERSTATION_API encode_ws : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<encode_ws> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of weatherstation::encode_ws.
       *
       * To avoid accidental use of raw pointers, weatherstation::encode_ws's
       * constructor is in a private implementation
       * class. weatherstation::encode_ws::make is the public interface for
       * creating new instances.
       */
      static sptr make(long int sample_rate, float pulse_length_ms, bool debug);
    };

  } // namespace weatherstation
} // namespace gr

#endif /* INCLUDED_WEATHERSTATION_ENCODE_WS_H */

