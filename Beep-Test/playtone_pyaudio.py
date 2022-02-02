#!/usr/bin/python3
# -*- coding:utf-8 -*-

#refer: https://markhedleyjones.com/projects/python-tone-generator
import multiprocessing as mp
import numpy 
import pyaudio
import math
import time
import wave
from datetime import datetime
 
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

class Recorder(object):
      def __init__(self, channels=1,rate=44100,frames_per_buffer=1024,input_device_index=2):
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
          
      def _prepare_file(self, fname,mode='wb'):
          wavefile = wave.open(fname,mode)
          wavefile.setnchannels(self.channels)
          wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
          wavefile.setframerate(self.rate)
          return wavefile  

     # def save_fft_data(self):
          
############################ Usage Example ##########################      
"""
Provides WAV recording functionality via two approaches:
Blocking mode (record for a set duration):
>>> rec = Recorder(channels=2)
>>> with rec.open('blocking.wav','wb') as recfile:
         recfile.record(duration=5.0)
Non-blocking mode (start and stop recording):
>>> rec = Recorder(channels=2)
>>> with rec.open('nonblocking.wav','wb') as recfile2:
         recfile2.start_recording()
         time.sleep(5.0)
         recfile2.stop_recording()
"""         
      
      
      
#### own usage ####

def beep(frequency=440, duration=5, amplitude=0.5):
    
    generator = ToneGenerator()
    generator.play(frequency,duration,amplitude)
    
def rec(fname):
    data = Recorder(input_device_index=2)
    with data.open(fname,'wb') as recfile:
         recfile.start_recording()
         time.sleep(duration)
         recfile.stop_recording()
        

    

if __name__ == '__main__':
   FILENAME = datetime.now().strftime("%b_%d_%H;%M;%S_beep_test.wav")
   
   p1 = mp.Process(target=beep, args=(440,10,0.5))
   p2 = mp.Process(target=rec, args=(FILENAME,))
   
   p1.start()
   p2.start()
   
   p1.join()
   p2.join()

