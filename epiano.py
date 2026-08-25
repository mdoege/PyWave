#!/usr/bin/env python3

# Polyphonic Python MIDI synthesizer

# python epiano.py [MIDI channel 0-15]

import pyaudio
import mido
import sys, struct, time
from math import pi, sin, log

# sleep time in main loop
SLEEP = 0.01

# audio buffer size (determines latency)
BSIZE = 256

# sample rate
ARATE = 44100

# maximum polyphony
MAXPOLY = 8

# volume
VOLUME = 1500

# active MIDI channel (0 to 15), or -1 to listen on all channels
CHAN = -1
# The MIDI channel can also be set via an integer commandline argument:
if len(sys.argv) > 1:
    CHAN = int(sys.argv[1])
if CHAN > -1:
    print("*** using MIDI channel", CHAN)

# use MIDI velocity for amplitude scaling?
USE_VEL = True

# sustain notes (i.e., ignore note_off events)?
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
        # check if note belongs to correct MIDI channel
        if CHAN > -1:
            if msg.channel != CHAN:
                continue

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
                a_min, a_max, a_sel = log(21), log(108), log(msg.note)
                lossfac = 50000 - 49000 * ((a_sel - a_min) / (a_max - a_min))
                lossfac *= ARATE / 44100
                amp_loss = 1 - 1 / lossfac

                # add optional MIDI velocity-based amplitude scaling
                if USE_VEL:
                    ini_amp = (msg.velocity / 127) ** (1 / 3)
                else:
                    ini_amp = 1

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
                        ini_amp,
                        amp_loss,
                        msg.note,
                        2.0 * pi / (ARATE / freq),
                        0,
                        0,
                        ini_amp,
                        ini_amp,
                        ini_amp,
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
