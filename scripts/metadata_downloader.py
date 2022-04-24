#!/usr/bin/env python3

# USE - Should need to change only the path variables to point to your file locations.
# Use this file in place of a .bat or .sh script (eg in the same directory as your downloads normally)
# Feel free to reach out if anything is confusing or busted


# Used for "manually" tracking what has and hasn't already been downloaded
# May not work well with excessively large channels (still need to verify this, not sure why it wouldn't)


#Run yt-dlp commands
import subprocess

import os
import sys

#regex
import re

import time

import pandas as pd


import JSONHandler

COMMENT_LIMIT = False
MAX_COMMENTS = 10000

#  __  __         _ _  __        _   _    _
# |  \/  |___  __| (_)/ _|_  _  | |_| |_ (_)___
# | |\/| / _ \/ _` | |  _| || | |  _| ' \| (_-<
# |_|  |_\___/\__,_|_|_|  \_, |  \__|_||_|_/__/
#                         |__/
# ===============================================================
# Modify this for your setup
# Used as an argument alongside yt-dlp, yt-dlp can handle globbing, relative paths, etc
#config_path = ''
config_path = os.path.normpath("~/school/cs4243/project/temp/project.conf")

# Path to archive file that contains already-downloaded video IDs
#archive_path = ''
archive_path = os.path.normpath("archive.txt")


# Batch file containing channel URLs
batch_path = os.path.normpath("batch_vids.txt")

# ===============================================================


#For loading symbol
def spinning_cursor():
    while True:
        for cursor in "|/-\\":
            yield cursor

#Attempt at loading progress bar as it's longer
def progress_bar(max_length=10, char='#'):

    bars = []
    for i in range(1, max_length + 1):
        bars.append(''.join([x*i for x in char]))

    while True:
        for cursor in bars:
            yield cursor

def ytdlp_get_channel_name(channel_url, seconds=5):
    channel_name = ''

    args = ytdlp_simulate.split(' ')
    args.append(channel_url)
    # print(args)

    # Run yt-dlp
    print(args)
    # Assumes everything will work
    output = subprocess.Popen(args,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              )

    start_time = time.time()
    # Print and parse the output line by line as yt-dlp runs
    print(iter(output.stdout.readline, ""))
    for stdout_line in iter(output.stdout.readline, ""):
        #print(len(stdout_line))
        if len(stdout_line) > 0:
            print(stdout_line[:-1])
            channel_match = re.search(b"^\[download\] Downloading playlist:.*", stdout_line)

            #Last line hit, parse out channel name
            if channel_match:
                channel_name = channel_match.group().decode().split(' ')[3:]
                channel_name = channel_name[:-2]
                channel_name = ' '.join(channel_name)
                break

        else:
            break

        #X seconds have passed
        if time.time() - start_time > seconds:
            #Kill the process
            output.kill()
            break


    output.stdout.flush()
    return channel_name



def ytdlp_get_ids(channel_url):
    '''
    Run yt-dlp --simulate and parse output of command for video IDs
    Returns list of video IDs and channel name
    '''
    ytdlp_simulate = "yt-dlp --simulate "

    video_ids = []
    channel_name = ''

    args = ytdlp_simulate.split(' ')
    args.append(channel_url)
    # print(args)

    # Run yt-dlp
    print(args)
    # Assumes everything will work
    output = subprocess.Popen(args,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    # Print and parse the output line by line as yt-dlp runs
    # FIXME - Hangs here on T-series channel consistently, error indicates its loop line itself (immediately below)
    print(iter(output.stdout.readline, ""))
    for stdout_line in iter(output.stdout.readline, ""):
        #print(len(stdout_line))
        if len(stdout_line) > 0:
            print(stdout_line[:-1])
            match = re.search(b"^\[youtube\] [A-Z,a-z,0-9,_,-]{11}", stdout_line)
            channel_match = re.search(b"^\[download\] Finished downloading playlist:.*", stdout_line)

            if match:
                # split on space and add ID to list
                video_id = match.group().decode().split(' ')[1]
                if video_id not in video_ids:
                    video_ids.append(video_id)
                #print(match.group().decode())

        else:
            break
        #print(end='')

    output.stdout.flush()
    return video_ids

def ytdlp_download_videos(videos, progress=False, quiet=False):

    num_downloads = 0
    total_videos = len(videos)

    start_time = time.time()

    for video in videos:
        if progress is True:
            print("Video {}/{}  - id: {} - Total Time: {}".format(num_downloads + 1, total_videos, video, int(time.time() - start_time)))
        # If video is successfully downloaded, count it
        if ytdlp_download_video(video, quiet) == 0:
            num_downloads += 1

        #Decrement total num of vids left as one failed
        else:
            total_videos -= 1

    return num_downloads

def ytdlp_download_video(video, quiet=False):

    args = ytdlp_args[:]
    if quiet is True:
        args.append("--quiet")

    # Comment limit is set
    if COMMENT_LIMIT is True and MAX_COMMENTS > 0:
        args.append("--extractor-args \"youtube:max_comments={},all,all,all\"".format(MAX_COMMENTS))

    args.append("https://www.youtube.com/watch?v=" + video)

    spinner = spinning_cursor()
    num_cursors = 10

    # Run yt-dlp to download video metadata
    output = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    start_time = time.time()

    # 10 hour max limit for a single video to finish
    max_time = 3600 * 10
    #max_time = 10

    # Print and parse the output line by line as yt-dlp runs
    if quiet is False:
        for stdout_line in iter(output.stdout.readline, ""):
            if time.time() - start_time > max_time:
                return 1
            #print(len(stdout_line))
            if len(stdout_line) > 0:
                print(stdout_line[:-1])

            else:
                break


    # Wait for yt-dlp to finish running to get return code
    while output.poll() is None:
        if time.time() - start_time > max_time:
            return 1
        # Print loading icon so you know it's working
        # If this stops spinning, something broke
        #sys.stdout.write(next(spinner))
        progress = next(spinner)
        for i in range(num_cursors):
            sys.stdout.write(progress)
        sys.stdout.flush()
        time.sleep(0.001)
        for i in range(num_cursors):
            sys.stdout.write('\b')
        #time.sleep(0.5)

    # If return code is 0 (success) then append video ID to archive file
    if output.returncode == 0:
        append_file_list(archive_path, ["youtube " + video])

    # TODO
    # add else to throw the video non-working ID into a log file for reference later on
    # Don't expect this to be very necessary
    #
    return output.returncode

def write_file_list(path, write_list, filename=None):
    '''
    Write list to file
    2 required arguments
    Path - path to directory or file
    write_data - data to be written

    Optional
    filename - filename for when path is a directory

    returns integer value
        0 - success
        nonzero - error
    '''
    #Check if path is a directory and filename was set
    if os.path.isdir(path) and filename is not None:
        with open(os.path.join(path, filename), 'w') as wf:
            wf.write('\n'.join(str(line) for line in write_list))
            wf.write('\n')

    #Path is to file
    elif os.path.isfile(path):
        with open(os.path.join(path), 'w') as wf:
            wf.write('\n'.join(str(line) for line in write_list))
            wf.write('\n')

    else:
        return 1

    return 0


def append_file_list(path, write_list, filename=None):
    '''
    Append list to file
    2 required arguments
    Path - path to directory or file
    write_data - data to be written

    Optional
    filename - filename for when path is a directory

    returns integer value
        0 - success
        nonzero - error
    '''
    # If path doesn't exist and path isn't to a file
    # TODO - Create path default instead
    # if not os.path.exists(path) and not os.path.isfile(path):
    #     #os.makedirs(path)
    #     return 1

    #Check if path is a directory and filename was set
    if os.path.isdir(path) and filename is not None:
        with open(os.path.join(path, filename), 'a') as wf:
            wf.write('\n'.join(str(line) for line in write_list))
            wf.write('\n')

    #Path is to file or path isn't a file but filename is None, implying path should be a filepath
    elif os.path.isfile(path) or not os.path.isfile(path) and filename is None:
        with open(os.path.join(path), 'a') as wf:
            wf.write('\n'.join(str(line) for line in write_list))
            wf.write('\n')

    else:
        return 1

    return 0

def remove_file_list(path, remove_list, filename=None):
    '''
    Remove elements of list from file
    2 required arguments
    Path - path to directory or file
    write_data - data to be written

    Optional
    filename - filename for when path is a directory

    returns integer value
        0 - success
        nonzero - error
    '''

    lines = []
    if os.path.isdir(path) and filename is not None:
        with open(os.path.join(path, filename), 'r+') as fp:
            lines = fp.readlines()
            for element in remove_list:
                if element in lines:
                    lines.remove(element)

            fp.write('\n'.join(str(line) for line in lines))
            fp.write('\n')


    #Path is to file or path isn't a file but filename is None, implying path should be a filepath
    elif os.path.isfile(path) or not os.path.isfile(path) and filename is None:
        with open(os.path.join(path), 'r+') as fp:
            lines = fp.readlines()
            for element in remove_list:
                if element in lines:
                    lines.remove(element)

            fp.write('\n'.join(str(line) for line in lines))
            fp.write('\n')

    else:
        return 1

    return 0


def get_ids_from_jsons():
    '''
    Parse all .info.json files for their IDs
    Removes non-video IDs

    returns list of video IDs in ytdlp archive format (with "youtube" prefix)
        example: youtube hd-y7uRHBTg
    '''
    id_list = JSONHandler.JSONHandler().dump_select_key('id')
    for video in id_list:
        if len(video) != 11:
            id_list.remove(video)

    for video in id_list:
        id_list[id_list.index(video)] = "youtube " + video

    return id_list

if __name__ == '__main__':
    # used to get video IDs
    ytdlp_simulate = "yt-dlp --simulate "

    # Download video information
    #ytdlp_download = "yt-dlp --config-location"
    ytdlp_args = ["yt-dlp",
                "-v",
                "--ignore-errors",
                "--output", "'videos/%(channel)s_%(uploader_id)s/%(upload_date)s/%(title)s.%(ext)s'",
                "--restrict-filenames",
                "--write-info-json",
                "--write-comments",
                "--write-thumbnail",
                "--convert-thumbnails", "jpg",
                "--skip-download",
                ]
    # List of channels from batch file for yt-dlp (no longer to be used in the yt-dlp options as this script should manage it)
    channels = []

    # Get a list of video IDs in existing json files
    id_list = get_ids_from_jsons()
    append_file_list(archive_path, id_list)

    # Create dict where key is video ID and value is key number
    archive_dict = pd.read_csv(archive_path, delimiter=' ', header=None).to_dict()[1]
    archive_dict = dict([(value, key) for key, value in archive_dict.items()])


    # Reads all of the channel URLs into the channels[] list
    with open(os.path.join(batch_path), 'r') as batch_file:
        lines = batch_file.readlines()
        for line in lines:
            #If the URL doesn't end in a / add one
            #Assumes specific format currently adhered to in current list
            # if line[-2] != "/":
            #     line = line.rstrip('\n') + '/'

            channels.append(line)



    # List of video IDs to download any new videos
    new_downloads = []

    # List of completed channel URLs
    completed_channels = []

    # Go through each channel URL and see if it's been downloaded before
    # Download undownloaded videos
    for channel_url in channels:
        video_ids = []

        channel_name = ytdlp_get_channel_name(channel_url)
        video_ids = ytdlp_get_ids(channel_url)

        # If video ID not in archive file then add to list for downloads
        for video in video_ids:
            if video not in archive_dict:
                new_downloads.append(video)

        print("Downloading video info from: {}".format(ytdlp_get_channel_name(channel_url)))
        #num_downloads = ytdlp_download_videos(list(dict.fromkeys(new_downloads)), True, True)
        num_downloads = ytdlp_download_videos(list(dict.fromkeys(new_downloads)), True, False)
        #If there are no new_downloads (videos) OR all videos were downloaded, then mark ias compelted
        if len(new_downloads) == 0 or num_downloads == len(new_downloads):

            #Remove from batch file and append to completed file
            with open(os.path.join(batch_path), 'r+') as fp:
                #Append to completed file
                append_file_list(os.getcwd(), completed_channels, 'completed.txt')

                remove_file_list(os.path.join(batch_path), [channel_url])


    # FIXME - Can add harmless duplicates to file
    # Solution may be best in another script to replicate "sort -u" capability
    # with open('batch_vids.txt', 'r+') as fp:
    #     lines = fp.readlines()

    #     index = 0
    #     #print(lines)
    #     for line in lines:
    #         #If the URL doesn't end in a / add one
    #         #Assumes specific format currently adhered to in current list
    #         if line[-2] != "/":
    #             line = line.rstrip('\n') + '/'
    #         lines[index] = line
    #         index += 1
    #     for channel in completed_channels:
    #         #if channel[:-1] in lines:
    #         # Was accounting for the trailing slash or not but 2nd if should be redundant now
    #         if channel in lines:
    #             print("COMPLETED: " + channel)
    #             lines.remove(channel)
    #         if (channel[:-2] + '\n') in lines:
    #             print("COMPLETED: " + channel)
    #             lines.remove(channel[:-2] + '\n')

    #     # Point back to beginning of file before writing again
    #     # Otherwise it'll just dupe some or all of the file
    #     fp.seek(0, 0)

    #     # If there are no more urls in file, write empty file
    #     if len(lines) == 0:
    #         with open('batch_vids.txt', 'w') as fp:
    #             pass
    #     # Write remaining lines to file
    #     else:
    #         fp.writelines(lines)
