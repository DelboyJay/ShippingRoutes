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
        self.rm.load_routes(path)

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

    def test_get_all_routes_simple_1_set_1_route(self):
        data = [{"start": "Buenos Aires", "end": "New York", "journey_time": 6}, ]
        rm = RouteManager()
        rm.set_routes(data)
        a = rm.get_all_routes("Buenos Aires", "New York")
        self.assertListEqual([["Buenos Aires", "New York"]], a)

    def test_get_all_routes_simple_1_set_2_routes(self):
        data = [
            {"start": "Buenos Aires", "end": "New York", "journey_time": 6},
            {"start": "New York", "end": "Liverpool", "journey_time": 4},
        ]
        rm = RouteManager()
        rm.set_routes(data)
        a = rm.get_all_routes("Buenos Aires", "Liverpool")
        self.assertListEqual([["Buenos Aires", "New York", "Liverpool"]], a)

    def test_get_all_routes_simple_2_sets_of_2_route(self):
        data = [
            {"start": "Buenos Aires", "end": "New York", "journey_time": 6},
            {"start": "New York", "end": "Liverpool", "journey_time": 4},
            {"start": "Buenos Aires", "end": "Casablanca", "journey_time": 5},
            {"start": "Casablanca", "end": "Liverpool", "journey_time": 3},
        ]
        rm = RouteManager()
        rm.set_routes(data)
        a = rm.get_all_routes("Buenos Aires", "Liverpool")
        self.assertListEqual([
            ["Buenos Aires", "New York", "Liverpool"],
            ["Buenos Aires", "Casablanca", "Liverpool"],
        ], a)

    def test_get_all_routes_round_trip(self):
        data = [
            {"start": "Liverpool", "end": "Casablanca", "journey_time": 3},
            {"start": "Casablanca", "end": "Liverpool", "journey_time": 3},
        ]
        rm = RouteManager()
        rm.set_routes(data)
        a = rm.get_all_routes("Liverpool", "Liverpool")
        self.assertListEqual([
            ["Liverpool", "Casablanca", "Liverpool"]
        ], a)

    def test_get_all_routes_Invalid_port_names_1(self):
        """No ports specified"""
        rm = RouteManager()
        rm.set_routes([])
        with self.assertRaises(InvalidPortName):
            rm.get_all_routes("Buenos Aires", "Casablanca")

    def test_get_all_routes_Invalid_port_names_2(self):
        """Start port name invalid"""
        with self.assertRaises(InvalidPortName):
            self.rm.get_all_routes("Buenos Airesa", "Casablanca")

    def test_get_all_routes_Invalid_port_names_3(self):
        """Target port name invalid"""
        with self.assertRaises(InvalidPortName):
            self.rm.get_all_routes("Buenos Aires", "Casablancaa")

    def test_get_all_routes_Invalid_port_names_4(self):
        """Both port names are invalid"""
        with self.assertRaises(InvalidPortName):
            self.rm.get_all_routes("Buenos Airesa", "Casablancaa")

    def test_get_all_routes_3_sets_multiple_routes(self):
        results = [
            ["Buenos Aires", "New York", "Liverpool", "Casablanca"],
            ["Buenos Aires", "Casablanca"],
            ["Buenos Aires", "Cape Town", "New York", "Liverpool", "Casablanca"],
        ]
        a = self.rm.get_all_routes("Buenos Aires", "Casablanca")
        self.assertListEqual(results, a)

    def test_liverpool_to_liverpool_tests(self):
        results = [
            ['Liverpool', 'Casablanca', 'Liverpool'],
            ['Liverpool', 'Casablanca', 'Cape Town', 'New York', 'Liverpool'],
            ['Liverpool', 'Cape Town', 'New York', 'Liverpool'],
        ]
        routes = self.rm.get_all_routes("Liverpool", "Liverpool")
        self.assertListEqual(results, routes)
        times = [self.rm.get_direct_route_time(f) for f in routes]
        self.assertListEqual([6, 21, 18], times)

    def test_shortest_journey(self):
        self.assertEqual(8, self.rm.get_shortest_journey("Buenos Aires", "Liverpool"))
        self.assertEqual(18, self.rm.get_shortest_journey("New York", "New York"))
        with self.assertRaises(InvalidPortName):
            self.rm.get_shortest_journey("foobar", "New York")

    def test_find_number_of_routes(self):
        self.assertEqual(1, self.rm.get_number_of_routes("Liverpool", "Liverpool", lambda x: x == 3))
        self.assertEqual(1, self.rm.get_number_of_routes("Buenos Aires", "Liverpool", lambda x: x == 4))
        self.assertEqual(3, self.rm.get_number_of_routes("Liverpool", "Liverpool", lambda x: x <= 25))
        self.assertEqual(None, self.rm.get_number_of_routes("Liverpool", "Liverpool", lambda x: x == 2))
        with self.assertRaises(InvalidPortName):
            self.rm.get_number_of_routes("foobar", "New York", lambda x: x == 1)


if __name__ == '__main__':
    unittest.main()
