from machine import Pin, I2C, ADC
from utime import sleep
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import ubuntu_mono_15, ubuntu_mono_20

print("Konstanten festlegen")
SCL_Pin = 15
SDA_Pin = 14
Bewegungssensor_Pin = 2
WIDTH =128
HEIGHT= 64
alarm_led = Pin(10, Pin.OUT, value=0)


print("initialisiere Display, Pin und LED")
i2c=I2C(1,scl=Pin(SCL_Pin),sda=Pin(SDA_Pin),freq=200000)
oled_display = SSD1306_I2C(WIDTH,HEIGHT,i2c)
pir = Pin(Bewegungssensor_Pin, Pin.IN, Pin.PULL_DOWN)

moisture = ADC(26)
moisture_max = 48000
moisture_min = 20000

print("Toggle onBoard LED to signalize init sequence is done")
onboard_led = Pin(25, Pin.OUT, value=0)
onboard_led.value(1)
onboard_led.value(0)
# oled_display.text("Initialisiere...",0,10)
# oled_display.show()

def pir_handler(pin):
    # PIR-Sensor-Zustand lesen
    pir_value = pir.value()
    if pir_value == 1:
        # Alarm auslösen
        # print('Alarm wurde ausgelöst')
        alarm()

def text_ausgabe(t):
    print(t)
    oled_display.fill(0)
#     for x in range(len(t)):
#         oled_display.text(str(t[x]), 0, x*10)
#     result = "Feucht.: {0:0.2f}% \nStatus: {1}"
    print(type(t) == "tuple")
    if type(t) == tuple:
        oled_display.text("Feuchtigkeit:", 0, 10)
        oled_display.text("{0:0.2f}%".format(t[0]), 0, 20)
        oled_display.text("Status:", 0, 30)
        oled_display.text("{0}".format(t[1]), 0, 40)
    else:
        oled_display.text(t, 0, 10)

    oled_display.show()
#     sleep(3)
#     oled_display.fill(0)
#     oled_display.show()


def convert_moisture(m):
    moisture_base = moisture_max - moisture_min
    percentage = ((m-moisture_min)/moisture_base)*100
    if 100-percentage > 75.0:
        status = "Alles gut!"
    elif 100-percentage < 75.0 and 100-percentage > 40.0:
        status = "Etwas trocken hier"
    else:
        status = "Sofort giessen!"

    return 100-percentage, status

def alarm():
    actual_moisture = 0
    for x in range(5):
        actual_moisture += moisture.read_u16()

    actual_moisture /= 5
#     result = "Feucht.: {0:0.2f}% \nStatus: {1}"
    text_ausgabe(convert_moisture(actual_moisture))
    sleep(1)

text_ausgabe("Initialisiere...")

sleep(3)
pir.irq(trigger=Pin.IRQ_RISING, handler=pir_handler)
text_ausgabe("Erledigt, bereit")
