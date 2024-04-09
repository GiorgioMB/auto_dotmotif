# AutoMotif: Automated Motif Detection in Network Graphs
## What is it?
AutoMotif streamlines the identification and cataloging of motifs within network graphs. Utilizing NetworkX for graph manipulation, dotmotif for detecting motifs, and pandas for data management, it simplifies the process of uncovering patterns across both directed and undirected networks. Users can customize searches based on motif size, directionality, executors and the treatment of automorphisms, as well as even having the option to save the results for further analysis.

## Installation

```bash
pip install automotifs
```
## Quick Start
```python
from automotif import AutoMotif
from dotmotif import executors
import networkx as nx
# Example: A random directed graph
G = nx.gnp_random_graph(100, 0.5, directed=True)
# Set up AutoMotif
motif_finder = AutoMotif(Graph=G, size=3, directed=True, verbose=True, use_GrandISO=True)
# Start finding motifs
motifs = motif_finder.find_all_motifs()
# Calculate the Z-Score for the motifs
z_scores = motif_finder.calculate_zscore(num_random_graphs = 30, Executor = executors.NetworkXExecutor)
# Display the motifs found
motif_finder.display_all_motifs()
```
## Features
- **Automated Detection**: AutoMotif automates the detection of motifs, eliminating the need for manual parameter adjustments. It's designed to be efficient and user-friendly, allowing users to focus more on analysis and less on setup.
- **Flexible and Powerful**: Capable of handling both directed and undirected graphs, AutoMotif provides flexibility in defining motifs, including size and whether to consider automorphisms, ensuring a broad applicability across different types of network analyses.
- **Data Organization and Export**: Directly save your motifs to CSV files for easy access, further analysis, or sharing with your team or research community.
- **Z-Score Calculation**: Assess the statistical significance of detected motifs by calculating their Z-scores, providing insights into the rarity or commonality of patterns within your network compared to random expectations.
- **Visual Representation**: AutoMotif includes features for visualizing network motifs, allowing users to display them as graphs within the application. This aids in the qualitative analysis of motifs, offering a graphical representation of network patterns and their connections for easier interpretation and presentation.
## Contributions
We encourage contributions to AutoMotif! If you have ideas for improvements or new features, don't hesitate to open an issue or submit a pull request on our repository.
## License
AutoMotif is made available under the MIT License. See the LICENSE file for more details.
***
## Who made this? 
AutoMotif was developed by Giorgio Micaletto under the guidance of Professor Marta Zava at Bocconi University. This tool is designed to simplify and facilitate the complex process of network motif analysis.
Contacts:
- giorgio.micaletto@studbocconi.it
- [linkedin](linkedin.com/in/giorgio-micaletto/)
