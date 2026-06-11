#!/usr/bin/env python3

# Polyphonic Python MIDI synthesizer

import pyaudio
import mido
import struct, math, time
from math import pi, sin

# sleep time in main loop
SLEEP = 0.01

# audio buffer size (determines latency)
BSIZE = 256

# sample rate
ARATE = 44100

# maximum polyphony
MAXPOLY = 8

# volume
VOLUME = 1000

# sustain notes?
SUSTAIN = False

################################################################################

# list of currently active notes
notes = []

snd_len = 3 * ARATE


# callback function for audio data
def callback(in_data, frame_count, time_info, status):
    data = b""
    for i in range(frame_count):
        v = 0
        for n in notes:
            n[6] += n[5]
            n[7] += 14.0 * n[5]
            n[8] = max(0, n[8] - 1 / snd_len)
            n[9] = max(0, n[9] - 4 / snd_len)
            n[10] = max(0, n[10] - 0.25 / snd_len)
            v += n[2] * (
                n[8] * sin(n[6] + 0.58 * n[9] * sin(n[7]))
                + n[10] * sin(n[6] + 0.89 * n[10] * sin(n[6]))
                + n[10] * sin(n[6] + 0.79 * n[10] * sin(n[6]))
            )
            n[2] *= n[3]
        b = struct.pack("h", round(VOLUME * v))
        data += b
    return data, pyaudio.paContinue


# open mido and pyaudio inputs/outputs
inport = mido.open_input()
paud = pyaudio.PyAudio()
stream = paud.open(
    format=paud.get_format_from_width(2),
    channels=1,
    rate=ARATE,
    output=True,
    frames_per_buffer=BSIZE,
    stream_callback=callback,
)

# print("latency [s] = %.5f" % stream.get_output_latency())

while True:
    for msg in inport.iter_pending():
        # process new note
        if msg.type == "note_on":
            if msg.velocity == 0:
                # turn note off (if velocity = 0)
                if not SUSTAIN:
                    for n in notes:
                        if n[4] == msg.note:
                            n[3] = n[3] ** 6
            else:
                # get note frequency in Hz
                freq = 440 * 2 ** ((msg.note - 69) / 12)

                # get amplitude loss factor per sample
                #   (higher frequencies decay more quickly)
                a_min, a_max, a_sel = math.log(21), math.log(108), math.log(msg.note)
                lossfac = 50000 - 49000 * ((a_sel - a_min) / (a_max - a_min))
                lossfac *= ARATE / 44100
                amp_loss = 1 - 1 / lossfac

                # append new note to list of active notes
                #   note data:
                #   0  * unused
                #   1  * frequency in Hz
                #   2  * current amplitude
                #   3  * amplitude loss factor
                #   4  * MIDI key number
                #   5  * oscillator increment
                #   6  * main oscillator phase
                #   7  * overtone oscillator phase
                #   8/9/10  * FM amplitudes
                notes.append(
                    [
                        0,
                        freq,
                        1,
                        amp_loss,
                        msg.note,
                        2.0 * pi / (ARATE / freq),
                        0,
                        0,
                        1,
                        1,
                        1,
                    ]
                )

                # remove notes that have gone almost silent
                newnotes = []
                for n in notes:
                    if n[2] > 0.001:
                        newnotes.append(n)
                notes = newnotes

                # apply maximum polyphony cutoff with priority for latest notes
                if len(notes) > MAXPOLY:
                    notes = notes[-MAXPOLY:]

        # increase amplitude loss of note when note_off event happens
        if msg.type == "note_off" and not SUSTAIN:
            for n in notes:
                if n[4] == msg.note:
                    n[3] = n[3] ** 6

    try:
        time.sleep(SLEEP)
    except:  # exception handler hides ugly backtrace when pressing Ctrl-C
        break

stream.close()
paud.terminate()
inport.close()
