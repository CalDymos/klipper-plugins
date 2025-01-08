import logging

class FakeOutputPin:

    def __init__(self, config):

        self.printer = config.get_printer()

        self.is_pwm = config.getboolean('pwm', False)
        self.scale = config.getfloat('scale', 1., above=0.) if self.is_pwm else 1.0

        self.last_value = config.getfloat(
            'value', 0., minval=0., maxval=self.scale) / self.scale

        self.shutdown_value = config.getfloat(
            'shutdown_value', 0., minval=0., maxval=self.scale) / self.scale

        self.name = config.get_name().split()[-1]
        gcode_macro = self.printer.load_object(config, 'gcode_macro')

        self.gcode = gcode_macro.load_template(config, 'gcode', '')

        # Printer events
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.register_event_handler("klippy:connect", self._handle_connect)
        self.printer.register_event_handler("klippy:shutdown",  self._handle_shutdown)

        # GCODE commands
        gcode = self.printer.lookup_object('gcode')
        gcode.register_mux_command("SET_PIN", "PIN", self.name,
                                   self.cmd_SET_PIN,
                                   desc=self.cmd_SET_PIN_help)

    def _handle_connect(self):
        # Add this as an output_pin so it will show up in various UI
        # like fluidd or mainsail and klipperScreen we can use it in GCODE like
        # any other macros:
        #   printer['output_pin my_pin'].value
        output_pin_name = 'output_pin ' + self.name
        self.printer.add_object(output_pin_name, self)

        # fluidd/mainsail reads the configfile for these. This is another hack, but
        # it seems to be ok. Confirmed that SAVE_CONFIG doesn't pick this up.
        printer_config = self.printer.lookup_object('configfile')
        
        pin_status = {
            'pin': "VP",
            'value': self.last_value,
            'shutdown_value': self.shutdown_value              
        }

        # only works till klipper 0.12.0-346
        if hasattr(printer_config, 'status_settings'):
            self.klipper_version = "<= 0.12.0-346"
            if self.is_pwm: # slider
                pin_status['scale'] = self.scale
                pin_status['pwm'] = True
            else: # button
                pin_status['pwm'] = False
                      
            printer_config.status_settings[output_pin_name] = pin_status

        # since Klipper version 0.12.0-347 only on/off elements work and no sliders anymore
        elif hasattr(printer_config, 'status_raw_config'):
            self.is_pwm = False
            pin_status['pwm'] = "False" # must be a string, otherwise KlipperScreen will crash
            pin_status['scale'] = 1.0
            printer_config.status_raw_config[output_pin_name] = pin_status

    def _handle_ready(self):
        # Run the GCODE on startup
        self.gcode.run_gcode_from_command()

    def _handle_shutdown(self):
        # Not sure if this is really even valid, running GCODE
        # on shutdown.
        self._set_value(self.shutdown_value)

    def _set_value(self, value):
        if value != self.last_value:
            self.last_value = value
            self.gcode.run_gcode_from_command()

    def get_status(self, eventtime):
        return {'value': self.last_value}

    cmd_SET_PIN_help = "Set the value of an output pin"
    def cmd_SET_PIN(self, gcmd):
        value = gcmd.get_float('VALUE', minval=0., maxval=self.scale)
        if self.is_pwm:
            value /= self.scale
        else:
            value = 1 if value > 0 else 0
        self._set_value(value)

def load_config_prefix(config):
    return FakeOutputPin(config)
