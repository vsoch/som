'''
google/modals.py: models for datastore

'''

from som.api.google.storage.validators import (
    validate_model
)

import google.cloud.datastore as datastore
from som.api.google.storage.datastore import (
    get_key_filters,
    parse_keys
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
            task = task._Entity
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
        '''A ModelBase is a controller for a general DataStore
        Entity. Most of the variables in init are for initial
        validation, and further fields etc are stored with
        the Entity itself (_Entity)
        :param _fields: intiial fields to validate on model creation
        :param _key: the initial key used for the entity
        :param _Entity: the final generated (validated) entity
        '''
        self._fields = validate_model(self.model['fields'])
        self._key = client.key(*self.model['key'])
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
                bot.logger.debug("adding %s to Entity" %(key))
                self._Entity[key] = value
            else:
                if add_new == True:
                    bot.logger.debug("%s found existing in Entity, overwriting" %(key))
                    self._Entity[key] = value


    def get_or_create(self,client):
        '''get_or_create will get or create an object using a transaction.
        If an entity object already exists with the object, it is overridden
        '''
        with client.transaction():
           self._Entity = client.get(*self._key)
           if not self._Entity:
               self._Entity = self.create(client)
        return self._Entity


    def setup(self,client,fields=None):
        '''setup will generate a new Entity without saving it (for batches)
        '''
        if self._exclude_from_indexes is not None:
            self._Entity = datastore.Entity(key=self._key,
                                            exclude_from_indexes=self._exclude_from_indexes)
        else:
            self._Entity = datastore.Entity(self._key)
        if fields is not None:
            self.update_fields(fields)


    def save(self,client):
        '''save just calls put for the current _Entity'''
        client.put(self._Entity)


    def create(self,client,fields=None,save=True):
        '''create a new entity
        :param client: the datastore client
        :param fields: additional fields to add
        :param save: save the entity to datastore (default True)
        '''
        self.setup(client,fields)
        self._Entity['created'] = datetime.datetime.utcnow()
        self._Entity['updated'] = datetime.datetime.utcnow()
        # Add initial fields, if defined
        for field,value in self._fields.items():
            self._Entity[field] = value
        if save:
            self.save(client)
        return self._Entity


    def delete(self,client):
        '''delete an entity'''
        key = None
        if self._Entity is not None:
            key = self._Entity.key
            client.delete(key)
            bot.logger.debug("Deleting %s" %(key))
        return key


    def update_or_create(self,client,fields=None,save=True):
        '''update or create will update or create an entity.
        '''
        entity = client.get(self._key)

        # The entity is being created, add timestamp
        if not entity:
           entity = self.create(client,fields,save)         #insert
        else: 
            entity = self.update(client,fields,save)        #upsert
        return self._Entity


    def update(self,client,fields=None,save=True):
        '''update an entity, meaning updating the local and then pushing
        (saving) to the datastore. This overrides the datastore version
        by default. To simply get the datastore version and override
        the local, use get'''
        if self._Entity is None:
            self._Entity = client.get(self._key)
        self._Entity['updated'] = datetime.datetime.utcnow()
        # Update any fields
        if fields is not None:
            for field,value in fields.items():
                self._Entity[field] = value
        if save:
            self.save(client)
        return self._Entity


    def get(self,client):
        '''get an entity, and override the currently set _Entity in the model
        if it is not retrieved yet. If already retrieved, does not update.
        '''
        if self._Entity is None:
            with client.transaction():
                self._Entity = client.get(*self._key)
        return self._Entity