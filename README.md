# Funktionsmotor

## Hilfreiche Links

https://sensorkit.joy-it.net/index.php?title=KY-053_Analog_Digital_Converter<br>
https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15<br>
https://circuitpython.readthedocs.io/projects/ads1x15/en/latest/<br>
https://joy-it.net/files/files/Produkte/SBC-CAN01/SBC-CAN01-Anleitung-20201021.pdf<br>
https://itnext.io/raspberry-pi-read-only-kiosk-mode-the-complete-tutorial-for-2021-58a860474215<br>
https://www.makeuseof.com/how-to-run-a-raspberry-pi-program-script-at-startup

## Informationen

| Sensor         | CAN ID | Multiplikator | CAN Faktor |
| -------------- | ------ | ------------- | ---------- |
| Krümmer       | 200    | 1             | 1          |
| Katalysator    | 201    | 1             | 1          |
| Ölwanne       | 202    | 1             | 1          |
| Drehzahl       | 203    | 1             | 1          |
| Leistung       | 204    | 100           | 0.01       |
| Moment         | 205    | 100           | 0.01       |
| Spritverbrauch | 206    | 100           | 0.01       |

<br>
<img src="https://gitlab.com/Retch/funktionsmotor/-/raw/main/fritzing.png" alt="Schematic" width="600" >
<br>
<br>

# Fertige Raspbian Images

## Fertiges Image für die SD Karte hier verfügbar
https://gitlab.com/Retch/funktionsmotor-images/-/raw/main/funktionsmotor-raspbian-2022-1-28.img<br>
Auf die SD Karte brennen. Der erste Start kann ein paar Minuten in Anspruch nehmen.

## Optional
Wie in der Anleitung bei Punkt 6 Read-Only machen<br>
https://itnext.io/raspberry-pi-read-only-kiosk-mode-the-complete-tutorial-for-2021-58a860474215

# Schrittweise Installation
## Vorbereitung
Als erstes muss das Raspbian Image auf die SD Karte geschrieben werden.

Einstellen, dass python3 benutzt wird wenn man "python" eintippt und nicht python2:<br>
<code>sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10</code>

Pigpio (für Frequenzmessung) und Can-Utils installieren<br>
<code>sudo apt-get install pigpio can-utils</code>

Pigpio beim start automatisch laden<br>
<code>sudo systemctl enable pigpiod</code>

Config Datei öffnen<br>
<code>sudo nano /boot/config.txt</code><br>

Folgendes an das Ende der Datei hinzufügen und Raspberry neustarten

```
dtparam=i2c_arm=on
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
dtoverlay=sp1-1cs
dtoverlay=i2c-gpio,bus=4,i2c_gpio_sda=17,i2c_gpio_scl=27
```

Projekt auf dem Raspberry herunterladen<br>
<code>git clone https://github.com/HenningCV/funktionsmotor-fh.git</code>

In das Projektverzeichnis wechseln<br>
<code>cd funktionsmotor-fh/</code>

Python packages installieren<br>
<code>sudo -H pip install -r requirements.txt</code>

Programm testen<br>
<code>python main.py</code>
