"""
Purpose: Play 440 Hz tone through external speaker, record by ref mic and deliver to internal speaker to play in out of phase
"""
import signal
import sys

import pyaudio
import time
import wave

import multiprocessing as mp
import numpy as np
import scipy.fft as fft

# Stop signal handler by Ctrl-C
stop_event = mp.Event()

## pyaudio setup ##
FORMAT = 
CHANNELS = 
RATE = 
FRAMES_PER_BUFFER = 
#####################


## helper code ##



#####################


def ref_mic(p, q1, stop_event):   
   
    def callback(in_data, frame_count, time_info, status):
#             data = rms(in_data)
            
            # convert the in_data into float
            audio_data = np.fromstring(in_data, dtype=np.float32) 
            
            # filter to 100Hz to 1000Hz using np.fft.fft. Refer: https://www.youtube.com/watch?v=s2K1JfNR7Sc
            n = len(audio_data)
            fhat = np.fft.fft(audio_data,n)
            PSD = fhat * np.conj(fhat) / n  # give the power density of all signals
            
            # used PSD to filter out noise
            indices = PSD > lowPSD and PSD < highPSD  # where lowPSD is the signal with low threshold and highPSD with highthreshold (
           
            
            
            
            # invert the filtered signal
            
            
            # revert the float data into byte string 
            
            
            q1.put(in_data)
            
#             print("q1:", q1.get())
            # I want to hear the inverted data
            return out_data, pyaudio.paContinue 
        
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        input=True,
        input_device_index=2,
        stream_callback=callback)
    
    while not stop_event.wait(0):
        # start stream
        stream.start_stream()

    # stop stream
    stream.stop_stream()
    stream.close()
    
    
def speaker(p, q1, stop_event):
    def callback(in_data,frame_count,time_info,status):
        q1.get()
        return
    
    stream = p.open(
        format=FORMAT, 
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        output=True,
        output_device_index=1,
        stream_callback=callback)
   
    while not stop_event.wait(0):
        stream.start_stream()
    stream.stop_stream()
    stream.close()


if __name__ == '__main__':
    
    # ctrl-c
    signal.signal(signal.SIGINT, stop)
    
    p = pyaudio.PyAudio()
    q1 = mp.Queue()
    
    p1 = mp.Process(target=ref_mic, arg=(q1,))
    p1.start()
    p1.join()
    p1.terminate()
    
    
#refer: https://stackoverflow.com/questions/22101023/how-to-handle-in-data-in-pyaudio-callback-mode
