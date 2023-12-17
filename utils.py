import io
from collections import OrderedDict, namedtuple
from dataclasses import dataclass
from typing import Dict

import numpy as np
from PIL import Image


Dimension = namedtuple('Dimension', ['width', 'height'])


@dataclass
class Size:
    dimension: Dimension
    bitrate: float
    max_size: int = -1  # bytes
    frame_pixels: int = None
    fps: int = 5

    def __post_init__(self):
        self.frame_pixels = (self.dimension.width // 8) * (self.dimension.height // 8) * 3
        if self.max_size == -1:
            # frame_pixels * fps * seconds
            self.max_size = self.frame_pixels * self.fps * 10


Sizes: Dict[str, Size] = OrderedDict({
    '360': Size(Dimension(480, 360), 1.5),
    '480': Size(Dimension(720, 480), 4),
    '720': Size(Dimension(1280, 720), 7.5),
    '1080': Size(Dimension(1920, 1080), 12),
    '2160': Size(Dimension(3840, 2160), 24),
    '7680': Size(Dimension(7680, 4320), 48, None),
})


class Constants:
    PNG_HEADER = b'\x00\x00\x00\x00IEND\xaeB`\x82'


class Frame:
    def __init__(self, raw_frame_data, id) -> None:
        self.cursor = 0
        self.id = id
        self.frame = self._img_bytes_to_array(raw_frame_data)

    def _img_bytes_to_array(self, frame) -> np.ndarray[np.uint8]:
        data = io.BytesIO(frame)
        img = Image.open(data)
        img = img.resize((img.width // 8, img.height // 8), Image.Resampling.NEAREST)
        vals = np.asarray(img, dtype=np.uint8).flatten()
        vals = np.rint(np.divide(vals, 16)).astype(np.uint8)
        final = (((vals[::2] << 4) | vals[1::2]))
        if self.id == 0:
            final.tofile('final_dec.bin')
        return final


        # np.left_shift(vals, 3, where=np.)

    def read_buffer(self, size) -> np.ndarray[np.uint8]:
        val = self.frame[self.cursor:self.cursor + size]
        self.cursor += size
        return val

    def read_int(self, size) -> int:
        return int.from_bytes(self.read_buffer(size))

    def read_str(self, size) -> str:
        return self.read_buffer(size).tobytes().decode()
