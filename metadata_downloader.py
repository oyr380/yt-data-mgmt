#!/usr/bin/env python3

#Run yt-dlp commands
import subprocess

#regex
import re

import pandas as pd
import time

# Modify this for your setup
#config_path = ''
config_path = "~/school/cs4243/project/temp/project.conf"
#archive_path = ''
archive_path = "/home/kerensky/Documents/school/UTSA/cs4243/project/temp/total_archive.txt"

# used to get video IDs
ytdlp_simulate = "yt-dlp --simulate "

# Download video information
ytdlp_download = "yt-dlp --config-location"

channels = []

# Create dict where key is video ID and value is key number
archive_dict = pd.read_csv(archive_path, delimiter=' ', header=None).to_dict()[1]
archive_dict = dict([(value, key) for key, value in archive_dict.items()])


# Assumes there is a file called "batch_vids.txt"
with open("batch_vids.txt", 'r') as batch_file:
    lines = batch_file.readlines()
    for line in lines:
        #If the URL doesn't end in a / add one
        #Assumes specific format currently adhered to in current list
        if line[-2] != "/":
            line = line.rstrip('\n') + '/'

        channels.append(line.rstrip("\n"))



# List of video IDs to download any new videos
new_downloads = []

# List of completed channel URLs
completed_channels = []

# Go through each channel URL
for channel_url in channels:
    video_ids = []

    # Get a list of the channel's video IDs for comparison later
    args = ytdlp_simulate.split(' ')
    args.append(channel_url)
    # print(args)

    # Run yt-dlp
    print(args)
    # Assumes everything will work
    output = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Print and parse the output line by line as yt-dlp runs
    for stdout_line in iter(output.stdout.readline, ""):
        #print(len(stdout_line))
        if len(stdout_line) > 0:
            print(stdout_line[:-1])
            match = re.search(b"^\[youtube\] [A-Z,a-z,0-9,_,-]{11}", stdout_line)

            if match:
                # split on space and add ID to list
                video_id = match.group().decode().split(' ')[1]
                if video_id not in video_ids:
                    video_ids.append(video_id)
                #print(match.group().decode())

        else:
            break
        #print(end='')

    # If video ID not in archive file then add to list for downloads
    for video in video_ids:
        if video not in archive_dict:
            new_downloads.append(video)

    #If there are no new_downloads then channel marked as complete
    if len(new_downloads) == 0:
        completed_channels.append(channel_url)

# Add completed channel to completed.txt
with open('completed.txt', 'a+') as fp:
    fp.writelines(completed_channels)

# Remove completed channel from batch_vids.txt
with open('batch_vids.txt', 'w+') as fp:
    lines = fp.readlines()
    for channel in completed_channels:
        if channel in lines:
            lines.remove(channel)
    fp.writelines(lines)


# Go through each new video ID and download the data
# Updates the archive file after successful download
for video in new_downloads:
    args = ytdlp_download.split(' ')
    args.append(config_path)
    args.append(video)


    print(args)

    # Run yt-dlp to download video metadata
    output = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Print and parse the output line by line as yt-dlp runs
    for stdout_line in iter(output.stdout.readline, ""):
        #print(len(stdout_line))
        if len(stdout_line) > 0:
            print(stdout_line[:-1])
        else:
            break
    # Wait for yt-dlp to finish running to get return code
    while output.poll() is None:
        time.sleep(0.5)

    # If return code is 0 (success) then append video ID to archive file
    if output.returncode == 0:
        with open(archive_path, 'a') as fp:
            newline = "youtube " + video
            #fp.write('\n')
            fp.write(newline)
            fp.write('\n')
    # TODO
    # add else to throw the video ID into a log file for reference later on
    # Don't expect this to be very necessary
