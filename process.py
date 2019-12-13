import tarfile
import bz2
import zipfile
import os
import nltk
from pprint import pprint
import json
from shutil import rmtree
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from multiprocessing import Pool

root = '/media/standard/DATA/twitter'
wdir = 'working'
 
en_stopwords = stopwords.words('english')
stemmer = PorterStemmer()

def xmkdir(d):
	if os.access(d, os.F_OK):
		rmtree(d)
	os.mkdir(d)

keywords = [
	'energy',
	'renewable',
	'solar',
	'power ',
	'nuclear',
	'hydro',
	'pollution',
	'geothermal',
	'coal ',
	'electric vehicle',
	' ev '
	'biofuels',
	'co2',
	'co 2',
	'carbon dioxide',
	'waste',
	'greenhouse'
]
def run(args):
	file = args[0]
	dest = args[1]

	print(f'FILTERING {file}')

	tar = tarfile.open(
		name = file,
		mode = 'r:'
	)

	pid = os.getpid()
	wd = f'{wdir}/{pid}'

	# Get a clean working directory
	xmkdir(wd)

	try:
		tar.extractall(wd)
	except tarfile.ReadError:
		pass
	tar.close()

	out = open(dest, 'w')
	seen = {}
	total = 0
	not_loadable = 0
	not_english = 0
	deleted = 0
	bad_form = 0
	duplicates = 0
	non_ce = 0
	processed = 0
	for r, dirs, files in os.walk(wd):
		for file in files:
			filename = os.path.join(r, file)
			try:
				for line in bz2.open(filename, mode='r'):
					total = total + 1
					try:
						post = json.loads(line)
					except:
						not_loadable = not_loadable + 1
						print(f"Couldn't parse line in {filename}")
						continue

					if 'lang' in post:
						if post['lang'] != 'en':
							not_english = not_english + 1
							continue
					elif 'delete' in post:
						deleted = deleted + 1
						continue
					else:
						bad_form = bad_form + 1
						continue

					# Many posts seem to be duplicates
					key = post['id_str']
					if key in seen:
						duplicates = duplicates + 1
						continue
					seen[key] = True

					txt = post['text'].lower()
					cont = False
					for pat in keywords:
						if pat in txt:
							cont = True
							break
					if not cont:
						non_ce = non_ce + 1
						continue

					if 'timestamp_ms' in post:
						out.write(post['timestamp_ms'])
					elif 'created_at' in post:
						out.write(post['created_at'])
					out.write(' ' + txt.replace('\n', '\t') + '\n')
					processed = processed + 1
			except EOFError: pass
			except PermissionError: pass
	out.write('\n' + ' '.join([
		str(total),
		str(not_loadable),
		str(not_english),
		str(deleted),
		str(bad_form),
		str(duplicates),
		str(non_ce),
		str(processed)
	]))
	out.close()
	rmtree(wd)

if __name__ == '__main__':
	xmkdir(wdir)
	todo = []
	for year in [2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012]:
		for file in os.listdir(f'{root}/{year}'):
			prefix, ext = os.path.splitext(file)
			dest = f'{root}/keywords_3/{year}/{prefix}.txt'
			if os.access(dest, os.F_OK):
				print(f'CACHED @{dest}')
				continue
			todo.append([f'{root}/{year}/{file}', dest])
	Pool(32).map(run, todo)
	rmtree(wdir)