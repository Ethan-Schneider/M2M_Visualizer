This repository if for designing and producing videos of robots navigating in different environments. 

### Installing packages 
pip install -r /path/to/requirements.txt


## Example command line argument 
python main.py maps/small_restricted.map 3600_informed_uniform_fast_SCF_none_ecbs_10_40_0_no_seq_full.json output_video.mp4 0 50

python main.py maps/[map name].map [insert json data file here].json [output file name].mp4 [start timestep] [final timestep]