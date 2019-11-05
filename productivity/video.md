Video file handling
===================

Handbrake Usage
------------

Handbrake is a DVD ripping tool, running on all platforms. Under Linux, create an image from DVD disc like:

    HandBrakeCLI -i /dev/cdrom -t 1 -f mkv -e x264 -b 1500 --two-pass -a 2 -E lame -B 256 --decomb -m -o ~"/Downloads/Die stille Revolution.mkv"
