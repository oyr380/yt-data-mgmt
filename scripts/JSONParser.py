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
            'n_entries',
            'playlist_count',
            'playlist_index',
            'playlist',
            'playlist_id',
            'playlist_title',
            'playlist_uploader',
            'playlist_uploader_id',
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


# class JSONParser:
    # def __init__(self):

# Check if the json is malformed (eg from interrupted download)
def check_json_complete(path):
    try:
        json.loads(path)
        return True
    except ValueError as e:
        print("ERROR: {}".format(e))
        print("Malformed JSON: {}".format(path))
        return False




if __name__ == '__main__':
    json_files = JSONHandler.JSONHandler()
    #json_files.PRINT_OUTPUT = False
    json_files.get_files()
    #json_files.dump_keys()

    json_list = []
    # print(sorted(json_files.files))
    #Go through each file and verify it's a complete json
    for json_file in json_files.files:
        with open(json_file, 'r') as file:
            print(check_json_complete(json_file))
#            data = json.load(file)
#            for key in root_keys:
#                if key == 'comment':
