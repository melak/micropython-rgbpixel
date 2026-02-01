from machine import Pin
from rgbpixel import RGBPixel
import time

RED = Pin(46)
GRN = Pin(0)
BLU = Pin(45)

def test_pixel(p):
    for x in range(0, 3):
        for y in range(0, 256):
           if x == 0:
               p[0] = (255 - y, 0, y)
           elif x == 1:
               p[0] = (0, y, 255 - y)
           else:
               p[0] = (y, 255 - y, 0)
           p.write()

           time.sleep_ms(10)

def run():
    px = RGBPixel(red = RED, green = GRN, blue = BLU, invert = True)
    test_pixel(px)

    px = RGBPixel(red = RED, green = GRN, blue = BLU, invert = True,
                  scaler = (0.1, 0.4, 0.9))
    test_pixel(px)

    px = RGBPixel(red = RED, green = GRN, blue = BLU, invert = True,
                  scaler = RGBPixel.SMLP34RGB_lumi_scaler)
    test_pixel(px)

    def unity_scaler(pixel):
        return (pixel[0], pixel[1], pixel[2])

    px = RGBPixel(red = RED, green = GRN, blue = BLU, invert = True,
                  scaler = unity_scaler)
    test_pixel(px)

if __name__ == '__main__':
    run()
