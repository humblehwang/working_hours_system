from flask import Blueprint, render_template
import os

working_hours_api = Blueprint('working_hours', __name__)

from . import working_hours