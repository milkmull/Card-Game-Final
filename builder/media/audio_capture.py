import os
import wave
import threading

import pyaudio

def get_sound_length(file):
    length = 0
    with wave.open(file) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        length = frames / float(rate)
    return length

class Audio_Capture:
    FORMAT = pyaudio.paInt16
    WIDTH = pyaudio.get_sample_size(FORMAT)
    CHANNELS = 1
    SAMPLE_RATE = 44100
    FRAMES_PER_BUFFER = 1024

    OUT = "data/snd/temp/custom.wav"
    
    @staticmethod
    def get_path():
        return Audio_Capture.OUT
        
    @staticmethod
    def clear_path():
        if os.path.exists(Audio_Capture.OUT):
            os.remove(Audio_Capture.OUT)
    
    @staticmethod
    def get_devices(p):
        devices = []
        
        try:
            info = p.get_host_api_info_by_index(0)
        except IOError:
            return devices
            
        numdevices = info.get("deviceCount")
        for i in range(numdevices):
        
            try:
                device = p.get_device_info_by_host_api_device_index(0, i)
            except IOError:
                return devices
                
            name = device.get("name")
            max_channels = device.get("maxInputChannels")
            if max_channels > 0:
                devices.append((name, i))

        return devices
    
    def __init__(self, seconds):
        self.p = pyaudio.PyAudio()
        self.device_index = 0
        self.devices = Audio_Capture.get_devices(self.p)

        self.length = seconds
        self.frames = []
        self.stream = None
        self.thread = None
        self.saved_file = False
        self.stop_record = False
        self.finished = False
        
    @property
    def device(self):
        if self.devices:
            return self.devices[self.device_index]
        
    @property
    def recording(self):
        recording = False
        if self.stream:
            try:
                recording = self.stream.is_active()
            except OSError:
                pass
        return recording
        
    def __del__(self):
        self.close()
        
    def refresh(self):
        self.close()
        last_name = self.device[0]
        self.__init__(self.length)
        for i, (name, index) in enumerate(self.devices):
            if name == last_name:
                self.device_index = i
                break
            
    def set_recording_length(self, seconds):
        self.length = seconds
        
    def get_current_length(self):
        return round(len(self.frames) * (Audio_Capture.FRAMES_PER_BUFFER / Audio_Capture.SAMPLE_RATE), 2)
        
    def reset(self):
        self.frames.clear()
        self.saved_file = False
        self.stop_record = False
        self.finished = False
        
    def start(self):
        if not self.recording:
            self.reset()
            t = threading.Thread(target=self.record)
            t.start() 
            self.thread = t
        
    def stop(self):
        self.stop_record = True
        if self.thread:
            if self.thread.is_alive():
                self.thread.join()
            self.thread = None
            
    def close(self):
        self.stop()
        self.end_stream()
        self.p.terminate()
        self.clear_path()
        
    def start_stream(self):
        self.stream = self.p.open(
            format=Audio_Capture.FORMAT,
            channels=Audio_Capture.CHANNELS,
            rate=Audio_Capture.SAMPLE_RATE, 
            frames_per_buffer=Audio_Capture.FRAMES_PER_BUFFER,
            input=True,
            input_device_index=self.device[1]
        )
        self.stream.start_stream()
        
    def end_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
    def record(self):
        if not self.devices:
            return
            
        self.start_stream()

        t = int((Audio_Capture.SAMPLE_RATE / Audio_Capture.FRAMES_PER_BUFFER) * self.length)
        
        for _ in range(t):
            try:
                data = self.stream.read(Audio_Capture.FRAMES_PER_BUFFER)
                self.frames.append(data)
            except IOError:
                self.stop_record = True
            if self.stop_record:
                break     
                
        self.end_stream()
        self.write_wav()
        self.finished = True
        
    def write_wav(self):
        data = b"".join(self.frames)
        try:
            with wave.open(Audio_Capture.OUT, "wb") as sound_file:
                sound_file.setnchannels(Audio_Capture.CHANNELS)
                sound_file.setsampwidth(Audio_Capture.WIDTH)
                sound_file.setframerate(Audio_Capture.SAMPLE_RATE)
                sound_file.writeframes(data)
            self.saved_file = True
        except wave.Error:
            pass
  