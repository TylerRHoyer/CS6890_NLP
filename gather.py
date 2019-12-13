from urllib import request
from calendar import monthrange
from os import path

root = '/media/standard/DATA/twitter'

def download(url, file):
	if path.exists(file):
		print(f'CACHED "{url}" @ "{file}"')
	else:
		try:
			print(f'GET "{url}"')
			request.urlretrieve(url, file)
		except:
			print(f'FAILED "{url}"')

def days(year, month):
	return range(1, monthrange(year, month)[1] + 1)
# Stopped using zip files

# year = 2019
# for month in range(1, 9):
# 	for day in days(year, month):
# 		download(
# 			f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/twitter_stream_{year}_{month:02}_{day:02}.tar',
# 			f'{root}/{year}/{month:02}_{day:02}.tar')

# year = 2018

# # Late April 2018 the archive team switched to a new format for storage.
# # Before the 24th, each month had one tar file. Afterwards, there was one per a day.
# # Also, Nov and Dec marked the beginning of using underscores instead of hyphens in the file name.

# # Download the monthly tar files
# for month in range(1, 5):
# 	download(
# 		f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/archiveteam-twitter-stream-{year}-{month:02}.tar',
# 		f'{root}/{year}/{month:02}.tar')

# Download the daily files (including those from late April)
# for month in range(4, 11):
# 	for day in days(year, month):
# 		download(
# 			f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/twitter-{year}-{month:02}-{day:02}.tar',
# 			f'{root}/{year}/{month:02}_{day:02}.tar')

# # begin using hyphins and remove archiveteam from url
# for month in range(11, 13):
# 	for day in days(year, month):
# 		download(
# 			f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/twitter_stream_{year}_{month:02}_{day:02}.tar',
# 			f'{root}/{year}/{month:02}_{day:02}.tar')

# year = 2017
# for month in range(1, 7):
# 	download(
# 		f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/archiveteam-twitter-stream-{year}-{month:02}.tar',
# 		f'{root}/{year}/{month:02}.tar')

# for month in range(7, 12):
# 	for day in days(year, month):
# 		download(
# 			f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/twitter-stream-{year}-{month:02}-{day:02}.tar',
# 			f'{root}/{year}/{month:02}_{day:02}.tar')

# December's data was lumped together with november
# year = 2017
# month = 12
# for day in days(year, month):
# 	download(
# 		f'https://archive.org/download/archiveteam-twitter-stream-{year}-11/twitter-stream-{year}-12-{day:02}.tar',
# 		f'{root}/{year}/{month:02}_{day:02}.tar')

# for year in range(2012, 2017):
# 	for month in range(1, 13):
# 		download(
# 			f'https://archive.org/download/archiveteam-twitter-stream-{year}-{month:02}/archiveteam-twitter-stream-{year}-{month:02}.tar',
# 			f'{root}/{year}/{month:02}.tar')

# year = 2011
# for month in range(9, 13):
# 	for day in days(year, month):
# 		download(
# 			f'https://archive.org/download/archiveteam-json-twitterstream/twitter-stream-{year}-{month:02}-{day:02}.zip',
# 			f'{root}/{year}/{month:02}_{day:02}.zip')