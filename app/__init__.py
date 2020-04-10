from flask import Flask

webapp = Flask(__name__)

from app import main
from app import dynamo
from app import comprehend
from app import Login
from app import fileupload




