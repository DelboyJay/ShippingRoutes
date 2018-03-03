import yaml


# Exception that signals an invalid port name was specified
class InvalidPortName(Exception):
    pass


# Exception that signals an invalid route was specified
class InvalidRouteError(Exception):
    pass


class RouteManager:

    def __init__(self):
        self.routes = None
        self.mapped_routes = None

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
        return 0

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
        if self.mapped_routes.get(start_port) is None:
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
        return 0

    def load_routes(self, filename):
        """
        Load route data from a YAML file
        :param filename: yaml filename
        :return: A data object that represents the yaml file content
        """
        with open(filename) as han:
            self.routes = yaml.load(han)
        self._get_all_port_destinations()

    def set_routes(self, routes_list):
        self.routes = routes_list
        self._get_all_port_destinations()

    def _get_all_port_destinations(self):
        """
        Creates a dictionary where the keys are all of the ports you can start from and the values are a list of
        destinations and times to the next port.
        :return: dict
        """
        self.mapped_routes = {route["start"]: [route2 for route2 in self.routes if route2["start"] == route["start"]]
                              for route in self.routes}


def main():
    rm = RouteManager()
    rm.load_routes("test_files/routes.yml")
    pass


if __name__ == '__main__':
    main()
