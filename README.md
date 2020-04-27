# chaptinator

Add chapters on scene changes to videos (e.g. slide changes in presentations)


## Install

`chaptinator` requires `ffmpeg` to be installed on your system and for it to
be in `PATH`.
Follow the instructions on https://ffmpeg.org/ and make sure the commands
`ffmpeg` and `ffprobe` are available in your favorite shell (bash, zsh,
Powershell, ...).

Then install this package via pip. For a global installation use

```bash
sudo pip install chaptinator
```

and for a user-local installation use

```bash
pip install --user chaptinator
```


## Usage

```bash
chaptinator VIDEO [-t TITLE] [-a AUTHOR] [-c CHANGE_THRESH] [-s] [-r] [-v] [-m METADATA_FILE]
```

`-t TITLE` sets the title in the metadata (default: filename)

`-a ARTIST` sets the artist in the metadata

`-c CHANGE` "value between 0 and 1 to indicate a new scene; a low value
reflects a low probability for the current frame to introduce a new scene,
while a higher value means the current frame is more likely to be one"
-- https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect

`-s` scales the tagged result video to a height 720 while keeping the aspect
ratio

`-r` reduces the framerate to 5fps, which is optimal to save bandwidth when
powerpoint slides are the sole video content. Lower values cause problems with
some browser video players

`-v` converts the audio to MP3 with VBR (Variable BitRate) and a quality
setting of 8, which is optimal for speech with relatively long segments of
silence.
(Lame is compiled into the standard `ffmpeg` library while the Frauenhofer AAC,
which supports VBR, is not)

`-m METADATA_FILE` disables the cut detection and instead uses the provided
metadata file. This file has to have the structure described in
https://ffmpeg.org/ffmpeg-formats.html#Metadata-1


## Example

```bash
# increase cut detection threshold to 0.4, scale the video and reduce framerate
chaptinator foo.mp4 -t "Video Title" -a "Author Name" -c 0.4 -s -r

# read cuts from metadata file
chaptinator foo.mp4 -m metadata.txt
```

## Use Cases

`chaptinator` could be used to add chapters to presentation slides that were
recorded in PowerPoint and exported as video.

But of course it works with any video file that has cuts in it, just adjust
the `-c` parameter to your preference.
