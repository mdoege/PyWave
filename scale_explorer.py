#!/usr/bin/python

# Explore scales interactively

# left and right to move tonic
# up and down to select scale

import pygame

# keyboard layout:

# 4 octaves centered on middle C
MIN_NOTE, MAX_NOTE, WKEYS, LEFT_OCT = 36, 85, 29, 3
# 5 octaves
# MIN_NOTE, MAX_NOTE, WKEYS, LEFT_OCT = 36, 97, 36, 3
# full 88-key piano keyboard
# MIN_NOTE, MAX_NOTE, WKEYS, LEFT_OCT = 21, 109, 52, 1 + 5/7

WHITE = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 180, 180, 180
BLUE = 0, 0, 255
RED = 255, 0, 0
RED2 = 180, 0, 0

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

# https://en.wikipedia.org/wiki/Tetrachord#Romantic_era

tet_maj = "221"
tet_min = "212"
tet_har = "131"
tet_umi = "122"

scales = (
    (tet_maj + "2" + tet_maj, "Diatonic major"),
    (tet_min + "2" + tet_umi, "Natural minor"),
    (tet_maj + "2" + tet_har, "Harmonic major"),
    (tet_min + "2" + tet_har, "Harmonic minor"),
    (tet_har + "2" + tet_har, "Gypsy major"),
    (tet_maj + "2" + tet_umi, "Melodic major"),
    (tet_min + "2" + tet_maj, "Melodic minor"),
    (tet_umi + "2" + tet_har, "Neapolitan minor"),
)


def mk_scale(t, num):
    o = [t]
    for x in scales[num][0]:
        t += int(x)
        o.append(t)
    return o


class ShowKeys:
    def __init__(s):
        pygame.init()
        s.res = 1800, 300  # default window size
        s.screen = pygame.display.set_mode(s.res, pygame.RESIZABLE)
        pygame.display.set_caption("Scale Explorer (Diatonic major)")
        s.screen.fill(WHITE)
        s.clock = pygame.time.Clock()
        s.tonic = 60
        s.num = 0
        s.scale = mk_scale(s.tonic, s.num)

    def events(s):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.running = False
            if event.type == pygame.VIDEORESIZE:
                s.res = event.w, event.h
                # print(s.res)
                s.screen = pygame.display.set_mode(s.res, pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                s.tonic += 1
                s.scale = mk_scale(s.tonic, s.num)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                s.tonic -= 1
                s.scale = mk_scale(s.tonic, s.num)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                s.num = min(s.num + 1, len(scales) - 1)
                s.scale = mk_scale(s.tonic, s.num)
                pygame.display.set_caption(f"Scale Explorer ({scales[s.num][1]})")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                s.num = max(0, s.num - 1)
                s.scale = mk_scale(s.tonic, s.num)
                pygame.display.set_caption(f"Scale Explorer ({scales[s.num][1]})")

    def run(s):
        s.running = True
        while s.running:
            s.clock.tick(15)
            s.events()
            s.update()
        pygame.quit()

    def update(s):
        s.screen.fill(BLUE)

        kw = s.res[0] // WKEYS
        ww = kw - 4
        wb = int(0.6 * kw) - 4

        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            col = WHITE
            if i in s.scale:
                col = RED
            if p[1] == 0:
                pygame.draw.rect(s.screen, col, [x - ww // 2, 0, ww, s.res[1]])

        for i in range(MIN_NOTE, MAX_NOTE):
            p = kp[i % 12]
            oc = i // 12 - LEFT_OCT
            x = kw * (p[0] + 7 * oc + 0.5)
            col = BLACK
            if i in s.scale:
                col = RED2
            if p[1]:
                pygame.draw.rect(s.screen, col, [x - wb // 2, 0, wb, 0.63 * s.res[1]])

        pygame.display.flip()


c = ShowKeys()
c.run()
