#!/bin/env/usr python3

import sys
import os
import json
import JSONHandler

JSON_DEBUG = True
PRINT_OUTPUT = True

COMMENT_LIMIT = True
MAX_COMMENTS = 10000


# Default directory name to store cleaned jsons
save_dir = os.path.join('cleaned_jsons')

#python3 JSONHandler.py <target_directory> <save_directory>
# Arguments optional
# Default target directory is current working directory
# Default save directory is target_dir/cleaned_jsons
root_keys = [
            'id',
            'title',
            'thumbnail',
            'description',
            'upload_date',
            'uploader',
            'uploader_id',
            'uploader_url',
            'duration',
            'view_count',
            'age_limit',
            'webpage_url',
            'categories',
            'tags',
            'playable_in_embed',
            'is_live',
            'was_live',
            'live_status',
            'like_count',
            'channel',
            'channel_follower_count',
            'availability',
            'full_title',
            'display_id',
            'ext',
            'filesize_approx',
            'format_note',
            'width',
            'height',
            'resolution',
            'fps',
            'dynamic_range',
            'vcodec',
            'vbr',
            'acodec',
            'abr',
            'asr',
            'comment_count',
            'epoch',
            '_type',
            'duration_string',
            'comments',
]

# Nested keys that only apply to comments
# May be redundant
comment_keys = [
            'id',
            'text',
            'timestamp',
            'time_text',
            'like_count',
            'is_favorited',
            'author',
            'author_id',
            'author_thumbnail',
            'author_is_uploader',
            'parent',
]


# Keys that may not be present
# eg video has likes/dislikes disabled
optional_keys = [
   'like_count'
]


# List of illegal characters in filenames. Can be preference as well
illegal_filename_characters = ['/', '\\']

# class JSONParser:
    # def __init__(self):

# Check if the json is malformed (eg from interrupted download)
# Takes in file object
def check_json_complete(file):
    try:
        # print(path)
        # json.dumps(file)
        json.load(file)
        return True
    except (ValueError, TypeError) as e:
        print("ERROR: {}".format(e))
        return False


def parse_json(root_keys, comment_keys, json_dict):
    '''
    Parse out relevant fields and return dict representing parsed json
    '''

    ret_dict = {}

    for key in root_keys:
        # if key == 'comments':
        #     #Store each comment in a dict then append it to root comments list
        #     for comment_key in comment_keys:
        #         print(comment_key)
        # else:
        #

        # NOTE
        # 'full_title' seems to be an alternate keyname for 'fulltitle'
        # seems to be an outlier
        # check if this is the case and modify dictionary to adhere to more common "full_title"
        if key == 'full_title':
            if key not in json_dict and 'fulltitle' in json_dict:
                json_dict['full_title'] = json_dict.pop('fulltitle')
            else:
                print(key)
                print("Title: {} --- URL: {}".format(json_dict['title'], json_dict['webpage_url']))

        # If an optional key isn't present in the json, skip to the next field
        if key not in json_dict and key in optional_keys:
            #print(key)
            #sys.exit()
            continue

        if key in json_dict:
            ret_dict[key] = json_dict[key]
        else:
            print(key)
            print("Title: {} --- URL: {}".format(json_dict['title'], json_dict['webpage_url']))
            #TODO Add function to write these video IDs to separate file
            #sys.exit()


        # Necessary for non-video json files
        # try:
        #     ret_dict[key] = json_dict[key]
        #     print(json_dict['webpage_url'])
        # except KeyError as e:
        #     print(e)
        #     print(json_dict['webpage_url'])
        #     sys.exit()
    return ret_dict


def get_json_value_from_path(json_path, key):
    '''
    Take path to .json file and key
    Return the value of that key in the file
    Return -1 if not found
    '''
    with open(json_path, 'r') as fp:
        return get_json_value(fp, key)

def get_json_value(json_file, key):
    '''
    Get value from a json file object for a given key
    return value if found
    return -1 if not found
    '''
    json_dict = json.load(json_file)

    if key in json_dict:
        return json_dict[key]
    else:
        return -1



def is_channel_json(json_path):
    '''
    Determine if json is for a youtube channel or not
    Uses length of ID to determine this
    return true or false accordingly
    '''
    with open(json_path, 'r') as fp:
        json_dict = json.load(fp)
        if len(json_dict['id']) == 24:
            return True
        else:
            return False


def is_video_json(json_path):
    '''
    Determine if json is for a youtube video or not
    Uses length of ID to determine this
    return true or false accordingly
    '''
    with open(json_path, 'r') as fp:
        json_dict = json.load(fp)
        if len(json_dict['id']) == 11:
            return True
        else:
            return False

def get_video_ids(json_files):
    '''
    Returns a list of youtube video IDs
    Removes channel IDs (and other invalid IDs) based on length
    Valid video IDs are 11 characters long
    '''

    ids = json_files.dump_select_key('id')
    for id in ids:
        if len(id) != 11:
            ids.remove(id)

    return ids


#TODO - Add return boolean return to allow simple error handling
def write_json(json_dict, write_path):
    '''
    Saves json_dict (dictionary representation of parsed video json)
    write_path is the directory to save to
        Normally this should just be save_path from main()
    '''
    #Example my/path/Pewdiepie/videoname/
    write_dir = os.path.join(write_path, json_dict['channel'], '')
    #Example videoname_o23_sz5412p.json
    filename = json_dict['id'] + ".clean.json"

    for c in illegal_filename_characters:
        if c in filename:
            filename = filename.replace(c, '_')

    #Make channel directory if it doesn't exist
    if not os.path.exists(write_dir):
        os.mkdir(write_dir)

    # Will overwrite existing file
    with open(os.path.join(write_dir, filename), 'w') as fp:
        json.dump(json_dict, fp)




if __name__ == '__main__':

    # No arguments passed
    if len(sys.argv) < 2:
        path = os.getcwd()
        save_path = os.path.join(path, save_dir)

    # Check if path to jsons was provided as first argument
    elif len(sys.argv) < 3:
        if os.path.exists(sys.argv[1]):
            path = sys.argv[1]
            save_path = os.path.join(path, save_dir)
        else:
            print("Path does not exist: {}".format(sys.argv[1]))
            sys.exit(1)

    # Else if path to jsons and save path was provided
    elif len(sys.argv) < 4:
        if os.path.exists(sys.argv[1]) and os.path.exists(sys.argv[2]):
            path = sys.argv[1]
            save_path = sys.argv[2]
        elif not os.path.exists(sys.argv[1]):
            print("Path does not exist: {}".format(sys.argv[1]))
            sys.exit(1)
        elif not os.path.exists(sys.argv[2]):
            print("Path does not exist: {}".format(sys.argv[2]))
            sys.exit(1)


    # Creates the save directory if necessary
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    JSONHandler.PRINT_OUTPUT = False
    JSONHandler.JSON_DEBUG = False
    json_files = JSONHandler.JSONHandler()

    json_files.path = path

    json_files.get_files()

    video_ids = get_video_ids(json_files)
    json_list = []
    #Go through each file and verify it's a complete json
    for json_file in json_files.info_files:
        if is_video_json(json_file):
            #Open same file twice to lazily pass one for json format verification
            with open(json_file, 'r') as file, open(json_file, 'r') as filecopy:
                # print(check_json_complete(json_file))
                # if Complete json file, parse it and save parsed json to new file
                if check_json_complete(filecopy):
                    data = json.load(file)
                    json_dict = parse_json(root_keys, comment_keys, data)

                    print("Saving {} as {}...".format(json_file, json_dict['id']))
                    #TODO - Save json dict to new file at save_path
                    write_json(json_dict, save_path)
                    #TODO - Record saved video ID in completed parsed_videos.txt file
                    #TODO - incorporate this parsed_videos.txt file into overall function

                else:
                    #TODO add to broken file for later redownload
                    #NOTE - Perhaps remove from archive directory?
                    #print("Broken")
                    print()

        elif is_channel_json(json_file):
            with open(json_file, 'r') as file, open(json_file, 'r') as filecopy:
                # print(check_json_complete(json_file))
                # if Complete json file, parse it and save parsed json to new file
                if check_json_complete(filecopy):
                    data = json.load(file)
                    json_dict = parse_json(root_keys, comment_keys, data)

                    print("Saving {} as {}...".format(json_file, json_dict['id']))
                    write_json(json_dict, save_path)
