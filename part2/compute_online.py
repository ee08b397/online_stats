from blinker import signal
from mockredis import MockRedis as StrictRedis

from tree import Tree, Edge
from stream import stream

"""
This is the process that consumes from the stream, dispatching edges as well as growth statistics.

`Tree` represents the database interface. We 'fire' growth statistics using blinker.signal. 
"""
def grow_trees(stream):
    tree = Tree()
    node_added = signal('node_added')
    for parent, child, created_at in stream:
        candidate = Edge(parent, child, created_at)
        if tree.should_add(candidate):
            tree.add(candidate)
            if tree.is_root(candidate):
                node_added.send('grow_trees', tree_name=tree.name, edge=candidate) 
            node_added.send('grow_trees', tree_name=tree.name, edge=candidate)
    return tree

"""
In this case we use a "redis cache" (mock redis) to aggregate our stats. Redis provides the required atomicity, 
but you may want something else for production (see redis' persistence features, AOF vs RDB)
"""
conn = StrictRedis()

def online_size(sender, tree_name=None, edge=None):
    conn.incr('{0}.size'.format(tree_name)) 
     
def online_depth(sender, tree_name=None, edge=None):
    with conn.lock('{0}.depth'.format(tree_name)):
        current_depth = conn.get('{0}.depth'.format(tree_name)) or 0
        if int(current_depth) < edge.generation:
            conn.set('{0}.depth'.format(tree_name), edge.generation)

"""
Subscribe our online methods to the node_added event.
"""
signal('node_added').connect(online_size)
signal('node_added').connect(online_depth)

"""
Start the stream and grow the tree(s)!
"""
datastream = stream(nodes=10)
tree = grow_trees(datastream)

"""
Well... We can't have absolutely zero tests....
"""
roots = tree.get_roots()
depth = 0
for root in roots:
    depth = max(depth, tree.get_depth(root))

"""
Check online calculations
"""
# Labels the generation of the child, starts at 0, hence the +2.
print "Online Depth", int(conn.get('MyTree.depth')) + 2 
assert int(conn.get('MyTree.depth')) + 2 == depth
print "Online Size", conn.get('MyTree.size')

