SportsSystem Crawler
===============================

Overview
--------

A simple crawler for SportsSystems results.

Quickstart
----------

Clone this repo and run:

    pip install -r requirements-local.txt

Then you can call run:

    python go.py <EVENT_ID>

The spider will run and fetch all the data stored for that event, once complete it'll output some simple stats.


Contributing
------------

To get the docs up and running with auto refresh run:

    sphinx-autobuild docs docs/_build/html --port 8000 --watch sportsystem_crawler

Example
-------

TBD