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
To install the required packages run the following:

   pip install virtualenv
   virtualenv venv
   . venv/Scripts/activate
   pip install -r ./requirements.txt

TEST CASES
------------------------------------------------------------------------
To run the test cases use the following:

   python3 -m unittest test_cases
