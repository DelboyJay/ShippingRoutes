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

    def get_all_routes(self, start_port, end_port):
        """
        Returns a list of a list of routes.
        :param start_port: The start port
        :param end_port: The final port destination
        :return: list of list of strings
        """
        port_hash = {f["start"] for f in self.routes}
        return []

    def get_number_of_routes(self, start_port, end_port, fn_count_filter):
        """
        Given a start and end port this function returns the shortest route
        :param start_port: Name fo the starting port
        :param end_port: name of the End port
        :param fn_count_filter: a lambda function that allows for data filtering
        :return: The shortest number of days for the entire journey
        """
        return 0

    def load_data(self, filename):
        """
        Load route data from a YAML file
        :param filename: yaml filename
        :return: A data object that represents the yaml file content
        """
        with open(filename) as han:
            self.routes = yaml.load(han)


def main():
    rm = RouteManager()
    rm.load_data("test_files/routes.yml")
    pass


if __name__ == '__main__':
    main()
