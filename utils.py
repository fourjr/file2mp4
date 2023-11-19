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
        self.frame_pixels = self.dimension.width * self.dimension.height * 3
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


def img_bytes_to_array(frame) -> np.ndarray[np.uint8]:
    data = io.BytesIO(frame)
    img = Image.open(data)
    return np.asarray(img, dtype=np.uint8).flatten()


class Constants:
    PNG_HEADER = b'\x00\x00\x00\x00IEND\xaeB`\x82'


class Frame:
    def __init__(self, raw_frame_data) -> None:
        self.cursor = 0
        self.frame = img_bytes_to_array(raw_frame_data)

    def read_buffer(self, size) -> np.ndarray[np.uint8]:
        val = self.frame[self.cursor:self.cursor + size]
        self.cursor += size
        return val

    def read_int(self, size) -> int:
        return int.from_bytes(self.read_buffer(size))

    def read_str(self, size) -> str:
        return self.read_buffer(size).tobytes().decode()
