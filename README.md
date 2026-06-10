![PyWave](pywave.jpg "PyWave banner")

## Overview

This repository contains three Python MIDI synthesizers which can be played in real-time, e.g. from a USB MIDI keyboard, a MIDI file, or an on-screen MIDI keyboard such as [VMPK](https://vmpk.sourceforge.io/). They all require [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) (for audio output) and [mido](https://github.com/mido/mido) (for MIDI event handling):

* multi_synth.py: polyphonic additive synthesizer with 8-note polyphony by default
* multi_wave.py: polyphonic wavetable synthesizer with 12-note polyphony by default
* midi_synth.py: simple monophonic additive synthesizer

The helper script midi_play.py can be used to play back a MIDI file to these synthesizers.

Multi_synth.py and midi_synth.py produce a piano-like timbre using three sine waves like PySynth A and an exponential decay like PySynth B, so they sound very similar to PySynth A and B. Multi_wave.py on the other hand loads a wavetable with a guitar-like sound by default.

### Wavetables

The <tt>wavetables</tt> directory contains some other wavetables for multi_wave.py. There also some Python scripts in that directory that demonstrate how to create wavetables.

It is also possible to convert wavetables from other synthesizers. Often these are in 32-bit floating point format, so they need to be exported as 16-bit integer WAVs in Audacity. The number of samples per waveform needs to be set in multi_wave.py. Also, the volume should be set low enough so that multi_wave.py does not crash even when many notes are playing simultaneously.

### Audio problems

If you hear crackling audio from these scripts, you might want to

* quit other applications, especially web browsers.
* increase audio buffer size (<tt>BSIZE</tt>) in the scripts or reduce maximum polyphony (<tt>MAXPOLY</tt>).
* make sure you are running a recent Python version, because Python performance tends to improve with each release.

### Credits

* [2010_mavericks_competition.jpg](https://commons.wikimedia.org/wiki/File:2010_mavericks_competition_edit1.jpg): photo by Shalom Jacobovitz; derivative work: Brocken Inaglory, CC BY-SA 2.0 <https://creativecommons.org/licenses/by-sa/2.0>, via Wikimedia Commons

