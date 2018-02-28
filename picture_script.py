#!/usr/bin/env python3

import sys
import pyscope
import pygame
import PIL
import os
import random
import signal
import time
from time import sleep
from PIL import Image, ExifTags

def do_exit():
    pygame.quit()
    sys.exit(0)

def signal_handler(signal, frame):
    do_exit()

def check_input():
    events = pygame.event.get()
    quit_events = (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_q)
    for event in events:
        if event.type == pygame.KEYDOWN and event.key in quit_events:
            do_exit()
        if event.type == pygame.QUIT:
            do_exit()

def rotate_and_save(infilepath, outfilepath, dispwidth, dispheight):
    image=Image.open(infilepath)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass
    imgwid = image.size[0]
    imghei = image.size[1]

    dispratio = dispwidth / dispheight
    imgratio = imgwid / imghei

    resizeratio = 1.0
    is_width_constrained = False
    if imgratio > dispratio:
        resizeratio = dispwidth / imgwid
        is_width_constrained = True
    else:
        resizeratio = dispheight / imghei

    newwid = int(imgwid * resizeratio)
    newhei = int(imghei * resizeratio)

    image = image.resize((newwid, newhei), Image.ANTIALIAS)
    image.save(outfilepath,"BMP")
    image.close()
    return is_width_constrained

def doloop(filepathlist, draw_scope):
    is_second_img = False
    ready_img = None

    for filepath in filepathlist:
        time_begin = time.process_time()
        check_input()
        dest_file = "/var/tmp/tmp1.BMP" if is_second_img else "/var/tmp/tmp0.BMP"
        is_second_img = not is_second_img
        try:
            is_width_constrained = rotate_and_save(filepath, dest_file, draw_scope.size[0], draw_scope.size[1])
        except (IOError, OSError) as err:
            print("OSError: {}".format(err))
            continue
        check_input()
        ready_img = pygame.image.load(dest_file).convert()
        check_input()
        drawX = 0
        drawY = 0
        if is_width_constrained:
            drawY = (draw_scope.size[1] - ready_img.get_height()) // 2
        else:
            drawX = (draw_scope.size[0] - ready_img.get_width()) // 2
        draw_scope.screen.fill((0,0,0))
        draw_scope.screen.blit(ready_img,(drawX,drawY))
        check_input()
        pygame.display.flip()
        check_input()
        time_end = time.process_time()
        min_img_time = 50.0
        elapsed_img_time = time_end - time_begin
        while elapsed_img_time < min_img_time:
            check_input()
            sleep(0.5)
            time_end = time.process_time()
            elapsed_img_time = time_end - time_begin

def main(args):
    pygame.init()
    pygame.mouse.set_visible(False)

    draw_scope = pyscope.pyscope()

    dirbase = '/media/usb0/pictures'
    if len(args) > 0:
        dirbase = args[0]
    filetypes = ('.jpg','.JPG','.jpeg','.JPEG','.gif','.GIF','.png','.PNG','.bmp','.BMP')
    filesgrabbed = []
    for root, dirs, files in os.walk(dirbase):
        for file in files:
            if file.endswith(filetypes):
                filesgrabbed.append(os.path.join(root, file))

    print("Numfiles: {}".format(len(filesgrabbed)))
    while len(filesgrabbed) > 0:
        random.shuffle(filesgrabbed)
        doloop(filesgrabbed, draw_scope)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])

