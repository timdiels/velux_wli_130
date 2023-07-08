- The IR commands include: open/close/stop automatically/manually motor 1/2/3
- Commands sent in sequence are executed in sequence. E.g. send open motor 1, open motor 2 first opens window 1, then
  window 2 (or opens your window and then your screen; whatever is connected to your motors).
- If the LED of the panel lights up for a second or more, it received a valid command but the security code is wrong. If
  the LED does not light up, it received a malformed command.


## Usage
- Turn off power to your input panel (unsure whether necessary but always safer, for the device; it won't hurt you as
  it's just 5VDC).
- Set the security code of your input panel (WLI) to 1011100000 (the 10 dip switches).
- Turn the power back on.

ESPHome:

- See `esphome/ir_codes.yaml` in this repo for the IR codes in ESPHome config format. See `esphome/example.yaml` for an
  example of how to use them. (ESPHome also has transmit_pronto but it'd be trickier to edit those codes to prevent the
  manual commands from stuttering)

Flipper Zero:

- Copy `flipper.ir` to `infrared/` on your SD card (rename it to `velux.ir` or something). You could use a shorter duty
  cycle to save power as those also seem to work.
- Open it up on the flipper and try it out


### Converting the IR codes to other remotes
I don't have a remote myself, but I did find
[the IR codes of the WLR 100](https://files.remotecentral.com/view/5562-14340-1/velux_wlx-130_skylight.html#files).
It's in pronto ccf format (proprietary philips universal remote format, popular on remotecentral); I included it in the
repo, see `pronto`. I converted it with
irscrutiziner (spreadsheet output gives a machine readable csv format) and converted that with convert.py to a flipper
remote. Overview of converters:

- [irscrutinizer](http://www.harctoolbox.org/IrScrutinizer.html) gave me more detail than ccf2pulse
- [This node script](https://gist.github.com/XMB5/a877ab620d812260f2da8380aac050d3) converts pronto hex to a flipper IR
  file but you'd first need to convert the ccf to pronto hex.
- [ccf2pulse](https://github.com/gsauthof/pronto-ccf) seems to work if you know the right frequency; but doesn't include
  all info that irscrutinizer did, e.g. command names.
- decodeccf (Windows)
- [Philips ProntoEdit](https://www.remotecentral.com/news/545/philips_prontoedit_professional_30_posted_for_all.html) (Windows)


## IR code analysis
The frequency is 32121 Hz. A duty cycle of 0.33 works for me, but most duty cycles seem to work. According to the
remotecentral readme, the security code is 1000000000 but that did not work for me.

Each code actually sends the same command twice. The second pulse is sometimes repeated differently (-1214 is repeated
as -1183 if it's the second pulse). There's a longer pause before the repeated command is sent and a much longer pause
after the very last command (I've edited the much longer pause to be shorter so that manual open/close opens
continuously instead of stuttering).

All codes use these set of pulses `{-1183, -1214, -373, 436, 1245}`, not including the long pauses between commands.

Bits are pairs of short/long pulses. 0 is a short-long pair, 1 is a long-short pair and pairs start with a positive
pulse; negative pulses are just delays during which no IR is sent.

Indices of pulses which remain constant per group of commands (e.g. all commands whose name contains 'm1' form the m1 group):

```
m1 [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
m2 [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
m3 [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
stop [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
up_auto [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
up_manual [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
down_auto [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
down_manual [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
all [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
```

Bits 0-2 are the action:

```
001 up_auto
010 up_manual
011 down_auto
100 down_manual
101 stop
```

Bits 3-6 are motor 1, 2 or 3

```
001 m1
010 m2
100 m3
```

Bits 7-10 are constant across all commands, but no clue what they're for:

```
0000
```

Bits 11-20 are the security key which unlike the pronto readme suggested is not 1000000000 but:

```
1011100000
```

I haven't figured out how to generate new IR codes, I tried but the LED did not respond, I'm guessing there are some
parity bits.
