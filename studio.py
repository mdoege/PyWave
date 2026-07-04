#!/usr/bin/env python

# Simple MIDI recording studio

import mido
import sys, time

try:
    NORMAL = int(sys.argv[1]) - 1  # patch for normal play
except:
    NORMAL = 0
CONTROL = NORMAL + 1  # patch for control codes

inp = mido.get_input_names()[-1]

print("*** using device %s for MIDI input" % inp)

port = mido.open_input(inp)
out = mido.open_output()

buf = []
cont = False

msg = mido.Message("program_change", program=NORMAL)
out.send(msg)


def play(b):
    now = -1
    time.sleep(1)
    msg = mido.Message("program_change", program=NORMAL)
    out.send(msg)
    for t, x in b:
        if now < 0:
            now = t
        ts = t - now
        if ts > 0:
            time.sleep(ts)
        out.send(x)
        now = t
    msg = mido.Message("program_change", program=CONTROL)
    out.send(msg)
    print("Playback done")


def save(b):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    last = -1
    track.append(mido.Message("program_change", program=NORMAL))
    for t, x in b:
        if last < 0:
            last = t
        y = mido.Message(x.type, note=x.note, velocity=x.velocity)
        tempo = mido.bpm2tempo(120)
        y.time = int(
            mido.second2tick(t, mid.ticks_per_beat, tempo)
            - mido.second2tick(last, mid.ticks_per_beat, tempo)
        )
        track.append(y)
        last = t
    fn = time.strftime("%y%m%d_%H%M%S.mid")
    mid.save(fn)
    print("File saved as", fn)


print("MIDI-STUDIO")
print("===========")
print("C = Info")
print("D = Playback")
print("E = Save File")
print("G# = Clear")

while True:
    for msg in port.iter_pending():
        if msg.type == "program_change" and msg.program == CONTROL:
            cont = True
            print("Entered control mode")
        if msg.type == "program_change" and msg.program == NORMAL:
            cont = False
            print("Left control mode")
        if not cont and (msg.type == "note_on" or msg.type == "note_off"):
            buf.append((time.time(), msg))
            print(len(buf), msg)
        if cont and msg.type == "note_on" and msg.note % 12 == 0:
            print(f"Info: {len(buf)} events in buffer")
            if len(buf):
                dt = buf[-1][0] - buf[0][0]
                print(f"Total buffer time: {int(dt // 60)} min, {int(dt % 60)} secs")
        if cont and msg.type == "note_on" and msg.note % 12 == 2:
            print(f"Playing back {len(buf)} events...")
            play(buf)
        if cont and msg.type == "note_on" and msg.note % 12 == 4:
            print(f"Saving {len(buf)} events...")
            save(buf)
        if cont and msg.type == "note_on" and msg.note % 12 == 8:
            print("Buffer cleared")
            buf = []
