# -*- coding: utf-8 -*-
"""
Author: Ainul Rahim
Tone Generator
"""

import numpy as np
import pyaudio
import math
from signal import pause

def sinewave(buffer_offset, x_max, omega, amplitude, frames_per_buffer):
    if buffer_offset + frames_per_buffer -1 == x_max:
        # we don't need a full buffer or audio so pad the end with 0's
        xs = np.arange(buffer_offset, x_max)
        tmp = amplitude * np.sin(xs * omega)
        out = np.append(tmp, np.zeros(frames_per_buffer - len(tmp)))
        
    else:
        xs = np.arange(buffer_offset, buffer_offset + frames_per_buffer)
        out = amplitude * np.sin(xs * omega)
        buffer_offset += frames_per_buffer
        return out
    

def play_tone(frequency, frequency2, duration, samplerate, frames_per_buffer, amplitude):
    omega = float(frequency) * (np.pi*2) / samplerate
    omega2 = float(frequency2) * (np.pi*2) / samplerate
    amplitude = amplitude
    buffer_offset = 0
    x_max = math.ceil(samplerate * duration) - 1
    print(x_max)
    
    def callback(in_data, frame_count, time_info, status):
        print('still out')
        if buffer_offset < x_max:
            print('in')
            data = sinewave(buffer_offset, x_max, omega, amplitude, frames_per_buffer).astype(np.int16) + sinewave(buffer_offset, x_max, omega2, amplitude, frames_per_buffer).astype(np.int16)
            return (data.tostring(), pyaudio.paContinue)
        else:
            print('here')
            return(None, pyaudio.paComplete)
        
    
    s = p.open(format=pyaudio.paInt16,
               channels=1,
               rate=samplerate,
               output=True,
               frames_per_buffer=frames_per_buffer,
               stream_callback=callback,
               output_device_index = 1)

if __name__ == '__main__':
    
    p = pyaudio.PyAudio()
    # buffer_offset = 0
    play_tone(440, 1000, 1, 44100, 4410, 5000)
    pause() # since running in console it will end when the script end. Thonny keeps the background run. so adding pause() solve this problem
    
# NOTE: even though the duration is set to be 1, it runs longer than 1s. duration is step_duration meaning, time(in seconds) to play at each step