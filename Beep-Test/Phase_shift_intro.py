#!/usr/bin/env python
# -*- coding: utf-8 -*-
# refer: https://stackoverflow.com/questions/23377665/python-scipy-fft-wav-files
# refer for phase shift : 
import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack
import numpy as np
from matplotlib import pyplot as plt
import time
import cmath

fname = 'Feb_07_16;21;07_beep_test.wav'

fs_rate, signal = wavfile.read(fname)
print("Frequency sampling", fs_rate)
l_audio = len(signal.shape)
print("Channels", l_audio)
if l_audio == 2:
    signal = signal.sum(axis=1) / 2
N = signal.shape[0]
print("Complete Samplings N", N)
secs = N / float(fs_rate)
print("total secs of file", secs)
Ts = 1.0/fs_rate # sampling interval in time
print("Timestep between samples Ts", Ts)
t = scipy.arange(0, secs, Ts) # time vector as scipy arange field / numpy.ndarray

# Finding angle of signal
FFT_complex = scipy.fft(signal)
FFT_angle = np.angle(FFT_complex,1) # get angle in degrees (deg=1), radians deg=0

# Introducing phase shift +180degrees
newSignalFFT = FFT_complex * cmath.rect(1., np.pi/2)

# Reverse FFT
newSignal = scipy.ifft(newSignalFFT)

tic = time.perf_counter()
FFT = abs(scipy.fft(signal)) # gives absolute value of complex number
toc = time.perf_counter()
print(f"calculated for {toc - tic:0.4f} seconds")

FFT_side = FFT[range(int(N/2))] # one side FFT range
freqs = scipy.fftpack.fftfreq(signal.size, t[1]-t[0])
fft_freqs = np.array(freqs)
freqs_side = freqs[range(int(N/2))] # one side frequency range
fft_freqs_side = np.array(freqs_side)

############# Plotting #############
plt.subplot(411)
p1 = plt.plot(t, signal, "g") # plotting the signal
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.subplot(412)
p2 = plt.plot(freqs, FFT, "r") # plotting the complete fft spectrum
plt.xlabel('Frequency (Hz)')
plt.ylabel('Count dbl-sided')
plt.subplot(413)
p3 = plt.plot(freqs_side, abs(FFT_side), "b") # plotting the positive fft spectrum
plt.xlabel('Frequency (Hz)')
plt.ylabel('Count single-sided')
plt.subplot(414)
p3 = plt.plot(t, newSignal, "k")
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.savefig(fname+'.png', bbox_inches='tight')
plt.show()

np.savetxt(fname+'.txt', FFT_angle)
