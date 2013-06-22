#!/usr/bin/env python

from noprogress import db
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

db.create_all()
