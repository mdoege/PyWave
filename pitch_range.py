#!/usr/bin/env python

# Show pitch range of a MIDI file (highest/lowest notes)

import mido
import sys

fn = sys.argv[1]
low, high = 255, -1

for msg in mido.MidiFile(fn):
    if msg.type == "note_on":
        low = min(low, msg.note)
        high = max(high, msg.note)

print(fn)
print(low, "to", high)

p = "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"


def name(x):
    return "%s%u" % (p[x % 12], x // 12 - 1)


print(name(low), "to", name(high))
print("%.2f octaves" % ((high - low) / 12))
