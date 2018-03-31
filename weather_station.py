import time
import os.path
from collections import deque
from bme280 import BME280
from matplotlib import dates
import matplotlib.pyplot as plt


class WeatherStation(object):

    def __init__(self, update_time=300, logfile=None, maxbuffer=None,
                 stdout_print=True, **kwargs):
        self.sensor = BME280(**kwargs)
        self._update_time = update_time
        self._databuffer = deque(maxlen=maxbuffer)
        self.date_format = "%d-%m-%Y %H:%M:%S"
        self._print = stdout_print
        self._stop = False
        self._data = {
            "temperature": None,
            "pressure": None,
        }

        if logfile is not None:
            self._open_and_load(logfile)
        else:
            self._logfile = None


    def _open_and_load(self, logfile):
        if os.path.isfile(logfile):
            nspaces_format = len(self.date_format.split())
            self._logfile = open(logfile, "r+")
            for line in self._logfile:
                line = line.split()
                date = " ".join(line[:nspaces_format])
                epoch = time.mktime(time.strptime(date, self.date_format))
                temperature = float(line[nspaces_format])
                pressure = float(line[nspaces_format + 1])
                self._databuffer.append((epoch, temperature, pressure))
        else:
            self._logfile = open(logfile, "w")

    def run(self, maxtime=None):
        start = time.time()
        while not self._stop:
            self.update_values()
            time.sleep(self._update_time)

            if maxtime is not None:
                if time.time() > (start + maxtime):
                    break


    def plot(self):
        date, temperature, pressure = zip(*self._databuffer)
        date = [dates.num2date(dates.epoch2num(i))
                for i in date]
        _, ax = plt.subplots()
        ax2 = ax.twinx()
        ax.plot(date, temperature)
        ax2.plot([],[], label="Tmeperature")
        ax2.plot(date, pressure, label="Pressure")
        ax.set_ylabel(r"Temperature ($^\circ$C)")
        ax2.set_ylabel("Pressure (hPa)")
        ax2.legend()


    def update_values(self):
        self.sensor.update()
        self._data["temperature"] = self.sensor.temperature
        self._data["pressure"] = self.sensor.pressure

        self._databuffer.append((time.time(),
                                 self._data["temperature"],
                                 self._data["pressure"]))

        if self._logfile is not None:
            self._logfile.write(time.strftime(self.date_format))

            data = "    {:5.2f}    {:8.1f}\n".format(self._data["temperature"],
                                                     self._data["pressure"])
            self._logfile.write(data)
            self._logfile.flush()

        if self._print:
            text = "{} -> temperature = {:5.2f} C; Pressure = {:8.1f} hPa"
            text = text.format(time.strftime(self.date_format),
                               self._data["temperature"],
                               self._data["pressure"])
            print(text)

    def close(self):
        """
        Closes the log file, if any
        """
        if self._logfile is not None:
            self._logfile.close()
