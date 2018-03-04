import argparse
import logging
import os
import re
import sys

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


def get_script_name():
    """
    returns the name of this script with out the .py extension
    :return:
    """
    _, filenameext = os.path.split(__file__)
    filename, _ = os.path.splitext(filenameext)
    return filename


def get_logger():
    """
    Easy wat to get the main logging object
    :return:
    """
    return logging.getLogger(get_script_name())


def setup_logging(log_filename=None):
    """
    Sets up logging to stdout and optionally to a file.
    :param log_filename: Optional filename to also log output to.
    :return: None
    """
    my_logger = get_logger()
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_filename is not None:
        path, _ = os.path.split(os.path.abspath(log_filename))
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        handlers.append(logging.FileHandler(log_filename, encoding="UTF8"))

    for handler in handlers:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s'))
        my_logger.addHandler(handler)
    my_logger.setLevel(logging.INFO)
    return my_logger


def process_command_line():
    """
    Process the command line using the argparse module
    :return:
    """
    parser = argparse.ArgumentParser("")
    parser.add_argument("-l", "--log-filename", dest="log_filename", help="Specify the output log filename.")
    parser.add_argument(dest="routes_filename",
                        help="Specify the filename of a yml file that contains all of the routes.")

    subparsers = parser.add_subparsers(help='sub-command help')

    drt_parser = subparsers.add_parser("direct-route-time", help="Find out the total time for a specific route.")
    drt_parser.add_argument(dest="route_list", nargs="*",
                            help='A space-separated list of ports to find the total journey time for. if port names '
                                 'are made up of multiple words, please use quotes. i.e. '
                                 '"Buenos Aires" Cassablanca ...')
    drt_parser.set_defaults(func=direct_route_time)

    sj_parser = subparsers.add_parser("shortest-route",
                                      help="Find the shortest route given a starting and a target port.")
    sj_parser.add_argument(dest="start_port", help="The port to start from.")
    sj_parser.add_argument(dest="target_port", help="The target port to arrive at.")
    sj_parser.set_defaults(func=shortest_route)

    nr_parser = subparsers.add_parser("show-routes",
                                      help="Shows how many possible routes from start to target port.")
    nr_parser.add_argument(dest="start_port", help="The port to start from.")
    nr_parser.add_argument(dest="target_port", help="The target port to arrive at.")
    nr_parser.set_defaults(func=show_routes)

    rws_parser = subparsers.add_parser("routes-with-stops",
                                       help="Shows the routes from start to target port that meets the number of stops "
                                            "criteria.")
    rws_parser.add_argument(dest="start_port", help="The port to start from.")
    rws_parser.add_argument(dest="target_port", help="The target port to arrive at.")
    rws_parser.add_argument(dest="criteria", help="The filter criteria. i.e. ==5 or <=10")
    rws_parser.set_defaults(func=route_length_with_criteria)

    rwt_parser = subparsers.add_parser("routes-with-time",
                                       help="Shows the routes from start to target port that meets the total time "
                                            "criteria.")
    rwt_parser.add_argument(dest="start_port", help="The port to start from.")
    rwt_parser.add_argument(dest="target_port", help="The target port to arrive at.")
    rwt_parser.add_argument(dest="criteria", help='The filter criteria. i.e. "==5" or "<=10". NOTE: Always enclose '
                                                  'the criteria in quotes to avoid it being misinterpreted by the '
                                                  'command line processor.')
    rwt_parser.set_defaults(func=route_time_with_criteria)

    return parser.parse_args()


def direct_route_time(args, **kwargs):
    """
    Show the total direct route time given a list of ports
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    log = get_logger()
    rm = kwargs["route_manager"]
    assert isinstance(rm, RouteManager)
    route = args.route_list
    full_journey = " => ".join(route)
    log.info("The total time for the route %s is %s days.\n" % (full_journey, rm.get_direct_route_time(route)))


def shortest_route(args, **kwargs):
    """
    Show the shortest route(s) given the start and target port.
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    log = get_logger()
    rm = kwargs["route_manager"]
    assert isinstance(rm, RouteManager)
    shortest_time = rm.get_shortest_journey(args.start_port, args.target_port)
    message = "Shortest journey time is:\n"
    routes = rm.get_all_routes(args.start_port, args.target_port)

    for route in [route for route in routes if rm.get_direct_route_time(route) == shortest_time]:
        full_journey = " => ".join(route)
        message += "\t%s   Total days: %s\n" % (full_journey, rm.get_direct_route_time(route))
    log.info(message)


def show_routes(args, **kwargs):
    """
    Show the routes given the start and target port
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    log = get_logger()
    rm = kwargs["route_manager"]
    assert isinstance(rm, RouteManager)
    message = "The routes between %s and %s are:\n" % (args.start_port, args.target_port)
    routes = rm.get_all_routes(args.start_port, args.target_port)
    for route in routes:
        full_journey = " => ".join(route)
        message += "\t%s   Total days: %s\n" % (full_journey, rm.get_direct_route_time(route))
    log.info(message)


def route_length_with_criteria(args, **kwargs):
    """
    Show the routes given the start and target port that meet the specified criteria
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    log = get_logger()
    rm = kwargs["route_manager"]
    assert isinstance(rm, RouteManager)
    routes = rm.get_all_routes(args.start_port, args.target_port)

    # Limit what the user can specify as the criteria string. If the user is not from a trusted source then this
    # code can be used to limit what they can execute to ensure it is safe to execute
    m = re.search("(==|!=|<=|>=|<|>)[\d]+", args.criteria)
    if not m:
        raise ValueError("The search criteria is limited to the form (==|!=|<=|>=|<|>)[\d]+", args.criteria)

    # WARNING: This following could be dangerous because it executes a string as python code from the user.
    # Therefore it is assumed that this call is from a trusted source. The regex check above will increase safety
    # however.
    criteria = eval("lambda x:x%s" % args.criteria)

    message = "The routes between %s and %s with the criteria 'Route length %s' are:\n" % (
        args.start_port, args.target_port, args.criteria)
    for route in [route for route in routes if criteria(len(route))]:
        full_journey = " => ".join(route)
        message += "\t%s   Total days: %s\n" % (full_journey, rm.get_direct_route_time(route))
    log.info(message)


def route_time_with_criteria(args, **kwargs):
    """
    Show the routes given the start and target port that meet the specified criteria
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    log = get_logger()
    rm = kwargs["route_manager"]
    assert isinstance(rm, RouteManager)
    routes = rm.get_all_routes(args.start_port, args.target_port)

    # Limit what the user can specify as the criteria string. If the user is not from a trusted source then this
    # code can be used to limit what they can execute to ensure it is safe to execute
    m = re.search("(==|!=|<=|>=|<|>)[\d]+", args.criteria)
    if not m:
        raise ValueError("The search criteria is limited to the form (==|!=|<=|>=|<|>)[\d]+", args.criteria)

    # WARNING: This following could be dangerous because it executes a string as python code from the user.
    # Therefore it is assumed that this call is from a trusted source. The regex check above will increase safety
    # however.
    criteria = eval("lambda x:x%s" % args.criteria)

    message = "The routes between %s and %s with the criteria 'Route total time %s' are:\n" % (
        args.start_port, args.target_port, args.criteria)
    for route in [route for route in routes if criteria(rm.get_direct_route_time(route))]:
        full_journey = " => ".join(route)
        message += "\t%s   Total days: %s\n" % (full_journey, rm.get_direct_route_time(route))
    log.info(message)


def main():
    """Main Loop"""
    log = setup_logging()
    try:
        args = process_command_line()
        rm = RouteManager()
        rm.load_routes(args.routes_filename)
        args.func(args, route_manager=rm)
    except InvalidPortName as ex:
        log.error("The port name specified was invalid. Please check spelling and case. [%s]" % ex.args[1])
    except InvalidRouteError as ex:
        log.error("The route specified was invalid. [%s]" % ex.args[1])
    except Exception as ex:
        log.error("An unspecified error was encountered.")
        log.exception(ex)


if __name__ == '__main__':
    # only run the main loop if this script was called from the command line
    main()
