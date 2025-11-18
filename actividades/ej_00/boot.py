def connect_to(ssid, passwd) -> None:

    """Conecta el microcontrolador a la red indicada.

    Parameters
    ----------
    ssid : str
        Nombre de la red a conectarse
    passwd : str
        Contraseña de la red
    """
    
    import network
    from time import sleep
    
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to network...")
        sta_if.active(True)
        sta_if.connect(ssid, passwd)
        while not sta_if.isconnected():
            print(".",end="")
            sleep(.05)
    
    return sta_if.ifconfig()[0]

print(connect_to("Cooperadora Alumnos", ""))

import machine
i2c = machine.I2C(scl=machine.Pin(22),sda=machine.Pin(21))
print(i2c.scan())
from ssd1306 import SSD1306_I2C
oled = SSD1306_I2C(128, 32, i2c)
oled.text(connect_to("Cooperadora Alumnos", ""), 0, 0)
oled.show()
