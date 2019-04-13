import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer

Fs = 22050
windowLength = 1024

frequencies = np.arange(windowLength / 2) * Fs / windowLength

nBars = 30

windowRate = Fs / windowLength

overlap = 0
shift = windowLength - overlap

gamma = 2
_, splitInds = np.unique(
    np.round(((frequencies / np.max(frequencies))**(1 / gamma)) * (nBars - 1)), True)
splitInds = splitInds[1:]


def groupFrequencies(magnitudes):
    return np.split(magnitudes, splitInds)


def transform(channel):
    windowed = channel * np.hamming(channel.size)
    FFT = np.fft.rfft(windowed)
    mag = np.sqrt(FFT.real**2 + FFT.imag**2)
    scaled = np.log(mag)
    bins = groupFrequencies(scaled)
    meanMag = np.array(list(map(lambda bin: np.max(bin), bins)))
    return meanMag


smoothingConstant = 0.00007


def smooth(mag, prevSmoothedMag):
    adjustedSmoothingConstant = smoothingConstant**(1 / windowRate)
    smoothedMag = prevSmoothedMag * adjustedSmoothingConstant + \
        mag * (1 - adjustedSmoothingConstant)
    return smoothedMag


fig, ax = plt.subplots()
rects = ax.bar(np.arange(nBars * 2), np.zeros(nBars * 2))
ax.set_ylim([0, 20])


def display(spectrum):
    for rect, h in zip(rects, spectrum):
        rect.set_height(h)
    fig.canvas.draw()
    plt.pause(0.0001)


leftChannel = np.zeros(windowLength)
rightChannel = np.zeros(windowLength)
sampleNum = 0
prevSmoothedMag = np.zeros(nBars * 2)
firstWindow = True
prevTime = timer()
frames = 0

for data in sys.stdin:
    sample = data.split()
    if len(sample) == 2:
        [left, right] = sample
    else:
        left = right = 0

    leftChannel[sampleNum] = left
    rightChannel[sampleNum] = right

    if sampleNum == windowLength - 1:
        leftSpectrum = transform(leftChannel)
        rightSpectrum = transform(rightChannel)
        spectrum = np.concatenate(
            (leftSpectrum, np.flip(rightSpectrum)))
        if firstWindow:
            firstWindow = False
        else:
            spectrum = smooth(spectrum, prevSmoothedMag)
        prevSmoothedMag = spectrum

        display(spectrum)
        frames += 1

        t = timer()
        dt = t - prevTime
        if dt >= 1:
            fps = frames / dt
            prevTime = t
            frames = 0
            print(fps)

        leftChannel = np.roll(leftChannel, -shift)
        rightChannel = np.roll(rightChannel, -shift)
        sampleNum = windowLength - shift
    else:
        sampleNum += 1
