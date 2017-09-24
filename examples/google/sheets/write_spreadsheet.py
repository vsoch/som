
'''
You will first want to generate an application credential file, and export
path to environment variable GOOGLE_SHEETS_CREDENTIALS

GOOGLE_SHEETS_CREDENTIALS=/path/to/client_secrets.json
export GOOGLE_SHEETS_CREDENTIALS

'''

from som.api.google.sheets import Client
from datetime import datetime, timedelta

sheet_id = "1aw3WUx7iDA3qNEBBHCKuDj252Lx5hAxj_G2LCSW0-R4"
gb_day = 315

cli = Client()

# Define date range for metric
start_date = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
end_date = datetime.now().strftime("%m/%d/%Y")

# Get previous values
values = cli.read_spreadsheet(sheet_id)

# Create row, append
# pipeline	start_date	end_date	duration (days)	G/day GetIt	G/day SendIt
# Define new row, add

row = [1,              # pipeline
       start_date,     # start_date
       end_date,       # end_date
       None,           # duration (days)
       None,           # G/day GetIt
       amount,         # G/day SendIt
       None,           
       None,
       None,
       None,
       None]

values.append(row)

# Update sheet
result = cli.write_spreadsheet(sheet_id, values)
