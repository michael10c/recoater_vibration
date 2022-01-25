import numpy as np
import json
from matplotlib import pyplot as plt
# rfft: only real side
#from scipy.fft import rfft, rfftfreq
from scipy.fftpack import rfft, rfftfreq


def read_values():
    """ read_values() returns data from json file
    """

    # grab number of samples (sample size) from data
    sampleSize = data['sampleSize']
    # grab period ( sampling interval) from data
    samplingInterval = data['samplingInterval']
    # grab accel values
    values = (data['values'])

    return sampleSize, samplingInterval, values


# cannot REUSE NAME!!!!!

# Reading data, assign path to variable
# On BBB
#accelFilePath = '/home/debian/recoater_vibration/data/testing_code/x_axis.txt'
# accelFilePath = '/var/lib/node-red/frfRawData/force.txt'

## X axis
# on PC
accelFilePath = "C:\\Users\\Michael\\Documents\\master\\data\\testing_code\\x_axis.txt"

# start list, do I need this?
# accelSignal = []

# open file above and load the json object into data variable
with open(accelFilePath) as f:
    data = json.load(f)

# obtain values from file above and save into variables
number_of_samples, period, accelSignal = read_values()

# calc the freq from period
sampling_frequency = 1 / period
print("Sampling Frequency: ", sampling_frequency, " Hz")
print("Number of Samples: ", number_of_samples, " Samples")

# convert from string to float, each data point
accelSignal = [float(i) for i in accelSignal]

# convert list to array
array_accel_x = np.array(accelSignal)

## Y axis
# on PC
accelFilePath = "C:\\Users\\Michael\\Documents\\master\\data\\testing_code\\y_axis.txt"

# open file above and load the json object into data variable
with open(accelFilePath) as f:
    data = json.load(f)

# obtain values from file above and save into variables
number_of_samples, period, accelSignal = read_values()

# calc the freq from period
sampling_frequency = 1 / period
print("Sampling Frequency: ", sampling_frequency, " Hz")
print("Number of Samples: ", number_of_samples, " Samples")

# convert from string to float, each data point
accelSignal = [float(i) for i in accelSignal]

# convert list to array
array_accel_y = np.array(accelSignal)

array_accel = np.vstack([array_accel_x, array_accel_y])

# create empty array for centering
accel_centered = np.zeros([len(array_accel[:, 0]), len(array_accel[0, :])])
norm_center = np.zeros([len(array_accel[:, 0]), len(array_accel[0, :])])

# find the max point in data of accel, used to center the freq
max_accel = np.amax(array_accel, axis=1)
min_accel = np.amin(array_accel, axis=1)
range_accel = max_accel - min_accel
mid_accel = range_accel / 2
mean_accel = array_accel.mean(axis=1)


# center the signal to prevent the spike at zero
# need to remove if whole signal is not a sin wave
# accelSignal_center = [i - (max_accel/2) for i in accelSignal]
for i in range(len(array_accel)):
    accel_centered[i] = (array_accel[i] - mean_accel[i])

max_accel_centered = np.amax(accel_centered, axis=1)

# normalize signal
for i in range(len(array_accel)):
    norm_center[i] = (accel_centered[i] / max_accel_centered[i])

# RMS of signal
rms = np.sqrt(np.mean(norm_center ** 2))
# print(normalized_accel)
# print(accelSignal_center)
print("RMS = ", rms)

# time = []
# for i in range(0, len(accelSignal), 1):
#    time.append(i * period)

# my_fig = plt.figure(figsize=(10.0, 4.0))
# time = my_fig.add_subplot(2, 2, 1)
# time_c = my_fig.add_subplot(2, 2, 2)
# time_cn = my_fig.add_subplot(2, 2, 3)
# freq = my_fig.add_subplot(2, 2, 4)



# time domain
plot1 = plt.figure("Time Domain X Axis")
plt.title('Time vs Amplitude')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(array_accel[0])
plot2 = plt.figure("Time Domain Y Axis")
plt.title('Time vs Amplitude')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(array_accel[1])

plot3 = plt.figure("Time Domain 3")
plt.title('Time vs Amplitude, centered  X Axis')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(accel_centered[0])
plot4 = plt.figure("Time Domain 4")
plt.title('Time vs Amplitude, centered  Y Axis')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(accel_centered[1])

plot5 = plt.figure("Time Domain 5")
plt.title('Time vs Amplitude, Normalized and Centered  X Axis')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(norm_center[0])
plot6 = plt.figure("Time Domain 6")
plt.title('Time vs Amplitude, Normalized and Centered  Y Axis')
plt.xlabel('Time (ms)')
plt.ylabel('Amplitude')
plt.plot(norm_center[1])

# calc FFT
# normalize FFT and * 2 to get same magnitude as time domain
y_mag = (rfft(norm_center) / number_of_samples) * 2
x_freq = rfftfreq(number_of_samples, period)

# freq domains
plot7 = plt.figure("Frequency Domain 7")
plt.title('Frequency vs Magnitude, Normalized')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.plot(x_freq, np.abs(y_mag[0]))
plot8 = plt.figure("Frequency Domain 8")
plt.title('Frequency vs Magnitude, Normalized')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.plot(x_freq, np.abs(y_mag[1]))
plt.show()


#  Convert output to list for creating json file
x_freq = list(x_freq)
y_mag = list(y_mag)


# Define output file
jsonFile = {
    "frequency": x_freq,
    "magnitude": y_mag
}

# On laptop
saveDataFilepath = "C:\\Users\\Michael\\Documents\\master\\data\\testing_code\\x_axis_fft.txt"

# push

# On BBB
# saveDataFilepath = '/var/lib/node-red/frfRawData/frf.txt'
#saveDataFilepath = '/home/debian/recoater_vibration/data/testing_code/z_axis_fft.txt'


f = open(saveDataFilepath, "w")
f.write(str(jsonFile))
f.close()

print("Hello from Windows")




























# grouping plots
# # plot2 = plt.figure("Time Domain2")
# time_c.set_title('Time vs Amplitude, centered')
# time_c.set_xlabel('Time (ms)')
# time_c.set_ylabel('Amplitude')
# time_c.plot(accel_centered)
#
# # plot3 = plt.figure("Time Domain3")
# time_cn.set_title('Time vs Amplitude, Normalized and Centered')
# time_cn.set_xlabel('Time (ms)')
# time_cn.set_ylabel('Amplitude')
# time_cn.plot(norm_center)
#
# # calc FFT
# # normalize FFT and * 2 to get same magnitude as time domain
# y_mag = (rfft(norm_center) / number_of_samples) * 2
# x_freq = rfftfreq(number_of_samples, period)
#
# # freq domains
# # plot4 = plt.figure("Frequency Domain")
# freq.set_title('Frequency vs Magnitude, Normalized')
# freq.set_xlabel('Frequency (Hz)')
# freq.set_ylabel('Magnitude')
# freq.plot(x_freq, np.abs(y_mag))
# plt.show()
