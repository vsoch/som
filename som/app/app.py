from flask import (
    Flask, 
    render_template, 
    request
)

from som.wordfish.structures import structure_folder

from flask_restful import Resource, Api
from werkzeug import secure_filename
import webbrowser
import tempfile
import shutil
import random
import os

# SERVER CONFIGURATION ##############################################
class SomServer(Flask):

    def __init__(self, *args, **kwargs):
        super(SomServer, self).__init__(*args, **kwargs)

        # Set up temporary directory on start of application
        self.tmpdir = tempfile.mkdtemp()
        self.folder = None  # Dataset folder
        self.dataset = {} # Dataset json


# API VIEWS #########################################################
# eventually we can have views or functions served in this way...

app = SomServer(__name__)
api = Api(app)

class apiIndex(Resource):
    '''apiIndex
    Main view to show the entire dataset
    '''
    def get(self):
        return app.dataset


#class apiViewImage(Resource):
#    '''apiViewImage
#    shows an image 
#    '''
#    def get(self, url):
#        return {"ids": subset.id.tolist(),
#                "words":difference.index.tolist()}
              
# Add all resources
#api.add_resource(apiIndex,'/api/dataset') # start month, day, year / end month, date, year
#api.add_resource(apiViewImage,'/api/dataset/image/<path:url>')


@app.route('/som/annotate')
def annotate_images():
    return render_template('annotate_images.html')

@app.route('/som/dataset/explore')
def dataset_explorer():
    app.folder = 'cookies'
    app.dataset = structure_folder(app.folder,relative_path=True)
    collection_name = app.dataset['collection']['name']
    entities = app.dataset['collection']['entities']
    return render_template('dataset_explorer.html',entities=entities,
                                                   collection_name=collection_name)



# START FUNCTIONS ##################################################
    
# View a dataset folder
def run_dataset_explorer(folder,port=None):
    app.dataset = structure_folder(folder,relative_path=True)
    if port==None:
        port=8088
    print("It goes without saying. I suspect now it's not going.")
    webbrowser.open("http://localhost:%s/som/dataset/explorer" %(port))
    app.run(host="0.0.0.0",debug=False,port=port)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
