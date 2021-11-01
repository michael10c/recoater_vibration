
import numpy as np
import matplotlib.pyplot as plt
import scipy.linalg as la
import math
import json
import scipy.signal
import sys

from matplotlib import pyplot as plt
# rfft: only real side
from scipy.fft import fft, fftfreq, rfft, rfftfreq


def read_values():
    # grab number of samples (sample size) from data
    number_of_samples = data['sampleSize']
    # grab period ( sampling interval) from data
    period = data['samplingInterval']
    # grab accel values
    accelSignal = (data['values'])

    return number_of_samples, period, accelSignal



### Reading force data
#   On BBB
# accelFilepath = '/home/debian/frfRawData/force.txt'
# accelFilepath = '/var/lib/node-red/frfRawData/force.txt'

# assign path to varialbe
accelFilepath='C:\\Users\\Michael\\OneDrive - Georgia Institute of Technology\\recoater blade masters\\code\\test_data\\accel2.txt'

# start list
accelSignal = []

# open file above and load the json object into data variable
with open(accelFilepath) as f:
    data = json.load(f)

# obtain values from file above and save into variables
number_of_samples, period, accelSignal = read_values()

# calc the freq from period
sampling_frequency = 1 / period
print("Sampling Frequency: ", sampling_frequency, " Hz")
print("Number of Samples: ", number_of_samples, " Samples")

# convert to float, each data point
accelSignal = [float(i) for i in accelSignal]

# convert list to array
array_accel = np.array(accelSignal)

# create empty array for centering
accel_centered = np.zeros([len(array_accel)])

# find the max point in data of accel, used to center the freq
max_accel = array_accel.max()

# center the signal to prevent the spike at zero
# need to remove if whole signal is not a sin wave
# accelSignal_center = [i - (max_accel/2) for i in accelSignal]

for i in range(0, len(array_accel), 1):
    accel_centered[i] = (array_accel[i] - (max_accel/2))*1.8/4095

# normalize signal
normalized_accel = (accel_centered / accel_centered.max())

# RMS of signal
rms = np.sqrt(np.mean(normalized_accel**2))
#print(normalized_accel)
#print(accelSignal_center)
print("RMS = ", rms)




#time = []
#for i in range(0, len(accelSignal), 1):
#    time.append(i * period)

# time domain
plot1 = plt.figure("Time Domain")
plt.title('Time vs Amplitude, Normalized')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(normalized_accel)
# git testing more more

# calc FFT
        # normalize FFT and * 2 to get same magnitude as time domain
y_mag = (rfft(normalized_accel)/number_of_samples)*2
x_freq = rfftfreq(number_of_samples, period)

# freq domains
plot2 = plt.figure("Frequency Domain")
plt.title('Frequency vs Magnitude, Normalized')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.plot(x_freq, np.abs(y_mag))
plt.show()

# Define output file
jsonFile = {
    "frequency": x_freq,
    "magnitude": y_mag
}

# On laptop
saveDataFilepath = 'C:\\Users\\Michael\\OneDrive - Georgia Institute of Technology\\recoater blade masters\\code\\test_data\\fft.txt'

# On BBB
# saveDataFilepath = '/var/lib/node-red/frfRawData/frf.txt'


f = open(saveDataFilepath, "w")
f.write(str(jsonFile))
f.close()

print("Hello from ATL")
