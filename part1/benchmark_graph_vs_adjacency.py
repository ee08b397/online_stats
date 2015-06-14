import math
import timeit

setup_graph = """
from descendants_graph import graph, get_descendants 
root = graph[0]
"""

setup_adjacency = """
from descendants_adjacency import A_tree, get_descendants_fast 
"""

graph_trials = timeit.repeat(setup=setup_graph, stmt="get_descendants(root)", number=1000000, repeat=5)
adjacency_trials = timeit.repeat(setup=setup_adjacency, stmt="get_descendants_fast(0, A_tree)", number=1000000, repeat=5)

print "Graph: (of 5 trials) max={0}, min={1}, mean={2}".format(max(graph_trials), min(graph_trials), sum(graph_trials)/len(graph_trials)) 
print "Adjacency: (of 5 trials) max={0}, min={1}, mean={2}".format(max(adjacency_trials), min(adjacency_trials), sum(adjacency_trials)/len(adjacency_trials)) 

