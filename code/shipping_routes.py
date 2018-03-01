import yaml


# Exception that signals an invalid port name was specified
class InvalidPortName(Exception):
    pass


# Exception that signals an invalid route was specified
class InvalidRouteError(Exception):
    pass


def get_direct_route_time(destinations):
    """
    Given a list of destinations this function calculates the total time to reach the final destination.
    :param destinations: list of destinations names. The first name is the port to start from.
    :return: length of time in days
    :exception InvalidRouteError: raised if the route is invalid and a time cannot be calculated.
    """
    return 0


def get_shortest_journey(start_city, end_city):
    """
    Given a start and end city this function returns the shortest route
    :param start_city: Name fo the starting city
    :param end_city: name of the End city
    :return: The shortest number of days for the entire journey
    """
    return 0


def get_number_of_routes(start_city, end_city, number_of_stops):
    """
    Given a start and end city this function returns the shortest route
    :param start_city: Name fo the starting city
    :param end_city: name of the End city
    :param number_of_stops:
    :return: The shortest number of days for the entire journey
    """
    return 0


def load_data(filename):
    """
    Load route data from a YAML file
    :param filename: yaml filename
    :return: A data object that represents the yaml file content
    """
    with open(filename) as han:
        return yaml.load(han)


def main():
    data = load_data("test_files/routes.yml")
    pass


if __name__ == '__main__':
    main()
