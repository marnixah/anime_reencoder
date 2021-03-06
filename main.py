#!/bin/python3
from pathlib import Path
import shutil
import subprocess
import os
import sys
import time
import ffmpeg
import glob

scanning = False

os.makedirs("./tmp/in/", exist_ok=True)
os.makedirs("./tmp/out/", exist_ok=True)

f = open('log.txt','w', encoding="utf-8")
f.write('')
f.close()
del f

def log(msg):
    print(msg)
    f = open('log.txt', 'a',  encoding="utf-8")
    f.write(msg+"\n")
    f.flush()
    f.close()


try:
    input_location = str(Path(sys.argv[1]))
    if not Path(input_location).exists():
        sys.exit("{} is not a valid folder".format(input_location))
except IndexError as e:
    sys.exit("Usage: python main.py <input folder>")

for f in glob.glob("./tmp/in/*") + glob.glob("./tmp/out/*"):
    os.remove(f)


def scan(folder):
    global scanning
    if scanning:
        return False
    i=0
    scanning = True
    videos = Path(folder).rglob('**/*.mkv')
    for video in videos:
        i+=1
        log("Scanning {} for HEVC".format(str(video)))
        codecs = []
        probed = False
        while not probed:
            try:
                streams = ffmpeg.probe(str(video))['streams']
                probed = True
            except:
                pass

        for stream in streams:
            try:
                codecs.append(stream['codec_name'])
            except KeyError:
                pass
        if 'hevc' in codecs:
            continue
        reencode(video)
    scanning = False


def reencode(video):
    log("Copying {} to local tmp folder".format(video))
    shutil.copy(str(video), "./tmp/in/{}".format(video.name))
    log("Sending {} to the re-encode queue".format(video))
    cmd = ["HandBrakeCLI", "--preset-import-file", "./Anime.json",
           "-Z", "Anime", "-i", "./tmp/in/{}".format(video.name), "-o", "./tmp/out/{}".format(video.name)]
    p = subprocess.Popen(cmd)
    p.communicate()

    if p.returncode != 0:
        print("encoder failed on {}, going to next video file".format(video))
        return

    move(video)
    os.remove("./tmp/in/{}".format(video.name))


def move(video):
    relative_dir = str(video.parents[0])[len(input_location):]
    os.makedirs(input_location + relative_dir, exist_ok=True)
    out = "{0}/{1}/{2}".format(input_location, relative_dir, video.name)
    if os.path.exists(out):
        os.remove(out)
    shutil.move("./tmp/out/{}".format(video.name), out)


if __name__ == "__main__":
    scan(input_location)
    sys.exit("All anime in {} is now HEVC".format(input_location))