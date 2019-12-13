from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import gensim

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from nltk import pos_tag
import re

import pickle

import numpy as np

import multiprocessing
import multiprocessing.pool

keep = [5, 6, 7, 12, 19, 23, 29]

analyser = SentimentIntensityAnalyzer()
model = gensim.models.ldamodel.LdaModel.load('lda2.model')
for i in keep:
	print(i, model.print_topic(i))
en_stopwords = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# We sub-class multiprocessing.pool.Pool instead of using multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

def get_sentences(text):
	text = text.lower()
	text = re.sub('[\n\'\"]+', '', text)
	text = re.sub('http[s]*[^\s]+', '', text)
	text = re.sub('[@&]\w+', '', text)
	text = re.sub('rt', '', text)
	return re.findall('[^.?!;:]+', text)


# Keep adjectives, nouns, verbs, and adverbs.
keep_pos = {
	'J': wordnet.ADJ,
	'N': wordnet.NOUN,
	'V': wordnet.VERB,
	'R': wordnet.ADV
}
def filter(sentence):
	words = re.split('[\s()\[\],^+*`/]', sentence.strip())
	words = [
		word
		for word in words
		if not word is '' and not word in en_stopwords
	]
	pos = pos_tag(words)
	pos = [
		(pair[0], keep_pos[pair[1][0].upper()])
		for pair in pos
		if pair[1][0].upper() in keep_pos
	] 
	return [
		lemmatizer.lemmatize(pair[0], pair[1])
		for pair in pos
	]

def get_scores(sentence):
	return analyser.polarity_scores(sentence)

def get_topics(sentence):
	words = filter(sentence)
	bow = model.id2word.doc2bow(words)
	return model.get_document_topics(bow)

def get_sentiments(text):
	sentences = get_sentences(text)
	total = np.zeros([4, model.num_topics])
	for sentence in sentences:
		if sentence == '':
			continue
		topics = get_topics(sentence)
		scores = get_scores(sentence)
		for topic in topics:
			i = topic[0]
			if i in keep:
				w = topic[1]
			else:
				w = 0
			total[0][i] += w * scores['neg']
			total[1][i] += w * scores['neu']
			total[2][i] += w * scores['pos']
			total[3][i] += w * scores['compound']
	return total

f = open('word_3_filtered.txt', 'r')

# We need to make sure the times / lines are in order.
# This matters later when we interpolate them into time
# steps and calculate windowed mean / std.
times = []
tToL = {}
print('Reading')
i = 0
for line in f.readlines():
	i = i + 1
	t = re.match('^\d{13}', line)
	if t == None:
		continue
	times.append(t[0])
	if t[0] in tToL:
		tToL[t[0]].append(line[14:])
	else:
		tToL[t[0]] = [line[14:]]
times = np.sort(times)
lines = []
last = 0
for t in times:
	if t == last:
		continue
	last = t
	for line in tToL[t]:
		lines.append(line)

print('Collecting Sentiments')
sentiments = MyPool(32).map(get_sentiments, lines)

print('Writing')
pickle.dump(times, open('times.pck', 'wb'))
pickle.dump(sentiments, open('sentiments.pck', 'wb'))
