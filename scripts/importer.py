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



    print("Recursively finding all *.clean.json files under \"{}\"".format(path))
    # Find and store all .clean.json files in list
    jsons = JSONHandler.JSONHandler()
    jsons.path = path
    jsons.get_files()
    clean_jsons = jsons.clean_files
    info_jsons = jsons.info_files

    count = 0
    for json_path in clean_jsons:
        val = JSONParser.get_json_value_from_path(json_path, 'id')
        video_title = JSONParser.get_json_value_from_path(json_path, 'title')
        # Upload json to videos collection if video not found
        if not video_collection.find_one({'id':val}):
            with open(json_path, 'r') as fp:
                json_obj = json.load(fp)
                try:
                    print("Importing {} into {} collection.".format(video_title, 'videos'))
                    video_collection.insert_one(json_obj)
                except:
                    print("{} failed to import into {} collection.".format(video_title, 'videos'))
            print("---------")
            count +=1

    print("Uploaded {} documents".format(count))
