# Large Scale Data Management Project Data Management Repository

## Table of Contents
- [Requirements](#requirements)
- [Overview](#overview)
- [How to use](#how-to-use)
- [TODO](#todo)
- [Done](#done)




### Requirements 
Scripts were primarily run in Linux environments, including WSL 2.0, though were also used on Windows 10 and should work on Windows 10+.

* Reliable internet connection
* Python 3
  * dnspython
  * pymongo
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) installed and in current path/environment.
* [MongoDB](https://mongodb.com/) with two collections named *videos* and *channels* and write access

### Overview
This is part of a project used to collect, clean, analyze, and present over 10GB of data. Over 40GB of YouTube data was downloaded and over ~20GB of data has been cleaned uploaded to the directory across at least 5 separate devices. 
The MongoDB database used has over **14GB** of data **after compression** with over **140,000** documents representing individual data or channel data in the database.
![image](https://user-images.githubusercontent.com/90591648/166892693-c56d4fc1-6867-4681-9656-7292183c6883.png)

MongoDB indexing was used to maintain query performance for relevant queries presented from the website. Queries on exceptionally large channels would take up to a minute but should now take less than 1 second.

#### JSONHandler.py and JSONParser.py
Both use native Python libraries.

#### importer.py
* pymongo
  * pip install pymongo
* dnspython
  * pip install dnspython
* JSONHandler.py (above)
* JSONParser.py (above)

#### metadata_downloader.py
* JSONHandler.py (above)
* [pandas](https://pandas.pydata.org/)
  * pip install pandas
----

### How To Use
General workflow is as follows
1. `python metadata_downloader.py`
    - Reads a file (batch_vids.txt by default) and downloads metadata from Youtube for channels/videos in file. Overwrites partial/incomplete JSON files.
    - Defaults to sorting comments by "top" (as determined by YouTube) and downloading a maximum of 10,000 comments per video
2. `python JSONParser.py`
    - Cleans data and stores in directory (cleaned_jsons by default) with suffix ".clean.json". Skips partial/incomplete JSON files
3. `python importer.py`
    - Find all .clean.json files (from previous step) and import them into MongoDB database (provide URI for DB access)
    - Uses video/channel ID to determine if a JSON is already recorded in the database. To re-import, remove that ID from the database manually.

The scripts do the heavy lifting by default. For custom/advanced use, check the README in the scripts directory.
Each script is designed to pick up where it last left off where possible, avoiding duplicating efforts and saving time.

---

### Todo 
These are features we'd like to implement, time permitting.
* Log failed imports to file 
* Shrink JSONs too big for database by truncating comments
  * Ideally this would get as close to a target size (16MB) as possible 

---

### Done
Successfully implemented features
* Update metadata_downloader to include arguments directly
* Write json parser script to remove unwanted fields (cleaning)
 * Add option for limiting comment count and sort by top comments (reduce filesize)
* Script finding partial/broken .json files (part of JSONPArser.py)
* Write script parse out video ID value. Add IDs to archive.txt file. For creating archive.txt from current downloads
* MongoDB Importer script
* Importer script runs 1 query per collection for verification
* Get Channel json files
* Update metadata_downloader to first parse out all the videoIDs from the channel on youtube and store the IDs in a file
  * Prioritize the file in subsequent downloads (much faster)

