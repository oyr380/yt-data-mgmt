This is an example directory to use for learning, troubleshooting, and to illustrate how the scripts work.
The scripts work only from the current working directory and below so it is safe to run any script from this directory without risk of making a mess somewhere else.

Example use-case is to run the scripts from this directory.
Copy the python scripts from their directory using `cp ../scripts/*py .` into here **or** run them directly from here using `python ../scripts/metadata_downloader.py` (for example)

`metadata_downloader.py` will read **batch_vids.txt** and begin downloading the video list for the channel in the file. 

Files  and directories will be created as each script runs, explore them and figure out your workflow. The simplest style is to run the scripts in the same directory as **batch_vids.txt**
