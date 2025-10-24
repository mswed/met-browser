## Classifications

Since the API does not expose the `classification` field the classifications dictionary is built from the csv found at https://github.com/metmuseum/opecaccess. The list is not sanitized in any way other than marking empty entries as N/A.

### Data Coverage

Because of the API limitation and the use of the csv file, there are about 14,000 new records in the database, and some obsolete records in the csv file. For this exercise I've decided to leave it this way, under the assumption that for a production app these additional records can be a fetched incrementally, dealing the with API rate limits.

Records in DB: 498172
Records in local index: 484956
In DB but not local: 14135
In local but not DB: 919

## Images

I could not find clear documentation on how to fetch all of the records that have an image. It seems like it should be straight forward as the API offers a `hasImages` parameter on the search endpoint. However it must be accompanied with a `q` parameter as well, and a `*` wildcard does not seem to get all of the records.

I have decided to iterate over the alpahbet and save all found record ids in a local cache that can be updated by the user. While it's unclear how much of the records with images it finds, this method finds 348,803 records which is offers a coverage of ~70%

A secondary issue, is that while the API returns records that are supposed to have an image, if the image is marked as not in the public domain, the image url is not provided.In these cases and additional client side filter is applied removing the records without an image and updating the count to be "approximate".
