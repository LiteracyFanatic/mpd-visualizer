import os
import sys
import numpy as np
from timeit import default_timer as timer
import asyncio
import websockets
import json

Fs = 44100
windowLength = 1024

frequencies = np.arange(windowLength / 2) * Fs / windowLength

nBars = 60

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


async def processAudio():
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

            yield json.dumps(spectrum.tolist())

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


async def sendFrame(websocket, path):
    async for frame in processAudio():
        t_0 = timer()
        await websocket.send(frame)
        t_1 = timer()
        dt = t_1 - t_0
        print(f'latency: {dt}')


asyncio.get_event_loop().run_until_complete(
    websockets.serve(sendFrame, 'localhost', 8765))
asyncio.get_event_loop().run_forever()
