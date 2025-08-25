This repository if for designing and producing videos of robots navigating in different environments. 

### Installing packages 
pip install -r /path/to/requirements.txt

### Installing ffmpeg 
To create videos, we will need to install the ffmpeg executable. Go to https://www.ffmpeg.org/download.html and follow the instructions to download a zip file for your OS, then place "ffmpeg.exe" into the exe directory. 

## Example command line argument 
python main.py maps/symbotic_small.map 3600_informed_uniform_fast_SCF_none_ecbs_10_40_0_no_seq_full.json output_video.mp4 0 50
