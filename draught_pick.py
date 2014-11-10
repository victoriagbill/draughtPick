# draughtPick website and application for EE 382V, Fall 2014
# Created by Victoria Bill and Steve Rutherford
from __future__ import with_statement
import os
import urllib
from datetime import datetime, timedelta
import time
import collections

from google.appengine.api import users
from google.appengine.api import mail, images, files
from google.appengine.ext import ndb
from google.appengine.ext import blobstore, deferred
from google.appengine.ext.webapp import blobstore_handlers

import jinja2
import webapp2
import re
import json
