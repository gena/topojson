import unittest
import topojson
import geopandas


class TestDedup(unittest.TestCase):
    # duplicate rotated geometry bar with hole interior in geometry foo
    def test_duplicate_rotated_hole_interior(self):
        data = {
            "foo": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [[0, 0], [20, 0], [10, 20], [0, 0]],  # CCW
                        [[3, 2], [10, 16], [17, 2], [3, 2]],  # CW
                    ],
                    [[[6, 4], [14, 4], [10, 12], [6, 4]]],  # CCW
                ],
            },
            "bar": {
                "type": "Polygon",
                "coordinates": [[[17, 2], [3, 2], [10, 16], [17, 2]]],
            },
        }
        topo = topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        # print(topo)
        self.assertEqual(len(topo["bookkeeping_duplicates"]), 2)
        self.assertEqual(topo["bookkeeping_geoms"], [[0, 1], [2], [3]])

    def test_two_polygon_reversed_shared_arc(self):
        data = {
            "abcda": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },  # rotated to BCDAB, cut BC-CDAB
            "befcb": {
                "type": "Polygon",
                "coordinates": [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]],
            },
        }
        topo = topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        self.assertEqual(len(topo["bookkeeping_duplicates"]), 2)
        self.assertEqual(topo["bookkeeping_shared_arcs"], [2])
        self.assertEqual(topo["bookkeeping_arcs"], [[2, 0], [1, 2]])

    def test_duplicate_polygon_no_junctions(self):
        data = {
            "abca": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]],
            },
            "acba": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [0, 1], [1, 0], [0, 0]]],
            },
        }
        topo = topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        self.assertEqual(len(topo["bookkeeping_duplicates"]), 2)
        self.assertEqual(topo["bookkeeping_shared_arcs"], [0])
        self.assertEqual(topo["bookkeeping_arcs"], [[0], [0]])
        self.assertEqual(topo["bookkeeping_geoms"], [[0], [1]])

    def test_shared_line_ABCDBE_and_FBCG(self):
        data = {
            "abcdbe": {
                "type": "LineString",
                "coordinates": [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]],
            },
            "fbcg": {
                "type": "LineString",
                "coordinates": [[0, 1], [1, 0], [2, 0], [3, 1]],
            },
        }
        topo = topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        self.assertEqual(len(topo["bookkeeping_duplicates"]), 2)
        self.assertEqual(topo["bookkeeping_shared_arcs"], [3])
        self.assertEqual(topo["bookkeeping_arcs"], [[0, 3, 1], [2, 3, 4]])

    def test_egypt_sudan(self):
        data = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
        data = data[(data.name == "Egypt") | (data.name == "Sudan")]
        topo = topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        self.assertEqual(len(topo["bookkeeping_shared_arcs"]), 1)