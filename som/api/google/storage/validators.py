'''
validators.py simple validation and cleaning of model data structures

'''

def validate_model(fields):
    '''remove_nones will remove any None fields from a passed dictionary
    '''
    keepers = dict()
    for entry in fields:
        if entry['value'] is not None:
            keepers[entry['key']] = entry['value']
        else:
            if entry['required'] == True:
                bot.logger.error("Field %s is required for this entity.",entry['key'])
    return keepers

