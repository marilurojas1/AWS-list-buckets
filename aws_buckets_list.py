#This Python tool will list the buckets in a AWS account.
#It requires the installtion of the SDK for Python https://aws.amazon.com/sdk-for-python/
#and to setup your environment credentials  https://github.com/boto/boto3
#It will list: Bucket name, Creation date of the bucket, Number of files in the bucket, total size of the files,
#last modified date (most recent file of a bucket) and how much it cots per month the bucket.

#The source code is based on this examples:
#https://github.com/aws-samples/aws-python-sample/blob/master/s3_sample.py
#https://alexwlchan.net/2018/01/listing-s3-keys-redux/
#It requireds the installation of pytz library to manage datetimes.

import sys
import argparse
import boto3
import datetime
import pytz


#define a class to store buckets results
class bucket_results:
     """__init__() functions as the class constructor"""
     def __init__(self):
        self.bucket_name = ''
        self.creation_date = ''
        bucket_location = ''
        self.size_bytes = ''
        self.last_modified_file = ''
        self.number_of_files = ''
        self.cost_bucket = ''

#convet bytes to human readable
def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


#As per defined in her https://aws.amazon.com/s3/pricing/
def pricing(price):
    return {
        'GLACIAR': 0.005,
        'STANDARD_IA': 0.019,
        'ONEZONE': 0.0152,
        'REDUCER_REDUNDANCY': 02
    }.get(price, .025)


#Retreieve objects in bucket
def get_matching_s3_objects(bucket, prefix='', suffix=''):
    """
    Generate objects in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)

        try:
            contents = resp['Contents']
        except KeyError:
            return

        for obj in contents:
            key = obj['Key']

            if key.startswith(tuple(prefix)) and key.endswith(tuple(suffix)):
                yield obj
        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def get_matching_s3_keys(bucket, prefix='', suffix='', size='', cost='', total_files='', latest_file_modified=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        if  obj['LastModified'] > latest_file_modified:
            latest_file_modified = obj['LastModified']
        storage_class = obj['StorageClass'] 
        yield latest_file_modified
        #yield obj['StorageClass']
	size += obj['Size']
        yield size
        price = pricing(price=storage_class)
        cost += (obj['Size']/1000000000.0) * price  #size converted to GB to get the cost
        yield cost
        total_files += 1
        yield total_files


#Retrieving all the buckets
def list_buckets(prefix='', suffix=''):
   buckets_resultList = []
   s3client = boto3.client('s3')
   list_buckets_resp = s3client.list_buckets()
   for buckets in list_buckets_resp['Buckets']:
       bucket_location = s3client.get_bucket_location(Bucket=buckets['Name'])
       objects = list(get_matching_s3_keys(bucket=buckets['Name'], prefix=prefix, suffix=suffix, size=0, cost=0.0, total_files=0,
                      latest_file_modified = datetime.datetime(1970, 01, 01, 00, 00, 00, 0, pytz.UTC)))
       data =  bucket_results()
       data.bucket_name = buckets['Name']
       data.creation_date =  buckets['CreationDate']
       data.bucket_location = bucket_location['LocationConstraint']
       if not objects: #This information is stored in case no parameters are given , then it will list all the buckets, including the empty ones.
              data.last_modified_file = ''
              data.size_bytes = 0
              data.number_of_files = 0
              data.cost_bucket = 0
       if objects:
          data.last_modified_file = objects[-4]
          data.size_bytes =  objects[-3]
          data.cost_bucket = objects[-2]
          data.number_of_files = objects[-1]
       buckets_resultList.append (data)
   return(buckets_resultList)



def main(argv):
#If a prefix or suffix is passed, it will print only the buckets that match the criteria, else it will print all the buckets, even the empty ones.
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", default=[''], help="Setting a prefix to list objects in a specific path, eg: -p folder/SubFolder/log")
    parser.add_argument("-sx", "--suffix", default=[''], help="setting a suffix for type of objects to retrieve, '-sx .png' '-sx .png .txt' ")
    parser.add_argument("-s", "--sort_by", default='', help="Sort the results, valid options are: size, location, total_files, date and cost. An invalid option will be ignored ")
    args = parser.parse_args()
    buckets_list=list_buckets(args.prefix,args.suffix)
    bucket_results = buckets_list
    if args.sort_by == 'size':
       bucket_results  = sorted(buckets_list, key=lambda size: size.size_bytes)
    if args.sort_by == 'location':
       bucket_results  = sorted(buckets_list, key=lambda location: location.bucket_location)
    if args.sort_by == 'total_files':
       bucket_results  = sorted(buckets_list, key=lambda files: files.number_of_files)
    if args.sort_by == 'date':
       bucket_results  = sorted(buckets_list, key=lambda date: date.creation_date)
    if args.sort_by == 'cost':
       bucket_results  = sorted(buckets_list, key=lambda cost: cost.cost_bucket)
    for bucket in bucket_results:
        if  bucket.size_bytes == 0 and args.prefix==[''] and args.suffix==['']: 
            print('name:{}, creation:{}, location: {}, Bucket is emtpy!!!'.
                  format(bucket.bucket_name, bucket.creation_date, bucket.bucket_location))
        if bucket.size_bytes > 0:
             print('name:{}, creation:{}, location: {}, size:{}, files:{}, last modified:{},cost: {}'
                   .format(bucket.bucket_name, bucket.creation_date, bucket.bucket_location, sizeof_fmt(bucket.size_bytes), bucket.number_of_files,bucket.last_modified_file,bucket.cost_bucket))

if __name__== "__main__":
  main(sys.argv)
