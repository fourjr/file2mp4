import subprocess

import numpy as np
from tqdm import tqdm

from utils import Constants, Frame


FILE_NAME = input('File name: ')
process = subprocess.run(
    f'ffmpeg -i "{FILE_NAME}" -pix_fmt rgb24 -c:v png -f rawvideo -',
    shell=True, check=True, capture_output=True
)

out = process.stdout

out_array = []
for i in out.split(Constants.PNG_HEADER):
    if i:
        out_array.append(i + Constants.PNG_HEADER)

frames = [Frame(frame) for frame in out_array]


# parse all other frames
file_data = np.empty(0, dtype=np.uint8)
curr_data_len = 0
for n, frame in tqdm(enumerate(frames), unit='f', total=len(frames)):
    if n == 0:
        # read metadata
        fn_len = frame.read_int(4)
        fn = frame.read_str(fn_len)
        data_len = frame.read_int(8)

    file_data = np.concatenate((file_data, frame.read_buffer(data_len - curr_data_len)), dtype=np.uint8)
    curr_data_len = len(file_data)

file_data.tofile(f'result/{fn}')
print(f'result/{fn}')
