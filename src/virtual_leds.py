# LED Segment aliases
#
# Allows you to define custom LED configs that address only parts of a chain.
#
# For example:
#
# [neopixel sb_leds]
# chain_count: 3
# pin: PA0
# color_order: GRBW
# 
# [neopixel case_lights]
# chain_count: 20
# pin: PA1
# color_order: GRBW
#
# [virtual_leds logo_led]
# leds: sb_leds (1)
# 
# [virtual_leds nozzle_leds]
# leds: sb_leds (2,3)
#
# [virtual_leds all_leds]
# leds: 
#    sb_leds
#    case_lights
#
# Copyright (C) 2019-2022  Maple Leaf Makers <mapleleafmakers@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import logging
from .led import LEDHelper

class PrinterVirtualLeds:
    def __init__(self, config):
        self.printer = printer = config.get_printer()
        name = config.get_name().split()[1]
        
        # Initialize color data
        self.configChains = [self.parse_chain(line) for line in config.get('leds').split('\n') if line.strip()]
        self.led_helper = LEDHelper(config, self.update_leds, 1)
        
        # Register commands
        printer.register_event_handler("klippy:ready", self.handle_ready)

    def handle_ready(self):
        self.leds = []
        for chainName, leds in self.configChains:
            chain = self.printer.lookup_object(chainName)
            for led in leds:
                self.leds.append((chain, led))
        
    def parse_chain(self, chain):
        chain = chain.strip()
        leds=[]
        parms = [parameter.strip() for parameter in chain.split()
                    if parameter.strip()]
        if parms:
            chainName=parms[0].replace(':',' ')
            ledIndices   = ''.join(parms[1:]).strip('()').split(',')
            for led in ledIndices:
                if led:
                    if '-' in led:
                        start, stop = map(int,led.split('-'))
                        if stop == start:
                            ledList = [start-1]
                        elif stop > start:
                            ledList = list(range(start-1, stop))
                        else:
                            ledList = list(reversed(range(stop-1, start)))
                        for i in ledList:
                            leds.append(int(i))
                    else:
                        for i in led.split(','):
                            leds.append(int(i)-1)

            return chainName, leds
        else:
            return None, None
        
    def update_leds(self, led_state, print_time):
        chains_to_update = set()
        for color, (chain, led) in zip(led_state, self.leds):
            chain.led_helper.led_state[led] = color
            chains_to_update.add(chain)
        for chain in chains_to_update:
            chain.led_helper.update_func(chain.led_helper.led_state, None)

    
    def get_status(self, eventtime=None):
        state = []
        chain_status = dict()
        for chain, led in self.leds:
            if chain not in chain_status:
                status = chain.led_helper.get_status(eventtime)['color_data']
                chain_status[chain] = status

            state.append(chain_status[chain][led])
        return dict(color_data=state)

def load_config_prefix(config):
    return PrinterVirtualLeds(config)
