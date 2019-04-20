import os
import sys
import json
from timeit import default_timer as timer
from tkinter import *
from statistics import mean

root = Tk()
cw = root.winfo_screenwidth()
ch = root.winfo_screenheight()
c = Canvas(root, width=cw, height=ch)
c.pack()

scaling = 10

rects = []


def draw(magnitudes, fps):
    c.delete(ALL)

    w = cw / len(magnitudes)
    gap = w / 8
    if len(rects) == 0:
        for i in range(len(magnitudes)):
            h = scaling * magnitudes[i]
            x1 = i * w + gap
            y1 = ch
            x2 = x1 + w - gap
            y2 = y1 - h
            rects.append(c.create_rectangle(x1, y1, x2, y2, fill='blue'))
    else:
        for i in range(len(magnitudes)):
            h = scaling * magnitudes[i]
            x1 = i * w + gap
            y1 = ch
            x2 = x1 + w - gap
            y2 = y1 - h
            c.coords(rects[i], x1, y1, x2, y2)
    if fps:
        c.create_text(cw, 0, anchor=NE, text=str(round(fps)),
                      font=('Times', '24'))
    root.update()


nSamples = 5
samples = []
fps = None

for data in sys.stdin:
    t_0 = timer()
    magnitudes = json.loads(data)
    draw(magnitudes, fps)
    t_1 = timer()
    dt = t_1 - t_0
    samples.append(1 / dt)
    if len(samples) == nSamples:
        fps = mean(samples)
        print(fps)
        samples.pop(0)

# while True:
#     print('reading')
#     data = sys.stdin.readline()
#     if not data:
#         print('break')
#         break
#     print(data)
#     print('load')
#     magnitudes = json.loads(data)
#     print(magnitudes)
#     print('draw')
#     draw(magnitudes)

# print('done')


# def engine():
#     data = sys.stdin.readline()
#     if not data:
#         print('break')
#         break
#     t_0 = timer()
#     magnitudes = json.loads(data)
#     draw(magnitudes, fps)
#     t_1 = timer()
#     dt = t_1 - t_0
#     samples.append(1 / dt)
#     if len(samples) == nSamples:
#         fps = mean(samples)
#         print(fps)
#         samples.pop(0)
#     root.after(16, engine)


# engine()
# mainloop()
