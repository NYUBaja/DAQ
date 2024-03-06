import os
import sensor_ids
import driver_telemetry
import math
from datetime import datetime
from datapoint import Datapoint
import numpy as np
from numpy.fft import fft
from copy import copy
from statistics import mean

class Formulas:
    """
    This class should be used to do more complex calculations of data from the sensors.
    For instance we use formulas.py to use the fourier transform to find the frequency of the hall sensor to get
    the speed of the car. All graphical calculations will most likely be handled by Mercury Telemetry. This class may be
    redundant and obselete once we fully integrate Hg Telemetry. We designed forulas to be made as an instance so calculations can be logged seperately
    """
    def __init__(self):
        now = datetime.now()
        self.log = open(os.getcwd() + "/datalogs/Formulas_" + now.strftime("%m%d%Y_%H-%M-%S") + ".txt","x")  # timestamping the text file and making a new log
        self.log.write("Test formulas\n")


    def calculate_speed(self, data_point):
        data_point.outputs = [data_point.outputs[0] * 60 * math.pi * driver_telemetry.WHEEL_DIAMETER/ (66360 * 10)]

    def calculate_fourier_speed(self, data_point):
        """
         This method is the same as the MATLAB method in the project directory.
         We use a Fast Fourier transform to find the dominant frequency
        of the periodic pulse function generated by the hall sensor.
        This frequency will be directly proportional to the speed of the car.
        :param data_point: Datapoint of samples from the Hall sensor. Should be 100 samples for each calculation for best results
        :return: The speed of the car (hopefully)

        """

        Fs = 100 #sampleing frequency = 9600
        x = copy(data_point.outputs)   #array of sampled hall effect values
        average = mean(x)
        for i in range(len(x)):
            x[i] -= average     #subtract mean
        nfft = 512
        y = np.fft.fft(np.array(x), nfft)       #apply fourier transform
        y = np.absolute(y * y)                   #raw power spectrum density
        lst =  list(y.tolist())                       #convert NumPY array to list
        lst = lst[1:1+int(nfft/2)]                     #truncate to half spectrum
        m = max(lst)                            #get max value
        index = lst.index(m)                    #find index of max value
        f_scale = [i * Fs / nfft for i in range(int(nfft/2)+1)]  #scale index to frequency
        frequency = f_scale[index]              #calc frequency
        self.log.write("Calculated Dominant Fourier Frequency: " + str(frequency) + " at time t = " + str(data_point.t)+"\n")
        data_point.sense_id = sensor_ids.FOURIER_SPEED
        data_point.name = "Fourier Speed"
        data_point.num_outputs = 1
        data_point.series_names = ["Fourier Speed"]
        data_point.outputs = [frequency]
        data_point.units = ["hz"]
        return frequency

    def calculate_rising_falling_speed(self, data_point):
        threshold = 30.0
        sampling_time = 0.5 #seconds
        rising_edges = 0
        falling_edges = 0
        x = data_point.outputs
        prev_value = x[0]
        for value in x:
            if value > threshold and prev_value < threshold:
                rising_edges+=1
            elif value < threshold and prev_value > threshold:
                falling_edges+=1
            prev_value = value
        periods = (rising_edges + falling_edges) / 2
        frequency = periods * (1 / sampling_time)
        self.log.write("Calculated Rising/Falling Frequency: " + str(frequency) + " at time t = " + str(data_point.t) + "\n")
        data_point.sense_id = sensor_ids.RISING_FALLING_SPEED
        data_point.name = "Rising Falling Speed"
        data_point.num_outputs = 1
        data_point.series_names = ["Rising Falling Speed"]
        data_point.outputs = [frequency]
        data_point.units = ["hz"]
        return frequency

    def apply_calculation(self, data_point: Datapoint):
        if data_point.sense_id == sensor_ids.HALL_EFFECT:
            self.calculate_speed(data_point)
















