import os
import subprocess
from argparse import ArgumentParser

import numpy as np
from tqdm import tqdm

from utils import Constants, Frame


parser = ArgumentParser(prog='file2mp4 decoder', description='Decodes a mp4 back into a file', epilog='Source: https://github.com/fourjr/file2mp4')
parser.add_argument('filename')
parser.add_argument('-d', '--debug', action='store_true', default=False)
args = parser.parse_args()

DEBUG_MODE = args.debug
FILE_NAME = args.filename

print(f'File name: {FILE_NAME}')

cmd = f'ffmpeg -y -hide_banner -v warning -stats -i "{FILE_NAME}" -pix_fmt rgb24 -c:v png -f rawvideo -'
if DEBUG_MODE:
    cmd += f' debug/dec/frame%03d.png'

process = subprocess.run(
    cmd,
    shell=True, check=True, stdout = subprocess.PIPE,
)

out = process.stdout

out_array = []
for i in out.split(Constants.PNG_HEADER):
    if i:
        out_array.append(i + Constants.PNG_HEADER)

frames = [Frame(frame, n) for n, frame in enumerate(out_array)]


# parse all other frames
file_data = None
cursor = 0
for n, frame in tqdm(enumerate(frames), unit='f', total=len(frames)):
    if n == 0:
        # read metadata
        fn_len = frame.read_int(4)

        try:
            fn = os.path.basename(frame.read_str(fn_len))
        except UnicodeDecodeError:
            raise ValueError('Invalid frame data, please check your input file')

        print('fn', fn)
        data_len = frame.read_int(8)
        file_data = np.empty(data_len, dtype=np.uint8)

    read_val = frame.read_buffer(data_len - cursor)
    ind = np.arange(cursor, cursor + len(read_val))
    np.put(file_data, ind, read_val)
    cursor += len(read_val)

file_data.tofile(f'result/{fn}')
print(f'result/{fn}')
