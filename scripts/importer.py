#!/usr/bin/env python3

import os
import sys
import json
import JSONHandler
import JSONParser

import dns
from pymongo import MongoClient


JSONHandler.JSON_DEBUG=False
JSONHandler.PRINT_OUTPUT=False

#TODO - delete test URI
URI_TEST = 'mongodb+srv://bigdata:cs4243@cluster0.k5iv2.mongodb.net/project-test'
#URI_TEST = 'mongodb+srv://bigdata:cs4243@cluster0.k5iv2.mongodb.net/project'

def mongo_connect(URI):
    '''
    Connect to mongodb via the URI
    Exit if failed to connet
    '''
    try:
        client = MongoClient(URI_TEST)
    except:
        print("ERROR: Could not connect to database.")
        sys.exit(1)

    print("Connected to database")
    return client

def check_jsons_complete(jsons):
    '''
    Go through each json filepath in a list and check if it's properly formatted
    '''
    for json in jsons:
        with open(json, 'r') as fp:
            if not JSONParser.check_json_complete(fp):
                jsons.remove(json)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        path = os.getcwd()
    else:
        if os.path.exists(sys.argv[1]):
            path = sys.argv[1]
        else:
            print("ERROR: \"{}\" is an invalid path".format(sys.argv[2]))
            sys.exit(1)


    print("Connecting to MongoDB")
    client = mongo_connect(URI_TEST)

    db = client['project-test']
    video_collection = db.videos
    channel_collection = db.channels

    print("Getting list of videos in {} collection".format("videos"))
    database_vids = video_collection.distinct("id")
    print("Getting list of videos in {} collection".format("channels"))
    database_channels = channel_collection.distinct("id")

    vid_dict = dict(zip(database_vids, range(len(database_vids)) ))
    channel_dict = dict(zip(database_channels, range(len(database_channels)) ))

    print("Recursively finding all *.clean.json files under \"{}\"".format(path))
    # Find and store all .clean.json files in list
    jsons = JSONHandler.JSONHandler()
    jsons.path = path
    jsons.get_files()
    clean_jsons = jsons.clean_files
    info_jsons = jsons.info_files

    upload_count = 0

    counter = 0

    total = len(clean_jsons)

    for json_path in clean_jsons:
        val = JSONParser.get_json_value_from_path(json_path, 'id')
        counter += 1

        try:
            if len(val) == 11 or len(val) == 24:
                print("File Progress - {}/{}".format(counter, total))
                #If this is a video json
                #Video IDs are 11 characters long
                if len(val) == 11:
                    video_title = JSONParser.get_json_value_from_path(json_path, 'title')
                    # Upload json to videos collection if video not found
                    # If video is not already in collection, try to import it
                    if val not in vid_dict:
                        with open(json_path, 'r') as fp:
                            json_obj = json.load(fp)
                            try:
                                print("Importing {} into {} collection.".format(video_title, 'videos'))
                                video_collection.insert_one(json_obj)
                            except:
                                print("{} failed to import into {} collection.".format(video_title, 'videos'))
                        print("---------")
                        upload_count +=1

                # If this is a channel json
                elif len(val) == 24:
                    uploader = JSONParser.get_json_value_from_path(json_path, 'id')

                    if val not in channel_dict:
                        with open(json_path, 'r') as fp:
                            json_obj = json.load(fp)
                            try:
                                print("Importing {} into {} collection.".format(uploader, 'channels'))
                                channel_collection.insert_one(json_obj)
                            except:
                                print("{} failed to import into {} collection.".format(uploader, 'channels'))
                        print("---------")
                        upload_count +=1

        except:
            print("ERROR: Failed import")
            print("Does not appear to be channel or video!")
            print("ID: {}".format(val))
            sys.exit(1)


    print("Uploaded {} documents".format(upload_count))
