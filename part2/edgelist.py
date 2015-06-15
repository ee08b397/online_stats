import igraph
from collections import defaultdict
from collections import deque
import datetime
import random
from blinker import signal 
from mockredis import MockRedis as StrictRedis

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

class Edge(object):
    def __init__(self, parent, child, created_at):
        self.parent = parent
        self.child = child
        self.created_at = created_at
        self.generation = 0

class Tree(object):

    def __init__(self):
        self.name = 'MyTree'
        self.parent_to_child = defaultdict(list) 
        self.child_to_parent = {} 

    def would_be_leaf(self, edge):
        if edge.child in self.parent_to_child:
            return False
        return True

    def is_earliest_parent(self, edge):
        if edge.child not in self.child_to_parent:
            return True
        existing_edge = self.child_to_parent[edge.child]
        if existing_edge.created_at < edge.created_at:
            return False
        return True

    def should_add(self, edge):
        is_leaf = self.would_be_leaf(edge)
        is_earliest = self.is_earliest_parent(edge)
        return all([
            self.would_be_leaf(edge), 
            self.is_earliest_parent(edge)])

    def is_root(self, edge):
        return edge.parent not in self.child_to_parent and edge.parent in self.parent_to_child 

    def get_roots(self):
        roots = []
        for parent, children in self.parent_to_child.items():
            for edge in children:
                if self.is_root(edge):
                    roots.append(edge.parent)
        return roots

    def get_depth(self, root):
        depth = 0
        current_generation = deque([root])
        next_generation = True
        while next_generation:
            next_generation = deque()
            while current_generation:
                node = current_generation.popleft()
                child_edges = self.parent_to_child[node]
                for edge in child_edges:
                    next_generation.append(edge.child)
            depth += 1
            current_generation = next_generation
        return depth

    def get_generation(self, edge):
        if edge.parent in self.child_to_parent:
            ancestor = self.child_to_parent[edge.parent]
            return ancestor.generation + 1
        return 0 

    def add(self, edge):
        self.parent_to_child[edge.parent].append(edge)
        self.child_to_parent[edge.child] = edge
        edge.generation = self.get_generation(edge)
        print "Set generation to", edge.generation

    def get_edgelist(self):
        print "Returning edgelist with {0} parents".format(len(self.parent_to_child))
        for parent, edge in self.parent_to_child.items():
            yield edge.parent, edge.child

def grow_trees(stream):
    tree = Tree()
    edge_added = signal('edge_added')
    roots = 0
    for parent, child, created_at in stream:
        candidate = Edge(parent, child, created_at)
        if tree.should_add(candidate):
            tree.add(candidate)
            if tree.is_root(candidate):
                roots += 1
                edge_added.send('grow_trees', tree_name=tree.name, edge=candidate)
            edge_added.send('grow_trees', tree_name=tree.name, edge=candidate)
    return tree

conn = StrictRedis()

def online_tree_size(sender, tree_name=None, edge=None):
    conn.incr('{0}.size'.format(tree_name)) 
     
def online_tree_depth(sender, tree_name=None, edge=None):
    with conn.lock('{0}.depth'.format(tree_name)):
        current_depth = conn.get('{0}.depth'.format(tree_name)) or 0
        if int(current_depth) < edge.generation:
            conn.set('{0}.depth'.format(tree_name), edge.generation)

signal('edge_added').connect(online_tree_size)
signal('edge_added').connect(online_tree_depth)

datastream = stream(nodes=10)
tree = grow_trees(datastream)

# Calculate depth with bfs 
roots = tree.get_roots()
depth = 0
for root in roots:
    depth = max(depth, tree.get_depth(root))
print "Direct depth", depth

"""
Check online calculations
"""
# Labels the generation of the child, starts at 0.
print "Depth", int(conn.get('MyTree.depth')) + 2 
print "Size", conn.get('MyTree.size')

