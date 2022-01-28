#!/usr/bin/python3
# -*- coding:utf-8 -*-

#refer: https://markhedleyjones.com/projects/python-tone-generator

import numpy 
import pyaudio
import math
import time
 
 
class ToneGenerator(object):
 
    def __init__(self, samplerate=44100, frames_per_buffer=4410):
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.frames_per_buffer = frames_per_buffer
        self.streamOpen = False
 
    def sinewave(self):
        if self.buffer_offset + self.frames_per_buffer - 1 > self.x_max:
            # We don't need a full buffer or audio so pad the end with 0's
            xs = numpy.arange(self.buffer_offset,
                              self.x_max)
            tmp = self.amplitude * numpy.sin(xs * self.omega)
            out = numpy.append(tmp,
                               numpy.zeros(self.frames_per_buffer - len(tmp)))
        else:
            xs = numpy.arange(self.buffer_offset,
                              self.buffer_offset + self.frames_per_buffer)
            out = self.amplitude * numpy.sin(xs * self.omega)
        self.buffer_offset += self.frames_per_buffer
        return out
 
    def callback(self, in_data, frame_count, time_info, status):
        if self.buffer_offset < self.x_max:
            data = self.sinewave().astype(numpy.float32)
            return (data.tostring(), pyaudio.paContinue)
        else:
            return (None, pyaudio.paComplete)
 
    def is_playing(self):
        if self.stream.is_active():
            return True
        else:
            if self.streamOpen:
                self.stream.stop_stream()
                self.stream.close()
                self.streamOpen = False
            return False
 
    def play(self, frequency, duration, amplitude):
        self.omega = float(frequency) * (math.pi * 2) / self.samplerate
        self.amplitude = amplitude
        self.buffer_offset = 0
        self.streamOpen = True
        self.x_max = math.ceil(self.samplerate * duration) - 1
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.samplerate,
                                  output=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)
 
 
###############################################################################
#                                 Usage Example                               #
###############################################################################
 
# generator = ToneGenerator()
 
# frequency_start = 50        # Frequency to start the sweep from
# frequency_end = 10000       # Frequency to end the sweep at
# num_frequencies = 200       # Number of frequencies in the sweep
# amplitude = 0.50            # Amplitude of the waveform
# step_duration = 0.43        # Time (seconds) to play at each step
 
# for frequency in numpy.logspace(math.log(frequency_start, 10),
#                                 math.log(frequency_end, 10),
#                                 num_frequencies):
 
#     print("Playing tone at {0:0.2f} Hz".format(frequency))
#     generator.play(frequency, step_duration, amplitude)
#     while generator.is_playing():
#         pass                # Do something useful in here (e.g. recording)

#### own usage ####
def record(duration=60):
    
    # Constants for audio devices
    FORMAT  = pyaudio.paInt16    # 24-bit the mic is 24-bit with sample rate of 96kHz
    CHANNELS = 1                 # number of audio streams to use. Since there is one speaker and one mic, use 2 streams
    RATE = 44100               # 44kHz
    FRAMES_PER_BUFFER = 1024    # 
    
    p = pyaudio.PyAudio()
    
    data = [] #place holder for data output
    data.append([])
    data.append([])
    def callback(in_data, frame_count, time_info, status):
            fromType = numpy.int16
            dfloat = numpy.frombuffer(in_data,fromType).astype(numpy.float) # convert integer to float values
            data_np = numpy.array(dfloat) # convert float data into numpy array
            data_fft = numpy.fft.fft(data_np) # transform into freq domain
            data[0].append(in_data)
            data[1].append(data_fft)
            
            return in_data, pyaudio.paContinue

        
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        input=True,
        input_device_index=2,
        stream_callback = callback)
    
   
    # start stream
    stream.start_stream()

    # control how long the stream to record
    time.sleep(duration) # in seconds

    # stop stream
    stream.stop_stream()   
    
    stream.close()
    
    return data

def beep(frequency=440, duration=5, amplitude=0.5):
    
    generator = ToneGenerator()
    generator.play(frequency,duration,amplitude)
    
    while generator.is_playing():
        data = record(5)
        
    return data
    
    
    
    
    
import csv

if __name__ == '__main__':
   result = beep(440,5,0.5)
   with open('Beep_test_1.csv','w') as file:
       write = csv.write(file)
       
   file.write(str(result))

