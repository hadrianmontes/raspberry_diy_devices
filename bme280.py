import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte


class BME280(object):

    DEFAULT_ADDRESS = 0x76
    REGISTERS = {"RESET": 0xE0,
                 "CRTL_MEAS": 0xF4,
                 "TRIMMING_START": 0x88,
                 "DATA": 0xF7}
    RESET_WORD = 0xB6
    TRIMMING_LENGTH = 24

    def __init__(self, busaddress=1, address=None, bus=None):
        """
        Creattes a bme280 temperature, pressure and (optionally)
        humidity using I2C.

        Parameters
        ----------
        busaddress : int (optional)
            THe bus addres were the I2C devices are found. This should
            be 0 for the raspberrypi rev. 1 and 1 for the other (at
            least until rev3. For non raspberrypi devices you must
            find the correct value. Default 1.
        address : int or None (optioanl)
            The I2C address of the device. If None the default one
            will be used. Default None.

        bus : smbus.SMBus or None
            If not None an open bus were the object can be found. If
            None a new bus will be opened. Default None

        """

        self._chip_id = None
        self._chip_version = None
        self._trimming = {}
        self._data = {"temperature": None,
                      "pressure": None,
                      "humidity": None}

        if address is None:
            self._address = self.DEFAULT_ADDRESS
        else:
            self._address = address

        if bus is None:
            self._bus = smbus.SMBus(busaddress)
        else:
            self._bus = bus

        self._read_chip_info()
        self._read_trimming()

    def _read_trimming(self):
        # Trimmings for temperature
        trimming_start = self.REGISTERS["TRIMMING_START"]
        trimmings = self.bus.read_i2c_block_data(self.address,
                                                 trimming_start,
                                                 self.TRIMMING_LENGTH)
        # combine the trims
        first = trimmings[::2]
        second = trimmings[1::2]
        trims = []
        for first, second in zip(first, second):
            trims.append(self._combine_bytes(first, second))
        trims[4:] = [c_short(value).value for value in trims[4:]]
        self._trimming["temperature"] = trims[:3]
        self._trimming["pressure"] = trims[3:]

    def _read_data(self):
        data = self.bus.read_i2c_block_data(self.address,
                                            self.REGISTERS["DATA"],
                                            8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        self._data["temperature"] = self._refine_temperature(temp_raw)
        self._data["pressure"] = self._refine_pressure(pres_raw)
        self._data["humidity"] = self._refine_humidity(hum_raw)

    @staticmethod
    def _combine_bytes(first, second):
        return (second << 8) + first

    def _read_chip_info(self):
        (self._chip_id,
         self._chip_version) = self.bus.read_i2c_block_data(self.address,
                                                            0xD0, 2)

    def _refine_humidity(self, humidity):
        return humidity
 
    def _refine_temperature(self, temperature):
        """
        Temperature must be int 32
        """
        # Witchcraft from the datasheet (page 23)

        dig1, dig2, dig3 = self._trimming["temperature"]

        var1 = ((((temperature>>3)-(dig1<<1)))*(dig2)) >> 11
        var2 = (((((temperature>>4) - (dig1))
                  * ((temperature>>4) - (dig1))) >> 12) * (dig3)) >> 14
        temperature_fine = var1 + var2
        return temperature_fine

    def _refine_pressure(self, pressure):
        # More witchcraft from page 23 of the datasheet

        (dig1, dig2, dig3, dig4, dig5, dig6,
         dig7, dig8, dig9) = self._trimming["pressure"]
        temperature = self._data["temperature"]

        var1 = (temperature/2.0) - 64000.0
        var2 = var1 * var1 * dig6 / 32768.0
        var2 = var2 + var1 * dig5 * 2.0
        var2 = (var2/4.0)+(dig4 * 65536.0)
        var1 = (dig3 * var1 * var1 / 524288.0 + dig2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig1
        if var1 == 0.0:
            return 0

        p_refined = 1048576.0 - pressure
        p_refined = (p_refined - (var2 / 4096.0)) * 6250.0 / var1
        var1 = dig9 * p_refined * p_refined / 2147483648.0
        var2 = p_refined * dig8 / 32768.0
        p_refined = p_refined + (var1 + var2 + dig7) / 16.0
        return p_refined

    @property
    def address(self):
        """
        I2C address of the sensor
        """
        return self._address
    @address.setter
    def address(self, value):
        self._address = value

    @property
    def bus(self):
        """
        Returns the opened bus to the device
        """
        return self._bus

    @property
    def chip_id(self):
        """
        Id of the chip
        """
        return self._chip_id

    @property
    def chip_version(self):
        """
        The version of the chip
        """
        return self._chip_version

    @property
    def temperature(self):
        """
        Returns the refined temperature
        """
        return float(((self._data["temperature"] * 5) +128) >> 8)/100.

    @property
    def pressure(self):
        """
        Returns the refined pressure
        """
        return self._data["pressure"] / 100.0

    @property
    def status(self):
        """
        Returns the oversampling in temperature, pressure and current mode
        """
        value = self.bus.read_i2c_block_data(self.address,
                                             self.REGISTERS["CTRL_MEAS"], 1)[0]

        temp_over = value >> 5
        value -= temp_over << 5

        hum_over = value >> 2
        value -= hum_over << 2

        return (temp_over, hum_over, value)

    def reset(self):
        """
        Resets the sensor
        """
        self.bus.write_byte_data(self.address, self.REGISTERS["RESET"],
                                 self.RESET_WORD)

    def update(self):
        """
        Updates the readings of the sensor
        """
        self._read_data()
