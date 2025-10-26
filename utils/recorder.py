import sounddevice as sd
import wave
import numpy as np
from config import SAMPLE_RATE, CHANNELS

class Recorder:
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.frames = []
        self.stream = None
        self.filename = "record.wav"
        self.wav_path = "output.wav"


    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def start(self, filename="record.wav"):
        self.filename = filename
        self.frames = []
        print("[Recorder] 麦克风已开启")
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype='int16',
            callback=self._callback
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            print("[Recorder] 麦克风已关闭")

        data = np.concatenate(self.frames, axis=0)
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(data.tobytes())
