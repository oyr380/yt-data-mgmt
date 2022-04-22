#!/bin/env/usr python3

import sys
import os
import json
import JSONHandler

JSON_DEBUG = True
PRINT_OUTPUT = True


#TODO check children videos (eg cocomelon) and music videos (eg eminem)
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
            #'n_entries',
            #'playlist_count',
            #'playlist_index',
            #'playlist',
            #'playlist_id',
            #'playlist_title',
            #'playlist_uploader',
            #'playlist_uploader_id',
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
                sys.exit()

        # If an optional key isn't present in the json, skip to the next field
        if key not in json_dict and key in optional_keys:
            print(key)
            sys.exit()
            continue

        if key in json_dict:
            ret_dict[key] = json_dict[key]
        else:
            print(key)
            print("Title: {} --- URL: {}".format(json_dict['title'], json_dict['webpage_url']))
            sys.exit()


        # Necessary for non-video json files
        # try:
        #     ret_dict[key] = json_dict[key]
        #     print(json_dict['webpage_url'])
        # except KeyError as e:
        #     print(e)
        #     print(json_dict['webpage_url'])
        #     sys.exit()
    return ret_dict



def is_channel_json(json_path):
    if json_path.split('/')[-2] == 'NA':
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
    print(len(ids))
    for id in ids:
        if len(id) != 11:
            ids.remove(id)

    print(len(ids))
    return ids



if __name__ == '__main__':

    # Check if path was provided as first argument
    # Subsequent arguments ignored
    if len(sys.argv) < 2:
        path = os.getcwd()
    else:
        if os.path.exists(sys.argv[1]):
            path = sys.argv[1]
        else:
            print("Path does not exist: {}".format(sys.argv[1]))
            sys.exit(1)

    JSONHandler.PRINT_OUTPUT = False
    JSONHandler.JSON_DEBUG = False
    json_files = JSONHandler.JSONHandler()

    json_files.path = path

    json_files.get_files()

    #JSONHandler.PRINT_OUTPUT = True
    video_ids = get_video_ids(json_files)
    sys.exit()
    json_list = []
    # print(sorted(json_files.files))
    #Go through each file and verify it's a complete json
    for json_file in json_files.files:

        #Skip channel-jsons identifiable via parent directory
        if is_channel_json(json_file):
            continue

        #Open same file twice to lazily pass one for verification
        with open(json_file, 'r') as file, open(json_file, 'r') as filecopy:
            # print(check_json_complete(json_file))
            # if Complete json file, parse it
            if check_json_complete(filecopy):
                data = json.load(file)

                print(json_file)
                print(len(data))
                json_dict = parse_json(root_keys, comment_keys, data)

                #TODO - Save json dict to new file
                #TODO - Record saved video ID in completed parsed_videos.txt file
                #TODO - incorporate this parsed_videos.txt file into overall function

            else:
                #TODO add to broken file for later redownload
                #NOTE - Perhaps remove from archive directory?
                #print("Broken")
                print("")
