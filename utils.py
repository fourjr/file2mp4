import io
from collections import namedtuple
from dataclasses import dataclass

import numpy as np
from PIL import Image


Dimension = namedtuple('Dimension', ['width', 'height'])


@dataclass
class Size:
    dimension: Dimension
    bitrate: float
    max_size: int = -1  # bytes
    frame_pixels: int = None

    def __post_init__(self):
        self.frame_pixels = self.dimension.width * self.dimension.height * 3
        if self.max_size == -1:
            # frame_pixels * fps * seconds
            self.max_size = self.frame_pixels * 60 * 10


class Sizes:
    P7680: Size = Size(Dimension(7680, 4320), 48, None)
    P2160: Size = Size(Dimension(3840, 2160), 24)
    P1080: Size = Size(Dimension(1920, 1080), 12)
    P720: Size  = Size(Dimension(1280, 720), 7.5)
    P480: Size  = Size(Dimension(720, 480), 4)
    P360: Size  = Size(Dimension(480, 360), 1.5)

    @classmethod
    def clsiter(cls):
        return iter([cls.P360, cls.P480, cls.P720, cls.P1080, cls.P2160, cls.P7680])


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
