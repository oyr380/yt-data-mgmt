# Large Scale Data Management Project Data Management Repository

### Requirements 
###### note - python3 assumed
#### importer.py
* pymongo
  * pip install pymongo
* dnspython
  * pip install dnspython



---

### Todo
* Find out channel keys we care about

---
### Optional Todo
* refactor downloader script to be tidier
* Optional fancy option is to download only new video information then jump back to the file (time permitting) 


### Done
* Update metadata_downloader to include arguments directly
* Write json parser script to remove unwanted values (cleaning)
* Script finding partial/broken .json files (part of JSONPArser.py atm)
* Write script parse out video ID value. Add IDs to archive.txt file. For creating archive.txt from current downloads
* MongoDB Importer script
* Update metadata_downloader to first parse out all the videoIDs from the channel on youtube and store the IDs in a file
  * Prioritize the file in subsequent downloads (much faster)

