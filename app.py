from flask import Blueprint, Flask, jsonify
from flasgger import Swagger
from flasgger.utils import swag_from
from flask.views import MethodView
import sys
from collections import namedtuple
import collections
sys.path.append('./utils')
sys.path.append('./conf')
sys.path.append('./common')
from redis_utils import RedisUtils
from config_utils import ConfigurationReader
import json
import requests
"""

HMSET 100 file_id 100 file_name f_100 description desc1 platform A creation_time 11-08-2020-10:00:00
HMSET 101 file_id 101 file_name f_101 description desc1 platform A creation_time 11-08-2020-10:00:00
HMSET 102 file_id 102 file_name f_102 description desc1 platform A creation_time 11-08-2020-10:00:00
HMSET 103 file_id 103 file_name f_103 description desc1 platform A creation_time 11-08-2020-10:00:00
HMSET 104 file_id 104 file_name f_104 description desc1 platform A creation_time 11-08-2020-10:00:00

HMSET 105 file_id 105 file_name f_105 description desc1 platform A deletion_time 11-08-2020-10:00:00
HSET 100 downloaded_by

"""

class RedisConfigurationReader(ConfigurationReader):
    def __init__(self, config_file):
        super().__init__(config_file)

    def get_redis_settings(self):
        try:
            return self.configuration["redis_cache_settings"]
        except KeyError:
            raise Exception(
                'The  redis configurations are not configured, please configure in yml file'
            )

r = RedisUtils()
config = RedisConfigurationReader('./conf/redis_settings.yml')
config.read_config_file()
r.strict_connect(**config.get_redis_settings())
print(r.__dict__)

app = Flask(__name__)

example_blueprint = Blueprint("example_blueprint", __name__)

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Flasgger",
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        ('Access-Control-Allow-Credentials', "true"),
    ],
    "specs": [
        {
            "version": "0.0.1",
            "title": "Api v1",
            "endpoint": 'v1_spec',
            "description": 'API for gathering information to  analyze the behavior of a file in relation to other files',
            "route": '/v1/spec',
            "rule_filter": lambda rule: rule.endpoint.startswith(
                'should_be_v1_only'
            ),
            # definition_filter is optional
            # it is a callable to filter the definition models to include
            "definition_filter": lambda definition: (
                'v1_model' in definition.tags)
        },
        {
            "version": "0.0.2",
            "title": "Api v2",
            "description": 'API for gathering information to  analyze the behavior of a file in relation to other files',
            "endpoint": 'v2_spec',
            "route": '/v2/spec',
            "rule_filter": lambda rule: rule.endpoint.startswith(
                'should_be_v2_only'
            ),
            "definition_filter": lambda definition: (
                'v2_model' in definition.tags)
        }
    ]
}


class DictionaryObject(object):
    """
    Turns a python dictionary into a class
    """

    def __init__(self, dictionary, class_name="object"):
        """Constructor"""
        self.class_name = class_name
        for a, b in dictionary.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a.lower(), [
                    DictionaryObject(x) if isinstance(x, dict) else x
                    for x in b
                ])
            else:
                setattr(self, a.lower(),
                        DictionaryObject(b) if isinstance(b, dict) else b)

    def covert_to_flat_dict(self, d, parent_key='', sep='_', to_upper=False):
        """
            convert the nested dictionary to a flat dictionary
        """
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if to_upper:
                new_key = new_key.upper()
            if isinstance(v, collections.MutableMapping):
                items.extend(
                    self.covert_to_flat_dict(
                        v, new_key, sep=sep, to_upper=to_upper).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def __repr__(self):
        """"""
        return "<{}: {}>".format(self.class_name, self.__dict__)

swag = Swagger(app)  # you can pass config here Swagger(config={})

# file schema definitions 
class FileAPI(MethodView):

    def get(self, file_id):
        """
        Get a list of files
        First line is the summary
        All following lines until the hyphens is added to description
        ---
        tags:
          - files
        parameters:
          - name: file_id
            in: path
            description: ID of file (type any number)
            required: true
            type: integer
            default: 100
        responses:
          200:
            description: Returns a list of files
            schema:
                type: array
                items:
                    $ref: '#/definitions/File'
        """
        data = {
            "file": [
                {"name": "Fil01", "file_id": file_id,"platform" :"platform1", "creation_date":'12/10/2020-10:04:00'},

            ]
        }
        return jsonify(data)

    def post(self):
        """
        Create a new file
        First line is the summary
        All following lines until the hyphens is added to description
        ---
        tags:
          - files
        parameters:
          - in: body
            name: body
            schema:
              id: File
              required:
                - name
                - description 
                - creation_date
                - platform 
                - file_id
              properties:
                file_id:
                  type: integer
                  description: id for file
                  default: 100
                name:
                  type: string
                  description: description for file
                  default: File-<>
                creation_date:
                  type: date-time
                  description: name for file
                  default: File-<>
                platform:
                  type: string
                  description: platform for file
                  default: File-<>
                description:
                  type: string
                  description: description for file
                  default: File-<>
                
        responses:
          201:
            description: New file created
            schema:
                type: array
                items:
                    $ref: '#/definitions/File'
          import: "not_found.yaml"
        """
        return jsonify(
            {"data": request.json, "status": "New file created"}
        ), 201


view = FileAPI.as_view('files')
app.add_url_rule(
    '/v1/files/<int:file_id>',
    view_func=view,
    methods=['GET'],
    endpoint='should_be_v1_only'
)
app.add_url_rule(
    '/v1/files',
    view_func=view,
    methods=['POST'],
    endpoint='should_be_v1_only_post'
)

# app routes for the views
@app.route('/v1/files/<int:file_id>/downloadspec', endpoint='should_be_v1_only_downloads')
@swag_from('file_download_specs.yml')
def get_download_specification(file_id):
    return jsonify({'file_name': "file_name"})


@app.route('/v1/files/<int:file_id>/executespec', endpoint='should_be_v1_only_execution')
@swag_from('file_execution_specs.yml')
def get_execution_specification(file_id):
    return jsonify({'file_name': "file_name"})


@app.route('/v1/files/<int:file_id>/deletespec', endpoint='should_be_v1_only_deletion')
@swag_from('file_deletion_specs.yml')
def get_deletion_specification(file_id):
    return jsonify({'file_name': "file_name"})


# Add metadata about a file and its relationships to other files in the system
"""
This is the test result end point to demonstrate the output
"""
@app.route('/v1/files/<int:file_id>/metadataspec', endpoint='should_be_v1_only_metadata')
@swag_from('file_metadata_specs.yml')
def get_metadata_specification(file_id):
    return jsonify(
          {
            "download_specs": [
                {"file_name":"Fil01", "file_id": file_id, "platform": "platform1", "creation_date": '12/10/2020-10:04:00'}
            ],
            "deletion_specs": [
                {"file_name": "Fil01", "file_id": file_id,
                    "platform": "platform1", "creation_date": '12/10/2020-10:04:00'}
            ],
            "execution_specs":[
                {"file_name": "Fil01", "file_id": file_id,
                    "platform": "platform1", "creation_date": '12/10/2020-10:04:00'}
            ]}
    )

"""
 Implementation of Given a file, list all files that downloaded/executed/deleted it

"""
@app.route('/v1/files/<int:file_id>/metadataspecR', endpoint='should_be_v1_only_metadataR')
@swag_from('file_metadata_specs.yml')
def get_metadata_specification_v2(file_id):

    output_result ={}
    relation_markers =["downloaded_by","executed_by","deleted_by"]
    for item in relation_markers:
        try:
            output_arr = []
            print(str(item)+":"+str(file_id))
            stored_values = r.connection.lrange(str(item)+":"+str(file_id),0,-1)
            for i in stored_values:

                output_arr.append(r.connection.hgetall(i))
            output_result[item] =output_arr
            
            print(output_result)
        except Exception as e:
            print("specified relation doesnt exist",str(e))

  
    return json.dumps(output_result)


"""
API definitions for the 
"""
@app.route("/v1/metadata/<file_id>/<item_type>", methods=['POST'],
           endpoint="should_be_v1_only_metadata_update")
           
def add_metadata(file_id, item_type):
    """
    Inserting the metadata
    Get a single item_type as  for the target_type
    ---
    tags:
      - metadata
    parameters:
      - name: file_id
        in: path
        description: currently only "file_id" is supported
        required: true
        type: string
        default: 101
      - name: item_type
        in: path
        description: currently only "deleted_by , downloaded_by , executed_by" is supported
        required: true
        type: string
        default: downloaded_by
      - in: body
        name: body
        schema:
          id: rec_metadata
          required:
            - type
            - type_item
          properties:
            type:
              type: integer
              description: string which is out of three deleted_by , downloaded_by , executed_by
              default: deleted_by
            exclude:
              type: array
              description: item_ids to insert in to  from type list
              default: [123, 101]
              items:
                  type: integer
            context:
              type: object
              schema:
                $ref: '#/definitions/rec_metadata'
    responses:
      200:
        description: success string if metadata insert is successful
        schema:
          id: rec_response
          properties:
            opening_id:
              type: integer
              description: The id of the file with status
              default: 123456
      204:
         description: Error inserting the value
    """
    pass

"""
This is to add cross origin site requests
"""
@app.after_request
def allow_origin(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://example.com'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


app.run(debug=True)
