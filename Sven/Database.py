"""
Copyright (C) 2014, Web Bender Consulting, LLC. - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Elijah Ethun <elijahe@gmail.com>
"""

"""
Database.py

Module containing Postgres database connection and usage methods.
"""

import psycopg2
import psycopg2.extras
import traceback
from Sven.Methods import *


class Database(object):
  connection = None
  cursor = None

  def __init__(self, config):
    self.connection = psycopg2.connect(
      database = config['db_name'],
      user = config['db_user'],
      password = config['db_pass'],
      host = config['db_host']
    )

    self.cursor = self.connection.cursor(
      cursor_factory = psycopg2.extras.DictCursor)


  def execute(self, sql, parameters = []):
    try :
      self.cursor.execute(sql, parameters)
      return self.cursor
    except Exception, ex :
      self.connection.rollback()
      notice(traceback.format_exc())
      raise Exception(ex)


  def commit(self):
    self.connection.commit()


  @staticmethod
  def open(config):
    return Database(config)


  def close(self):
    self.connection.close()