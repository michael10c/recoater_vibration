import numpy as np
import json
from matplotlib import pyplot as plt
# from scipy.fftpack import rfft, rfftfreq
from scipy.signal import butter, filtfilt
import datetime



def read_values():
    # read_values() returns data from json file
    # grab number of samples (sample size) from data
    sampleSize = data['sampleSize']
    # grab period ( sampling interval) from data
    samplingInterval = data['samplingInterval']
    # grab accel values
    values = (data['values'])

    return sampleSize, samplingInterval, values


def read_file():
    # reads json file
    with open(accelFilePath) as f:
        data_temp = json.load(f)

    return data_temp


# Reading data, assign path to variable
# X axis ############
# On BBB
accelFilePath = '/home/debian/recoater_vibration/data/testing_code/x_axis.txt'
# on PC
# accelFilePath = "C:\\Users\\Michael\\Documents\\master\\data\\cube\\trial_1\\45\\x_axis.txt"

data = read_file()

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

# Y axis##########################
# on PC
# accelFilePath = "C:\\Users\\Michael\\Documents\\master\\data\\cube\\trial_1\\45\\y_axis.txt"
# on BBB
accelFilePath = '/home/debian/recoater_vibration/data/testing_code/y_axis.txt'

# open file above and load the json object into data variable
data = read_file()

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

# traditional statistics
std_dev = np.std(array_accel, axis=1)
print("Std Dev.", std_dev)


# center the signal to prevent the spike at zero
# need to remove if whole signal is not a sin wave
# accelSignal_center = [i - (max_accel/2) for i in accelSignal]
for i in range(len(array_accel)):
    accel_centered[i] = (array_accel[i] - mean_accel[i])


# axis, index, values
noisy = accel_centered[1]
x = (range(len(noisy)))
fs = sampling_frequency
T = (1/fs) * len(noisy)
cutoff = 500

nyq = 0.5 * fs
# no large impact since not interested in precise freq
order = 2
n = int(T * fs)

def butter_lowpass_filter(noisy, cutoff, fs, order):
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    # analog = false to work at all
    b, a = butter(order, normal_cutoff, btype='low')
    y = filtfilt(b, a, noisy)
    return y


y = butter_lowpass_filter(noisy, cutoff, fs, order)

# plot1 = plt.figure("X-axis_filtered")
plt.subplot(2, 1, 1)
plt.plot(x, noisy, 'b-', linewidth=0.5, label='non-filtered data')
plt.subplot(2, 1, 2)
plt.plot(x, y, 'g-', linewidth=0.5, label='filtered data')
# plt.show()

# save = "C:\\Users\\Michael\\Desktop\\temp\\x-axis_filtered.png"
saveFigurePath_x = '/home/debian/recoater_vibration/data/testing_code/x_axis_filtered.png'
plt.savefig(saveFigurePath_x)

max_accel = np.amax(y)

# normalize signal
#for i in range(len(array_accel)):
#    norm_center[i] = (accel_centered[i] / max_accel_centered[i])

# RMS of signal
#rms = np.sqrt(np.mean((norm_center ** 2), axis=1))
#print("RMS = ", rms)

# # time domain
# plot1 = plt.figure("Time Domain X Axis")
# plt.title('Time vs Amplitude')
# plt.xlabel('Time (ms)')
# plt.ylabel('Amplitude')
# plt.plot(array_accel[0])
# plot2 = plt.figure("Time Domain Y Axis")
# plt.title('Time vs Amplitude')
# plt.xlabel('Time (ms)')
# plt.ylabel('Amplitude')
# plt.plot(array_accel[1])
#
# plot3 = plt.figure("Time Domain 3")
# plt.title('Time vs Amplitude, centered  X Axis')
# plt.xlabel('Time (ms)')
# plt.ylabel('Amplitude')
# plt.plot(accel_centered[0])
# plot4 = plt.figure("Time Domain 4")
# plt.title('Time vs Amplitude, centered  Y Axis')
# plt.xlabel('Time (ms)')
# plt.ylabel('Amplitude')
# plt.plot(accel_centered[1])
#
# plot5 = plt.figure("Time Domain 5")
# plt.title('Time vs Amplitude, Normalized and Centered  X Axis')
# plt.xlabel('Time (ms)')
# plt.ylabel('Amplitude')
# plt.plot(norm_center[0])
# plot6 = plt.figure("Time Domain 6")
# plt.title('Time vs Amplitude, Normalized and Centered  Y Axis')
# plt.xlabel('Time (ms)')
# plt.ylabel('Amplitude')
# plt.plot(norm_center[1])

# calc FFT
# normalize FFT and * 2 to get same magnitude as time domain
# magnitude_FFT = (rfft(norm_center) / number_of_samples) * 2
# frequency_FFT = rfftfreq(number_of_samples, period)

print("Maximum acceleration: ", max_accel, "m/s^2")
#print("Minimum acceleration: ", min_accel, "m/s^2")
# print("Frequency of maximum magnitude: ", frequency_FFT[np.argmax(magnitude_FFT, axis=1)], "Hz")

# # freq domains
# plot7 = plt.figure("Frequency Domain X-axis")
# plt.title('Frequency vs Magnitude, Normalized')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Magnitude')
# plt.plot(frequency_FFT, np.abs(magnitude_FFT[0]))
# saveFigurePath_x = '/home/debian/recoater_vibration/data/testing_code/x_axis_FFT.png'
# plt.savefig(saveFigurePath_x)

# plot8 = plt.figure("Frequency Domain Y-Axis")
# plt.title('Frequency vs Magnitude, Normalized')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Magnitude')
# plt.plot(frequency_FFT, np.abs(magnitude_FFT[1]))
# plt.show()

#  Convert output to list for creating json file
# frequency_FFT = frequency_FFT.tolist()
# x_axis_magnitude = np.abs(magnitude_FFT).tolist()[0]
# y_axis_magnitude = np.abs(magnitude_FFT).tolist()[1]

# Define output file
# jsonFile = {
#     "frequency_FFT": frequency_FFT,
#     "x_axis_magnitude": x_axis_magnitude,
#     "y_axis_magnitude": y_axis_magnitude
# }

# On BBB
# saveDataFilepath = '/home/debian/recoater_vibration/data/testing_code/processed_accel.txt'
# saveFigurePath_y = '/home/debian/recoater_vibration/data/testing_code/y_axis_FFT.png'
# On laptop
# saveDataFilepath = "C:\\Users\\Michael\\Documents\\master\\data\\testing_code\\x_axis_fft.txt"

# plt.savefig(saveFigurePath_y)


# f = open(saveDataFilepath, "w")
# f.write(str(jsonFile))
# f.close()

print("Hello from BBB")
print("Timestamp: ", datetime.datetime.now())











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
