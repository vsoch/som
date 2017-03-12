'''
google/modals.py: models for datastore

'''

from som.storage.google.validators import (
    validate_model
)

import google.cloud.datastore as datastore
from som.storage.google.datastore import (
    get_key_filters,
    parse_keys,
    print_datastore_path
)

from som.logman import bot
import datetime
import collections
import sys
import os

######################################################################################
# Object Manager
######################################################################################

class BatchManager:
    '''a batch manager is bucket to hold multiple objects to filter, query, etc.
    It a way to compile a set, and then run through a transaction.
    '''

    def __init__(self):
        self.objects = []


    def get_kinds(self,client):
        '''get_kinds'''
        query = client.query(kind='__kind__')
        query.keys_only()
        return [entity.key.id_or_name for entity in query.fetch()]


    def add(self,task):
        '''return all objects in the set
        '''
        if not isinstance(task,datastore.Entity):
            task = task.this
        self.objects.append(task)

        

    def get(self,client,keys):
        '''get will return a list of tasks based on keys, where each
        key is a single key or a model key type (eg "Collection") and
        corresponding identifier Eg:

          keys = ["Collection",["Entity",12345]]

        '''
        with parse_keys(keys) as keys:
            return client.get_multi(keys)



    def delete(self,client,keys):
        '''delete a set of model objects based on user provided keys'''
        with parse_keys(keys) as keys:
            return client.delete_multi(keys) # note sure if returning this 
                                             # returns a status or nothing
                                             # same for get, need to test
                                             # (currently on airplane)


    def insert(self,client,clear_queue=True):
       '''insert will run a transaction for a set of tasks
       '''
       if len(self.objects) > 0:
           tasks = self.objects
           with client.transaction():
               client.put_multi(tasks)
               if clear_queue:
                   self.objects = []
               return tasks
       return None


    def query(self,client,kind=None,filters=None,order=None,projections=None,
              run=True,limit=None,keys_only=False,distinct_on=None,query=None,
              ancestor=None):
        '''query will run a query for some kind of model (eg 'Collection')
        :param kind: the kind of model to query
        :param filters: a list of lists of tuples, each length 3, with 
        :param order: optional one or more orderings -descending / ascending
        :param projections: if defined, return a dictionary of lists of each
        :param run: Default true to execute query. False returns query object
        :param limit: an integer limit of results to return
        :param distinct_on: one or more fields to make distinct
        :param query: if provided, will not start with basic query
        :param ancestor: if provided, query for the provided ancestor
                       
             FIELD OPERATOR VALUE
             "description" "=' "this is a description" 
         
             ANCESTOR EXAMPLE
             ancestor = client.key('TaskList', 'default')

        '''
        if ancestor is not None:
            if isinstance(ancestor,list) or isinstance(ancestor,str):
                ancestor = client.key(*ancestor)

        if query == None:
            if kind is None:
                bot.logger.error("You must define 'kind' to run a query.")
                sys.exit(1)
            query = client.query(kind=kind.upper(),ancestor=ancestor) # uppercase first letter

        if distinct_on != None:
            if not isinstance(distinct_on,list):
                distinct_on = [distinct_on]
            query.distinct_on = ['category', 'priority']

        # Add filters to the query
        if filters is not None:
            for f in filters:
                query.add_filter(f[0], f[1],f[2])

        # Apply order to the query (eg, ['-priority']
        if order is not None:
            if not isinstance(order,list):
                order = [order]
            query.order = order

        # Return a projection, an extraction of fields from a set
        if projections is not None:
            return self.projection(client,query,projections)

        if keys_only:
            query.keys_only()
  
        # Do we not want to run the query?
        if not run:
            return query

        result = None

        try:
            if keys_only:
                result = list([e.key for e in query.fetch(limit=limit)])
            else:
                result = list(query.fetch(limit=limit))

        except (google.cloud.exceptions.BadRequest,
                google.cloud.exceptions.GrpcRendezvous):
            bot.logger.error("Error with query.")         
            pass

        return result


    def query_key(self,client,kind,keys,**kwargs):
        '''query_key is an entry to query that adds a key filter to the query
        '''
        if operator == None:
            operator = '>'

        if operator not in get_key_filters():
            bot.logger.error("%s is not a valid operator.", operator)
            sys.exit(1)

        keys = parse_keys(keys)
        query = client.query(kind=kind)
        for key in keys:
            query.key_filter(key, operator)

        return self.query(client,**kwargs)



    def query_date(self,client,kind,startyear=None,startday=None,startmonth=None,
                   endyear=None,endday=None,endmonth=None,**kwargs):
        '''query_date is an entry to query that sets up a date filter.
        '''
        start_date = None
        end_date=None
        if startyear is not None and startday is not None and startmonth is not None:
            start_date = datetime.datetime(startyear, startmonth, startday)
        if endyear is not None and endmonth is not None and endday is not None:
            end_date = datetime.datetime(endyear, endmonth, endday)
        if start_date == None and end_date == None:
            bot.logger.warning('''Both start date and end date are null, did you provide
                                  year, month, day for one or both?''')
     
        query = client.query(kind=kind)
        if start_date is not None:
            query.add_filter('created', '>', start_date)
        if end_date is not None:
            query.add_filter('created', '<', end_date)
     
        return self.query(client,**kwargs)
        

    def projection(self,client,query,projections,add_loners=False):
        '''extract a subset of a query, meaning a dictionary with key value
        pairs for field/results lists. By default, to preserve indexing,
        only objects with all projection fields are added to the result.
        You can change this behavior by setting add_loners = True
        ''' 
        if not isinstance(projections,list):
            projections = [projections]

        # Find a more elegant way to do this
        results = dict()
        for projection in projections:
            results[projection] = []
                    
        for task in query.fetch():
            loner = False
            for p in projections: 
                if p not in task:
                    longer=True
                    break

            # Find more elegant way to not need to loop twice    
            for p in projections:
                if not loner or (loner and add_loners):
                    results[p].append(task[p])

        return results




######################################################################################
# Base Client Class
######################################################################################

# https://cloud.google.com/datastore/docs/concepts/entities#datastore-basic-entity-python

class ModelBase:

    def __init__(self,client):
        self.fields = validate_model(self.model['fields'])
        self.key = client.key(*self.model['key'])
        if "exclude_from_indexes" in self.model:
            self.exclude_from_indexes = self.model['exclude_from_indexes'] # Can be None
        else:
            self.exclude_from_indexes = None

    def __str__(self):
        return print_datastore_path(self.key)

    def __repr__(self):
        return print_datastore_path(self.key)


    def get_keypath(self):
        return list(self.key.flat_path)
      

    def get_name(self):
        return list(self.key.flat_path)[-1]


    def update_key(self,client,key):
        '''update key will add a key to a model, and return a 
        unique set of keys
        '''
        if key is not None:
           flat_key = list(self.key.flat_path)
           if isinstance(key,list):
               flat_key = flat_key + key
           else: 
               flat_key.append(key)
           self.key = client.key(*flat_key)


    def update_fields(self,new_fields,add_new=True):
        '''update fields will update the model's fields with an input dictionary
        new fields are added if add_new=True (default)
        '''
        for key,value in new_fields.items():
            if key in self.fields:
                self.fields[key] = value
            else:
                if add_new == True:
                    self.fields[key] = value


    def get_or_create(self,client,key=None):
        '''get_or_create will get or create an object using a transaction.
        '''
        with client.transaction():
           self.update_key(client,key)
           entity = client.get(*self.key)

           # The entity is being created, add timestamp
           if not entity:
               entity = self.create(client)
        return entity


    def setup(self,client,fields=None):
        '''setup will generate a new Entity without saving it (for batches)
        '''
        if self.exclude_from_indexes is not None:
            entity = datastore.Entity(key=self.key,
                                      exclude_from_indexes=self.exclude_from_indexes)
        else:
            entity = datastore.Entity(self.key)
        if fields is not None:
            self.fields.update(fields)
        return entity


    def create(self,client,fields=None):
        '''create a new entity
        '''
        entity = self.setup(client,fields)
        self.fields['created'] = datetime.datetime.utcnow()
        self.fields['updated'] = datetime.datetime.utcnow()
        for field,value in self.fields.items():
            entity[field] = value
        client.put(entity)
        return entity


    def delete(self,client):
        '''delete an entity'''
        client.delete(self.key)
        return key


    def update_or_create(self,client,fields=None):
        '''update or create will update or create an entity.
        '''
        entity = client.get(self.key)

        # The entity is being created, add timestamp
        if not entity:
           entity = self.create(client)            #insert
        else: 
            entity = self.update(client,fields) #upsert
        return entity


    def update(self,client,fields=None,key=None):
        '''update an entity. Returns None if does not exist.'''
        entity = None
        with client.transaction():
           entity = client.get(self.key)
           if entity:
               if fields is not None:
                   self.update_fields(fields)

               self.fields['updated'] = datetime.datetime.utcnow()

               for field,value in self.fields.items():
                   entity[field] = value
        return entity


    def get(self,client):
        '''get an entity. Returns None if does not exist.'''
        entity = None
        with client.transaction():
           entity = client.get(self.key)
        return entity
