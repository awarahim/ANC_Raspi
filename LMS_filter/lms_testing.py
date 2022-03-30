import pyaudio
import numpy as np
import fir_filter
import multiprocessing as mp
import signal
import sys
import pylab as pl
import time
import csv
from datetime import datetime

## helper function ##
def device_check():
    p = pyaudio.PyAudio()
    devices = []
    
    for ii in range(p.get_device_count()):
        devices.append(p.get_device_info_by_index(ii).get('name'))
        print(p.get_device_info_by_index(ii).get('name'))
    p.terminate()
    return devices

device_check()



# Stop signal handler by Ctrl-C
stop_event = mp.Event()

def stop(signum, frame):
    global stop_event
#     logging.info(f"SIG[{signum}] " + 'KeyboardInterrupt ' + str(datetime.now()))
    print('KeyboardInterrupt')
    stop_event.set()
    
# Constants for audio devices
FORMAT  = pyaudio.paInt16    # 24-bit the mic is 24-bit with sample rate of 96kHz
CHANNELS = 1                 # number of audio streams to use. Since there is one speaker and one mic, use 2 streams
RATE = 44100                # 44.1kHz
FRAMES_PER_BUFFER = 1024    # number of frames the speaker is taking in 



def ref_mic(p, q1, stop_event):
    global FORMAT
    global CHANNELS
    global RATE
    global FRAMES_PER_BUFFER
    
    
    
    f = fir_filter.FIR_filter(np.zeros(FRAMES_PER_BUFFER))
    y = np.empty(FRAMES_PER_BUFFER)
    fnoise = 1500
    fs = 44100
    mu = 0.0015
    
    
    def callback(in_data, frame_count, time_info, status):
#         print(in_data)
        file = datetime.now().strftime('%b_%d_%H_%M_%S_LMS_test.csv')
        fromType = np.int16
        d = np.frombuffer(in_data,fromType).astype(np.float) # convert data from buffer from int16 to float
        
        for i in range(FRAMES_PER_BUFFER):
            ref_noise = np.sin(2.0 * np.pi * fnoise/fs * i)
#             print(ref_noise)
            canceller = f.filter(ref_noise) # a constant to be cancelled
#             print(canceller)
            output_signal = d[i] - canceller # becomes the error/desired signal
#             print(output_signal)
            f.lms(output_signal, mu) # updates the impulse response coefficient
            y[i] = output_signal
#             print(len(y))
        
        pname = datetime.now().strftime('%b_%d_%H_%M_%S')
        pl.figure()
        pl.plot(y)
        pl.savefig('filtered_data'+ pname +'.jpg')
        pl.figure()
        pl.plot(d)
        pl.savefig('raw_data' + pname +'.jpg')
#         q1.put(y)
#         print(len(q1.get()))

        #   save data of volume difference in csv file but this code don't work
        with open(file,'a') as fwrite:
            writer = csv.writer(fwrite)
            writer.writerows([d,y])
            fwrite.close()
        
        return in_data, pyaudio.paContinue
    
    
    
    stream2 = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=FRAMES_PER_BUFFER,
        input=True,
        input_device_index=2,
        stream_callback = callback)

#   k = 0
    
    print('ref mic running...')
    
    while not stop_event.wait(2):
            # start stream
        stream2.start_stream()
#         k = k+1
        print('still recording')
    
    print('ref mic is stopped')
    stream2.stop_stream()
    print('stream is stopped')
    stream2.close()
    print('stream is closed')
    
    
# def filtering(data_in, ntaps=1024, mu=0.01, fnoise=1200, fs=44100):
#     # filtering single frequency
#     
#     f = fir_filter.FIR_filter(np.zeros(ntaps))
#     y = np.empty(ntaps)                        # Return a new array of given shape and type, without initializing entries.empty, unlike zeros, does not set the array values to zero, and may therefore be marginally faster. On the other hand, it requires the user to manually set all the values in the array, and should be used with caution.
#     
#     tic = time.time()
#     for i in range(ntaps):
#         data_in[i] = q1.get()
#         ref_noise = np.sin(2.0 * np.pi * fnoise/fs * i)
#         canceller = f.filter(ref_noise) # a constant to be cancelled
#         output_signal = data_in[i] - canceller # becomes the error/desired signal
#         f.lms(output_signal, mu) # updates the impulse response coefficient
#         y[i] = output_signal
#     
#     toc = time.time() - tic
#     print('how long it takes to filter 100 data points: ', toc)
#     
#     pl.figure(1)
#     pl.plot(y)
#     pl.show()
        
if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    
    maxsize = 100
    NTAPS = maxsize
    LEARNING_RATE = 0.001
    FNOISE = 1200 # in Hz
    FS = 44100 # in Hz
    
    audio = pyaudio.PyAudio()
    
    q1 = mp.Queue(maxsize)
    
    p1 = mp.Process(target=ref_mic, args=(audio,q1, stop_event))
#     p2 = mp.Process(target=filtering, args=(NTAPS, LEARNING_RATE, FNOISE, FS, q1, stop_event))
    
    p1.start()
#     p2.start()
    
    p1.join() # must have
#     p2.join()
    
    
    print('FIN')
