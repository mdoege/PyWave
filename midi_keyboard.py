#!/usr/bin/python

# On-screen MIDI keyboard using PyGame and mido

import os
# let focus mouse clicks through to application
os.environ["SDL_MOUSE_FOCUS_CLICKTHROUGH"] = "1"

import pygame
import mido

# window size
SIZE = 1800, 300

# MIDI note velocity
VELOCITY = 80

# frame rate
FPS = 100

inport = mido.open_input()
outport = mido.open_output()

# keyboard layout:

# 4 octaves centered on middle C = C4 (from C2 to C6)
MIN_NOTE, MAX_NOTE, WKEYS, LEFT_OCT = 36, 85, 29, 3
# 5 octaves (from C2 to C7)
# MIN_NOTE, MAX_NOTE, WKEYS, LEFT_OCT = 36, 97, 36, 3
# full 88-key piano keyboard
# MIN_NOTE, MAX_NOTE, WKEYS, LEFT_OCT = 21, 109, 52, 1 + 5/7

WHITE = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 150, 150, 140
BLUE = 0, 0, 255
RED = 255, 0, 0

kp = (
    (0, 0),
    (0.45, 1),
    (1, 0),
    (1.55, 1),
    (2, 0),
    (3, 0),
    (3.4, 1),
    (4, 0),
    (4.5, 1),
    (5, 0),
    (5.6, 1),
    (6, 0),
)

kw = SIZE[0] // WKEYS
ww = kw - 4
wb = int(0.6 * kw) - 4
YP = SIZE[1] // 7

class ShowKeys:
    def __init__(s):
        pygame.init()
        s.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("MIDI keyboard")
        s.screen.fill(WHITE)
        s.clock = pygame.time.Clock()
        # lights for internal MIDI notes
        s.on = 200 * [0]
        # lights for external MIDI notes
        s.ext = 200 * [0]
        s.mouse = False
        s.back = pygame.Surface(SIZE)
        s.background()

    def events(s):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                s.mouse = True
            if event.type == pygame.MOUSEBUTTONUP:
                s.mouse = False
            if event.type == pygame.QUIT:
                s.running = False

    def run(s):
        s.running = True
        while s.running:
            s.clock.tick(FPS)
            s.events()
            s.update()
        pygame.quit()

    def test_key(s, mx, my, rect):
        x, y, xd, yd = rect
        if not s.mouse:
            return False
        if (x <= mx <= x + xd) and (y <= my <= y + yd):
            return True
        else:
            return False

    def background(s):
        s.back.fill(BLACK)

        # draw white keys
        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            if p[1] == 0:
                pygame.draw.rect(s.back, GRAY, [x - ww // 2, 0, ww, SIZE[1]])

        # draw black keys
        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            if p[1]:
                pygame.draw.rect(s.back, BLACK, [x - wb // 2, 0, wb, 0.63 * SIZE[1]])

    def update(s):
        # process MIDI events from other sources
        for msg in inport.iter_pending():
            # ignore percussion channel
            if msg.type == "note_on" and msg.channel != 9:
                s.ext[msg.note] = 1
            if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                s.ext[msg.note] = 0

        s.screen.blit(s.back, (0, 0))

        # draw white keys
        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            if p[1] == 0:
                if s.on[i] or s.ext[i]:
                    pygame.draw.rect(
                        s.screen, RED, [x - ww // 2, SIZE[1] - YP, ww, YP]
                    )

        # draw black keys
        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            if p[1]:
                if s.on[i] or s.ext[i]:
                    pygame.draw.rect(
                        s.screen, RED, [x - wb // 2, 0.63 * SIZE[1] - YP, wb, YP]
                    )

        mx, my = pygame.mouse.get_pos()

        # test black keys
        on_black = False
        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            if p[1]:
                if s.test_key(mx, my, [x - wb // 2, 0, wb, 0.63 * SIZE[1]]):
                    if s.on[i] == 0:
                        msg = mido.Message("note_on", note=i, velocity=VELOCITY)
                        outport.send(msg)
                    s.on[i] = 1
                    on_black = True
                else:
                    if s.on[i] == 1:
                        msg = mido.Message("note_off", note=i)
                        outport.send(msg)
                    s.on[i] = 0

        # test white keys
        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            if p[1] == 0:
                if s.test_key(mx, my, [x - ww // 2, 0, ww, SIZE[1]]) and not on_black:
                    if s.on[i] == 0:
                        msg = mido.Message("note_on", note=i, velocity=VELOCITY)
                        outport.send(msg)
                    s.on[i] = 1
                else:
                    if s.on[i] == 1:
                        msg = mido.Message("note_off", note=i)
                        outport.send(msg)
                    s.on[i] = 0

        pygame.display.flip()


c = ShowKeys()
c.run()
