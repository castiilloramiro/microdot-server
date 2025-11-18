# Aplicacion del servidor
# --- Configuración del Servidor Web Microdot y Periféricos ---
from microdot import Microdot, Response
import network
from time import sleep
from machine import Pin, SoftI2C
import ssd1306

I2C_SDA_PIN = 21
I2C_SCL_PIN = 22
OLED_ADDR = 0x3C # Dirección común del SSD1306

# 2. Credenciales WiFi
WIFI_SSID = "Cooperadora Alumnos"
WIFI_PASSWORD = "" 

try:
   
    i2c = SoftI2C(sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN))
  
    oled = ssd1306.SSD1306_I2C(64, 32, i2c, addr=OLED_ADDR)
except Exception as e:
   
    print("ADVERTENCIA: No se pudo inicializar el OLED.")
    oled = None # Si falla, oled será None

# --- Función de Conexión ---

def connect_wifi(ssid, password):
    """Conecta el microcontrolador a la red y retorna la IP asignada."""
    sta_if = network.WLAN(network.STA_IF)
    
    if not sta_if.active():
        sta_if.active(True)

    if not sta_if.isconnected():
        print('Conectando a la red...')
        sta_if.connect(ssid, password)
        # Mostrar estado en OLED
        if oled:
            oled.fill(0)
            oled.text('Conectando...', 0, 0)
            oled.show()

        while not sta_if.isconnected():
            print(".", end="")
            sleep(0.5)
            
    ip = sta_if.ifconfig()[0]
    print('\nConfiguración de red:', sta_if.ifconfig())
    return ip

# --- Lógica de Inicialización ---
try:
    ip = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    
 
    if oled:
        oled.fill(0)
        oled.text('IP:', 0, 0)
        oled.text(ip, 0, 15)
        oled.show()
        
except Exception as e:
    print("ERROR FATAL: No se pudo conectar a WiFi.", e)
    ip = None # La aplicación no puede arrancar sin IP


app = Microdot()
Response.default_content_type = 'text/html' 


@app.route('/')
def index(request):
    try:
        with open('index.html', 'r') as file:
            html = file.read()
    except OSError:
        return "Error: index.html no encontrado.", 500

    # Variables a reemplazar en el HTML
    variables = {
        '{{#}}': "Actividad 1",
        '{{Mensaje}}': "Control de LED RGB con Microdot",
        '{{Alumno}}': "Castillo Ramiro"
    }
    
    for placeholder, valor in variables.items():
        html = html.replace(placeholder, valor)
    
    return html

# Rutas para servir archivos estáticos (CSS y JS)

@app.route('/styles/base.css')
def serve_css(request):
    try:
        with open('styles/base.css', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    except OSError:
        return "Not Found", 404

@app.route('/scripts/base.js')
def serve_js(request):
    try:
        with open('scripts/base.js', 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except OSError:
        return "Not Found", 404

# --- Arranque del Servidor ---
if ip:
    print(f"Servidor Microdot corriendo en http://{ip}")
    # Nota: El host debe ser la IP obtenida para que sea accesible externamente
    app.run(host=ip, port=80, debug=True)
else:
    print("Servidor detenido: No se pudo obtener una dirección IP.")
