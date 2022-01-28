#!/usr/bin/python3
# -*- coding:utf-8 -*-

# 1. Play the beep (500Hz)
# 2. Record the beep

import pygame
import numpy as np

#defining output device
import pygame._sdl2 as sdl2

pygame.init()
is_capture = 0  # zero to request playback devices, non-zero to request recording devices
num = sdl2.get_num_audio_devices(is_capture)
names = [str(sdl2.get_audio_device_name(i, is_capture), encoding="utf-8") for i in range(num)]
print("\n".join(names))
pygame.quit()



#1. Play beep
def beep(duration=60000):
    fs = 44100
    freq = 440

    pygame.mixer.pre_init(44100,-16,2,1024)
    # sampling freq, size, channels, buffer

    # Sampling frequency
    # Analog audio is recorded by sampling it 44100 times per second,
    # and then these samples are used to reconstruct the audio signal
    # when playing it back

    # size
    # the size argument represents how many bits are used for each audio sample.
    # if the value is negative then signed sample values will be used

    # channels
    # 1 = mono, 2 = stereo

    # buffer
    # the buffer argument controls the number of internal samples
    # used in the sound mixer. It can be lowered to reduce latency,
    # but sound dropout may occur. It can be raised to larger values to
    # ensure the playback never skips, but it will impose latency on sound playback

    arr = np.array([4096*np.sin(2.0*np.pi*freq*x/fs) for x in range(0,fs)]).astype(np.int16)
    arr2 = np.c_[arr,arr] # since 2 channels
    sound = pygame.sndarray.make_sound(arr2)
    sound.play(-1)
    pygame.time.delay(duration) # in milliseconds 60000 is 60s
    sound.stop()
    
    return arr2

#2
import pyaudio
import time
# Constants for audio devices
FORMAT  = pyaudio.paInt16    # 24-bit the mic is 24-bit with sample rate of 96kHz
CHANNELS = 2                 # number of audio streams to use. Since there is one speaker and one mic, use 2 streams
RATE = 44100               # 44kHz
FRAMES_PER_BUFFER = 1024    # 


def record(duration=60):
    data = [] #place holder for data output
    data.append([])
    data.append([])
    
    def callback(in_data, frame_count, time_info, status):
            fromType = np.int16
            dfloat = np.frombuffer(in_data,fromType).astype(np.float) # convert integer to float values
            data_np = np.array(dfloat) # convert float data into numpy array
            data_fft = np.fft.fft(data_np) # transform into freq domain
            data[0].append(in_data)
            data[1].append(data_fft)
            
            return in_data, pyaudio.paContinue

        
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        input=True,
        input_device_index=3,
        stream_callback = callback)
    
   
    # start stream
    stream.start_stream()

    # control how long the stream to record
    time.sleep(duration) # in seconds

    # stop stream
    stream.stop_stream()   
    
    stream.close()
    
    return data
    
#### Execute #####
import multiprocessing as mp

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    
    p1 = mp.Process(target=beep)
    p2 = mp.Process(target=record)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    p1.terminate()
    p2.terminate()
    
