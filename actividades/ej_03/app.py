from microdot import Microdot, Response
import network
from time import sleep
from machine import Pin, SoftI2C
import ssd1306
from neopixel import NeoPixel
import ds18x20
import onewire
import time

# --------------------------------------------------------
# CONFIGURACIÓN HARDWARE
# --------------------------------------------------------

# OLED por I2C
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
oled = ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)

# LEDs simples
led1 = Pin(32, Pin.OUT)
led2 = Pin(33, Pin.OUT)
led3 = Pin(25, Pin.OUT)

# Todos apagados al inicio
led1.value(0)
led2.value(0)
led3.value(0)

# NeoPixels (4 LEDs)
np = NeoPixel(Pin(27), 4)
for i in range(4):
    np[i] = (0, 0, 0)
np.write()

# Sensor DS18B20 y buzzer
buzzer_pin = Pin(14, Pin.OUT)
ds_pin = Pin(19)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

temperatureCelsius = 24

# --------------------------------------------------------
# WIFI
# --------------------------------------------------------

def connect_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)

    if not sta_if.isconnected():
        print('Conectando a la red...')
        sta_if.connect(ssid, password)

        while not sta_if.isconnected():
            print(".", end="")
            sleep(0.5)

    print('Configuración de red:', sta_if.ifconfig())
    return sta_if.ifconfig()[0]


WIFI_SSID = "Cooperadora Alumnos"
WIFI_PASSWORD = ""

# Mostrar IP en OLED
try:
    ip = connect_wifi(WIFI_SSID, WIFI_PASSWORD)

    oled.fill(0)
    oled.text("Accede con:", 0, 0)
    oled.text(ip, 0, 12)
    oled.show()

except Exception as e:
    print("Error en OLED o WiFi:", e)


app = Microdot()
Response.default_content_type = 'text/html'


@app.route('/')
def index(request):
    with open('index.html', 'r') as file:
        html = file.read()

    variables = {
        '{{#}}': "Actividad 2 - Microdot",
        '{{Mensaje}}': "LEDs y Temperatura",
        '{{Alumno}}': "Castillo Ramiro"
    }

    for placeholder, valor in variables.items():
        html = html.replace(placeholder, valor)

    return html



@app.route('/styles/base.css')
def serve_css(request):
    with open('styles/base.css', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}


@app.route('/scripts/base.js')
def serve_js(request):
    with open('scripts/base.js', 'r') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}




@app.route('/led/<led_num>/toggle')
def toggle_led(request, led_num):
    try:
        led_num = int(led_num)

        if led_num == 1:
            led1.value(not led1.value())
            return str(led1.value())

        elif led_num == 2:
            led2.value(not led2.value())
            return str(led2.value())

        elif led_num == 3:
            led3.value(not led3.value())
            return str(led3.value())

        else:
            return "LED no válido", 400

    except Exception as e:
        return f"Error: {str(e)}", 500




@app.route('/neopixel/<r>/<g>/<b>')
def set_neopixel(request, r, g, b):
    try:
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        for i in range(4):
            np[i] = (r, g, b)

        np.write()
        return f"OK: {r},{g},{b}", 200

    except Exception as e:
        return f"Error: {str(e)}", 500




@app.route('/sensors/ds18b20/read')
async def temperature_measuring(request):
    global ds_sensor

    ds_sensor.convert_temp()
    time.sleep_ms(1)

    roms = ds_sensor.scan()
    for rom in roms:
        temperatureCelsius = ds_sensor.read_temp(rom)

    return {'temperature': temperatureCelsius}




@app.route('/setpoint/set/<int:value>')
async def setpoint_calculation(request, value):
    if value >= temperatureCelsius:
        buzzer_pin.on()
        return {'buzzer': 'On'}

    else:
        buzzer_pin.off()
        return {'buzzer': 'Off'}


# --------------------------------------------------------
# INICIAR SERVIDOR
# --------------------------------------------------------

app.run(host=ip, port=80, debug=True)
# Aplicacion del servidor# Aplicacion del servidor
