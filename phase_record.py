import multiprocessing as mp
import pyaudio
import numpy as np
import wave

from datetime import datetime
import time

import math
from signal import pause

################################ Recording Sound ########################################################################
class Recorder(object):
      def __init__(self, channels=1,rate=48000,frames_per_buffer=4800,input_device_index=1):
          # with monitor, input_device_index=2, without monitor = 1
          
          self.channels = channels
          self.rate = rate
          self.frames_per_buffer = frames_per_buffer
          self.input_device_index = input_device_index
       
      def open(self, fname, mode='wb'):
          return RecordingFile(fname,mode,self.channels,self.rate,self.frames_per_buffer,self.input_device_index)
       
class RecordingFile(object):
      def __init__(self,fname,mode,channels,rate,frames_per_buffer,input_device_index):
          self.fname = fname
          self.mode = mode
          self.channels = channels
          self.rate = rate
          self.frames_per_buffer = frames_per_buffer
          self.input_device_index = input_device_index
          self._pa = pyaudio.PyAudio()
          self.wavefile = self._prepare_file(self.fname, self.mode)
          self._stream = None
      
      def __enter__(self):
          return self
       
      def __exit__(self,exception,value,traceback):
          self.close()
      
      # Blocking mode
      def record(self, duration):
          self._stream = self._pa.open(format=pyaudio.paInt16,
                                       channels = self.channels,
                                       rate = self.rate,
                                       input = True,
                                       frames_per_buffer = self.frames_per_buffer,
                                       input_device_index= self.input_device_index)
          for _ in range(int(self.rate / self.frames_per_buffer * duration)):
              audio = self._stream.read(self.frames_per_buffer)
              self.wavefile.writeframes(audio)
          return None
         
      # Callback mode
      def start_recording(self):
          self._stream = self._pa.open(format=pyaudio.paInt16,
                                       channels = self.channels,
                                       rate = self.rate,
                                       input = True,
                                       frames_per_buffer = self.frames_per_buffer,
                                       input_device_index= self.input_device_index,
                                       stream_callback=self.get_callback())
          self._stream.start_stream()
          return self
        
      def stop_recording(self):
          self._stream.stop_stream()
          return self
  
      def get_callback(self):
          def callback(in_data,frame_count,time_info,status):
              self.wavefile.writeframes(in_data)
              return in_data, pyaudio.paContinue
          return callback
       
      def close(self):
          self._stream.close()
          self._pa.terminate()
          self.wavefile.close()


def rec(fname,duration=10):
    data = Recorder()
    with data.open(fname,'wb') as recfile:
         recfile.start_recording()
         time.sleep(duration)
         recfile.stop_recording()
         
#################### Playing Specific Frequency Tone ######################################
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
    

def play_tone(frequency, duration, samplerate, frames_per_buffer, amplitude, output_device_index=1):
    omega = float(frequency) * (np.pi*2) / samplerate
    amplitude = amplitude
    buffer_offset = 0
    x_max = math.ceil(samplerate * duration) - 1
    print(x_max)
    
    def callback(in_data, frame_count, time_info, status):
        if buffer_offset < x_max:
            data = sinewave(buffer_offset, x_max, omega, amplitude, frames_per_buffer).astype(np.int16)
            return (data.tostring(), pyaudio.paContinue)
        else:
            return(None, pyaudio.paComplete)
        
    
    s = p.open(format=pyaudio.paInt16,
               channels=1,
               rate=samplerate,
               output=True,
               frames_per_buffer=frames_per_buffer,
               stream_callback=callback,
               output_device_index = output_device_index)
    
if __name__ == '__main__':
    FILENAME = datetime.now().strftime("%b_%d_%H;%M;%S_0mm.wav")
    FREQ = 440                 # in Hz
    DURATION = 10              # in s
    SAMPLERATE = 48000         # in Hz
    CHUNK = 4800               # frames_per_buffer
    AMP = 5000                 # since int16, range 5000 is half level to hear
    OUTPUT_DEVICE_INDEX = 0    # 0 for headless, 1 with monitor
    
    p1 = mp.Process(target=play_tone, args=(FREQ, DURATION, SAMPLERATE, CHUNK, AMP, OUTPUT_DEVICE_INDEX))
    p2 = mp.Process(target=rec, args=(FILENAME, DURATION))
    
    p1.start()
    time.sleep(1.5) # make the recording run first 1.5s then play sound 
    p2.start()
   
    p1.join()
    p2.join()
