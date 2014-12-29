import simplejson as json

from Sven.Methods import *
from Sven.Exception import *

class ConditionValues():
  def __init__(self):
    self.values = []


  def add(self, **kwargs):
    if not 'value' in kwargs or not 'name' in kwargs:
      raise ConditionException("ConditionValues instance must provide 'value' "
                               "and 'name'")

    self.values.append({
      'value' : kwargs['value'],
      'name' : kwargs['name'],
      'description' : getattr(kwargs, 'description', None)
    })


class Conditions():
  def __init__(self):
    self.conditions = []


  def add(self, **kwargs):
    if 'key' not in kwargs \
       or 'type' not in kwargs \
       or 'multiple' not in kwargs \
       or 'name' not in kwargs:
      raise ConditionException("Must provide 'key', 'type', 'multiple' and '"
                               "name' to Condition object")

    _types = ['float', 'int', 'bool',
              'string', 'list', 'dict',
              'time', 'date', 'datetime']

    if kwargs['type'] not in _types:
      raise ConditionException("Invalid 'type' provided")

    if kwargs['type'] in ['list', 'dict']:
      if 'multiple' not in kwargs:
        raise ConditionException("'multiple' field must be defined as boolean "
                                 "when type is 'list' or 'dict'")

      if kwargs['multiple'] not in [True, False]:
        raise ConditionException("'multiple' field must be boolean")

    if 'values' not in kwargs or ('values' in kwargs
                                  and not isinstance(kwargs['values'],
                                                     ConditionValues)):
      kwargs['values'] = ConditionValues()

    predicates = ['eq', 'ne', 'gt', 'lt', 'ge', 'le'];

    if 'predicates' in kwargs:
      if isinstance(kwargs['predicates'], (list, tuple)):
        for predicate in kwargs['predicates']:
          if predicate not in predicates:
            if predicate == 'all':
              kwargs['predicates'] = predicates
            else:
              raise ConditionException("Invalid predicate %s", (predicate,))
      elif kwargs['predicates'] not in predicates:
        raise ConditionException("Invalid predicate %s",
                                 (kwargs['predicates'],))
    else:
      # If no predicate is supplied, assume we are doing an exact match
      kwargs['predicates'] = ['eq']

    self.conditions.append({
      'key' : kwargs['key'],
      'type' : kwargs['type'],
      'multiple' : kwargs['multiple'],
      'name' : kwargs['name'],
      'description' : getattr(kwargs, 'description', None),
      'predicates' : kwargs['predicates'],
      'values' : kwargs['values'].values,
    })