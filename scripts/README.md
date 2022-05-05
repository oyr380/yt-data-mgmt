## Description and usage of each script

### Table of Contents
- [metadata_downloader](#metadata_downloaderpy)
  - [How to use](#how-to-use)
  - [Summary](#summary)
  - [Process](#process)
- [JSONParser](#jsonparserpy)
  - [How to use](#how-to-use-1)
  - [Summary](#summary-1)
  - [Process](#process-1)
- [JSONHandler](#jsonhandlerpy)
  - [How to use](#how-to-use-2)
  - [Summary](#summary-2)
- [importer](#importerpy)
  - [How to use](#how-to-use-3)
  - [Summary](#summary-3)
  - [Process](#process-2)

----



### metadata_downloader.py
**Requires** JSONHandler and pandas
#### How to use
`python metadata_downloader.py`
#### Summary
Uses yt-dlp to download channel and video metadata, recording a history of successful downloads.
Modify the script to modify the filenames or change defaults.

#### Process
Checks current working directory for **batch_vids.txt** and downloads each channel/video in the file. Stores successfully downloaded video IDs in **archive.txt**, including those in any directory under the current working directory (recursively).
Will store channel video IDs in a file for future reference to avoid parsing an entire channel again, delete or rename this file to get a fresh skim.

----
### JSONParser.py
#### How to use
**Requires** JSONHandler\
Each argument is optional.\
The directory to store cleaned JSONs into will be created if it doesn't exist\
`python JSONParser <Path to JSON directory to parse> <Directory to store cleaned JSONs in>`

#### Summary
Recursively searches from the current working directory or the provided path for all files ending in **.info.json** and then removes all JSON fields that are not desirable. These cleaned files are stored in cleaned_jsons or the provided path with the suffix **.clean.json**.
The script is not destructive by default and will only overwrite existing **.clean.json** files. This behavior is to satisfy safety while also allowing easy overwrites for any updated JSONs.

#### Process
Recursively searches files from provided path for all .info.json files, cleans them, then writes them to provided cleaned JSON directory, making it if neeeded. Will skip any broken JSON files.
Saves files using the video or channel ID as the filename for simple unique filenames that aren't overly long.
**NOTE** - Editing the script to use the title field may result in filenames that exceed the filename limit. This is not recommended.

----
### JSONHandler.py
#### How to use
Not normally invoked directly, though can be.\
Each argument is optional\
`python JSONHandler.py <key> <extension> <Path to operate from>`

#### Summary
Recursively searches for all keys and file extensions provided from the path provided. By default these are 'id', '.json', and the current working directory.
Incidentally will find all .clean.json and all .info.json files when invoked/declared from the path provided or the current working directory.
It is not recommended to use this directly as it's a helper class.

----
### importer.py
#### How to use
**Requires** pymongo and dnspython and JSONHandler and JSONParser\
Argument optional\
`python importer.py <Path to root directory to search under>`

#### Summary
Recursively searches for .clean.json files and attempts to import them to the MongoDB database prescribed by the global variable **URI**.
Prints out total progress based on number of files to be viewed for import and the total number of successful imports.
Exits on a total failure to recognize a JSON file to allow for review. 

#### Process
Connects to the MongoDB database using the provided URI, queries for all video and channel IDs in the database. Recursively finds all .clean.json files using JSONHandler and parses each file using JSONParser to get the 'id' value, then checks if it's a video or channel JSON and uploads it to the appropriate collection in the database if it's not already in the database.
Counts the number of successful uploads.


