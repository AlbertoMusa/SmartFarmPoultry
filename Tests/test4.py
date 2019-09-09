from jose import jws
import datetime

private_key = r"""
-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIBZJ/P6e1I/nQiBnQxx9aYDPAjwUtbV9Nffuzfubyuw8oAoGCCqGSM49
AwEHoUQDQgAEKSPVJGELbULai+viQc3Zz95+x2NiFvjsDlqmh6rDNeiVuwiwdf5l
lyZ0gbLJ/vheUAwtcA2z0csWU60MfBup3Q==
-----END EC PRIVATE KEY-----"""
configurationDict = {
        'time':     str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),    # Time the configuration was retrieved
        'id':  2,                           # id of the chicken hotel
        'config': {
            #Times action take place
            'timeLED':  {  # LED will be active between 05:00 - 21:00
                'openHour':     5,
                'openMinute':   0,
                'closeHour':    21,
                'closeMinute':  0,
            },
            'timeDoor':  {  # Door will open at 09:30, close on light sensor value
                'openHour':     9,
                'openMinute':   30,
                'closeHour':    -1,
                'closeMinute':  -1,
            },
            'timeNest':  {  # Nest will be open between 04:30-12:00
                'openHour':     4,
                'openMinute':   30,
                'closeHour':    12,
                'closeMinute':  0,
            },
            'timeKsr':  {  # KSR will be open between 06:00-10:00
                'openHour':     6,
                'openMinute':   0,
                'closeHour':    10,
                'closeMinute':  0,
            },
            'timeOnFly':  {  # OFP will be open between 06:00-10:00
                'openHour':     4,
                'openMinute':   45,
                'closeHour':    20,
                'closeMinute':  0,
            },
            # Brightness values
            'closeDoorBrightness': {  # Door will close if Brightness level falls below 10 Lux with 10 minutes of histeresis
                'lux':          10,
                'hysteresis':   10,     # in minutes
            },
            'ledOffBrightness': {  # Inside LEDs will go out if Brightness level is above 950 (will go on gain if below) with 5 min histersis
                'lux':          950,
                'hysteresis':   5,     # in minutes
            },
            #Configuration of motors
            'flapLeftFront':    { # I2C Addresses and ID where flap is connected, you can assign up to 3 physical motors to the same logical element
                'addresses':    [0x03,0x00,0x00],   # I2C address 0x03, 0x00 is off
                'numbers':      [1,0,0],            # First motor at this driver (a driver can have 2 motors or 3 LEDs)
                'time':         240,                # Time until motor is ready and has closed/opened
                'active':       True,               # Motor is active or not
            },
            'flapLeftBack':    {
                'addresses':    [0x03,0x00,0x00],
                'numbers':      [2,0,0],
                'time':         240,
                'active':       True,
            },
            'flapRightFront':    {
                'addresses':    [0x05,0x00,0x00],
                'numbers':      [1,0,0],
                'time':         240,
                'active':       True,
            },
            'flapRightBack':    {
                'addresses':    [0x05,0x00,0x00],
                'numbers':      [2,0,0],
                'time':         240,
                'active':       True,
            },
            'nestEject':    {
                'addresses':    [0x06,0x08,0x00],
                'numbers':      [2,2,0],
                'time':         240,
                'active':       True,
            },
            'flapKsr':    {
                'addresses':    [0x07,0x07,0x00],
                'numbers':      [1,2,0],
                'time':         240,
                'active':       False,
            },
            'onFlyPole':    {
                'addresses':    [0x06,0x08,0x00],
                'numbers':      [1,1,0],
                'time':         240,
                'active':       True,
            },
            # Configuration of LEDs
            'LEDTop':    {
                'addresses':    [0x01,0x00,0x00],
                'numbers':      [1,0,0],    # First LED at this driver, 0 means off
                'maxValue':     120,        # maximum value to which LED is dimmed
                'dimUpDelay':   10,         # delay in minutes the led starts to dimm up
                'dimDownDelay': 10,         # delay in minutes the led starts to dimm down
                'dimTime':      12,         # total dim time in minutes until at maxvalue
                'active':       True,       # If is active
            },
            'LEDMid':    {
                'addresses':    [0x01,0x00,0x00],
                'numbers':      [2,0,0],
                'maxValue':     120,
                'dimUpDelay':   10,
                'dimDownDelay': 10,
                'dimTime':      12,
                'active':       True,
            },
            'LEDBottom':    {
                'addresses':    [0x01,0x00,0x00],
                'numbers':      [3,0,0],
                'maxValue':     120,
                'dimUpDelay':   10,
                'dimDownDelay': 10,
                'dimTime':      12,
                'active':       True,
            },
            'LEDKsr':    {
                'addresses':    [0x01,0x00,0x00],
                'numbers':      [4,0,0],
                'maxValue':     120,
                'dimUpDelay':   10,
                'dimDownDelay': 10,
                'dimTime':      12,
                'active':       True,
            },
            'LEDNest':    {
                'addresses':    [0x02,0x00,0x00],
                'numbers':      [1,0,0],
                'maxValue':     120,
                'dimUpDelay':   10,
                'dimDownDelay': 10,
                'dimTime':      12,
                'active':       True,
            },
            'LEDAlways':    {
                'addresses':    [0x02,0x00,0x00],
                'numbers':      [2,0,0],
                'maxValue':     120,
                'dimUpDelay':   10,
                'dimDownDelay': 10,
                'dimTime':      12,
                'active':       True,
            },
        }
    }

test = "parola"
priv ="password"
signed = jws.sign(test.encode(), priv, algorithm='HS256')
print(signed)
data = jws.verify(signed, priv, algorithms=['HS256'])
print(data)
