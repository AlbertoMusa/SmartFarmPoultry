from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
import json

configurationDict = {
        #'time':     str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),    # Time the configuration was retrieved
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

def sign_data(private_key, data):
    if len(data) % 4 != 0:
        x = 4 - (len(data) % 4)
        print(x)
        for i in range(0, x):
            data = data + "a"
    print(data)
    rsakey = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(b64decode(data + "==="))
    sign = signer.sign(digest)
    return b64encode(sign)

def verify_sign(public_key, signature, data):
    if len(data) % 4 != 0:
        x = 4 - (len(data) % 4)
        print(x)
        for i in range(0, x):
            data = data + "a"
    rsakey = RSA.importKey(public_key)
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(b64decode(data + "==="))
    if signer.verify(digest, b64decode(signature)):
        return True
    return False

configurationDict2 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvdHAiOiJjc1ltMVBHN3FWWlEyaVJNUUdPbm1yQU1vUXM5dnZHUUJUYXM1a0ZKcHNCVUZFV0pHMyIsImtleSI6Ii0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tXG5NSUdmTUEwR0NTcUdTSWIzRFFFQkFRVUFBNEdOQURDQmlRS0JnUURyV01qeU01R3NQYU9ZNDBMYjBETkc5RHYxXG5HUFFjbEdHT0JiM2RWaU5rL2U0TEphS3Q3SHpwaW1VQnBlUUw2Qjlqakdad0Q5Q0paNTh3M1VLNU05SFhvTVJ1XG5SeHVQblpKWkE0aGtaeks0a011K1k1VHFkMEVoV1pYbHcraTRzZUJsWWdpNFBaay85a2hZTW8rUDhMR2FUb290XG56cUl2Y3hEUFZDb0Z6amRXQ1FJREFRQUJcbi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLSJ9.YDF65RwRlynsfQkOsxge0y82rdtQfSEJ5ITd8fUI-OM"
configurationDict3 = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9a"
print("step 1")
key = RSA.generate(1024)
print(key.exportKey())
print(key.publickey().exportKey())
print("step 2")
print(configurationDict)
signed = sign_data(key.exportKey(), json.dumps(configurationDict))
print(signed)
res = verify_sign(key.publickey().exportKey(), signed, json.dumps(configurationDict))
print("step 4")
print(res)