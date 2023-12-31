import io
import math
import subprocess
from argparse import ArgumentParser
from hashlib import md5

import numpy as np
from PIL import Image
from tqdm import tqdm

from utils import Sizes


parser = ArgumentParser(prog='file2mp4 encoder', description='Encodes any file into a mp4', epilog='Source: https://github.com/fourjr/file2mp4')
parser.add_argument('filename', help='file to encode')
parser.add_argument('-f', dest='fps', choices=range(1, 61), type=int, metavar='{1-60}', help='frames per second (default: 60)')
parser.add_argument('-r', dest='resolution', choices=(360, 480, 720, 1080, 2160, 7680), help='specific resolution for output (default: best fit)', type=int)
parser.add_argument('-d', dest='debug', default=False, help='enable debug mode for more verbose logging and saving (default: false)', action='store_true')
args = parser.parse_args()

DEBUG_MODE = args.debug
FILE_NAME = args.filename

with open(FILE_NAME, 'rb') as f:
    file_data = f.read()

file_size = len(file_data)

for name, size in Sizes.items():
    if args.resolution is not None:
        if name == str(args.resolution):
            CHOSEN_SIZE = size
            break
    else:
        if size.max_size is None or file_size < size.max_size:
            CHOSEN_SIZE = size
            break

FPS = args.fps or CHOSEN_SIZE.fps

if DEBUG_MODE:
    print(f'Debug Mode: True')

print(f'File name: {FILE_NAME}')
print(f'File size: {file_size} bytes')
print(f'Video size: {CHOSEN_SIZE.dimension.width}x{CHOSEN_SIZE.dimension.height} @ {FPS}fps {CHOSEN_SIZE.bitrate}Mbit/s')

# FORMAT: [LENGTH OF FILENAME (4bytes)][FILENAME][LENGTH OF FILEDATA (4bytes)][FILEDATA]
file_name_bytes = FILE_NAME.encode()

raw_data = len(file_name_bytes).to_bytes(4) + file_name_bytes + len(file_data).to_bytes(8) + file_data


# create the image data
img_io = io.BytesIO()

parsed_data = np.frombuffer(raw_data, dtype=np.uint8)

ls = parsed_data >> 4 # shift right by 2 bits
rs = parsed_data << 4 >> 4

final_data = np.insert(rs, np.arange(len(ls)), ls) * 16

n_bytes = len(final_data)  # we use bytes as each pixel (r/g/b) is 1 byte (0-255)
frame_count = math.ceil(n_bytes / CHOSEN_SIZE.frame_pixels)
pad_val = frame_count * CHOSEN_SIZE.frame_pixels - n_bytes  # how much to pad with black pixels (zeros)

padded_data = np.pad(final_data, (0, pad_val))  # pad only at the end
img_data = np.reshape(padded_data, (frame_count, CHOSEN_SIZE.dimension.height // 8, CHOSEN_SIZE.dimension.width // 8, 3))
# save images to buffer
print(f'Video duration: {frame_count} frame(s) {frame_count / FPS} second(s)')
print('Processing frames')
for n, frame in tqdm(enumerate(img_data), unit='f', total=frame_count):
    img = Image.fromarray(frame, mode='RGB')
    img = img.resize((CHOSEN_SIZE.dimension.width, CHOSEN_SIZE.dimension.height), Image.Resampling.NEAREST)
    img.save(img_io, format='png')
    if DEBUG_MODE:
        img.save(f'debug/enc/frame{n+1}.png')

print('Processing video')
# parse images to create video
new_fn = md5(FILE_NAME.encode()).hexdigest()[-8:]
if DEBUG_MODE:
    debug_args = ''
else:
    debug_args = '-v warning'
process = subprocess.run(
    # libaom-av1, libsvtav1
    f'ffmpeg -y -hide_banner {debug_args} -stats -f image2pipe -r {FPS} -i pipe: -c:v libaom-av1 -preset 3 -svtav1-params tune=0:enable-overlays=1:scd=1:scm=0:crf=1:qp=1 -cpu-used 8 -row-mt true -threads 8 -tile-columns 1 -tile-rows 0 -b:v {CHOSEN_SIZE.bitrate}M -pix_fmt gbrp -crf 0 "output/{new_fn}.mp4"',
    shell=True, input=img_io.getvalue(), check=True
)

print(f'output/{new_fn}.mp4')
