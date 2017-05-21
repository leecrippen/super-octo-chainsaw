#!/usr/bin/env python3

import sys
import pyscope
import pygame
import PIL
import glob
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
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            do_exit()
        if event.type == pygame.QUIT:
            do_exit()

def rotate_and_save(infilepath, outfilepath, dispwidth, dispheight):
    print("begin rot_and_save file: {}".format(infilepath))
    t = time.process_time()
    image=Image.open(infilepath)
    tn = time.process_time()
    print("Image.open time: {}".format(tn-t))
    t = tn
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
    tn = time.process_time()
    print("image.rotate time: {}".format(tn-t))
    t = tn
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
    tn = time.process_time()
    print("image.resize time: {}".format(tn-t))
    t = tn
    image.save(outfilepath,"BMP")
    tn = time.process_time()
    print("image.save time: {}".format(tn-t))
    t = tn
    image.close()
    print("end rot_and_save file: {}".format(infilepath))
    return is_width_constrained

def doloop(filepathlist, draw_scope):
    is_second_img = False
    ready_img = None

    for filepath in filepathlist:
        check_input()
        dest_file = "/var/tmp/tmp1.BMP" if is_second_img else "/var/tmp/tmp0.BMP"
        is_second_img = not is_second_img
        try:
            is_width_constrained = rotate_and_save(filepath, dest_file, draw_scope.size[0], draw_scope.size[1])
        except (IOError, OSError) as err:
            print("OSError: {}".format(err))
            continue
        check_input()
        t = time.process_time()
        ready_img = pygame.image.load(dest_file).convert()
        tn = time.process_time()
        print("pygame img load and convert time: {}".format(tn-t))
        t = tn
        check_input()
        drawX = 0
        drawY = 0
        if is_width_constrained:
            drawY = (draw_scope.size[1] - ready_img.get_height()) // 2
        else:
            drawX = (draw_scope.size[0] - ready_img.get_width()) // 2
        draw_scope.screen.fill((0,0,0))
        draw_scope.screen.blit(ready_img,(drawX,drawY))
        tn = time.process_time()
        print("screen blit time: {}".format(tn-t))
        t = tn
        check_input()
        pygame.display.flip()
        check_input()
        sleep(5)

def main(args):
    pygame.init()
    pygame.mouse.set_visible(False)

    draw_scope = pyscope.pyscope()

    dirbase = '/media/usb0/pictures/*'
    filetypes = ('*.jpg','*.JPG','*.jpeg','*.JPEG','*.gif','*.GIF','*.png','*.PNG')
    filesgrabbed = []
    for filetype in filetypes:
        filesgrabbed.extend(glob.glob(dirbase + filetype))

    print("Numfiles: {}".format(len(filesgrabbed)))
    while len(filesgrabbed) > 0:
        random.shuffle(filesgrabbed)
        doloop(filesgrabbed, draw_scope)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])

