import io
import math
import subprocess
from hashlib import md5

import numpy as np
from PIL import Image
from tqdm import tqdm

from utils import Sizes


FILE_NAME = input('File name: ')


with open(FILE_NAME, 'rb') as f:
    file_data = f.read()

file_size = len(file_data)

for size in Sizes.clsiter():
    if file_size < size.max_size:
        CHOSEN_SIZE = size
        break

print(f'File size: {file_size} bytes')
print(f'Video Size: {CHOSEN_SIZE.dimension.width}x{CHOSEN_SIZE.dimension.height} @ 60fps {CHOSEN_SIZE.bitrate}Mbit/s')

# FORMAT: [LENGTH OF FILENAME (4bytes)][FILENAME][LENGTH OF FILEDATA (4bytes)][FILEDATA]
file_name_bytes = FILE_NAME.encode()

raw_data = len(file_name_bytes).to_bytes(4) + file_name_bytes + len(file_data).to_bytes(8) + file_data
n_bytes = len(raw_data)  # we use bytes as each pixel (r/g/b) is 1 byte (0-255)

frame_count = math.ceil(n_bytes / CHOSEN_SIZE.frame_pixels)
print(f'Video duration: {frame_count} frame(s)')

pad_val = frame_count * CHOSEN_SIZE.frame_pixels - n_bytes  # how much to pad with black pixels (zeros)

# create the image data
img_io = io.BytesIO()

parsed_data = np.frombuffer(raw_data, dtype=np.uint8)
padded_data = np.pad(parsed_data, (0, pad_val))  # pad only at the end
img_data = np.reshape(padded_data, (frame_count, CHOSEN_SIZE.dimension.height, CHOSEN_SIZE.dimension.width, 3))

# save images to buffer

print('Processing frames')
for n, frame in tqdm(enumerate(img_data), unit='f', total=frame_count):
    img = Image.fromarray(frame, mode='RGB')
    img.save(img_io, format='png')

print('Processing video')
# parse images to create video
new_fn = md5(FILE_NAME.encode()).hexdigest()[-8:]
process = subprocess.run(
    f'ffmpeg -y -f image2pipe -i pipe: -framerate 60 -c:v libx264rgb -b:v {CHOSEN_SIZE.bitrate}M -pix_fmt rgb24 -lossless 1 -crf 0 "output/{new_fn}.mp4"',
    shell=True, input=img_io.getvalue(), check=True, capture_output=True
)

print(f'output/{new_fn}.mp4')
