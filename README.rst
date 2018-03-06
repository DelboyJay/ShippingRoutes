Shipping Routes
========================================================================

Calculates route times given a starting city and a destination city.
The script can also calculate the shortest journey, number of different routes and routs with a specified number of stops.

REQUIREMENTS
------------------------------------------------------------------------
Shipping routes requires python 3 and the following software:

* ``pyYAML`` - YAML parser and emitter for Python.

INSTALLATION
------------------------------------------------------------------------
To install the required packages, run the following:

* pip install virtualenv
* virtualenv venv
* . venv/Scripts/activate
* pip install -r ./requirements.txt

TEST CASES
------------------------------------------------------------------------
To run the test cases use the following:

* python3 -m unittest test_cases/test_shipping_routes.py

Or you can use the docker file:

* docker build . -t test_cases_shipping_routes
* docker run --name testcases test_cases_shipping_routes

ROUTE DATA
------------------------------------------------------------------------
The route data can be modified in the file test_files/routes.yml

Each item has three pieces of information: a start, end and journey_time and should be specified in the file as follows:

   - start: <starting port name>

     end: <final destination port name>

     journey_time: <time in days to get from start to end mentioned above.

USAGE
------------------------------------------------------------------------

The script's command line help can be obtained using the following:

* python3 shipping_routes.py --help

There are five commands that can be used with this script. Their names and meanings are as follows:

``direct-route-time``: Given a list of destinations find the total journey time

``shortest-route``: Given a start and target route, find the journey with the shortest number of hops.

``show-routes``: Given a start and target route, show all of the possible journey combinations.

``routes-with-stops``: Given a start and target route, show only those routes whose number of hops fulfills the conditional criteria set.

``routes-with-time``: Given a start and target route, show only those routes whose totel journey time fulfills the conditional criteria set.

To get help on a specific command type:

* python3 shipping_routes.py <command> --help

QUESTIONS
------------------------------------------------------------------------
Here are a list of the original questions and the command line in order to obtain the answer.

1) What is the total journey time for the following direct routes (your model should
indicate if the journey is invalid):

1a) Buenos Aires => New York => Liverpool

* python3 shipping_routes.py direct-route-time "Buenos Aires" "New York" Liverpool ../test_files/routes.yml

1b) Buenos Aires => Casablanca => Liverpool

* python3 shipping_routes.py direct-route-time "Buenos Aires" "Casablanca" Liverpool ../test_files/routes.yml

1c) Buenos Aires => Cape Town => New York => Liverpool  Casablanca

* python3 shipping_routes.py direct-route-time "Buenos Aires" "Cape Town" "New York" Liverpool Casablanca ../test_files/routes.yml

1d) Buenos Aires => Cape Town => Casablanca

* python3 shipping_routes.py direct-route-time "Buenos Aires" "Cape Town" Casablanca ../test_files/routes.yml

2) Find the shortest journey time for the following routes:

2a) Buenos Aires => Liverpool

* python3 shipping_routes.py shortest-route "Buenos Aires" Liverpool ../test_files/routes.yml

2b) New York => New York

* python3 shipping_routes.py shortest-route "New York" "New York" ../test_files/routes.yml

3) Find the number of routes from Liverpool to Liverpool with a maximum number of 3
stops:

* python3 shipping_routes.py routes-with-stops Liverpool Liverpool "==3" ../test_files/routes.yml

4) Find the number of routes from Buenos Aires to Liverpool where exactly 4 stops are
made:

* python3 shipping_routes.py routes-with-stops "Buenos Aires" Liverpool "==4" ../test_files/routes.yml

5) Find the number of routes from Liverpool to Liverpool where the journey time is less
than or equal to 25 days:

* python3 shipping_routes.py routes-with-stops "Liverpool" Liverpool "<=25" ../test_files/routes.yml
