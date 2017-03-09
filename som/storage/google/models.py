'''
google/modals.py: models for datastore

'''

from som.storage.google.validators import (
    validate_model
)

from som.storage.google.datastore import (
    get_key_filters,
    parse_keys,
    print_datastore_path
)

from som.logman import bot
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
        self.objects.push(task)


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
       '''run will run a transaction for a set of tasks
       '''
       if len(self.objects) > 0:
           tasks = self.objects
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
        self.fields = self.model['fields']
        self.key = self.model['key']
        self.exclude_from_indexes = self.model['exclude_from_indexes'] # Can be None

    def __str__(self):
        return print_datastore_path(self.key)

    def __repr__(self):
        return print_datastore_path(self.key)


    def update_key(self,key):
        '''update key will add a key to a model, and return a 
        unique set of keys
        '''
        if key is not None:
           self.key.append(key)
           self.key = list(set(self.key))

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
           self.update_key(key)
           entity = client.get(client.key(*self.key))

           # The entity is being created, add timestamp
           if not entity:
               entity = self.create(client)
        return entity


    def create(self,client):
        '''create a new entity
        '''
        key = client.key(*self.key)
        if self.exclude_from_indexes is not None:
            entity = datastore.Entity(key=key,
                                      exclude_from_indexes=self.exclude_from_indexes)
        else:
            entity = datastore.Entity(key)
        self.fields['created'] = datetime.datetime.utcnow()
        self.fields['updated'] = datetime.datetime.utcnow()
        entity.update(self.fields)
        client.put(entity)
        return entity


    def delete(self,client):
        '''delete an entity'''
        key = client.key(*self.key)
        client.delete(key)
        return key


    def update_or_create(self,client,fields):
        '''update or create will update or create an entity.
        '''
        key = client.key(*self.key)
        with client.transaction():
           entity = client.get(client.key(key))

           # The entity is being created, add timestamp
           if not entity:
               entity = self.create(client)            #insert
           else: 
               entity = self.update(client,fields) #upsert
        return entity


    def update(self,client,fields,key=None):
        '''update an entity. Returns None if does not exist.'''
        entity = None
        key = client.key(*self.key)
        with client.transaction():
           entity = client.get(client.key(key))
           if entity:
               update_fields(fields)
               self.fields['updated'] = datetime.datetime.utcnow()
               entity.update(self.fields)
        return entity


    def get(self,client,fields):
        '''get an entity. Returns None if does not exist.'''
        entity = None
        key = client.key(*self.key)
        with client.transaction():
           entity = client.get(client.key(key))
        return entity




######################################################################################
# Specs and Validation for Collection, Entity, Image
######################################################################################


def entity(uid,collection,metadata=None):
    '''entity returns an entity object
    parent is a collection
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'metadata','required':False,'value':metadata}]

    model = {'fields':fields,
             'key':['Collection',collection,'Entity', uid]}

    return model



def collection(name,description=None,metadata=None):
    '''entity returns an entity object
    parent is an owner
    '''
    fields = [{'key':'name','required':True,'value':name},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata}]

    model = {'fields':fields,
             'exclude_from_indexes': ['metadata','description'],
             'key':['Collection', name]}
    return model
    


def image(uid,entity,file_path,description=None,metadata=None):
    '''image returns an image object. entity is the parent
    '''
    fields = [{'key':'name','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata},
              {'key':'file_path','required':True,'value':file_path}]

    model = {'fields':fields,
             'key':['Entity',entity,'Image', uid]}
    return model
    


def text(uid,entity,file_path,description=None,metadata=None):
    '''text returns a text object. entity is the parent
    '''
    fields = [{'key':'uid','required':True,'value':uid},
              {'key':'description','required':False,'value':description},
              {'key':'metadata','required':False,'value':metadata},
              {'key':'file_path','required':True,'value':file_path}]

    model =  {'fields':fields,
             'key':['Entity',entity,'Text', uid]}
    return model




######################################################################################
# Core Models
######################################################################################

class Collection(ModelBase):
  
    def __init__(self,client,collection_name,**kwargs):
        self.model = collection(name=collection_name,**kwargs)
        self.model['fields'] = validate_model(self.model['fields'])
        super(Collection, self).__init__(client,**kwargs)
        self.this = self.get_or_create(client)


class Entity(ModelBase):

    def __init__(self,client,collection_name,**kwargs):
        self.collection = collection_name
        self.model = entity(uid=uid,
                            collection_name=collection_name,**kwargs)
        self.model['fields'] = validate_model(self.model['fields'])
        self.this = self.get_or_create(client)
        super(Entity, self).__init__(**kwargs)

   
    def collection(self,client):
        '''collection will return the collection associated with
        the entity
        '''
        return client.get(client.key("Collection",self.collection))


    def images(self,client):
        '''images will return images associated with the entity
        '''
        return client.get(client.key(*self.key, "Images"))
    

    def text(self,client):
        '''text will return text associated with the entity
        '''
        return client.get(client.key(*self.key, "Text"))


class Image(ModelBase):

    def __init__(self,client,entity_id,**kwargs):
        self.entity = entity_id
        self.model = image
        self.model['fields'] = validate_model(self.model['fields'])
        self.this = self.get_or_create(client)
        super(Image, self).__init__(**kwargs)

    def __repr__(self):
        return self.this


class Text(ModelBase):

    def __init__(self,client,entity_id,**kwargs):
        self.entity = entity_id
        self.model = text
        self.model['fields'] = validate_model(self.model['fields'])
        self.this = self.get_or_create(client)
        super(Text, self).__init__(**kwargs)

    def __repr__(self):
        return self.this
