## Note on Classifications

Since the API does not expose the `classification` field the classifications dictionary is built from the csv found at https://github.com/metmuseum/opecaccess. The list is not sanitized in any way other than marking empty entries as N/A.

## Data Coverage

Because of the API limitation and the use of the csv file, there are about 14,000 new records in the database, and some obsolete records in the csv file. For this exercise I've decided to leave it this way, under the assumption that for a production app these additional records can be a fetched incrementally, dealing the with API rate limits.

Records in DB: 498172
Records in local index: 484956
In DB but not local: 14135
In local but not DB: 919
