Automate opening/closing velux windows controlled by an old velux panel (WLI 130) or an infrared receiver (unsure what
the product number is but saw it in a video) attached to the controller (WLC 100).

There's multiple approaches one could take:

- Send the right IR signal to the WLI 130 (with an ESP32). This works, see `infrared` in this repo.
- Solder onto the WLI 130 to 'simulate' button presses. Should work, see
  https://homematic.simdorn.net/projekt-velux-dachfenster-rolladensteuerung/
- Replace the WLI with an ESP32 that sends the same signal onto the wires connected to the WLC. See `wired` in this
  repo. I figured out the digital signal but no clue how to drive the signal wire to ground to send a low without
  creating a short circuit as the controller seems to do a pull-up without a resistor. Somehow the input panel manages
  to do it though. https://electronics.stackexchange.com/q/671509/343117


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
The 3 switches control whether to fully open/close window 1, 2, 3 respectively with a single button press, without
having to hold the button. The 10 switches are a security code that should match the the code of the remote control (WLR
100). The rotary switch (0 to F) needs to match the value of a similar rotary switch on the WLC 100; if set to A, it
means it's the master input panel. The middle buttons are stop buttons. It also has a led which lights when a button is
pressed and it has an infrared receiver for the WLR 100.

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

