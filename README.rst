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