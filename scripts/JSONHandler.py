#!/bin/env/usr python3

import sys
import os
import json

JSON_DEBUG = True
PRINT_OUTPUT = True

#python3 JSONHandler.py <key> <ext> <path>
class JSONHandler:
    def __init__(self):
        self.info_files = []
        self.clean_files = []
        if len(sys.argv) < 4:
            self.path = os.getcwd()
        else:
            if os.path.exists(sys.argv[3]):
                self.path = sys.argv[3]
            else:
                print('ERROR: "{}" is an invalid path'.format(sys.argv[3]))
                sys.exit()
        #path is second arg
        if len(sys.argv) < 3:
            self.ext = '.json'
        else:
            self.ext = sys.argv[2]
        if len(sys.argv) < 2:
            self.key = 'id'
        else:
            self.key = sys.argv[1]

        self.get_info_files()

        if JSON_DEBUG:
            print("JSON HANDLER:\nKEY: {}\nPATH: {}".format(self.key, self.path))
            for each in self.files:
                print(each)



    def get_files(self):
        for subdir, dirs, files in os.walk(self.path):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filename.lower().endswith('.info.json'):
                    self.info_files.append(filepath)
                if filename.lower().endswith('.clean.json'):
                    self.clean_files.append(filepath)

    def dump_keys(self):
        ret = []
        for each in self.files:
            fp = open(each)
            data = json.load(fp)
            if self.key in data:
                val = (each, self.key, data.get(self.key))
                ret.append(val)
                if PRINT_OUTPUT:
                    print(val)
            fp.close()


    def dump_select_key(self, key):
        ret = []
        for each in self.files:
            fp = open(each)
            data = json.load(fp)
            if key in data:
                val = data.get(key)
                ret.append(val)
                if PRINT_OUTPUT:
                    print(val)
            fp.close()

        return ret

    # Yoinked from JSONParser.py for consolidation
    def check_json_complete(self, file):
        '''
        Check if the json is malformed (eg from interrupted download)
        Takes in file object
        '''
        try:
            json.load(file)
            return True
        except (ValueError, TypeError) as e:
            print("ERROR: {}".format(e))
            return False

if __name__=='__main__':
    JSONHandler().dump_keys()
