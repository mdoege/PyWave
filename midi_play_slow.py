#!/usr/bin/env python3

# Play back a MIDI file using mido, with optional transposition and slowdown factor

import mido
import sys, time

# transposition (halftones)
TRANSPOSE = 0

# slowdown factor
SLOW_FACTOR = 3

try:
    fn = sys.argv[1]
except:
    fn = "midi/wtk1-prelude1.mid"

out = mido.open_output()

allow = "note_on", "note_off"

for msg in mido.MidiFile(fn):
    time.sleep(SLOW_FACTOR * msg.time)
    if msg.type in allow:
        msg.note += TRANSPOSE
        out.send(msg)
