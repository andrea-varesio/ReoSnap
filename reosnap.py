#!/bin/python3
#https://github.com/andrea-varesio/ReoSnap
#version = 20220513.01

'''Save live snapshots of Reolink cameras'''

import argparse
import asyncio
import datetime
import os
import pathlib
import sys
import time

import requests

from PIL import Image

cwd = os.path.dirname(os.path.realpath(__file__))

def show_license():
    '''Show License'''

    print('\n**************************************************')
    print('"ReoSnap": Save live snapshots of Reolink camera feeds')
    print('Copyright (C) 2022 Andrea Varesio (https://www.andreavaresio.com/).')
    print('This program comes with ABSOLUTELY NO WARRANTY')
    print('This is free software, and you are welcome to redistribute it under certain conditions')
    print('Full license available at https://github.com/andrea-varesio/ReoSnap')
    print('**************************************************\n\n')

def parse_arguments():
    '''Parse arguments'''

    arg_parser = argparse.ArgumentParser(description = 'Description')
    res_group = arg_parser.add_mutually_exclusive_group()
    time_group = arg_parser.add_mutually_exclusive_group()

    res_group.add_argument('-r', '--resolution', help='[low/medium/high/max]', type=str)
    res_group.add_argument('--width', help='Width', type=int)
    res_group.add_argument('--height', help='Height', type=int)
    arg_parser.add_argument('-o', '--optimize', help='Optimize image', action='store_true')
    arg_parser.add_argument('-q', '--quality', help='[low/medium/high/max/0-100]', type=str)
    arg_parser.add_argument('-k', '--keep-og', help='Keep original files', action='store_true')
    time_group.add_argument('-H', '--hours', help='Hours', type=int)
    time_group.add_argument('-m', '--minutes', help='Minutes', type=int)
    time_group.add_argument('-s', '--seconds', help='Seconds', type=int)
    arg_parser.add_argument('-i', '--interval', help='Snapshot interval (default=4s)', type=int)
    arg_parser.add_argument('-O', '--output', help='Path to output directory', type=str)
    arg_parser.add_argument('-v', '--verbose', help='Enable verbosity', action='store_true')
    arg_parser.add_argument('-l', '--license', help='Show License', action='store_true')

    return arg_parser.parse_args()

def get_date():
    '''Get current date'''

    now = datetime.datetime.now()

    return now.strftime('%Y%m%d')

def get_timestamp():
    '''Get current timestamp'''

    now = datetime.datetime.now()

    return now.strftime('%Y%m%d_%H%M%S')

def get_file_res():
    '''Get snapshot resolution'''

    args = parse_arguments()
    res_levels = ['low', 'medium', 'high', 'max']

    if args.resolution and args.resolution not in res_levels:
        print('Invalid resolution')
        sys.exit(1)

    if args.resolution in [res_levels[3], 'M']:
        resolution = [2560, 1920]
    elif args.resolution in [res_levels[2], 'h']:
        resolution = [2048, 1536]
    elif args.resolution in [res_levels[1], 'm']:
        resolution = [1856, 1392]
    elif args.resolution in [res_levels[0], 'l']:
        resolution = [1600, 1200]
    elif args.width:
        resolution = [args.width,  args.width * 3 / 4]
    elif args.height:
        resolution = [args.height * 4 / 3, args.height]
    else:
        resolution = [1856, 1392]

    return resolution

def get_url(cam_ip, username, password):
    '''Get API url'''

    url_base = 'cgi-bin/api.cgi?cmd=Snap&channel=0'
    res_param = f'width={get_file_res()[0]}&height={get_file_res()[1]}'
    now = get_timestamp()

    return f'http://{cam_ip}/{url_base}&{res_param}&rs={now}&user={username}&password={password}'

def get_output_dir():
    '''Get output directory'''

    args = parse_arguments()

    if not args.output:
        return os.path.join(pathlib.Path.home(), 'Surveillance')

    if os.path.isdir(args.output):
        if args.output.startswith('./'):
            output_dir_root = os.path.join(os.getcwd(), args.output.replace('./', '', 1))
        elif args.output == '.':
            output_dir_root = args.output.replace('.', os.getcwd())
        else:
            output_dir_root = args.output
        return os.path.join(output_dir_root, 'Surveillance')

    print('Invalid output path')
    sys.exit(1)

def get_filepath(cam_name):
    '''Get camera variables'''

    cam_dir = os.path.join(get_output_dir(), get_date(), cam_name)
    filename = f'{get_timestamp()}_{cam_name}_snapshot.jpg'

    if not os.path.isdir(cam_dir):
        os.makedirs(cam_dir)

    return os.path.join(cam_dir, filename)

def get_file_quality():
    '''Get file quality'''

    args = parse_arguments()
    quality_levels = ['low', 'medium', 'high', 'max']

    if args.quality in [quality_levels[3], 'M']:
        return 100

    if args.quality in [quality_levels[2], 'h']:
        return 75

    if args.quality in [quality_levels[1], 'm']:
        return 50

    if args.quality in [quality_levels[0], 'l']:
        return 25

    if args.quality:
        return int(args.quality)

    return 40

async def save_snapshot(cam_no, cam_ip, username, password):
    '''Save optimized snapshot of camera feed'''

    args = parse_arguments()
    cam_name = f'cam_{cam_no}'
    file_path = get_filepath(cam_name)
    url = get_url(cam_ip, username, password)

    with open(file_path, 'wb') as snapshot_raw:
        snapshot_raw.write(requests.get(url).content)

    if args.optimize:
        with Image.open(file_path) as snapshot:
            snapshot.save(  file_path.replace('.jpg', '_optimized.jpg'),
                            optimize=True, quality=get_file_quality())
        if not args.keep_og:
            os.remove(file_path)

def get_cam_feed():
    '''Get camera feed'''

    cam_no = 0

    with open(os.path.join(cwd, 'credentials.txt'), 'r', encoding='utf-8') as creds:
        for line in creds.readlines():
            if not line.startswith('#'):
                cam_no += 1
                cam_ip = line.split(',')[0]
                username = line.split(',')[1]
                password = line.split(',')[2].rstrip()
                asyncio.run(save_snapshot(cam_no, cam_ip, username, password))

def get_interval():
    '''Get snapshots interval'''

    args = parse_arguments()

    if args.interval:
        return args.interval

    return 4

def get_rec_period():
    '''Get number of files to keep'''

    args = parse_arguments()

    if args.hours:
        return args.hours * 3600 / get_interval()

    if args.minutes:
        return args.minutes * 60 / get_interval()

    if args.seconds:
        return args.seconds / get_interval()

    return 12 * 3600 / get_interval()

def main():
    '''Main function'''

    args = parse_arguments()

    interval = get_interval()
    rec_period = get_rec_period()
    output_dir = get_output_dir()

    if args.license:
        show_license()
        sys.exit(0)

    i = 0

    while True:
        get_cam_feed()

        i += 1

        if args.verbose:
            print(f'Saved snapshot(s): {get_timestamp()} | #{i}')

        date_dir = os.path.join(output_dir, min(os.listdir(output_dir)))

        for cam_dir in os.listdir(date_dir):
            oldest_dir = os.listdir(os.path.join(date_dir, cam_dir))
            if not oldest_dir:
                try:
                    os.rmdir(os.path.join(date_dir, cam_dir))
                except FileNotFoundError:
                    print('FileNotFoundError')

        if not os.listdir(date_dir):
            try:
                os.rmdir(date_dir)
            except FileNotFoundError:
                print('FileNotFoundError')
            date_dir = os.path.join(output_dir, min(os.listdir(output_dir)))

        if i > rec_period:
            for cam_dir in os.listdir(date_dir):
                oldest_dir = os.listdir(os.path.join(date_dir, cam_dir))
                oldest_file = min(oldest_dir)
                try:
                    os.remove(os.path.join(date_dir, cam_dir, oldest_file))
                except FileNotFoundError:
                    print(f'FileNotFoundError: {os.path.join(date_dir, cam_dir, oldest_file)}')

        time.sleep(interval)

if __name__ == '__main__':
    main()
