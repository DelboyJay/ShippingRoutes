import os
import unittest

from codefiles.shipping_routes import RouteManager, InvalidRouteError, InvalidPortName


class TestCaseShippintRoutes(unittest.TestCase):
    def setUp(self):
        # Create a route manager
        self.rm = RouteManager()

        # Load the pre-defined routes
        path, _ = os.path.split(__file__)
        path = os.path.join(path, "../test_files/routes.yml")
        self.rm.load_data(path)

    def tearDown(self):
        pass

    def test_direct_route_times_valid(self):
        self.assertEqual(10, self.rm.get_direct_route_time(["Buenos Aires", "New York", "Liverpool"]))
        self.assertEqual(8, self.rm.get_direct_route_time(["Buenos Aires", "Casablanca", "Liverpool"]))
        self.assertEqual(19,
                         self.rm.get_direct_route_time(
                             ["Buenos Aires", "Cape Town", "New York", "Liverpool", "Casablanca"]))

    def test_direct_route_times_invalid_less_than_2_port_names(self):
        with self.assertRaises(InvalidRouteError):
            self.rm.get_direct_route_time([])

        with self.assertRaises(InvalidRouteError):
            self.rm.get_direct_route_time(["Buenos Aires"])

    def test_direct_route_times_invalid_route(self):
        with self.assertRaises(InvalidRouteError):
            self.rm.get_direct_route_time(["Buenos Aires", "Cape Town", "Casablanca"])

    def test_get_all_routes(self):
        results = [
            ["Buenos Aires", "Casablanca"],
            ["Buenos Aires", "New York", "Liverpool", "Casablanca"],
            ["Buenos Aires", "Cape Town", "New York", "Liverpool", "Casablanca"],
            ["Buenos Aires", "New York", "Liverpool", "Cape Town", "Casablanca"],
        ]
        self.assertListEqual(results, self.rm.get_all_routes("Buenos Aires", "Casablanca"))

    def test_shortest_journey(self):
        self.assertEqual(8, self.rm.get_shortest_journey("Buenos Aires", "Liverpool"))
        self.assertEqual(18, self.rm.get_shortest_journey("New York", "New York"))
        self.assertRaises(InvalidPortName, self.rm.get_shortest_journey("foobar", "New York"))

    def test_find_number_of_routes(self):
        self.assertEqual(8, self.rm.get_number_of_routes("Liverpool", "Liverpool", lambda x: x == 3))
        self.assertEqual(8, self.rm.get_number_of_routes("Buenos Aires", "Liverpool", lambda x: x == 4))
        self.assertEqual(8, self.rm.get_number_of_routes("Liverpool", "Liverpool", lambda x: x <= 25))
        self.assertRaises(InvalidPortName, self.rm.get_number_of_routes("foobar", "New York", lambda x: x == 1))


if __name__ == '__main__':
    unittest.main()
