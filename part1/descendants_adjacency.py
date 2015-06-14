from scipy.sparse import coo_matrix
from collections import deque

"""
Fully connected, directed tree.
0___
|   |
1   2___
    |   |
    3   4
        |
        5
"""
A_as_list = [  # 0, 1, 2, 3, 4, 5
                [0, 1, 1, 0, 0, 0], # 0 
                [0, 0, 0, 0, 0, 0], # 1
                [0, 0, 0, 1, 1, 0], # 2
                [0, 0, 0, 0, 0, 0], # 3
                [0, 0, 0, 0, 0, 1], # 4
                [0, 0, 0, 0, 0, 0]  # 5
    ]

A = coo_matrix(A_as_list, dtype='int8')
A_tree = A # We're going to import this later

def get_descendants(node, A, descendants=None):
    if not descendants:
        descendants = [] 
    
    descendants.append(node)

    children = A.getrow(node).indices 
    for child in children:
        descendants += get_descendants(child, A)

    return descendants

def get_descendants(node, A):
    unexplored = deque([node])
    descendants = set()
    while unexplored:
        node = unexplored.popleft()
        descendants.add(node)
        children = A.getrow(node).indices
        for child in children:
            unexplored.append(child)

    return descendants

def get_descendants(node, A):
    unexplored = deque([node])
    while unexplored:
        node = unexplored.popleft()
        yield node
        children = A.getrow(node).indices
        for child in children:
            unexplored.append(child)

get_descendants_fast = get_descendants

"""
Fully connected, directed graph with cycles 
0___
|   |
1   2___
    ^   v
    3<__4
        |
        5
"""
# Note: pysparse contains a sparse symmetric matrix implementation. Not shown here
# for consistency of the interface.
A_as_list = [  # 0, 1, 2, 3, 4, 5
                [0, 1, 1, 0, 0, 0], # 0 
                [0, 0, 0, 0, 0, 0], # 1
                [0, 0, 0, 0, 1, 0], # 2
                [0, 0, 1, 0, 0, 0], # 3
                [0, 0, 0, 1, 0, 5], # 4
                [0, 0, 0, 0, 0, 0]  # 5
]

A = coo_matrix(A_as_list, dtype='int8') 

def get_descendants(node, A, descendants=None):
    if not descendants:
        descendants = set() 
    
    descendants.add(node)

    children = A.getrow(node).indices 
    for child in children:
        if child not in descendants:
            descendants = descendants.union(get_descendants(child, A, descendants))

    return descendants

def get_descendants(node, A, descendants=None):
    unexplored = deque([node])
    descendants = set()
    while unexplored:
        node = unexplored.popleft()
        descendants.add(node)
        children = A.getrow(node).indices
        for child in children:
            if child not in descendants:
                unexplored.append(child)

    return descendants


class Database(object):

    class IntegrityError(Exception):
        pass

    def __init__(self):
        self.__primary_keys = set()

    def insert(self, node_id):
        if node_id not in self.__primary_keys:
            self.__primary_keys.add(node_id)
        else:
            raise Database.IntegrityError("Violation of unique constraint")


def get_descendants(node, A):
    db = Database()
    unexplored = deque([node])
    while unexplored:
        node = unexplored.popleft()
        try:
            db.insert(node)     
            yield node
        except Database.IntegrityError, e:
            continue

        children = A.getrow(node).indices
        for child in children:
            unexplored.append(child)


