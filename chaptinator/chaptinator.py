#!/usr/bin/env -S python -O
""" Add chapters on scene changes to videos (e.g. slide changes in presentations) """
import re
import tempfile

from subprocess import check_output, run, STDOUT
from argparse import ArgumentParser, Namespace
from os import path
from typing import List


def video_extract_cuts(video_file_name: str, change_threshold: float):
    command = ['ffmpeg',
               '-i', video_file_name,
               '-filter:v', f"select=\'gt(scene,{change_threshold})\',showinfo",
               '-nostats',
               '-f', 'null',
               '-']
    if __debug__:
        print(command)
    cuts = check_output(command, stderr=STDOUT)
    cuts = cuts.decode('utf-8').split('\n')
    return cuts


def extract_cut_times(cuts_raw: str):
    cut_times = [0]
    for line in cuts_raw:
        match = re.search(r'pts_time:([0-9.]*)', line)
        if match:
            time = match.group(1)
            cut_times.append(int(float(time) * 1000))
    return cut_times


def video_extract_duration(video_file_name: str):
    command = ['ffprobe',
               '-v', 'error',
               '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1',
               video_file_name]
    duration = check_output(command, stderr=STDOUT).strip()
    duration = int(float(duration) * 1000)
    return duration


def assemble_new_metadata(artist: str, cut_times: List[int], title: str):
    metadata = f""";FFMETADATA1
title={title}
artist={artist}
"""
    cut_time_pairs = zip(cut_times[:-1], cut_times[1:])
    for i, (start, end) in enumerate(cut_time_pairs, start=1):
        metadata += f"""[CHAPTER]
TIMEBASE=1/1000
START={start}
END={end - 1}
title={i}
"""
    if __debug__:
        print(metadata)
    return metadata


def write_new_video_file(filename_output, meta_file_name, settings,
    video_file_name):

    codec_params = []

    if settings.scale:
        codec_params += ["-vf", "scale=-1:720"]

    if settings.optimize:
        codec_params += ["-tune", "stillimage"]

    if settings.reduce_framerate:
        codec_params += ["-r", "5"]

    if settings.scale or settings.optimize or settings.reduce_framerate:
        codec_params += ["-c:v", "libx264",
                         "-crf", "23",
                         "-pix_fmt", "yuv420p",
                         "-preset", "ultrafast"]
    else:
        codec_params += ['-c:v', 'copy']


    if settings.compress_audio:
        codec_params += ["-q:a", "8"]

    if settings.downmix_mono:
        codec_params += ["-ac", "1"]

    if settings.compress_audio or settings.downmix_mono:
        codec_params += ["-c:a", "libmp3lame"]
    else:
        codec_params += ['-c:a', 'copy']

    command = ['ffmpeg',
               '-y',
               '-i', video_file_name,
               '-i', meta_file_name,
               '-map_metadata', '1']
    command += codec_params
    command += [filename_output]
    if __debug__:
        print(command)
    run(command, check=True)


class Main:
    """Main class"""
    parser: ArgumentParser
    args: Namespace

    def __init__(self):
        self.parser = ArgumentParser(description="chapterize power point exported videos")
        self.parser.add_argument("VIDEO", type=str,
                                 help="Input video file")
        self.parser.add_argument("-t", "--title", type=str,
                                 help="set title in metadata")
        self.parser.add_argument("-a", "--artist", type=str, default="",
                                 help="set artist in metadata")
        self.parser.add_argument("-c", "--change-threshold", type=float, default=0.1,
                                 help="set threshold for chapter detection")
        self.parser.add_argument("-s", "--scale", action="store_true",
                                 help="scale down to 720p")
        self.parser.add_argument("-r", "--reduce_framerate", action="store_true",
                                 help="reduce framerate to 5fps (optimal for slides)")
        self.parser.add_argument("-o", "--optimize", action="store_true",
                                 help="activate ffmpeg tune for stillimage (optimal for slides)")
        self.parser.add_argument("-v", "--compress_audio", action="store_true",
                                 help="convert audio to VBR MP3 with quality 8 (optimal for speech)")
        self.parser.add_argument("-d", "--downmix_mono", action="store_true",
                                 help="downmix both audio channels into a single mono audio channel")
        self.parser.add_argument("-m", "--meta", type=str,
                                 help="use existing meta data file "
                                      "(disables automated chapter detection)")
        try:
            self.args = self.parser.parse_args()
        except TypeError:
            self.parser.print_help()

    def main(self):
        filename = path.splitext(self.args.VIDEO)[0]
        filename_output = filename + '-chaptered.mp4'
        title = self.args.title if self.args.title else path.basename(filename)

        if self.args.meta:
            meta_file_name = self.args.meta
        else:
            meta_file_name = self.extract_metadata_from_video(title)

        write_new_video_file(filename_output, meta_file_name, self.args,
            self.args.VIDEO)

    def extract_metadata_from_video(self, title):
        cuts_raw = video_extract_cuts(self.args.VIDEO, self.args.change_threshold)
        cut_times = extract_cut_times(cuts_raw)
        cut_times.append(video_extract_duration(self.args.VIDEO))
        metadata = assemble_new_metadata(self.args.artist, cut_times, title)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as file_meta:
            file_meta.write(bytes(metadata, 'utf-8'))
            meta_file_name = file_meta.name
        return meta_file_name


if __name__ == '__main__':
    Main().main()
