# gr_weatherstation

gnuradio oot module made to spoof a weatherstation I bought in Lidl for $20 :)

## Compilation

For gnuradio 3.8:

mkdir build </br>
cd build </br>
cmake .. </br>
sudo make install </br>
sudo ldconfig

## Examples

examples/ws_rx.grc

![Reciever and decoder](examples/ws_rx.png)

examples/ws_tx.grc

![Encoder and transmitter](examples/ws_tx.png)

![Live demonstration](examples/gr_weatherstation.jpg)


