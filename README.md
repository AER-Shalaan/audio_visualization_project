**Real-Time Audio Visualizer - Full Detailed Explanation**

---

# 1. Introduction
This project is a real-time audio visualizer built using Python. It captures audio input from the microphone, processes it, and displays:
- A **smoothed waveform** (like an oscilloscope analog wave)
- A **real-time spectrogram** showing the frequency content.

It also features a **slider** that allows live control of sensitivity (amplification factor).

---

# 2. Key Libraries Used
- **pyaudio**: For capturing audio from microphone.
- **numpy**: For numerical operations.
- **scipy.signal**: For creating the spectrogram.
- **matplotlib**: For plotting waveform and spectrogram.
- **matplotlib.widgets**: For the interactive slider.

---

# 3. Audio Capturing
We use **PyAudio** to open a continuous audio stream:
```python
self.stream = self.p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
```
- **format**: 16-bit signed integer (paInt16)
- **channels**: Mono input (1 channel)
- **rate**: 44100 Hz sampling rate
- **chunk**: 1024 samples per read (about 23 ms of audio)

Every 23ms, we read 1024 samples from the microphone.

---

# 4. Buffer Management
Instead of just drawing 1024 samples, we maintain a **rolling buffer** of about **2 seconds** of audio:
```python
self.buffer_size = int(self.rate * buffer_seconds)
self.buffer = np.zeros(self.buffer_size, dtype=np.int16)
```
- When new samples come:
  - We **shift** the old buffer to the left (rolling window)
  - Insert the new samples at the end.

This simulates "time history" like an oscilloscope.

---

# 5. Smoothing Filter
Before plotting the waveform, we smooth the signal to make it look analog (no sharp jumps):
```python
def smooth(self, data, window_len=11):
    window = np.ones(window_len) / window_len
    return np.convolve(data, window, mode='same')
```

This is a **Moving Average Filter**.
- Equation:
  \[ \text{output}[n] = \frac{1}{N} \sum_{i=0}^{N-1} \text{input}[n-i] \]
- Where **N = window_len**.

It removes high-frequency noise and makes the curve smooth.

---

# 6. Waveform Plot
The smoothed buffer is plotted as:
```python
self.line_wave.set_ydata(self.ydata)
```
The `ydata` array is scaled by sensitivity (`self.sensitivity`) from the slider.

- **X-axis**: Sample index
- **Y-axis**: Amplitude after smoothing

The line is thin and green for a classic oscilloscope look.

---

# 7. Spectrogram Plot
The spectrogram is created using Short-Time Fourier Transform (STFT):
```python
f, t, Sxx = signal.spectrogram(self.buffer * self.sensitivity, self.rate, nperseg=512, noverlap=256)
```

- **nperseg = 512 samples** (about 11 ms window)
- **noverlap = 256 samples** (50% overlap)
- **Sxx**: Power spectral density matrix

We plot:
- **X-axis**: Time
- **Y-axis**: Frequency
- **Color**: Power (in dB)

Spectrogram Equation:
- STFT of signal \( x[n] \):
  \[ X(m, \omega) = \sum_{n=-\infty}^{\infty} x[n] w[n-m] e^{-j \omega n} \]

Where \( w[n] \) is a window function (Hann window internally used by Scipy).

---

# 8. Sensitivity Slider
The slider is built using Matplotlib's widgets:
```python
self.slider = Slider(ax_slider, 'Sensitivity', 0.1, 5.0, valinit=1.0)
```
- Ranges from 0.1x to 5.0x amplification.
- Controls how "tall" the waveform looks without affecting the real audio.

When the slider moves, the waveform and spectrogram automatically update in real-time.

---

# 9. Real-Time Update Loop
Animation is handled by Matplotlib's **FuncAnimation**:
```python
ani = FuncAnimation(self.fig, self.update, init_func=self.init_anim, interval=30, blit=False)
```
- Every 30ms:
  - Read new audio chunk.
  - Update waveform.
  - Update spectrogram.

**No need to press any button manually**.

---

# 10. Conclusion
This project simulates an **oscilloscope-like real-time** experience with Python.
- Smooth audio waveform.
- Clear dynamic spectrogram.
- Full real-time sensitivity control.

It is ideal for audio analysis, speech visualization, and educational purposes.

---

(Prepared by ChatGPT based on user's request for full technical breakdown)