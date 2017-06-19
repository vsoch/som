'''
google/modals.py: models for datastore

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from som.api.google.storage.validators import (
    validate_model
)

import google.cloud.datastore as datastore
from som.api.google.storage.datastore import (
    get_key_filters,
    parse_keys
)

from som.logger import bot
import datetime
import collections
import sys
import os

######################################################################################
# Object Manager
######################################################################################

class BatchManager:
    '''a batch manager is bucket to hold multiple objects to filter, query, etc.
    It a way to compile a set, and then run through a transaction. It must either
    be instantiated with a client, or one is generated dynamically.
    '''

    def __init__(self,client=None):
        if client is None:
            client = datastore.Client()
        self.client = client
        self.tasks = []
        self.queries = []

    def get_kinds(self):
        query = self.client.query(kind='__kind__')
        query.keys_only()
        return [entity.key.id_or_name for entity in query.fetch()]


    def get(self,kind,keys=None,limit=None,field=None,keys_only=False,ancestor=None):
        if keys is None:
            return self.query(kind=kind,
                              limit=limit,
                              ancestor=ancestor,
                              keys_only=keys_only)
        else:
            if not isinstance(keys,list):
                keys = [keys]
            if field is None:
                return self.client.get_multi(keys)
            else:
                for key in keys:
                    query = self.client.query(kind=kind.capitalize())
                    query.add_filter(field,'=',key)
                    self.add(query)
                return self.runQueries()                    


    def add(self,task):
        '''return all tasks in the set
        '''
        if isinstance(task,datastore.query.Query):
            self.queries.append(task)
        else:
            if not isinstance(task,datastore.Entity):
                task = task._Entity
            self.tasks.append(task)


    def delete(self,keys):
        '''delete a set of model objects based on user provided keys'''
        with parse_keys(keys) as keys:
            return self.client.delete_multi(keys) # note sure if returning this 
                                                  # returns a status or nothing
                                                  # same for get, need to test
                                                  # (currently on airplane)



    def runInsert(self,clear_queue=True):
       '''runInsert will run a transaction for a set of tasks
       '''
       tasks = None
       if len(self.tasks) > 0:
           tasks = self.tasks
           with self.client.transaction():
               self.client.put_multi(tasks)
           if clear_queue:
               self.tasks = []
       return tasks
       

    def runQueries(self,clear_queue=True):
       results = None
       if len(self.queries) > 0:
           results = []
           for query in self.queries:
               result = [x for x in query.fetch()]
               results = results + result
           if clear_queue:
               self.queries = []
       return results


    def query(self,kind=None,filters=None,order=None,projections=None,
              run=True,limit=None,keys_only=False,distinct_on=None,query=None,
              ancestor=None):
        '''query will run a query for some kind of model (eg 'Collection')
        :param kind: the kind of model to query
        :param filters: a list of lists of tuples, each length 3, with

             FIELD OPERATOR VALUE
             "description" "=' "this is a description" 
 
        :param order: optional one or more orderings -descending / ascending
        :param projections: if defined, return a dictionary of lists of each
        :param run: Default true to execute query. False returns query object
        :param limit: an integer limit of results to return
        :param distinct_on: one or more fields to make distinct
        :param query: if provided, will not start with basic query
        :param ancestor: if provided, query for the provided ancestor
                                
             ANCESTOR EXAMPLE
             ancestor = client.key('TaskList', 'default')

        '''
        if ancestor is not None:
            if isinstance(ancestor,list) or isinstance(ancestor,str):
                ancestor = self.client.key(*ancestor)

        if query == None:
            if kind is None:
                bot.error("You must define 'kind' to run a query.")
                sys.exit(1)
            query = self.client.query(kind=kind.capitalize(),ancestor=ancestor) # uppercase first letter

        if distinct_on is not None:
            if not isinstance(distinct_on,list):
                distinct_on = [distinct_on]
            query.distinct_on = distinct_on

        # Add filters to the query
        if filters is not None:
            for f in filters:
                query.add_filter(f[0], f[1],f[2])

        # Apply order to the query (eg, ['-priority']
        if order is not None:
            if not isinstance(order,list):
                order = [order]
            order = [x.lower() for x in order]
            query.order = order

        # Return a projection, an extraction of fields from a set
        if projections is not None:
            return self.projection(query,projections)

        if keys_only is True:
            query.keys_only()
  
        # Do we not want to run the query?
        if not run:
            return query

        result = None

        try:
            result = [x for x in query.fetch(limit=limit)]

        except (google.cloud.exceptions.BadRequest,
                google.cloud.exceptions.GrpcRendezvous):
            bot.error("Error with query.")         
            pass

        return result


    def query_key(self,kind,keys,**kwargs):
        '''query_key is an entry to query that adds a key filter to the query
        '''
        if operator == None:
            operator = '>'

        if operator not in get_key_filters():
            bot.error("%s is not a valid operator." %operator)
            sys.exit(1)

        keys = parse_keys(keys)
        query = self.client.query(kind=kind)
        for key in keys:
            query.key_filter(key, operator)

        return self.query(**kwargs)



    def query_date(self,kind,startyear=None,startday=None,startmonth=None,
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
            bot.warning('''Both start date and end date are null, did you provide
                           year, month, day for one or both?''')
     
        query = self.client.query(kind=kind)
        if start_date is not None:
            query.add_filter('created', '>', start_date)
        if end_date is not None:
            query.add_filter('created', '<', end_date)
     
        return self.query(**kwargs)
        

    def projection(self,query,projections,add_loners=False):
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

    def __init__(self,client=None):
        '''A ModelBase is a controller for a general DataStore
        Entity. Most of the variables in init are for initial
        validation, and further fields etc are stored with
        the Entity itself (_Entity)
        :param client: the datastore client, should be passed on init
        :param _fields: intiial fields to validate on model creation
        :param _key: the initial key used for the entity
        :param _Entity: the final generated (validated) entity
        '''
        if client is None:
            client = datastore.Client()
        self.client = client
        self._fields = validate_model(self.model['fields'])
        self._key = self.client.key(*self.model['key'])
        self._Entity = None
        if "exclude_from_indexes" in self.model:
            self._exclude_from_indexes = self.model['exclude_from_indexes'] # Can be None
        else:
            self._exclude_from_indexes = None

    def __repr__(self):
        if self._Entity is None:
            return "Entity:None"
        return str(self._Entity.key)

    def __str__(self):
        if self._Entity is None:
            return "Entity:None"
        return str(self._Entity.key)


    def get_keypath(self):
        return list(self._Entity.key.flat_path)
      
    def get_name(self):
        return list(self._Entity.key.flat_path)[-1]


    def update_fields(self,new_fields,add_new=True):
        '''update fields will update the model's fields with an input dictionary
        new fields are added if add_new=True (default). This does not by default save
        the entity.
        '''
        for key,value in new_fields.items():
            if key not in self._Entity.keys():
                bot.debug("adding %s to Entity" %(key))
                self._Entity[key] = value
            else:
                if add_new == True:
                    bot.debug("%s found existing in Entity, overwriting" %(key))
                    self._Entity[key] = value


    def get_or_create(self):
        '''get_or_create will get or create an object using a transaction.
        If an entity object already exists with the object, it is overridden
        '''
        with self.client.transaction():
           self._Entity = self.client.get(*self._key)
           if not self._Entity:
               self._Entity = self.create()
        return self._Entity


    def setup(self,fields=None):
        '''setup will generate a new Entity without saving it (for batches)
        '''
        if self._exclude_from_indexes is not None:
            self._Entity = datastore.Entity(key=self._key,
                                            exclude_from_indexes=self._exclude_from_indexes)
        else:
            self._Entity = datastore.Entity(self._key)
        if fields is not None:
            self.update_fields(fields)


    def save(self):
        '''save just calls put for the current _Entity'''
        self.client.put(self._Entity)


    def create(self,fields=None,save=True):
        '''create a new entity
        :param fields: additional fields to add
        :param save: save the entity to datastore (default True)
        '''
        self.setup(fields)
        self._Entity['created'] = datetime.datetime.utcnow()
        self._Entity['updated'] = datetime.datetime.utcnow()
        # Add initial fields, if defined
        for field,value in self._fields.items():
            self._Entity[field] = value
        if save:
            self.save()
        return self._Entity


    def delete(self):
        '''delete an entity'''
        key = None
        if self._Entity is not None:
            key = self._Entity.key
            self.client.delete(key)
            bot.debug("Deleting %s" %(key))
        return key


    def update_or_create(self,fields=None,save=True):
        '''update or create will update or create an entity.
        '''
        entity = self.client.get(self._key)

        # The entity is being created, add timestamp
        if not entity:
            entity = self.create(fields,save)         #insert
        else: 
            entity = self.update(fields,save)        #upsert
        return self._Entity


    def update(self,fields=None,save=True):
        '''update an entity, meaning updating the local and then pushing
        (saving) to the datastore. This overrides the datastore version
        by default. To simply get the datastore version and override
        the local, use get'''
        if self._Entity is None:
            self._Entity = self.client.get(self._key)
        self._Entity['updated'] = datetime.datetime.utcnow()
        # Update any fields
        if fields is not None:
            for field,value in fields.items():
                self._Entity[field] = value
        if save:
            self.save()
        return self._Entity


    def get(self):
        '''get an entity, and override the currently set _Entity in the model
        if it is not retrieved yet. If already retrieved, does not update.
        '''
        if self._Entity is None:
            with self.client.transaction():
                self._Entity = self.client.get(*self._key)
        return self._Entity
