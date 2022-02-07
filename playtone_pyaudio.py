#!/usr/bin/python3
# -*- coding:utf-8 -*-

#refer for tone sample: https://www.mediacollege.com/audio/tone/files/440Hz_44100Hz_16bit_30sec.wav
"""
Purpose: play 440Hz tone on internal speaker and record using error mic

"""
import multiprocessing as mp
import numpy 
import pyaudio
import math
import time
import wave
from datetime import datetime
 
 
class Recorder(object):
      def __init__(self, channels=1,rate=44100,frames_per_buffer=4410,input_device_index=1):
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
      
      
      
#### own usage ############################################################

# NONBLOCKING MODE    
def beep():
    
     ##### minimum needed to read a wave #############################
     # open the file for reading.
    wf = wave.open('440Hz_44100Hz_16bit_30sec.wav', 'rb')
     
    def callback_speaker(in_data, frame_count, time_info, status):

         data = wf.readframes(frame_count)
         return data, pyaudio.paContinue
     
     #create an audio object
    p2 = pyaudio.PyAudio()
     
     # open stream based on the wave object which has been input. Output_device_index=1 with monitor, without monitor=0
    stream3 = p2.open(format=p2.get_format_from_width(wf.getsampwidth()),
                     channels = wf.getnchannels(),
                     rate = wf.getframerate(),
                     output=True,
                     output_device_index=0,
                     stream_callback=callback_speaker)
#     
#     
     # start stream
    
    stream3.start_stream()
    print("speaker playing")
     
     # control how long the stream to play
    time.sleep(10)
#         
#         # stop stream
#         
    stream3.stop_stream()
#         wf.rewind()
         
    print('speaker stopped')    
     # cleanup stuff
    stream3.close()
#     
     # close PyAudio
    p2.terminate()
     
    wf.close()
    
def ref(fname,duration=10):
    data = Recorder()
    with data.open(fname,'wb') as recfile:
         recfile.start_recording()
         time.sleep(duration)
         recfile.stop_recording()
  

if __name__ == '__main__':
   FILENAME = datetime.now().strftime("%b_%d_%H;%M;%S_beep_test.wav")
   p1 = mp.Process(target=ref, args=(FILENAME,10))
   p2 = mp.Process(target=beep)
   
   p1.start()
   p2.start()
   
   p1.join()
   p2.join()
   
   
   # NOTE:
   # sound file keep not recording. Could be due to how I define input_device_index in the whole code.
   # with headless, input_device_index = 1, output_device_index = 0
   
