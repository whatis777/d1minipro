
import machine
import time
import dht

# The name of the configuration file
CONFIG_FILE_NAME = "config.json"
# configuration object parsed from CONFIG_FILE_NAME
config = None

pin = machine.Pin(2, machine.Pin.OUT)    # create output pin on GPIO2
dht22 = dht.DHT22(machine.Pin(4))


# ----------------------------------------------------------
# Loads and parses the JSON configuration file
# ----------------------------------------------------------
def loadConfig():
    import ujson
    import uio
    print('loading configuration file')

    f = None
    try:
        f = uio.open(CONFIG_FILE_NAME, 'r')
        content = f.read()
    except Exception as e:
        raise RuntimeError('unable to load configuration file {}. Maybe it does not exist or is corrupt? Error='.format(CONFIG_FILE_NAME), e)
    finally:
        if f is not None:
            f.close()

    config = ujson.loads(content)
    return config

# ----------------------------------------------------------
# Connects the device to a WLAN according to the properties
# in the configuration object
# ----------------------------------------------------------
def doConnect(config):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')

        ssid = str(config['wlan']['ssid'])
        password = str(config['wlan']['password'])

        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


# ----------------------------------------------------------
# Performs measurements of the given DHT22 reference.
# Must not be called more thn once every 2 seconds (DHT22 restriction)
# ----------------------------------------------------------
def measureDHT22(dht22):
    dht22.measure()
    temperature = dht22.temperature()
    humidity = dht22.humidity()
    print("temperature=", temperature)
    print("humidity=", humidity)

# ----------------------------------------------------------
# Pusblishes data via MQTT according to given MQTT configuration
# ----------------------------------------------------------
def publishData(config, topic, data):
    import ubinascii
    from umqtt.robust import MQTTClient
    CLIENT_ID = ubinascii.hexlify(machine.unique_id())
    print('Publishing data as client=', CLIENT_ID)

    brokerHost = str(config['mqtt']['brokerHost'])
    brokerPort = int(config['mqtt']['brokerPort'])

    mqtt = MQTTClient(CLIENT_ID, brokerHost, brokerPort)
    mqtt.connect()
    mqtt.publish('device/{}'.format(CLIENT_ID).encode(), '123.4')
    mqtt.disconnect()

# ----------------------------------------------------------
# MAIN / Entry point
# ----------------------------------------------------------

config = loadConfig()
doConnect(config)

while True:
    pin.on()
    #publishData(config)
    measureData(dht22)
    pin.off()
    time.sleep(5)
