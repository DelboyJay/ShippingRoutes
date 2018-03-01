import unittest

from code.shipping_routes import InvalidRouteError, get_direct_route_time, get_shortest_journey, InvalidPortName, \
    get_number_of_routes


class TestCaseShippintRoutes(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_direct_route_times_valid(self):
        self.assertEqual(10, get_direct_route_time(["Buenos Aires", "New York", "Liverpool"]))
        self.assertEqual(8, get_direct_route_time(["Buenos Aires", "Casablanca", "Liverpool"]))
        self.assertEqual(19,
                         get_direct_route_time(["Buenos Aires", "Cape Town", "New York", "Liverpool", "Casablanca"]))

    def test_direct_route_times_invalid(self):
        self.assertRaises(InvalidRouteError, get_direct_route_time([]))
        self.assertRaises(InvalidRouteError, get_direct_route_time(["Buenos Aires"]))
        self.assertRaises(InvalidRouteError, get_direct_route_time(["Buenos Aires", "Cape Town", "Casablanca"]))

    def test_shortest_journey(self):
        self.assertEqual(8, get_shortest_journey("Buenos Aires", "Liverpool"))
        self.assertEqual(18, get_shortest_journey("New York", "New York"))
        self.assertRaises(InvalidPortName, get_shortest_journey("foobar", "New York"))

    def test_find_number_of_routes(self):
        self.assertEqual(8, get_number_of_routes("Liverpool", "Liverpool", 3))
        self.assertRaises(InvalidPortName, get_number_of_routes("foobar", "New York", 1))


if __name__ == '__main__':
    unittest.main()
