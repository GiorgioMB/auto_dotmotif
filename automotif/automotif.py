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
import random
import pandas as pd 
import networkx as nx
import os
from dotmotif import Motif
from itertools import product
import dotmotif.executors as executors
from typing import Union
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from .GPU_Executor import AcceleratedExecutor

class AutoMotif:
    """
    Wrapper class for dotmotif to find all possible motifs in a graph automatically.
    Inputs:
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
    - use_GrandISO (bool, optional): Whether to use GrandISO for motif detection. Defaults to False.
    - use_GPU (bool, optional): Whether to use the GPU accelerated executor for motif detection. Defaults to False
    - personal_executor (dotmotif.executors.Executor, optional): Executor to use for motif detection. Defaults to None.
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
                 verbose: bool = False,
                 use_GrandISO: bool = False,
                 use_GPU: bool = False,
                 personal_executor: executors.Executor = None):
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
        if personal_executor is not None:
            self.Ex = personal_executor
        if use_GrandISO:
            self.Ex = executors.GrandIsoExecutor(graph = self.Graph)
            if personal_executor is not None:
                print("Warning: The Executor provided will be ignored in favor of GrandIsoExecutor as use_GrandISO is set to True")
        if use_GPU:
            os.environ['NETWORKX_AUTOMATIC_BACKENDS'] = 'cugraph'
            self.Ex = AcceleratedExecutor (graph = self.Graph)
            if personal_executor is not None or use_GrandISO == True:
                print("Warning: GPU Accelerator Executor will be used, ignoring other executors provided, as use_GPU is set to True")
        else:
            self.Ex = executors.NetworkXExecutor(graph = self.Graph)
        self.motifs = None
        self.generate_required_motifs()
        self.motifs_found = None
        if find:
            return self.find_all_motifs()    
    
    def generate_graphs(self, n: int) -> list:
        """
        Generate all possible graphs for n nodes, ignoring self-loops.
        If self.directed is False, generate directed graphs ensuring no isolated nodes.
        If self.directed is True, generate undirected graphs with symmetric adjacency matrices.
        Each graph is represented by its adjacency matrix.
        Inputs:
        - n (int): Number of nodes.
        """
        if self.verbose:
            print("Generating motifs for", n, "nodes")
        graphs = []
        if not self.directed:
            for edges in product([0, 1], repeat=int(n*(n-1)/2)):
                matrix = [[0 for _ in range(n)] for _ in range(n)]
                edge_index = 0
                for i in range(n):
                    for j in range(i+1, n):
                        matrix[i][j] = matrix[j][i] = edges[edge_index]
                        edge_index += 1
                has_isolated_node = False
                for i in range(n):
                    if all(matrix[i][j] == 0 for j in range(n)):
                        has_isolated_node = True
                        break
                if not has_isolated_node:
                    graphs.append(matrix)
        else:
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
        if self.verbose:
            print("Generated", len(graphs), "motifs for", n, "nodes")
        return graphs
    
    def matrix_to_motif(self, matrix: list, node_labels: list) -> Motif:
        """
        Convert an adjacency matrix to the specified motif format.
        Inputs:
        - matrix (list): Adjacency matrix.
        - node_labels (list): List of node labels.
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
    
    def generate_motifs(self, n: int) -> list:
        """
        Generate all unique motifs of n nodes and convert them to the desired format.
        Inputs:
        - n (int): Number of nodes in the motif.
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

        if self.verbose == True:
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

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize the filename by removing invalid characters and truncating it to 255 characters to prevent OS errors.
        Inputs:
        - filename (str): Filename to sanitize.
        """
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename[:255]  
    
    def generate_unique_filename(self, edges: dict) -> str:
        """
        Generates an unique filename based on the edges of the motif.
        Inputs:
        - edges (list): List of edges in the motif.
        """
        simplified_edges = "_".join(f"{source}to{target}" for source, target in edges)
        filename = f"{simplified_edges}.csv"
        return self.sanitize_filename(filename)

    def find_motifs(self, motif, size, save: bool = None, Executor: executors.Executor = None) -> pd.DataFrame:
        """
        Search for the specified motif in the graph and optionally save the results to a CSV file.
        Inputs:
        - motif (dotmotif.Motif): Motif to find.
        - size (int): Size of the motif.
        - save (bool): Whether to save the motif to a CSV file. Defaults to None.
        - Executor (dotmotif.executors.Executor): Executor to use for motif detection. Defaults to None.
        """
        if self.verbose == True:
            print("Finding motifs for size", size)
        if save is None: save = self.save
        if save == True:
            dir_to_save = self.path
            os.makedirs(os.path.join(dir_to_save, f"Size_{size}"), exist_ok = True)
            raw_name = [(source, target) for source, target, *_ in motif._g.edges]
            name = self.generate_unique_filename(raw_name)
            if Executor is not None:
                result = Executor.find(motif)
            else:
                result = self.Ex.find(motif)
            result_df = pd.DataFrame(result)
            result_df.to_csv(os.path.join(dir_to_save, f"Size_{size}", f"{name}"))
            if self.verbose == True:
                print("Saved motif to", os.path.join(dir_to_save, f"Size_{size}", f"{name}"))
        else:
            if Executor is not None:
                result = Executor.find(motif)
            else:
                result = self.Ex.find(motif)
            result_df = pd.DataFrame(result)
            return result_df
    
    def find_all_motifs(self) -> dict:
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
            self.motifs_found = final_dict
            return final_dict
        else:
            raise ValueError("No motifs found")
    
    def generate_random_graphs(self, num_nodes: int, num_graphs: int, seed: int = None) -> list:
        """
        Generate random graphs for Z-Score calculation, with the probability of an edge being present
        determined by a random value between 0 and 1.
        Inputs:
        - num_nodes (int): Number of nodes in the graph.
        - num_graphs (int): Number of random graphs to generate.
        - seed (int): Seed for random number generation for reproducibility. Defaults to None.
        """
        if self.verbose == True:
            print("Generating random graphs")
        graphs = []
        if seed is not None:
            np.random.seed(seed)
        for i in range(num_graphs):
            if self.verbose:
                if num_graphs > 10 and i % (num_graphs // 10) == 0 and i != 0:
                    print(f"Generated {i + 1} random graphs out of {num_graphs}")
                elif num_graphs <= 10:
                    print(f"Generated {i + 1} random graphs out of {num_graphs}")
            p = np.random.rand()
            graph = nx.fast_gnp_random_graph(num_nodes, p, directed = self.directed, seed = seed)
            graph.remove_edges_from(nx.selfloop_edges(graph))
            graphs.append(graph)
        return graphs

    def calculate_zscore(self, num_random_graphs: int = 100, display = False, Executor: executors.Executor = executors.GrandIsoExecutor, seed: int = None) -> dict:
        """
        Method to calculate the Z-Scores for each motif based on the number of motifs found in random graphs.
        Inputs:
        - num_random_graphs (int): Number of random graphs to generate. Defaults to 100.
        - display (bool): Whether to display the motifs. Defaults to False.
        - Executor (dotmotif.executors.Executor): Executor to use for motif detection. Defaults to GrandIsoExecutor.
        - seed (int): Seed for random number generation. Defaults to None.
        Returns:
        - dict: Dictionary containing the Z-Scores for each motif.
        - Saves the Z-Scores to a CSV file if save is set to True.
        """
        if self.verbose == True:
            print("Calculating Z-Scores")
        num_nodes = len(self.Graph.nodes)
        graphs = self.generate_random_graphs(num_nodes, num_random_graphs, seed)
        if self.verbose == True:
            print("Generated random graphs")
        actual_motifs = self.find_all_motifs() if self.motifs_found is None else self.motifs_found
        actual_motif_counts = {motif: len(df) for motif, df in actual_motifs.items()}
        random_motif_counts = {motif: [] for motif in actual_motifs.keys()}
        if self.verbose == True:
            print("Finding motifs in random graphs")
        for graph in graphs:
            for motif in actual_motifs.keys():
                try:
                    executor = Executor(graph = graph)
                    result = self.find_motifs(motif, len(motif._g.nodes), save = False, Executor = executor)
                    random_motif_counts[motif].append(len(result))
                except ValueError as e:
                    print("Failed to generate motif", motif, "due to error:", e)
        if self.verbose == True:
            print("Calculating Z-Scores")
        if display:
            for motif in actual_motifs.keys():
                actual = actual_motif_counts[motif]
                random = random_motif_counts[motif]
                graph_types = ['Actual'] + ['Random'] * len(random)
                graph_numbers = ['Actual'] + ['Random {}'.format(i+1) for i in range(len(random))]
                motif_counts = [actual] + random
                df = pd.DataFrame({
                    'Graph Type': graph_types,
                    'Graph Number': graph_numbers,
                    'Motif Count': motif_counts
                })
                plt.figure(figsize=(10, 6))
                sns.barplot(x='Graph Number', y='Motif Count', hue='Graph Type', data=df, palette={'Actual': 'blue', 'Random': 'orange'}, dodge=False)
                plt.xlabel('Graphs')
                plt.ylabel('Motif Counts')
                plt.title('Motif Counts in Actual vs. Random Graphs')
                plt.xticks(rotation=45)  
                plt.legend(title='Graph Type')
                plt.tight_layout()
                if self.save:
                    dir_to_save = self.path
                    raw_name = [(source, target) for source, target, *_ in motif._g.edges]
                    name = self.generate_unique_filename(raw_name).split(".")[0]
                    os.makedirs(os.path.join(dir_to_save, "ZScores"), exist_ok = True)
                    plt.savefig(os.path.join(dir_to_save, "ZScores", f"Motif_{name}.png"))
                plt.show()
        motif_zscores = {}
        for motif, counts in random_motif_counts.items():
            actual_count = actual_motif_counts[motif]
            mean = np.mean(counts)
            std = np.std(counts)
            zscore = (actual_count - mean) / std
            motif_zscores[motif] = zscore
        if self.verbose == True:
            print("Z-Scores calculated")
        if self.save:
            if self.verbose == True:
                print("Saving Z-Scores")
            dir_to_save = self.path
            os.makedirs(os.path.join(dir_to_save, "ZScores"), exist_ok = True)
            zscore_df = pd.DataFrame(motif_zscores.items(), columns = ["Motif", "ZScore"])
            zscore_df.to_csv(os.path.join(dir_to_save, "ZScores", "ZScores.csv"))
        return motif_zscores
    
    def display_motif(self, motif: Motif) -> None:
        """
        Display the motif as a graph.
        Inputs:
        - motif (dotmotif.Motif): Motif to display.
        """
        Graph = motif.to_nx()
        nx.draw(Graph, with_labels = True)
    
    def display_all_motifs(self) -> None:
        """Display all motifs found in the graph."""
        if self.motifs_found is None:
            self.find_all_motifs()
        for motif in self.motifs_found.keys():
            self.display_motif(motif)
