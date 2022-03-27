/* -*- c++ -*- */

#define WEATHERSTATION_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "weatherstation_swig_doc.i"

%{
#include "weatherstation/decode_ws.h"
#include "weatherstation/encode_ws.h"
%}

%include "weatherstation/decode_ws.h"
GR_SWIG_BLOCK_MAGIC2(weatherstation, decode_ws);
%include "weatherstation/encode_ws.h"
GR_SWIG_BLOCK_MAGIC2(weatherstation, encode_ws);
