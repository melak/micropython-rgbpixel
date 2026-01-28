# micropython-rgbpixel

This module provides a driver for single discrete RGB LEDs with an API
reminiscent of the [NeoPixel](https://docs.micropython.org/en/latest/library/neopixel.html).


The basic principle is that this class represents a one-pixel long "strip".

The API is intended to be, as much as possible, upwards compatible with
that of NeoPixel's. Apparent oddities and approaches that do not readily
seem to make sense for single-pixel "strips" are a result of this decision.

# Installation

On network-connected hardware:

```python
>>> import mip
>>> mip.install("github:melak/micropython-rgbpixel")
Installing github:melak/micropython-rgbpixel/package.json to /lib
Copying: /lib/rgbpixel.py
Done
```

For non-networked hardware:

```bash
$ mpremote mip install github:melak/micropython-rgbpixel
Install github:melak/micropython-rgbpixel
Installing github:melak/micropython-rgbpixel/package.json to /lib
Installing: /lib/rgbpixel.py
Done                                    
```

See [the MicroPython package management documentation](https://docs.micropython.org/en/latest/reference/packages.html).
