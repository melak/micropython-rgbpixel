# vim: tabstop=4 shiftwidth=4 expandtab foldmethod=marker :

"""neopixel-ish control of discrete RGB LEDs"""

# Copyright (c) 2026 Tamas Tevesz <ice@extreme.hu>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# This module provides a driver for single discrete RGB LEDs with an API
# reminiscent of the NeoPixel one (c.f.
# https://docs.micropython.org/en/latest/library/neopixel.html).

from machine import PWM

class RGBPixel:
    """This class stores pixel data for a single discrete RGB LED connected
       to three PWM-capable pins. The application sets the pixel data and then
       calls RGBPixel.write() to update the pixel.

       The basic principle is that this class represents a one-pixel long "strip".

       The API is intended to be, as much as possible, upwards compatible with
       that of NeoPixel's. Apparent oddities and approaches that do not readily
       seem to make sense for single-pixel "strips" are a result of this decision.

       The control of the LEDs are done through machine.PWM. Some arguments are
       passed through to a machine.PWM object and as such familiarity with it
       is implied.

       Example:

           from machine import Pin
           import time
           import rgbpixel

           # Pins controlling the discrete RGB LED on the Waveshare ESP32-S3-Nano
           red = Pin(46)
           green = Pin(0)
           blue = Pin(45)

           px = rgbpixel.RGBPixel(red = red, green = green, blue = blue, invert = True)
           for x in range(0, 3):
               for y in range(0, 256):
                   if x == 0:
                       px[0] = (255 - y, 0, y)
                   elif x == 1:
                       px[0] = (0, y, 255 - y)
                   else:
                       px[0] = (y, 255 - y, 0)
                   px.write()

                   time.sleep_ms(10)

        The pixel value:
        ----------------

        The pixel value is an (r, g, b) tuple of integers between 0 to 255 inclusive.

        The scaler:
        -----------

        It is highly unlikely that the individual LED elements packaged together
        in an RGB LED come balanced or their driving circuitry accounts for the
        differences in their properties. Add to that that the human eye's sensitivity
        to various wavelenghts differs considerably, and it's easy to see how
        applying the same pixel value to the different elements can result in
        wildly varying levels of perceived brightnesses. The scaler is intended
        to help balance this effect by taking the supplied pixel value and applying
        a user-supplied modifier to the components before applying it to the pixel.

        There are two ways of supplying a scaler:

        * a three-element tuple of floats that will be used as a multiplier to the
          pixel value supplied. In practice, one of them (the "weakest" for any
          target property) will be 1 and the other two will be less than 1.

        * a function taking a pixel value and returning a modified pixel value.

        Applying a scaler (other than unity) almost certainly results in a reduced
        brightness, but potentially more correct colors.
    """

    def __init__(self, red, green, blue, n = 1, bpp = 3, timing = None, invert = False, freq = 5000, scaler = None):
        """Construct an RGBPixel object. The arguments are:

            red:    a PWM-capable entity controlling the red LED. Passed through
                    to machine.PWM.
            green:  a PWM-capable entity controlling the green LED. Passed through
                    to machine.PWM.
            blue:   a PWM-capable entity controlling the blue LED. Passed through
                    to machine.PWM.
            n:      if specified, must be 1, ignored otherwise (present for
                    NeoPixel compatibility).
            bpp:    if specified, must be 3, ignored otherwise (present for
                    NeoPixel compatibility).
            timing: ignored (present for NeoPixel compatibility).
            invert: boolean; whether to invert the output. You most likely will
                    need it for common anode LEDs (but consult your hardware
                    schematics). Passed through to machine.PWM.
            freq:   the frequency in Hz for the PWM cycle. Passed through
                    to machine.PWM.
            scaler: see discussion above.
        """
        if n != 1:
            raise ValueError('Only 1 pixel long strip is supported')
        if bpp != 3:
            raise ValueError('Only an RGB pixel is supported')
        self.scaler = scaler
        self.red = { 'value': 0, 'px': PWM(red, freq, duty = 0, invert = invert) }
        self.green = { 'value': 0, 'px': PWM(green, freq, duty = 0, invert = invert) }
        self.blue = { 'value': 0, 'px': PWM(blue, freq, duty = 0, invert = invert) }
        self.write()

    def write(self):
        """Writes the current pixel data to the LED.
        """
        red = self.red['value']
        green = self.green['value']
        blue = self.blue['value']

        if callable(self.scaler):
            red, green, blue = self.scaler((red, green, blue))
        elif self.scaler is not None:
            red = round(red * self.scaler[0])
            green = round(green * self.scaler[1])
            blue = round(blue * self.scaler[2])

        # Pixel values are 8 bits, PWM duty cycle is 10 bits - scale pixel values up
        red = ( red << 2 ) | ( red >> 6 )
        green = ( green << 2 ) | ( green >> 6 )
        blue = ( blue << 2 ) | ( blue >> 6 )

        self.red['px'].duty(red)
        self.green['px'].duty(green)
        self.blue['px'].duty(blue)

    def fill(self, value):
        """Set the value of the pixel to the specified value. Mostly retained
           for NeoPixel compatibility.
        """
        self[0] = value

    def __setitem__(self, index, value):
        """Set the pixel at *index* to the specified value. As the class
           represents a one-pixel long strip, *index* must always be 0.
        """
        if index != 0:
            raise IndexError('Strip index out of range')

        self.red['value'] = value[0] % 256
        self.green['value'] = value[1] % 256
        self.blue['value'] = value[2] % 256

    def __getitem__(self, index):
        """Gets the current value of the pixel. As the class represents a
           one-pixel long strip, *index* must always be 0.
        """
        if index != 0:
            raise IndexError('Strip index out of range')

        return (self.red['value'], self.green['value'], self.blue['value'])

    def __len__(self):
        """Returns the number of pixels in the strip. As the class represents
           a one-pixel long strip, it always returns 1.
        """
        return 1

    # These are more examples than anything immediately useful, chiefly because
    # I have eyeballed them off a mildly unreadable scanned chart off the
    # internets, but here we are.

    @staticmethod
    def SMLP34RGB_lumi_scaler(pixel):
        """Scaler function for the SMLP34RGB LED (as found on the Waveshare
           ESP-S3-Nano board) based on the luminous intensities of the light
           emitted by the individual LED elements in the RGB LED.
        """
        return (pixel[0], round(pixel[1] * 0.3182), round(pixel[2] * 0.875))

    @staticmethod
    def SMLP34RGB_photopic_scaler(pixel):
        """Scaler function for the SMLP34RGB LED (as found on the Waveshare
           ESP-S3-Nano board) based on the wavelengths of the light emitted by
           the individual LED elements in the RGB LED and modulated by a photopic
           efficiency function.
        """
        return (round(pixel[0] * 0.2521), round(pixel[1] * 0.1056), pixel[2])
