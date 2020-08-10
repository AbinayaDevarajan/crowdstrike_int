from flask import Flask, jsonify
from flasgger import Swagger
from flasgger import swag_from


app = Flask(__name__)
swagger = Swagger(app)


@app.route('/colors/<palette>/')
@swag_from('./conf/file_relations_api.yml')
def colors(palette):
    all_colors = {
        'cmyk': ['cian', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue'],
        'test': ['a', 'b', 'c', 'd']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)

app.run(debug=True)
