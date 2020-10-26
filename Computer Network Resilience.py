"""
BFS algorithm
"""
from collections import deque
import matplotlib.pyplot as plt
import random
import timeit

#code for bfs and graph resilience
def bfs_visited(ugraph, start_node):
    """
    returns all nodes that can be visited from start_node
    """
    queue = deque()
    visited = set([start_node])
    queue.append(start_node)
    while queue:
        node = queue.popleft()
        for neighbor in ugraph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited

def cc_visited(ugraph):
    """
    returns the set of connected components of ugraph
    """
    remaining = set(ugraph)
    connections = []
    while remaining:
        node = remaining.pop()
        connected = bfs_visited(ugraph, node)
        connections.append(connected)
        remaining = remaining.difference(connected)
    return connections

def largest_cc_size(ugraph):
    """
    returns the size of the largest connected component of ugraph
    """
    connections = cc_visited(ugraph)
    lenght = 0
    for connection in connections:
        size = len(connection) 
        if size > lenght:
            lenght = size
    return lenght

def compute_resilience(ugraph, attack_order):
    """
    Takes the undirected graph ugraph, a list of nodes attack_order and 
    iterates through the nodes in attack_order. For each node in the list, the
    function removes the given node and its edges from the graph and then
    computes the size of the largest connected component for the resulting 
    graph. The function should return a list whose (k + 1)th entry is the size 
    of the largest connected component in the graph after the removal of the 
    first k nodes in attack_order. The first entry (indexed by zero) is the 
    size of the largest connected component in the original graph.
    """
    graph = copy_graph(ugraph)
    components = [largest_cc_size(ugraph)]

    for node in attack_order:
        if node in graph:    
            del graph[node]
            for cell in graph:
                if node in graph[cell]:
                    graph[cell].remove(node)
            components.append(largest_cc_size(graph))    
    return components    

#helper functions

def copy_graph(graph):
    """
    Make a copy of a graph
    """
    new_graph = {}

    for node in graph:
        new_graph[node] = set(graph[node])
    return new_graph

def delete_node(ugraph, node):
    """
    Delete a node from an undirected graph
    """
    neighbors = ugraph[node]
    ugraph.pop(node)

    for neighbor in neighbors:
        ugraph[neighbor].remove(node)
    
def targeted_order(ugraph):
    """
    Compute a targeted attack order consisting
    of nodes of maximal degree
    
    Returns:
    A list of nodes
    """
    new_graph = copy_graph(ugraph)   
    order = []    
    
    while len(new_graph) > 0:
        max_degree = -1
        for node in new_graph:
            if len(new_graph[node]) > max_degree:
                max_degree = len(new_graph[node])
                max_degree_node = node     
                
        neighbors = new_graph[max_degree_node]
        new_graph.pop(max_degree_node)

        for neighbor in neighbors:
            new_graph[neighbor].remove(max_degree_node)
        order.append(max_degree_node)
    return order

def fast_targeted_order(ugraph):
    """
    returns a list of target nodes in order of maximum to minimum degree
    """
    graph = copy_graph(ugraph)
    DegreeSets = []
    number_of_nodes = len(graph.keys())
    degree_list = []

    for node in range(number_of_nodes):
        DegreeSets.append(set())
        
    for node in graph:
        DegreeSets[len(graph[node])].add(node)
     
    for degree in range(number_of_nodes - 1, -1, -1):
        while DegreeSets[degree]:
            node = DegreeSets[degree].pop()
            for edge in graph[node]:
                degree = len(graph[edge])
                DegreeSets[degree].remove(edge)
                DegreeSets[degree - 1].add(edge)
            degree_list.append(node)
            delete_node(graph, node)
    return degree_list        

def count_nodes_and_edges(ugraph):
    """
    returns a tuple of the quantity of nodes and edges of a graph
    """
    graph = set(ugraph)
    edges = 0

    for node in graph:
        edges += len(ugraph[node])
    return (len(graph), edges)

def random_order(ugraph):
    """
    returns a list of a random permutation of the nodes in the provided graph
    """   
    graph = list(ugraph)
    random.shuffle(graph)
    return graph

#Code for network, ER and UPA graphs

def load_graph(graph_file):
    """
    Function that loads a text representation of the graph
    
    Returns a dictionary that models a graph
    """
    graph_text = open(graph_file, "r")
    answer_graph = {}
    
    for line in graph_text:
        neighbors = line.split(' ')
        node = int(neighbors[0])
        answer_graph[node] = set([])
        for neighbor in neighbors[1 : -1]:
            answer_graph[node].add(int(neighbor))

    return answer_graph

def ER_graph(num, probability):
    """
    computes a undirected graph based on random chance 
    of a node having an edge with another node
    """
    graph = {}
    
    for node in range(num):
        graph[node] = set()
        
    for node in graph:
        for edge in graph:
            if random.random() < probability and node != edge:
                graph[node].add(edge)
                graph[edge].add(node)
    return graph

def UPA_graph(final, edges):
    """
    computes an undirected graph based on the UPA algorithm
    """
    graph = {}   
    nodes = list(range(edges + 1))

    for node in nodes:       
        graph[node] = set([])  

    for node in range(edges, final):
        graph2 = []
        for dummy in range(edges):    
            choice = random.choice(nodes)
            while choice == node:
                choice = random.choice(nodes)
            graph2.append(choice)
        graph[node] = set(graph2)  
        nodes.append(node)
        for neighbor in graph2:
            graph[neighbor].add(node)
            
    #assertions
    for node in graph:
        assert node not in graph[node], node
    return graph

def build_plot(data):
    """
    Build plot of a given graph
    """
    plot = []
    for degree in data:
        if data[degree] != 0.0 and degree != 0.0:
            plot.append((degree, data[degree]))
    return plot

#variables
target_node = 1239
er_ratio = 0.004
upa_edges = 3

#graphs
cn_graph = load_graph("Data\\Network_graph.txt")
er_graph = ER_graph(target_node, er_ratio)
upa_graph = UPA_graph(target_node, upa_edges)
attack_order = random_order(cn_graph)

#resiliences
cn_resilience = compute_resilience(cn_graph, attack_order)[1:]
er_resilience = compute_resilience(er_graph, attack_order)[1:]
upa_resilience = compute_resilience(upa_graph, attack_order)[1:]

#resilience graph plots
plt.plot(cn_resilience, "-b", label="Computer network resilience")
plt.plot(er_resilience, "-g", label="ER resilience, p = 0.004")
plt.plot(upa_resilience, "-r", label="UPA resilience, m = 3")

#labels
plt.legend(loc="upper right")
plt.ylabel("Largest connected component")
plt.xlabel("Nodes removed from graph")   
plt.title("Resilience graph (Q.1)") 
plt.show()

print("Q.1 - Graph plot finished")
print("Q.2 - All three graphs were resilient under random \
    attacks as the first 20% of their nodes are removed")
print("Q.3 - Targeted order = O(n+m)")
print("Fast targeted order = O(n^2+m)")

def time(func, graph):
    """
    computes the time to execute a function on a graph
    """
    start_time = timeit.default_timer()
    func(graph)
    return timeit.default_timer() - start_time
    
#plot calculations 2
upa_edges2 = 5
slow_attack_order = []
fast_attack_order = []

for size in range(10, 1000, 10):
    upa_graph2 = UPA_graph(size, upa_edges2)
    slow_attack_order.append(time(targeted_order, upa_graph2))
    fast_attack_order.append(time(fast_targeted_order, upa_graph2)) 

#resilience graph plots 2
plt.plot(slow_attack_order, "-b", label="Targeted order running time")
plt.plot(fast_attack_order, "-r", label="Fast targerted order runnning time")

#labels 2
plt.legend(loc="upper left")
plt.ylabel("Running time")
plt.xlabel("(UPA graph size)/10 with m = 5")   
plt.title("Running time analysis") 
plt.show()

print("Q.3 - Graph plot finished")

#variables 3
attack_order1 = fast_targeted_order(cn_graph)
attack_order2 = fast_targeted_order(er_graph)
attack_order3 = fast_targeted_order(upa_graph)

#resiliences 3 
cn_resilience = compute_resilience(cn_graph, attack_order1)[1:]
er_resilience = compute_resilience(er_graph, attack_order2)[1:]
upa_resilience = compute_resilience(upa_graph, attack_order3)[1:]

#resilience graph plots 3
plt.plot(cn_resilience, "-b", label="Computer network resilience")
plt.plot(er_resilience, "-g", label="ER resilience, p = 0.004")
plt.plot(upa_resilience, "-r", label="UPA resilience, m = 3")

#labels 3
plt.legend(loc="upper right")
plt.ylabel("Largest connected component")
plt.xlabel("Nodes removed from graph")   
plt.title("Optimized resilience graph") 
plt.show()

print("Q.4 - Graph plot finished")
print("Q.5 - The UPA and ER graphs are resilient under targeted \
    attacks as the first 20% of their nodes are removed")