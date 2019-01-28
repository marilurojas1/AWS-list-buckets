# AWS-list-buckets
This tool is a shell command line utility that will return information over all S3 buckets in an Amazon account

# Requirements:
-	AWS Python SDK: https://aws.amazon.com/sdk-for-python/
-	Setup your AWS environment credentials  https://github.com/boto/boto3
-	ptyz Python library in your environment to handle dates information: pip install pytz

# What information is returned

-	Bucket name
-	Creation date of the bucket
- 	Number of files within a bucket
- 	Total size of files in the bucket

	If a prefix or suffix is given, it will only return information for the buckets that match the condition; otherwise, it will print the whole list of buckets in the account, including the ones that are empty.
- 	Last modified date (most recent file of a bucket)

- 	An estimated of the cost for the buckets that are being retrieved. 
	The cost is based on the current prices listed in here https://aws.amazon.com/s3/pricing/ as 27th January, 2019. 
	Note that for price for S3 Standard Storage is based on the price of the first 50 TB / Month.
- 	The total size of files is listed in bytes, KB, MB, ...

# Optional arguments that can be given to the tool
-	-p PREFIX, --prefix PREFIX:

	Setting a prefix to list objects in a specific path, folder/SubFolder/log. It will look for all the folders that will match the path and objects that start with log*
	
-	-sx SUFFIX, --suffix SUFFIX:
  
	Setting a suffix for type of objects to search in the bucket, example '.png,.txt'
  
-	-s SORT_BY, --sort_by SORT_BY
  	
	By default, the buckest are retrieved in alphabetic order by default, so if the this option, eg. --sort_by size, is not used, the results will be listed in this order.
                        
	To sort the bucket results, the valid options are: 
	
	'size': Sort the results by size of buckets. 
	
	'location': Sort the results by bucket's location. A side note, if the bucket is created via the AWS web interface, the location is retrieve by 'None'. This seems to be a bug on AWS :-)
	
	'total_files': Sort the results by the number of files in the bucket.
	
	'date': Sort the results by creation date of a bucket.
	
	'cost': Sort the results by the cost of the bucket.
	
	If an invalid option is provided for this option, it ignore the option given and it will print the results in the default alphabetical order.
	
	# Tests
		python aws_buckets_list.py
		name:marrojas, creation:2019-01-16 02:44:05+00:00, location: ca-central-1, size:1.7MB, files:15, last modified:2019-01-27 19:32:33+00:00,cost: 3.3225097e-05
		name:marrojas1, creation:2019-01-22 03:04:49+00:00, location: ap-northeast-1, size:2.4KB, files:1, last modified:2019-01-26 22:59:54+00:00,cost: 6.075e-08
		name:testmarbucket, creation:2019-01-18 12:12:56+00:00, location: ca-central-1, size:1.8MB, files:13, last modified:2019-01-27 04:42:42+00:00,cost: 4.4758318e-05
		name:tmp-mar, creation:2019-01-27 18:52:27+00:00, location: None, Bucket is emtpy!!!
		name:tmp2mar, creation:2019-01-27 18:58:50+00:00, location: None, Bucket is emtpy!!!
		name:us-bucket-mar, creation:2019-01-22 16:05:57+00:00, location: None, Bucket is emtpy!!!
		name:us-bucket-mar1, creation:2019-01-22 16:25:43+00:00, location: us-east-2, Bucket is emtpy!!!
		
				
		python aws_buckets_list.py -sx png,txt
		name:marrojas, creation:2019-01-16 02:44:05+00:00, location: ca-central-1, size:1.7MB, files:10, last modified:2019-01-27 19:32:33+00:00,cost: 3.3082922e-05
		name:testmarbucket, creation:2019-01-18 12:12:56+00:00, location: ca-central-1, size:1.6MB, files:6, last modified:2019-01-26 22:57:53+00:00,cost: 4.0504125e-05


		python aws_buckets_list.py -sx .png,txt.py  -s size
		name:tmp-mar, creation:2019-01-27 18:52:27+00:00, location: None, size:7.1KB, files:1, last modified:2019-01-28 00:22:27+00:00,cost: 1.78425e-07
		name:testmarbucket, creation:2019-01-18 12:12:56+00:00, location: ca-central-1, size:1.6MB, files:7, last modified:2019-01-27 04:42:42+00:00,cost: 4.057715e-05
		name:marrojas, creation:2019-01-16 02:44:05+00:00, location: ca-central-1, size:1.7MB, files:11, last modified:2019-01-27 19:32:33+00:00,cost: 3.3122047e-05


		python aws_buckets_list.py -p folder/SubFolder/log
		name:marrojas, creation:2019-01-16 02:44:05+00:00, location: ca-central-1, size:1.1KB, files:3, last modified:2019-01-27 19:32:33+00:00,cost: 2.7675e-08



	# To be completed/improved:
	
-	This tool will test your patience as multithread processing it's not working as expected :-(
-	Since folders are considered as objects, those are included in the total files...  for now
-	The prefix format it passed as: /folder/inside_folder/obj, this need to be adapted to a better format such as: s3//mybucket/folder/inside_folder/obj
