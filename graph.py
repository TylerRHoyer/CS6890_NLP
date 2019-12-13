import igraph
import re
import json
from math import log
import numpy as np
from graph_tool.all import *
from graph_tool.flow import min_cut

# If anyone ever reads this, good luck running this!
# I wouldn't recommend it. It takes roughly 120ish GB
# of RAM. Yes, RAM. Second, the mincut method didn't
# yield very nice results. Probabilities need to be
# multiplied, not added together. You can use
# logerithmic weights -- but you also need to find the
# maximum cuts, not the minimum cuts. Inverting the
# weights led to issues as well... I'd recommend
# following a published paper for keyword
# identification.

# Who am I kidding, who else has terrabytes of HD
# space and 120 GB of ram on their personal computer?

def make_graph():
	num_vert = 0
	index = {}
	names = []
	edges = []
	weights = []

	print('opening')
	f = open('cor_2019.ncol', 'r')

	print('reading')
	for line in f.readlines():
		try:
			words = line.split(' ')
			a = words[0]
			b = words[1]
			w = int(words[2])
			if not a in index:
				index[a] = num_vert
				names.append(a)
				num_vert += 1
			if not b in index:
				index[b] = num_vert
				names.append(b)
				num_vert += 1
			edges.append((index[a], index[b]))
			weights.append(w)
		except ValueError:
			print('Bad line: ')
			print(line)
	print('closing')
	f.close()

	g = Graph()
	print('adding verts')
	g.add_vertex(len(names))
	g.add_edge_list(edges)
	g.new_vertex_property('string', vals=names)
	g.new_edge_property('float', vals=weights)
	print('saving')
	g.save('keywords_2019.gt')
	print('done')

def load_graph(location):
	g = load_graph(location)
	return g

def cut(g, word):
	if not g.vs(name=word):
		print('That keyword does not exist in this graph')
		return g
	c = g.mincut()
	c0 = c.subgraph(0)
	c1 = c.subgraph(1)
	if c0.vs(name=word):
		return c0
	else:
		return c1

print('loading graph')
g = load_graph('keywords_2019.gt')
saved = False
while True:
	print('Num Nodes: ')
	l = len(g.vs)
	print(l)
	n = int(input('What would you like to do: '))
	if n == 0:
		word = input('key word?: ')
		costs = np.zeros(l)
		total = 0
		for i in range(l):
			cut = g.st_mincut(word, i, capacity='weight')
			costs[i] = cut.value
			total += cut.value
			if i % 10 == 0:
				print(i / l)
		avg = total / l
		print(f'total cost: {total}, average: {avg}')
		m = float(input('min cost?: '))

		g.delete_vertices([i for i, v in enumerate(costs) if v < m])
	elif n == 1:
		for name in g.vs['name']:
			print(name)
	elif n == 2:
		try:
			filename = input('Where to save?: ')
			g.write(filename, format='ncol')
			saved = True
		except Exception:
			print('Failed to save')
	elif n == 3:
		if saved:
			break
		else:
			print('Not saved, select option 4 to skip save')
	elif n == 4:
		saved = True
	elif n == 5:
		print('opening json')
		f = open('totals_2019.json')
		print('loading json')
		w = json.load(f)
		print('converting')
		g.as_directed(mutual=True)
		print('editing')
		for e in g.es:
			e['weight'] = log(e['weight'] / w['occ'][g.vs[e.target]['name']])
	elif n == 6:
		igraph.plot(g)