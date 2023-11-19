## about
Uses pixel data to store file binary data
[inspiration](https://youtu.be/_w6PCHutmb4)

## example
[sample video](https://youtu.be/zjfkkXb_CIE)
```console
> certutil -hashfile 1Gb.dat MD5
MD5 hash of 1Gb.dat:
fae717cb3c1c7134ff7858246992f8b4

> python encode.py 1Gb.dat
File name: 1Gb.dat
File size: 1073741824 bytes
Video Size: 1280x720 @ 60fps 7.5Mbit/s
Video duration: 389 frame(s)
Processing frames
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 389/389 [00:52<00:00,  7.40f/s]
Processing video
output/a6721a9a.mp4

> python decode.py output/a6721a9a.mp4
File name: output/a6721a9a.mp4
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 389/389 [01:05<00:00,  5.91f/s]
result/1Gb.dat

> certutil -hashfile result/1GB.dat MD5
MD5 hash of result/1GB.dat:
fae717cb3c1c7134ff7858246992f8b4
```

## ideas
- Use audio as well to store data
- Combat yt compression?
- when decoding, statically assign memory so no need for concat

## libraries
- ffmpeg
- numpy
- PIL
- tqdm
