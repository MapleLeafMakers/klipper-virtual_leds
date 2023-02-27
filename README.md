# Klipper Virtual LEDs

This klipper addon greatly simplifies the configuration of advanced led setups by allowing you to define 'virtual led chains' that are composed of one or more segments of physical led chains. take the following neopixel configurations for example:

```ini
[neopixel sb_leds]
chain_length: 3
color_order: GRBW
pin: PA0
```

Without virtual_leds, it takes 2 commands to change the 2 nozzle leds:
    
    SET_LED LED=sb_leds INDEX=2 RED=1 TRANSMIT=0
    SET_LED LED=sb_leds INDEX=3 RED=1 TRANSMIT=1

With virtual_leds, you can define the nozzle leds as a separate chain:

```ini
[virtual_leds nozzle_leds]
leds: sb_leds (2,3)
```

Then set them with a single command:

    SET_LED LED=nozzle_leds RED=1
    
These virtual_leds work exactly like regular led strips and can even be used with the popular [led_effect](https://github.com/julianschill/klipper-led_effect) plugin.


## Installation
The module can be installed into a existing Klipper installation with an install script.

    cd ~
    git clone https://github.com/MapleLeafMakers/klipper-virtual_leds.git
    cd klipper-virtual_leds
    ./install-virtual_leds.sh

