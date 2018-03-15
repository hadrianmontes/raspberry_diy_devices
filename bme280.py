import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte


class BME280(object):
    DEFAULT_ADDRESS = 0x76

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

        if address is None:
            self._address = self.DEFAULT_ADDRESS
        else:
            self._address = address

        if bus is None:
            self._bus = smbus.SMBus(busaddress)
        else:
            self._bus = bus

        self._read_chip_info()

    def _read_chip_info(self):
        (self._chip_id, self._chip_version) = self.bus.read_i2c_block_data(self.address,
                                                                           0xD0, 2)

    @static_method
    def get_signed(da)
        
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
                     
