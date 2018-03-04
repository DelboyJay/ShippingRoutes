import argparse
import logging
import os
import re
import sys

# This line ensures that we can refer to the parent folders as a source root and allows modules to refer to the
# codefiles folder
sys.path.append(os.path.abspath(os.path.join(os.path.abspath(os.path.split(__file__)[0]), "..")))

from exceptions import InvalidRouteError, InvalidPortName
from route_manager import RouteManager

# The version number of this script
__this_version = "1.0.0"


def get_script_name():
    """
    returns the name of this script with out the .py extension
    :return:
    """
    _, filenameext = os.path.split(__file__)
    filename, _ = os.path.splitext(filenameext)
    return filename


def get_version():
    """return the script version number"""
    return __this_version


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
    parser = argparse.ArgumentParser(
        "%s v%s - This script provides information on shipping routes." % (get_script_name(), get_version()))
    parser.add_argument("-l", "--log-filename", dest="log_filename", help="Specify the output log filename.",
                        default=None)
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


def _create_lambda_criteria(criteria):
    """
    Creates a simple integer check lambda function given an operator-value string.
    Example "<=5",  "!=3", ">4" or "==7" etc
    :param criteria: A criteria string in the form of (==|!=|<=|>=|<|>)[\d]+
    :return: A lambda function.
    """

    # Limit what the user can specify as the criteria string. If the user is not from a trusted source then this
    # code can be used to limit what they can execute to ensure it is safe to execute
    m = re.search("(==|!=|<=|>=|<|>)[\d]+", criteria)
    if not m:
        raise ValueError("The search criteria is limited to the form (==|!=|<=|>=|<|>)[\d]+", criteria)

    # WARNING: This following could be dangerous because it executes a string as python code from the user.
    # Therefore it is assumed that this call is from a trusted source. The regex check above will increase safety
    # however.
    return eval("lambda x:x%s" % criteria)


def _get_route_with_criteria(start_port, target_port, criteria_str, fn_criteria, route_manager):
    log = get_logger()
    message = "The routes between %s and %s with the criteria 'Route length %s' are:\n" % (
        start_port, target_port, criteria_str)
    fn_base_criteria = _create_lambda_criteria(criteria_str)
    for route in route_manager.get_route_data_with_criteria(start_port, target_port,
                                                            lambda x: fn_base_criteria(fn_criteria(x))):
        full_journey = " => ".join(route)
        message += "\t%s   Total days: %s\n" % (full_journey, route_manager.get_direct_route_time(route))
    log.info(message)


def route_length_with_criteria(args, **kwargs):
    """
    Show the routes given the start and target port that meet the specified criteria
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    rm = kwargs["route_manager"]
    _get_route_with_criteria(args.start_port, args.target_port, args.criteria, len, rm)


def route_time_with_criteria(args, **kwargs):
    """
    Show the routes given the start and target port that meet the specified criteria
    :param args: arguments from the command line
    :param kwargs: should always contain a key called "route_manager" which points to a RouteManager object
    :return: None
    """
    rm = kwargs["route_manager"]
    _get_route_with_criteria(args.start_port, args.target_port, args.criteria, rm.get_direct_route_time, rm)


def main():
    """Main Loop"""

    # Set default logger until we can construct a proper one after processing the command line.
    log = get_logger()
    try:
        args = process_command_line()
        log = setup_logging(args.log_filename)
        rm = RouteManager()
        rm.load_routes(args.routes_filename)
        args.func(args, route_manager=rm)
        return 0
    except InvalidPortName as ex:
        log.error("The port name specified was invalid. Please check spelling and case. [%s]" % ex.args[1])
        return 1
    except InvalidRouteError as ex:
        log.error("The route specified was invalid. [%s]" % ex.args[1])
        return 1
    except Exception as ex:
        log.error("An unspecified error was encountered.")
        log.exception(ex)
        return 1


if __name__ == '__main__':
    # only run the main loop if this script was called from the command line
    exit(main())
