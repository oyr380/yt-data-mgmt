#!/bin/env/usr python3

import sys
import os
import json

JSON_DEBUG = False
PRINT_OUTPUT = True

#python3 JSONHandler.py <key> <path>
class JSONHandler:
    def __init__(self):
        self.files = []
        #path is second arg
        if len(sys.argv) < 3:
            self.path = os.getcwd()
        else:
            if os.path.exists(sys.argv[2]):
                self.path = sys.argv[2]
            else:
                print('ERROR: "{}" is an invalid path'.format(sys.argv[2]))
                sys.exit()
        if len(sys.argv) < 2:
            self.key = 'id'
        else:
            self.key = sys.argv[1]

        self.get_files()

        if JSON_DEBUG:
            print("JSON HANDLER:\nKEY: {}\nPATH: {}".format(self.key, self.path))
            for each in self.files:
                print(each)



    def get_files(self):
        for subdir, dirs, files in os.walk(self.path):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filename.lower().endswith('.json'):
                    self.files.append(filepath)

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


if __name__=='__main__':
    JSONHandler().dump_keys()
