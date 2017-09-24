
'''
You will first want to generate an application credential file, and export
path to environment variable GOOGLE_SHEETS_CREDENTIALS

GOOGLE_SHEETS_CREDENTIALS=/path/to/client_secrets.json
export GOOGLE_SHEETS_CREDENTIALS

'''

from som.api.google.sheets import Client

sheet_id = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
cli = Client()
values = cli.read_spreadsheet(sheet_id)
