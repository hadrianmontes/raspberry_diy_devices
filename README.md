# Raspberry DIY Devices
This module implements several classes to
interact with diferent sensors/devices conected to a raspberry pi.
Each device is impleneted in a separate file and independent from the
others (unless specified for some classes). The classes implemented
right now are:

  * Shift Register: A simple 8 bit shift register that can be chained to create bigger register.
    * File: [shift_register.py](./shift_register.py)
    * Fle Dependency: None
	* Status: Works for only 1 register, untested multiple ones
  * BME280 & BMP280: A temperature, pressure (and humidity) sensor conected by **I2C**.
    * File: [bme280.py](./bme280.py)
	* File Dependency: None
	* Status: Works for temperature and pressure and in the forced (manual) mode.
  * Weather station: Not a device _per se_ but a direct application of the BME280 sensor.
    * File: [weather_station.py](./weather_station.py)
	* File Dependency: [bme280.py](./bme280.py)
	* Status: In construction.

