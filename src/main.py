
import machine
import time
import dht

# The name of the configuration file
CONFIG_FILE_NAME = "config.json"
# configuration object parsed from CONFIG_FILE_NAME
config = None
mqttClient = None

pin2 = machine.Pin(2, machine.Pin.OUT)    # Embedded LED on GPIO2
pin14 = machine.Pin(14, machine.Pin.OUT)    # Status LED on on GPIO14
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
def wlanConnect(config):
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
def processDHT22(config, dht22):
    dht22.measure()
    temperature = dht22.temperature()
    humidity = dht22.humidity()

    temperatureTopic = 'device/{}/temperature'.format(getClientId()).encode()
    humidityTopic = 'device/{}/humidity'.format(getClientId()).encode()

    mqttPublish(config, temperatureTopic, temperature)
    mqttPublish(config, humidityTopic, humidity)


# ----------------------------------------------------------
# Connects to an MQTT broker according to given MQTT configuration
# ----------------------------------------------------------
def mqttConnect(config):
    from umqtt.robust import MQTTClient

    # extract properties from JSON-parsed configuration
    brokerHost = str(config['mqtt']['brokerHost'])
    brokerPort = int(config['mqtt']['brokerPort'])
    print('Connecting to broker {}:{} as client ID={}'.format(brokerHost, brokerPort, getClientId()))

    global mqttClient
    mqttClient = MQTTClient(getClientId(), brokerHost, brokerPort)
    mqttClient.connect()


# ----------------------------------------------------------
# Connects to an MQTT broker according to given MQTT configuration
# ----------------------------------------------------------
def mqttDisconnect():
    mqttClient.disconnect()


# ----------------------------------------------------------
# Pusblishes data via MQTT according to given MQTT configuration
# ----------------------------------------------------------
def mqttPublish(config, topic, data):
    print('Publishing data as client=', getClientId())

    mqttClient.publish(topic, str(data))


def getClientId():
    import ubinascii
    return ubinascii.hexlify(machine.unique_id())


# ----------------------------------------------------------
# MAIN / Entry point
# ----------------------------------------------------------

# initialize status LED with 0
pin14.off()

# Load JSON configuration file
config = loadConfig()

# Connect to WLAN
wlanConnect(config)

# set status LED to on
pin14.on()

while True:
    pin2.on()

    mqttConnect(config)
    processDHT22(config, dht22)
    mqttDisconnect()

    pin2.off()
    time.sleep(10)
