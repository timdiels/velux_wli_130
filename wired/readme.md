An approach which replaces the input panel with an ESP32 or Arduino. Managed to analyse the signal, was able to bit bang
it on an arduino output port but the connection to WLC is a bus so can't actually use an output pin directly. Even with
an NPN BJT transistor or an N-channel E-MOSFET, I'm not sure how to do it as it seems that the controller has a pull up
without a resistor. It must be possible somehow however as the input panel manages to do it.


## WLI-WLC connection
Multiple WLI can connect to the same WLC in a bus (simply connect all the yellow wires together, all the blue together,
...). Motors are activated in sequence, never at the same time; unsure whether that's a WLI or WLC limitation.

With circuit (the WLI 130) attached, it seems that:

- 1 yellow, power, 4.9V with nothing connected but can easily drop to 4.6V with a bit of load applied.
- 2 blue, signal. It defaults to 5.26-5.32V and expects us to pull it low to signal it. But 0 resistance upstream.
- 3 red, ground.

## Measurements
- Led does not light up, nor does the window open/close when either red or yellow wire is detached. Led lights up
  but Velux does nothing when only yellow and red are attached.
- yellow
  - 1.39mA flows from upstream to yellow circuit in idle
  - 9.3mA when holding any button, regardless of whether Velux moves
  - 3.3mA shortly after holding button. Stays there for a few seconds and then quickly drops to 1.39 again
- blue
  - 0.03mA Flows from upstream blue to circuit in idle.
  - 0.19mA when holding any button.
- I accidentally measured 338mA between upstream blue and red. Later confirmed that a 33k resistor between blue and red
  still results in 0.14mA (unsure how much mA exactly) while voltage dropped to around 4.6V (again, from memory). 4.6 /
  33000 = 0.14. So there's definitely no resistor upstream.
- 0.16mA when connecting yellow to red via a 33k resistor. Also no resistor upstream.
- Measuring just the upstream wires with nothing connected, no circuit: 4.92V from yellow to red, 5.32-5.5V from blue to red.
- Measuring with yellow and red connected to circuit, blue probe only connected to upstream. Yellow is 4.76V, blue is
  5.48V relative to red. When pressing a button it averages 4.5-4.6V.
- Measuring with blue probe connected to circuit I get 5.2V despite blue not connected to upstream.
- Measuring with all wires connected, yellow averages 4.75V, blue is 5.26V. Yellow averages 4.58V while pressing button.
  Blue drops to 0V for a low signal.


## signal analysis
In idle, line is kept high.

Bit representation:

- 0: long low, short high
- 1: long high, short low

Based on oscilloscope measurements when the WLI was configured to open/close the windows manually:

```
Up   velux 1  0 10011 111101
Up   velux 2  0 10011 111011
Up   velux 3  0 10011 111110
Down velux 1  0 10011 101111
Down velux 2  0 10011 110111
Down velux 3  0 10011 011111

# These buttons don't have a purpose in manual mode so that probably explains the odd code.
Stop velux 1  0 10110 011111
Stop velux 2  0 10110 011111
Stop velux 3  0 10110 011111
```

Each frame is 20ms, 12 bits, 1.6666ms per bit:

- 0: start bit
- 10011: No idea but I'm guessing this would change when I change the open/close settings from manual to auto. I would
  also expect the 0-F setting to appear in here.
- down velux 3 bit: 0 to make it go down
- down velux 1 bit
- down velux 2 bit
- up velux 2 bit
- up velux 1 bit
- up velux 3 bit

Timing (TODO update to the second more accurate batch of measurements):

- Frames come in pairs, 30ms between each frame in a pair. Time between pairs is 64.4ms. All the frames are exactly the
  same for the same button (I only looked at both frames of the first pair), it just repeats the same frame. So,
  timeline: 20ms - 30ms - 20ms - 64ms - repeat.
- Bit time 1.6666
- Long high/low 1.24
- Short high/low 0.52

Other notes:

- It's tempting to set multiple down/up bits at the same time but the controller can only actuate one motor at a time so
  it's probably just an invalid command. You can however send multiple commands in sequence and the controller will
  execute them in sequence.
- It's the same command whole time regardless of whether Velux can open or close further.


## Writing the signal
SPI and I2C hardware won't help us as they use a clock. The signal looks closest to UART, but without the RX and each 0
has a short high at the end of the bit and a 1 has a short low at the end (presumably to help with timing / staying in
sync); so I have to bit bang it. See `arduino_bit_bang` in repo.

