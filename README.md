An attempt to replace an old velux panel (WLI 130) with an ESP32 or Arduino to automate opening/closing velux windows.
The idea is to send the right signal onto the wires that presumably connect to a WLC 100.


## Possible solutions
- Send the same signal onto the wires attached to the WLI 130.
- Send the right IR signal to the WLI 130. This zip seems to contain IR codes for all the commands
  https://files.remotecentral.com/view/5562-14340-1/velux_wlx-130_skylight.html#files 
- Solder onto the WLI 130 to 'simulate' button presses
  https://homematic.simdorn.net/projekt-velux-dachfenster-rolladensteuerung/


## Device overview
These devices are actually WindowMaster.com devices and found some manuals there. I've included all relevant manuals in
this repo.

The system consists of:

- WLI 130 ...: The panel (there's probably a product label on the backside but can't unscrew one of the plugs)
- WLC 100: Control up to 3 windows. Connects to motors using either WLL 120 or WLL 500 cable.
- WLA 510: Rain sensor, connected to the WLC 100.
- WLL 120: Cable, between WLC 100 and the motors.
- WLL 500: 8-aderige cable, between WLC 100 and the motors.
- WMG 520: The motor in our window probably.

Related but we probably don't have any of these:

- WLI 110: Input panel for 1 velux.
- WLL 100: 2-aderige cable for connecting multiple WLC 100 in series.
- WLR 100: a remote control for this stuff
- WLX 130: a combo package that includes a WLC 100, WLI 130, WLR 100 and some WLL 500.
- WLB 100: A battery for powering the veluxes. Probably so you can still control them during an outage.
- Even more windowmaster manuals: WLF, WUC, WUF, WMU, WMX https://vbh-nl.com/service/documentatie/windowmaster/

Unrelated terms:

- MotorLink, LON and LonWorks are terms I found on windowmaker but these seem to be successors or something different
  entirely.


### Input panel (WLI 130)
The 3 switches control whether to fully open/close window 1, 2, 3 respectively on a single button press. This mode would
be easier for us.

The 10 switches are a security code that should match the the code of the remote control (WLR 100).

The rotary switch (0 to F) needs to match the value of a similar rotary switch on the WLC 100. If set to A, like ours,
it means it's the master input panel; we only have one, so duh.

The middle buttons are used to stop the velux motion.

#### Brief PCB inspection
The PCB is labelled "VIC-2 94V"; probably just means it's fire retardant (like "UL 94-5V"). The 123 sticker might cover
a further suffix.

There's an IC called GAAB 939511 XM02AB. Can't find datasheet.

There's an F012 3055L mosfet, I'm guessing this is for the signal? Can't find the exact datasheet but seems it's an
enhancing N-MOSFET which would make sense if used to produce the signal:

- <https://html.alldatasheet.com/html-pdf/57764/CET/3055L/44/1/3055L.html>
- <https://www.onsemi.com/pdf/datasheet/ntf3055l108-d.pdf>


### Controller (WLC 100)
No idea where it is located in the house. The cable from the WLI goes up, so probably somewhere in the roof.
WindowMaster also calls it Combilink.


### WLI-WLC connection
Multiple WLI can connect to the same WLC in a bus (simply connect all the yellow wires together, all the blue together,
...). Motors are activated in sequence, never at the same time; unsure whether that's a WLI or WLC limitation.

With circuit (the WLI 130) attached, it seems that:

- 1 yellow, power, 4.9V with nothing connected but can easily drop to 4.6V with a bit of load applied.
- 2 blue, signal. It defaults to 5.26-5.32V and expects us to pull it low to signal it. But 0 resistance upstream.
- 3 red, ground.

Logbook of measurements:

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
- Measuring just the upstream wires with nothing connected, no circuit: 4.92V from yellow to red, 5.32V from blue to red.
- Measuring with yellow and red connected to circuit, blue probe only connected to upstream. Yellow is 4.76V, blue is
  5.48V relative to red. When pressing a button it averages 4.5-4.6V.
- Measuring with blue probe connected to circuit I get 5.2V despite blue not connected to upstream.
- Measuring with all wires connected, yellow averages 4.75V, blue is 5.26V. Yellow averages 4.58V while pressing button.
  Blue drops to 0V for a low signal.


## signal
In idle, line is kept high.

Bit representation:

- 0: long low, short high
- 1: long high, short low

Based on oscilloscope measurements when the WLI was configured to open/close window while pressed, i.e. manual (easier
to read when inverting the bits, but I stuck to the above definition for now):

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

- I'm curious whether sending 011000 as last bits would make both veluxes go down at the same time. Not sure whether
  that's allowed though, it might just not support doing that.
- Same command whole time regardless of whether Velux can open or close further.


## Writing the signal
SPI and I2C hardware won't help us as they use a clock. The signal looks closest to UART, but without the RX and each 0
has a short high at the end of the bit and a 1 has a short low at the end (presumably to help with timing / staying in
sync); so I have to bit bang it.
