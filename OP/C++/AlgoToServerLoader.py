import urllib
from urllib import request
from urllib import parse

def push_algo(d):
	s = urllib.parse.urlencode(d)
	return urllib.request.urlopen('http://localhost:8000/algodb/cli/add_algo/' + '?' + s).read()


d = (
	('code', open('Dijkstra.cpp').read()),
	('name', 'Dijkstra'),
	('description', 'dijkstra finds minimalistic way in weighted graf'),
	('category', 'Grafs')
)

push_algo(d)


d = (
	('code', open('Floyd.cpp').read()),
	('name', 'Floyd'),
	('description', 'floyd finds minmal way from all vertices to all vertcies'),
	('category', 'Grafs')
)

push_algo(d)

d = (
	('code', open('Heap.cpp').read()),
	('name', 'Heap'),
	('description', 'Heap pop min elem, add elem, log(n)'),
	('category', 'Data Structure')
)

push_algo(d)
