### [bed_fans]
Configures a fan vary its speed based on the current temperature of a heater. The
value of the heater will be checked every second and the speed of the fan will
be adjusted based on the configured `ranges`.

Only one `bed_fans` section is supported. In the future, this may get moved into something
completely different, like a `linear_fans` section that supports multiple configurations.
```
[bed_fans]
enable_on_start: False
#   Enable when klipper starts. The default is False.
fan: fan_generic bed_fans
#   The fan to control.
heater: heater_bed
#   The heater to monitor. The default is heater_bed.
ranges: 40=0.2, 60=0.4, 90=0.6
#   A comma delimited list of temperature=speed pairs. When the temperature
#   of the heater meets the specified temperature, the fan will be set to
#   the configured speed. If the temperature drops below the lowest
#   specified value, the fan will be turned off.
```

#### QUERY_BED_FANS
`QUERY_BED_FANS`: queries bed fans for the current status and ranges.

#### SET_BED_FANS
`SET_BED_FANS [ENABLE=0|1] [RANGES=<value>]`: If ENABLE is specified, it
will enable or disable the automatic bed fans. If the fans are currently
running, it will *not* turn them off. If RANGES is specific, it will change 
the configured temperatures and speeds. *NOTE:* This value must not contain 
spaces! `RANGES=40=0.2,60=0.4,90=0.6`


### [fake_output_pin]
Creates a `fake` output pin. The pin and its configuration will be created dynamically and be made
available to web front ends as if it was a real pin. When the value changes, the configured
gcode will be executed.

`DISCLAIMER!` This has only been lightly tested. I consider this a hack and hopefully in the future
we'll get something better. It does create an entry in configfile "configuration" at runtime (in memory). 
I did confirm `SAVE_CONFIG` does not write out this runtime created configuration.

Only the subset of configuration values as noted below are supported. Because gcode is executed on a value
change, the utility of `shutdown_value` is questionable and may get removed (or changed) in the future.

### Examples
```
# Example of a sliding scale element
[fake_output_pin test_scale]
pwm: true
scale: 255
value: 0
shutdown_value: 0
gcode:
  {% set value = printer['output_pin test_scale'].value | float %}
  { action_respond_info(TEST SCALE: %.4f" % (value)) }
```

```
# Example of an on/off element
[fake_output_pin test_bool]
value: 0
shutdown_value: 0
gcode:
  {% set value = printer['output_pin test_bool'].value | float %}
  { action_respond_info(TEST BOOL: %s" % (value)) }
```

```
# Turn on/off bed_fans with a UI element
[fake_output_pin enable_bed_fans]
value: 0
shutdown_value: 0
gcode:
  {% set value = printer['output_pin enable_bed_fans'].value | int %}
  SET_BED_FANS ENABLE={value}
```
