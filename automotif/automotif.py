"""
AutoMotif: Automated Motif Detection in Network Graphs
This module implements the AutoMotif class, a comprehensive tool designed to automatically
identify and catalog all possible motifs within a given network graph. It leverages the
networkx library for graph manipulation, dotmotif for motif detection, and pandas for
data organization and storage. The implementation allows for customization of motif
size, directionality, and the inclusion of automorphisms, with options to save results
directly to CSV files for further analysis.

The class encapsulates functionality to generate all potential graph configurations,
convert these to motif objects, and then find these motifs within the specified graph.
It supports both directed and undirected graphs and provides extensive flexibility in
defining what constitutes a motif through its parameters.

Developed by Giorgio Micaletto under the supervision of Professor Marta Zava at Bocconi University,
this tool aims to facilitate the systematic study of network motifs.
"""
import pandas as pd 
import networkx as nx
import os
from dotmotif import Motif
from itertools import product
import dotmotif.executors as executors
from typing import Union

class AutoMotif:
    """
    Wrapper class for dotmotif to find all possible motifs in a graph automatically.
    Parameters:
    - Graph (networkx.Graph): The graph to analyze.
    - size (int): Size of the motif to find.
    - directed (bool, optional): Whether the graph is directed. Defaults to False.
    - allow_automorphism (bool, optional): Whether to allow automorphisms. Defaults to False.
    - upto (bool, optional): Whether to generate motifs from a lower bound to the specified size. Defaults to False.
    - lower (int, optional): Lower bound for motif size. Defaults to 3.
    - save (bool, optional): Whether to save the motifs to a CSV file. Defaults to False.
    - path (str, optional): Directory to save the motifs. Defaults to None.
    - find (bool, optional): Whether to find all motifs directly. Defaults to False.
    - verbose (bool, optional): Whether to print progress. Defaults to False.
    """
    def __init__(self, 
                 Graph: Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph], 
                 size: int, 
                 directed: bool = False, 
                 allow_automorphism: bool = False, 
                 upto: bool = False,
                 lower: int = 3, 
                 save: bool = False, 
                 path: str = None,
                 find: bool = False, 
                 verbose: bool = False):
        if not hasattr(Graph, "nodes") or not callable(getattr(Graph, "nodes")):
            raise ValueError("Graph should be a NetworkX graph")
        elif type(size) != int:
            raise ValueError("Size should be an integer")
        elif type(upto) != bool:
            raise ValueError("Upto should be a boolean")
        elif type(save) != bool:
            raise ValueError("Save should be a boolean")
        elif size < 3:
            print("Warning: Size should be greater than 2")
        elif size > 10:
            print("Warning: Motif detection after size 10 may become unstable")
        elif upto and verbose:
            print(f"Warning: Upto is set to True, this will generate motifs from size {lower} to {size}")
        elif save and path == None:
            raise ValueError("Path should be provided if save is set to True")
        self.Graph = Graph
        self.size = size
        self.upto = upto
        self.save = save
        self.path = path
        self.verbose = verbose
        self.directed = directed
        self.allow_automorphism = allow_automorphism
        self.lower = lower
        self.Ex = executors.NetworkXExecutor(graph = self.Graph)
        self.motifs = None
        self.generate_required_motifs()
        if find == True:
            self.find_all_motifs()    
    
    def generate_graphs(self, n):
        """
        Generate all possible directed graphs for n nodes, ignoring self-loops,
        and ensure no isolated nodes are present. Each graph is represented by its adjacency matrix.
        Parameters:
        - n (int): Number of nodes.
        Returns:
        - list: List of adjacency matrices representing all possible graphs.
        """
        if self.verbose == True:
            print("Generating graphs for", n, "nodes")
        graphs = []
        for edges in product([0, 1], repeat=n*(n-1)):
            matrix = [[0 for _ in range(n)] for _ in range(n)]
            edge_index = 0
            for i in range(n):
                for j in range(n):
                    if i != j:  
                        matrix[i][j] = edges[edge_index]
                        edge_index += 1
            has_isolated_node = False
            for i in range(n):
                if all(matrix[i][j] == 0 for j in range(n)) or all(matrix[j][i] == 0 for j in range(n)):
                    has_isolated_node = True
                    break
            if not has_isolated_node:
                graphs.append(matrix)
        print("Generated", len(graphs), "graphs for", n, "nodes")
        return graphs
    
    def matrix_to_motif(self, matrix, node_labels):
        """
        Convert an adjacency matrix to the specified motif format.
        Parameters:
        - matrix (list): Adjacency matrix.
        - node_labels (list): List of node labels.
        Returns:
        - Motif: Motif object.
        """
        motif_str = ""
        for i, row in enumerate(matrix):
            for j, edge in enumerate(row):
                if edge:
                    motif_str += f"{node_labels[i]} -> {node_labels[j]}\n"
        remove_automorphisms = not self.allow_automorphism
        ignore_direct = not self.directed
        motif_obj = Motif(input_motif=motif_str, enforce_inequality = True, exclude_automorphisms = remove_automorphisms, ignore_direction = ignore_direct)
        return motif_obj
    
    def generate_motifs(self, n):
        """
        Generate all unique motifs of n nodes and convert them to the desired format.
        Parameters:
        - n (int): Number of nodes.
        Returns:
        - list: List of motifs.
        """
        if self.verbose == True:
            print("Generating motifs for", n, "nodes")
        motifs = []
        graphs = self.generate_graphs(n)
        node_labels = [chr(ord('A') + i) for i in range(n)]
        for graph in graphs:
            motif_str = self.matrix_to_motif(graph, node_labels)
            if motif_str not in motifs:
                motifs.append(motif_str)
        print("Generated", len(motifs), "motifs for", n, "nodes")
        return motifs
    
    def generate_required_motifs(self):
        """Generate the required motifs based on the class parameters."""
        if self.verbose == True:
            print("Generating motifs")
        motifs = {}
        if self.upto == True:
            for i in range(self.lower, self.size + 1):
                motifs[i] = self.generate_motifs(i)
        else:
            motifs[self.size] = self.generate_motifs(self.size)
        self.motifs = motifs


    def sanitize_filename(self, filename):
        """
        Sanitize the filename to remove invalid characters and limit length.
        Parameters:
        - filename (str): The filename to sanitize.
        Returns:
        - str: Sanitized filename.
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename[:255]  
    
    def generate_unique_filename(self, edges, max_edges_in_name=5):
        """
        Generate a unique filename representing the graph's edges.
        Parameters:
        - edges (list): List of edges in the graph.
        - max_edges_in_name (int, optional): Maximum number of edges to include in the name. Defaults to 5.
        Returns:
        - str: Unique filename.
        """
        edge_str = ";".join(f"{source}-{target}" for source, target in edges)        
        simplified_edges = "_".join(f"{source}to{target}" for source, target in edges[:max_edges_in_name])
        filename = f"{simplified_edges}.csv"
        return self.sanitize_filename(filename)

    def find_motifs(self, motif, size, save: bool = None):
        """
        Find and optionally save motifs to a CSV file.
        Parameters:
        - motif (Motif): The motif to find.
        - size (int): Size of the motif.
        - save (bool): Whether to save the motifs to a file.
        """
        if self.verbose == True:
            print("Finding motifs for", size)
        if save is None: save = self.save
        if save == True:
            dir_to_save = self.path
            os.makedirs(os.path.join(dir_to_save, f"Size_{size}"), exist_ok = True)
            raw_name = [(source, target) for source, target, *_ in motif._g.edges]
            name = self.generate_unique_filename(raw_name)
            result = self.Ex.find(motif)
            result_df = pd.DataFrame(result)
            result_df.to_csv(os.path.join(dir_to_save, f"Size_{size}", f"{name}"))
            if self.verbose == True:
                print("Saved motif to", os.path.join(dir_to_save, f"Size_{size}", f"{name}"))
        else:
            result = self.Ex.find(motif)
            result_df = pd.DataFrame(result)
            return result_df
    
    def find_all_motifs(self):
        """Find all motifs based on the class parameters and optionally save them to files."""
        if self.verbose == True:
            print("Finding all motifs")
        final_dict = {}
        for size, motifs in self.motifs.items():
            if self.verbose == True:
                print("Finding motifs for size", size)
            for motif in motifs:
                try:
                    ret_df = self.find_motifs(motif, size)
                    final_dict[motif] = ret_df
                except ValueError as e:
                    print("Failed to generate motif", motif, "due to error:", e)
        if len(final_dict) != 0:
            return final_dict
