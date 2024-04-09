"""Module containing test cases for the package."""
import unittest
import networkx as nx
from automotif import AutoMotif
class TestAutoMotif(unittest.TestCase):
    def setUp(self):
        self.graph = nx.DiGraph()
        self.graph.add_edges_from([(1, 2), (2, 3), (3, 1)])

    def test_initialization(self):
        """Test whether the AutoMotif class initializes correctly with basic parameters."""
        automotif = AutoMotif(Graph=self.graph, size=3)
        self.assertIsInstance(automotif, AutoMotif)
        self.assertEqual(automotif.size, 3)
        self.assertFalse(automotif.directed)  
        self.assertFalse(automotif.allow_automorphism)

    def test_invalid_graph_type(self):
        """Test initialization with an invalid graph type."""
        with self.assertRaises(ValueError):
            AutoMotif(Graph="not a graph", size=3)

    def test_invalid_size_type(self):
        """Test initialization with an invalid motif size."""
        with self.assertRaises(ValueError):
            AutoMotif(Graph=self.graph, size="3")

    def test_generate_graphs(self):
        """Test the generation of all possible graph configurations."""
        automotif = AutoMotif(Graph=self.graph, size=3, verbose=True)
        generated_graphs = automotif.generate_graphs(3)
        self.assertGreater(len(generated_graphs), 0)

    def test_find_motifs(self):
        """Test finding motifs without saving to a CSV file."""
        automotif = AutoMotif(Graph=self.graph, size=3, find=True, verbose=True)
        motifs_found = automotif.find_all_motifs()
        self.assertIsInstance(motifs_found, dict)
        self.assertGreaterEqual(len(motifs_found), 0)

    def test_save_motifs(self):
        """Test the saving functionality, ensuring no exceptions are raised during the process."""
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tempdir:
            automotif = AutoMotif(Graph=self.graph, size=3, save=True, path=tempdir, verbose=True)
            try:
                automotif.find_all_motifs()
                save_successful = True
            except Exception as e:
                print(f"Error during save: {e}")
                save_successful = False
            self.assertTrue(save_successful)
            self.assertTrue(any(os.scandir(tempdir)))

if __name__ == '__main__':
    unittest.main()
