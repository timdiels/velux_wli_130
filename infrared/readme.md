I don't have a remote myself, but I did find
[the IR codes of the WLR 100](https://files.remotecentral.com/view/5562-14340-1/velux_wlx-130_skylight.html#files).
For these to work you have to set the security code of your input panel (WLI) to 1000000000 (the one with the 10 dip
switches).


It's in pronto ccf format (proprietary philips universal remote format, popular on remotecentral). I converted it with
irscrutiziner (spreadsheet output gives a machine readable csv format) and converted that with convert.py to a flipper
remote. Overview of converters:

- [irscrutinizer](http://www.harctoolbox.org/IrScrutinizer.html) gave me more detail than ccf2pulse
- [This node script](https://gist.github.com/XMB5/a877ab620d812260f2da8380aac050d3) converts pronto hex to a flipper IR
  file but you'd first need to convert the ccf to pronto hex.
- [ccf2pulse](https://github.com/gsauthof/pronto-ccf) seems to work if you know the right frequency; but doesn't include
  all info that irscrutinizer did, e.g. command names.
- decodeccf (Windows)
- [Philips ProntoEdit](https://www.remotecentral.com/news/545/philips_prontoedit_professional_30_posted_for_all.html) (Windows)

