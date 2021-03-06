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

COMMENT_LIMIT = True
TOP_COMMENTS_FIRST = True
MAX_COMMENTS = 10000


ytdlp_args = ["yt-dlp",
                "-v",
                "--ignore-errors",
                "--output", "'videos/%(channel)s_%(uploader_id)s/%(upload_date)s/%(title)s.%(ext)s'",
                "--restrict-filenames",
                "--write-info-json",
                "--write-comments",
                #"--write-thumbnail",
                #"--convert-thumbnails", "jpg",
                "--skip-download",
              ]
#  __  __         _ _  __        _   _    _
# |  \/  |___  __| (_)/ _|_  _  | |_| |_ (_)___
# | |\/| / _ \/ _` | |  _| || | |  _| ' \| (_-<
# |_|  |_\___/\__,_|_|_|  \_, |  \__|_||_|_/__/
#                         |__/
# ===============================================================
# Modify this for your setup
# Used as an argument alongside yt-dlp, yt-dlp can handle globbing, relative paths, etc
config_path = ''
#config_path = os.path.normpath("~/school/cs4243/project/temp/project.conf")

# Path to archive file that contains already-downloaded video IDs
#archive_path = ''
archive_path = os.path.normpath("archive.txt")
#archive_path = os.path.normpath('/home/dylan/Documents/grad_school/large_data/yt-data-mgmt/archive.txt')


# Batch file containing channel URLs
batch_path = os.path.normpath("batch_vids.txt")
#batch_path = os.path.normpath("/home/dylan/Documents/grad_school/large_data/yt-data-mgmt/batch-vids.txt")

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
    args.append(channel_url.strip())
    # print(args)

    # Run yt-dlp
    # Assumes everything will work
    output = subprocess.Popen(args,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              )

    start_time = time.time()
    # Print and parse the output line by line as yt-dlp runs
    #print(iter(output.stdout.readline, ""))
    print(output.stdout.readline().decode('utf8'))
    for stdout_line in iter(output.stdout.readline, ""):
        #print(len(stdout_line))
        if len(stdout_line) > 0:
            print(stdout_line[:-1].decode('utf8'))
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
    output.kill()  # added ,maybe a fix?
    return channel_name



def ytdlp_get_ids(channel_url):
    '''
    Run yt-dlp --simulate and parse output of command for video IDs
    Returns list of video IDs and channel name
    '''
    ytdlp_simulate = "yt-dlp --simulate "

    video_ids = []
    channel_name = ''

    #TODO - Check for file with channel_name that contains video IDs
    # If file exists and is not empty set video_ids to that
    args = ytdlp_simulate.split(' ')
    args.append(channel_url)
    # print(args)


    #Check if there's a file with the channel's info
    channel_name = ytdlp_get_channel_name(channel_url)


    channel_name = channel_name.replace(' ','_')
    video_id_filepath = os.path.join("channel_video_ids", "{}_vid_ids.txt".format(channel_name))

    #If channel video IDs exists in file, get the video IDs from there
    #Faster than waiting to parse the entire channel for larger channels
    if os.path.exists(video_id_filepath):
        with open(video_id_filepath, 'r') as fp:
            lines = fp.readlines()
            for vid_id in lines:
                video_ids.append(vid_id.replace('\n',''))

        return set(video_ids)


    # Run yt-dlp
    # Assumes everything will work
    output = subprocess.Popen(args,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    # Print and parse the output line by line as yt-dlp runs
    # FIXME - Hangs here on T-series channel consistently, error indicates its loop line itself (immediately below)
    print(output.stdout.readline().decode('utf8'))
    for stdout_line in iter(output.stdout.readline, ""):
        #print(len(stdout_line))
        if len(stdout_line) > 0:
            print(stdout_line[:-1].decode('utf8'))
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
    output.kill()



    #Write video_ids to file. Set to append just to be safe
    if not os.path.exists(video_id_filepath):
        video_id_dir = os.path.split(video_id_filepath)[0]
        if not os.path.isdir(video_id_dir):
            os.mkdir(video_id_dir)

        with open(video_id_filepath, 'a+') as fp:
            fp.write('\n'.join(str(line) for line in video_ids))

    return set(video_ids)

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
    # Max time to spend on a single video in seconds
    max_time = 3600 * 10
    if quiet is True:
        args.append("--quiet")

    # Comment limit is set
    if COMMENT_LIMIT is True and MAX_COMMENTS > 0:
        args.append("--extractor-args")
        #args.append("--extractor-args \"youtube:max_comments={},all,all,all\"".format(MAX_COMMENTS))
        #args.append("--extractor-args youtube:max_comments={},all,all,all".format(MAX_COMMENTS))
        args.append("youtube:max_comments={},{},{},all".format(MAX_COMMENTS, MAX_COMMENTS, MAX_COMMENTS))

        if TOP_COMMENTS_FIRST is True:
            args[-1] = args[-1] + ";comment_sort=top"
            #args.append("youtube:comment_sort=top")


        max_time = MAX_COMMENTS * 10

    #If comment limit is set to zero, don't write any comments
    elif COMMENT_LIMIT is True and MAX_COMMENTS == 0:
        args.remove("--write-comments")

    args.append("https://www.youtube.com/watch?v=" + video)

    spinner = spinning_cursor()
    num_cursors = 10

    # Run yt-dlp to download video metadata
    #print(args)
    output = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #NOTE - this may be useful for quiet option
    #output = subprocess.run(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    start_time = time.time()

    for stdout_line in iter(output.stdout.readline, ""):
        if time.time() - start_time > max_time:
            return 1
        if len(stdout_line) > 0:
            print(stdout_line[:-1])

        else:
            break

    # NOTE - Comments left in for future reference
    # Wait for yt-dlp to finish running to get return code
    while output.poll() is None:
        #if output.poll() is not None:
            #break
        if time.time() - start_time > max_time:
            return 1
        #print(stdout_line)
        #Print loading icon so you know it's working
        #If this stops spinning, something broke
        sys.stdout.write(next(spinner))
        #progress = next(spinner)
        #for i in range(num_cursors):
            #sys.stdout.write(progress)
        #sys.stdout.flush()
        #time.sleep(0.001)
        #for i in range(num_cursors):
            #sys.stdout.write('\b')
        #time.sleep(0.5)

    # If return code is 0 (success) then append video ID to archive file
    if output.returncode == 0:
        append_file_list(archive_path, ["youtube " + video])

    # TODO
    # add else to throw the video non-working ID into a log file for reference later on
    # Don't expect this to be very necessary
    #
    output.kill()
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


#FIXME
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

    file_to_append = ''

    write_list = set(write_list)
    lines = []
    #Check if path is a directory and filename was set
    if os.path.isdir(path) and filename is not None:
        file_to_append = os.path.join(path, filename)
        # if not os.path.exists(os.path.join(path, filename)):
        #     with open(os.path.join(path, filename), 'w') as wf:
        #         wf.write('')

        # with open(os.path.join(path, filename), 'a') as wf:
        #     wf.write('\n'.join(str(line) for line in write_list))

    #Path is to file or path isn't a file but filename is None, implying path should be a filepath
    # TODO Handle being given directory name as path
    # Shouldn't matter for project
    elif os.path.isfile(path):
        file_to_append = os.path.join(path)

        # if not os.path.exists(os.path.join(path)):
        #     with open(os.path.join(path, filename), 'w') as wf:
        #         wf.write()


    #Path isn't a file and filename is none
    elif not os.path.isfile(path) and filename is None:
        return 1

    else:
        return 1

    #Read lines from file to store them
    with open(os.path.join(file_to_append), 'r') as rf:
        lines = rf.readlines()

    #Add the write_list lines to the file's existing lines
    for line in write_list:
        lines.append(line)


    # Clear write_list and then populate it with all of the lines, stripping any newlines
    write_list = []
    for line in set(lines):
        write_list.append(line.rstrip())


    # Write all lines back to the file
    with open(os.path.join(file_to_append), 'w') as wf:
        wf.write('\n'.join(str(line) for line in write_list))
        wf.write('\n')

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

    #Open file and remove every instance of element in remove_list[] from the file
    #Write non-matching lines back to the file

    #Check if path is a directory and filename was set
    if os.path.isdir(path) and filename is not None:
        with open(os.path.join(path, filename), 'r+') as fp:
            lines = fp.readlines()
            for element in remove_list:
                while element in lines:
                    lines.remove(element)

            #Done to remove blank lines though would get other strange lines as well
            for curr_line in lines:
                if len(curr_line) < 10:
                    lines.remove(curr_line)

        #Write remaining lines back to file
        with open(os.path.join(path), 'w') as fp:
            fp.write(''.join(str(line) for line in lines))
            fp.write('\n')

    #Path is to file or path isn't a file but filename is None, implying path should be a filepath
    elif os.path.isfile(path) or not os.path.isfile(path) and filename is None:
        with open(os.path.join(path), 'r+') as fp:
            lines = fp.readlines()
            for element in remove_list:
                while element in lines:
                    lines.remove(element)

            #Done to remove blank lines though would get other strange lines as well
            for curr_line in lines:
                if len(curr_line) < 10:
                    lines.remove(curr_line)

        #Write remaining lines back to file
        with open(os.path.join(path), 'w') as fp:
            fp.write(''.join(str(line) for line in lines))
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
    # List of channels from batch file for yt-dlp (no longer to be used in the yt-dlp options as this script should manage it)
    channels = []
    archive_dict = []

    # Get a list of video IDs in existing json files
    id_list = get_ids_from_jsons()

    # Add video IDs from existing json files into archive file
    if append_file_list(archive_path, id_list) != 0:
        print(archive_path)
        print(id_list)




    #If the archive file exists and has at least 1 line then open it using pandas
    if os.path.isfile(archive_path):
        linecount = -1
        with open(archive_path, 'r') as fp:
            linecount = len(fp.readlines())

        if linecount > 0:
            # Create dict where key is video ID and value is key number
            archive_dict = pd.read_csv(archive_path, delimiter=' ', header=None).to_dict()[1]
            archive_dict = dict([(value, key) for key, value in archive_dict.items()])



    # Reads all of the channel URLs into the channels[] list
    with open(os.path.join(batch_path), 'r') as batch_file:
        lines = batch_file.readlines()
        for line in lines:
            # Avoid newlines
            if len(line) > 2:
                channels.append(line)



    # List of video IDs to download any new videos
    new_downloads = []

    # List of completed channel URLs
    completed_channels = []

    # Go through each channel URL and see if it's been downloaded before
    # Download videos that haven't been downloaded
    for channel_url in channels:
        video_ids = []

        channel_name = ytdlp_get_channel_name(channel_url)
        video_ids = ytdlp_get_ids(channel_url)

        # If video ID not in archive file then add to list for downloads
        for video in video_ids:
            if video not in archive_dict:
                new_downloads.append(video)

        #print("Downloading video info from: {}".format(ytdlp_get_channel_name(channel_url)))
        print("Downloading video info from: {}".format(channel_name))

        if len(new_downloads) > 0:
            #num_downloads = ytdlp_download_videos(list(dict.fromkeys(new_downloads)), True, True)
            num_downloads = ytdlp_download_videos(list(dict.fromkeys(new_downloads)), True, False)

        #If there are no new_downloads (videos) OR all videos were downloaded, then mark channel complete
        if len(new_downloads) == 0 or num_downloads == len(new_downloads):
            #Remove from batch file and append to completed file
            #with open(os.path.join(batch_path), 'r+') as fp:

            #Append to completed file
            completed_channels.append(channel_url)
            append_file_list(os.getcwd(), completed_channels, 'completed.txt')

            #Remove channel URL from batch_vids.txt
            remove_file_list(os.path.join(batch_path), [channel_url])
