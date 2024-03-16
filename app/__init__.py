"""
This contains the application factory for creating flask application instances.
Using the application factory allows for the creation of flask applications configured
for different environments based on the value of the CONFIG_TYPE environment variable
"""

from flask import Flask

def create_app():

    app = Flask(__name__)

    return app

