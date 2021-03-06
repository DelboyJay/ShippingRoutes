import yaml

from exceptions import InvalidRouteError, InvalidPortName


class RouteManager:
    """
    The Route Manager class
    This class manages the route data and provides functions to extract useful information.
    """

    def __init__(self):
        self.routes = None
        self.mapped_routes = None
        self.all_port_names = None

    def get_direct_route_time(self, destinations):
        """
        Given a list of destinations this function calculates the total time to reach the final destination.
        :param destinations: list of destinations names. The first name is the port to start from.
        :return: length of time in days
        :exception InvalidRouteError: raised if the route is invalid and a time cannot be calculated.
        """
        if len(destinations) < 2:
            raise InvalidRouteError("There must be two or more port names specified.")

        # Break the complete route up into smaller routes
        route_items = list(zip(destinations[0:], destinations[1:]))
        r = [route["journey_time"] for route_item in route_items for route in self.routes if
             route_item == (route["start"], route["end"])]
        if len(route_items) != len(r):
            # Find the routes that are invalid and create a string message for the user.
            invalid_routes = set(route_items).difference([(route["start"], route["end"]) for route in self.routes])
            msg = "\n\t".join([" => ".join(f) for f in invalid_routes])
            raise InvalidRouteError("One or more parts of this route are invalid.\n\t" + msg, invalid_routes)
        return sum(r)

    def get_shortest_journey(self, start_port, end_port):
        """
        Given a start and end port this function returns the shortest route
        :param start_port: Name fo the starting port
        :param end_port: name of the End port
        :return: The shortest number of days for the entire journey
        """
        routes = self.get_all_routes(start_port, end_port)
        return min([self.get_direct_route_time(f) for f in routes])

    def get_all_routes(self, start_port, end_port, prev_state=None):
        """
        Returns a list of a list of routes.
        :param start_port: The start port
        :param end_port: The final port destination
        :param prev_state: because this is a recursive function we need a way of remembering the previous state
                           This variable is a list of strings that holds the ports that we have visited thus far.
        :return: list of list of strings
        """
        # If this is the first time the function has been called then just add the starting port to a list.
        if prev_state is None:
            prev_state = [start_port]

        valid_routes = []
        if start_port not in self.all_port_names:
            raise InvalidPortName(
                "The port name %s is not valid. NOTE: Port names are also case sensitive." % start_port, start_port)

        if end_port not in self.all_port_names:
            raise InvalidPortName(
                "The port name %s is not valid. NOTE: Port names are also case sensitive." % start_port, start_port)

        for dst_port_info in self.mapped_routes[start_port]:
            # This check detect when we have reached our destination and adds it to our list of valid routes
            if dst_port_info["end"] == end_port:
                valid_routes.append(prev_state + [end_port])
                continue
            # This check stops us looping around forever. If we reach a destination that we have already visited then
            # we skip the route
            if dst_port_info["end"] in prev_state:
                continue
            # Get all possible routes that may or may not reach the intended destination
            valid_routes.extend(
                self.get_all_routes(dst_port_info["end"], end_port, prev_state + [dst_port_info["end"]]))

        return valid_routes

    def get_number_of_routes(self, start_port, end_port, fn_count_filter):
        """
        Given a start and end port this function returns the shortest route
        :param start_port: Name fo the starting port
        :param end_port: name of the End port
        :param fn_count_filter: a lambda function that allows for data filtering
        :return: The shortest number of days for the entire journey
        """
        routes = self.get_all_routes(start_port, end_port)
        a = [route for route in routes if fn_count_filter(len(route))]
        if len(a) == 0:
            return None
        return len(a)

    def load_routes(self, filename):
        """
        Load route data from a YAML file
        :param filename: yaml filename
        :return: A data object that represents the yaml file content
        """
        with open(filename) as han:
            self.routes = yaml.load(han)
        self._get_mapped_routes()
        self._get_all_port_names()

    def set_routes(self, routes_list):
        self.routes = routes_list
        self._get_mapped_routes()
        self._get_all_port_names()

    def get_route_data_with_criteria(self, start_port, target_port, fn_criteria):
        """
        Filter all routes between source and target ports given a criteria function
        :param start_port: The port name to start form
        :param target_port: The target port name
        :param fn_criteria: A function that returns true when a route should be returned given a route object in the
        form of:
        {"start": "<name>", "end":"<name>", "journey_time": <time in days>}
        :return: list of routes.
        """
        return [route for route in self.get_all_routes(start_port, target_port) if fn_criteria(route)]

    def _get_all_port_names(self):
        """
        Gets a complete list of all start and end port names
        """
        self.all_port_names = set([route["start"] for route in self.routes] + [route["end"] for route in self.routes])

    def _get_mapped_routes(self):
        """
        Creates a dictionary where the keys are all of the ports you can start from and the values are a list of
        destinations and times to the next port.
        :return: dict
        """
        self.mapped_routes = {route["start"]: [route2 for route2 in self.routes if route2["start"] == route["start"]]
                              for route in self.routes}
