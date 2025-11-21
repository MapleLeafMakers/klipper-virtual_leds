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
from . import led


class PrinterVirtualLeds:
    def __init__(self, config):
        self.config = config
        self.printer = config.get_printer()
        self.name = config.get_name().split()[1]
        self.configChains = [self.parse_chain(line) for line in config.get('leds').split('\n') if line.strip()]
        self.leds = []
        self.led_helper = led.LEDHelper(config, self.update_leds,
                                        sum(len(leds) for chain_name, leds in self.configChains))

        # Register commands
        self.printer.register_event_handler('klippy:ready', self.handle_ready)

    def handle_ready(self):
        for chain_name, leds in self.configChains:
            try:
                chain = self.printer.lookup_object(chain_name)
                if chain:
                    for led_index in leds:
                        self.leds.append((chain, led_index))
            except Exception as e:
                raise self.config.error(
                    "Virtual LED chain '%s' referenced in '%s' cannot be loaded:\n%s" % (chain_name, self.name, str(e)))

    @staticmethod
    def parse_chain(chain):
        chain = chain.strip()
        leds = []
        parms = [parameter.strip() for parameter in chain.split() if parameter.strip()]
        if parms:
            chain_name = parms[0].replace(':', ' ')
            led_indices = ''.join(parms[1:]).strip('()').split(',')
            for led_index in led_indices:
                if led_index:
                    if '-' in led_index:
                        start, stop = map(int, led_index.split('-'))
                        if stop == start:
                            led_list = [start - 1]
                        elif stop > start:
                            led_list = list(range(start - 1, stop))
                        else:
                            led_list = list(reversed(range(stop - 1, start)))
                        for i in led_list:
                            leds.append(int(i))
                    else:
                        for i in led_index.split(','):
                            leds.append(int(i) - 1)
            return chain_name, leds
        else:
            return None, None

    def update_leds(self, led_state, print_time):
        chains_to_update = set()
        for color, (chain, led_index) in zip(led_state, self.leds):
            chain.led_helper.led_state[led_index] = color
            chains_to_update.add(chain)
        for chain in chains_to_update:
            chain.led_helper.need_transmit = True
            if hasattr(chain.led_helper, '_check_transmit'):
                chain.led_helper._check_transmit()  # New klipper
            elif hasattr(chain.led_helper, 'check_transmit'):
                chain.led_helper.check_transmit(None)  # Older klipper / Kalico
            else:
                raise RuntimeError(
                    'Klipper version not compatible: led_helper missing \'_check_transmit\' and \'check_transmit\'.')

    def get_status(self, eventtime=None):
        state = []
        chain_status = {}
        for chain, led_index in self.leds:
            if chain not in chain_status:
                status = chain.led_helper.get_status(eventtime)['color_data']
                chain_status[chain] = status

            state.append(chain_status[chain][led_index])
        return {'color_data': state}


@staticmethod
def log(msg, *args, **kwargs):
    logging.info('Virtual LEDs: ' + str(msg))


def load_config_prefix(config):
    return PrinterVirtualLeds(config)
