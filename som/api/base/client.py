'''
client.py: simple clients for som api

'''

from som.api.base.connect import (
    api_base,
    api_version,
    SomApiConnection
)

from som.api.base.standards import spec
from som.logman import bot

class ClientBase(object):


    def __init__(self, spec=None, token=None, base=None, version=None):
 
        # Base and version consistent across
        if base == None:
            base = api_base

        if version == None:
            version = api_version

        self.base = base
        self.version = version
        self.study = None

        if spec != None:
            self.spec = spec

        self.api = SomApiConnection(token)


    def get_base(self,study=None):
        '''get_base returns the base api for a particular study
        '''
        if study is None:
            study = self.study
        return "%s/%s/%s" %(self.base,self.version,study)


    def deidentifiy_update(self,identifiers,test=False):
        '''deidentify update calls deidentify, but setting save_records
        to True to ensure that data is updated/written.
        '''
        return self.deidentify(identifiers,test=test,save_records=True)


    def deidentify(self,ids,test=False,save_records=False):
        '''deidentify will take a list of identifiers, and return the deidentified.
        if save_records is True, will save records. If False (default) only
        returns identifiers.
        :param identifiers: a list of identifiers (e.g., people)
        '''    
        # Default is production endpoint particular to the study
        study = self.study

        # Saving records (uid) or not (mrn) changes the endpoint
        action = "mrn"
        if save_records == True:
            bot.logger.debug("save_records is %s, no new data will be saved.")
            action = "uid"
        else:
            bot.logger.debug("save_records is %s, data will be saved.")

        # Testing overrides all other specifications
        if test == True:
            study = 'test'

        url = "%s/%s/%s/%s" %(api_base,api_version,action,study)

        response = self.api.post(url,data=ids)
        if "results" in response:
            return response['results']
        return response
