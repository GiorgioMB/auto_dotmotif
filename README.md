# AutoMotif: Automated Motif Detection in Network Graphs
## What is it?
AutoMotif streamlines the identification and cataloging of motifs within network graphs. Utilizing NetworkX for graph manipulation, dotmotif for detecting motifs, and pandas for data management, it simplifies the process of uncovering patterns across both directed and undirected networks. Users can customize searches based on motif size, directionality, and the treatment of automorphisms, and even save results for further analysis.

## Installation

```bash
pip install automotifs
```
## Quick Start
```python
from automotif import AutoMotif
import networkx as nx
# Example: A random directed graph
G = nx.gnp_random_graph(100, 0.5, directed=True)
# Set up AutoMotif
motif_finder = AutoMotif(Graph=G, size=3, directed=True, verbose=True)
# Start finding motifs
motifs = motif_finder.find_all_motifs()
```
## Features
- Automated Detection: Find motifs in your network without manually tweaking every parameter. AutoMotif takes care of the heavy lifting.
- Flexibility: Whether your networks are directed or undirected, AutoMotif can handle them. Plus, you can decide if you want to look for automorphisms and set the size of motifs to search for.
- Save for Later: Directly save your findings to CSV files, making it easier to analyze results or share them with others.
## Contributions
Contributions to AutoMotif are welcome! If you have suggestions for improvement or new features, feel free to open an issue or submit a pull request.
## License
AutoMotif is made available under the MIT License. See the LICENSE file for more details.
***
## Who made this? 
Giorgio Micaletto, under Professor Marta Zava's supervision at Bocconi University, put together AutoMotif. It was created to make network motif analysis less of a headache.

Contacts:
- giorgio.micaletto@studbocconi.it
- linkedin.com/in/giorgio-micaletto/
