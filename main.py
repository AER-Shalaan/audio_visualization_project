import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import struct
from scipy import signal
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

class RealTimeAudioVisualizer:
    def __init__(self, chunk=1024, rate=44100, buffer_seconds=2):
        self.chunk = chunk
        self.rate = rate
        self.format = pyaudio.paInt16
        self.channels = 1
        self.sensitivity = 1.0
        self.buffer_size = int(self.rate * buffer_seconds)
        self.buffer = np.zeros(self.buffer_size, dtype=np.int16)
        self.p = pyaudio.PyAudio()
        self.stream = None

        # UI Setup: One window with two subplots
        self.fig, (self.ax_waveform, self.ax_spec) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.subplots_adjust(hspace=0.5, bottom=0.25)

        # Waveform Plot
        self.xdata = np.arange(self.buffer_size)
        self.ydata = np.zeros(self.buffer_size)
        (self.line_wave,) = self.ax_waveform.plot(self.xdata, self.ydata, color='darkgreen', lw=1, animated=True)
        self.ax_waveform.set_ylim(-32768, 32767)
        self.ax_waveform.set_xlim(0, self.buffer_size)
        self.ax_waveform.set_title("Real-Time Smooth Audio Waveform", fontsize=14, fontweight='bold')
        self.ax_waveform.set_xlabel("Samples")
        self.ax_waveform.set_ylabel("Amplitude")
        self.ax_waveform.grid(True)

        # Spectrogram Plot
        self.spec_data = np.zeros((self.chunk//2, 1))
        self.spec_img = self.ax_spec.imshow(self.spec_data, aspect='auto', origin='lower', cmap='plasma', extent=[0,1,0,self.rate/2])
        self.ax_spec.set_title("Real-Time Spectrogram", fontsize=14, fontweight='bold')
        self.ax_spec.set_xlabel("Time")
        self.ax_spec.set_ylabel("Frequency (Hz)")

        # Sensitivity Slider
        ax_slider = self.fig.add_axes([0.2, 0.05, 0.6, 0.03])
        self.slider = Slider(ax_slider, 'Sensitivity', 0.1, 5.0, valinit=1.0)
        self.slider.on_changed(self.update_sensitivity)

        self.background = None

    def start_stream(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

    def read_chunk(self):
        raw = self.stream.read(self.chunk, exception_on_overflow=False)
        return np.array(struct.unpack(str(self.chunk) + 'h', raw))

    def smooth(self, data, window_len=11):
        if len(data) < window_len:
            return data
        window = np.ones(window_len)/window_len
        return np.convolve(data, window, mode='same')

    def update_sensitivity(self, val):
        self.sensitivity = val

    def update(self, frame):
        data_np = self.read_chunk()

        # Update buffer
        self.buffer = np.roll(self.buffer, -self.chunk)
        self.buffer[-self.chunk:] = data_np

        # Apply smoothing to waveform
        smooth_data = self.smooth(self.buffer * self.sensitivity, window_len=31)

        # Update waveform
        self.ydata = smooth_data
        self.line_wave.set_ydata(self.ydata)

        # Restore background and redraw line for fast blitting
        self.fig.canvas.restore_region(self.background)
        self.ax_waveform.draw_artist(self.line_wave)
        self.fig.canvas.blit(self.ax_waveform.bbox)
        self.fig.canvas.flush_events()

        # Update spectrogram
        self.ax_spec.clear()
        f, t, Sxx = signal.spectrogram(self.buffer * self.sensitivity, self.rate, nperseg=512, noverlap=256)
        self.ax_spec.imshow(10 * np.log10(Sxx + 1e-10), aspect='auto', origin='lower', extent=[t.min(), t.max(), f.min(), f.max()], cmap='plasma')
        self.ax_spec.set_title("Real-Time Spectrogram", fontsize=14, fontweight='bold')
        self.ax_spec.set_xlabel("Time")
        self.ax_spec.set_ylabel("Frequency (Hz)")

        return self.line_wave,

    def init_anim(self):
        self.background = self.fig.canvas.copy_from_bbox(self.ax_waveform.bbox)
        return self.line_wave,

    def run(self):
        print('🎤 Starting real-time smooth analog-like audio visualization with sensitivity control...')
        self.start_stream()
        ani = FuncAnimation(self.fig, self.update, init_func=self.init_anim, interval=30, blit=False)
        plt.show()

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

if __name__ == '__main__':
    visualizer = RealTimeAudioVisualizer()
    visualizer.run()
