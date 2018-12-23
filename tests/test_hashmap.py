import unittest
import topojson
import geopandas


class TestHasmap(unittest.TestCase):
    # duplicate rotated geometry bar with hole interior in geometry foo
    def test_hashmap_geomcol_multipolygon_polygon(self):
        data = {
            "foo": {
                "type": "GeometryCollection",
                "geometries": [
                    {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [
                                [[10, 20], [20, 0], [0, 0], [10, 20]],
                                [[3, 2], [10, 16], [17, 2], [3, 2]],
                            ],
                            [[[6, 4], [14, 4], [10, 12], [6, 4]]],
                        ],
                    },
                    {
                        "type": "Polygon",
                        "coordinates": [[[20, 0], [35, 5], [10, 20], [20, 0]]],
                    },
                ],
            }
        }
        topo = topojson.hashmap(
            topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        )
        # print(topo)
        self.assertEqual(
            topo["objects"]["data"]["geometries"][0]["arcs"], [[[4, 0]], [[1]], [[2]]]
        )

    def test_hashmap_backward_polygon(self):
        data = {
            "abc": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
            "def": {
                "type": "Polygon",
                "coordinates": [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]],
            },
        }
        topo = topojson.hashmap(
            topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        )
        self.assertEqual(topo["objects"]["data"]["geometries"][0]["arcs"], [[-3, 0]])
        self.assertEqual(topo["objects"]["data"]["geometries"][1]["arcs"], [[1, 2]])

    # this test should catch a shared boundary and a hashed multipolgon
    # related to https://github.com/Toblerity/Shapely/issues/535
    def test_albania_greece(self):
        data = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
        data = data[(data.name == "Albania") | (data.name == "Greece")]
        topo = topojson.hashmap(
            topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        )
        self.assertEqual(len(topo["arcs"]), 3)

    def test_benin_surrounding_countries(self):
        data = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
        data = data[data.continent == "Africa"]
        data = data[
            (data.name == "Niger")
            | (data.name == "Nigeria")
            | (data.name == "Burkina Faso")
            | (data.name == "Togo")
            | (data.name == "Benin")
        ]
        topo = topojson.hashmap(
            topojson.dedup(topojson.cut(topojson.join(topojson.extract(data))))
        )
        self.assertEqual(len(topo["arcs"]), 3)