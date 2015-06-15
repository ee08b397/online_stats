import igraph
import datetime
import random

def stream(nodes=1000):
    now = datetime.datetime.now()
    graph = igraph.Graph.Tree(n=nodes, children=1)
    print "Diameter", graph.diameter()
    if not graph.is_connected():
        raise Exception("Graph was disconnected.")
    for parent, child in graph.get_edgelist():
        yield parent, child, now - datetime.timedelta(seconds=random.randint(1, 24 * 60 * 60)) 

    """
    # Now make some problems:
    for i in xrange(100):
        parent, child = random.randint(0, nodes), random.randint(0, nodes)
        if parent != child:
            yield parent, child, now - datetime.timedelta(seconds=random.randint(1, 24 * 60 * 60))
    """

def stream(nodes=1000):
    """
    0
    |
    1___2___3
        |   |
        4   5___
            |   |
            6   7
    """
    edgelist = ((0,1),(1,2),(2,4),(2,3),(3,5),(5,6),(5,7))
    for parent, child in edgelist:
        yield parent, child, datetime.datetime(2012, 5, 18) 
