import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    try:
        the_drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [data.short() for data in the_drinks]

        }), 200
    except:
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        the_drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [data.long() for data in the_drinks]

        }), 200
    except:
        abort(404)


'''@TODO implement endpoint POST /drinks it should create a new row in the drinks table it should require the 
'post:drinks' permission it should contain the drink.long() data representation returns status code 200 and json {
"success": True, "drinks": drink} where drink an array containing only the newly created drink or appropriate status 
code indicating reason for failure '''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()

    try:
        the_title = body.get("title")
        the_recipe = body.get("recipe")
        if type(the_recipe) is dict:
            the_recipe = [the_recipe]
        new_drink = Drink(title=the_title, recipe=json.dumps(the_recipe))
        new_drink.insert()

        return jsonify({
            "success": True,
            "drinks": new_drink.long()

        }), 200
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    body = request.get_json()

    the_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if not the_drink:
        abort(404)

    try:

        the_title = body.get("title", None)
        the_recipe = body.get("recipe", None)

        if the_title is not None:
            the_drink.title = the_title

        if the_recipe is not None:
            the_drink.recipe = json.dumps(body['recipe'])

        the_drink.update()

        return jsonify({
            "success": True,
            "drinks": [the_drink.long()]
        }), 200

    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    try:
        the_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if the_drink is None:
            abort(404)

        the_drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200

    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify(
        {"success": False,
         "error": 404,
         "message": "resource not found"
         }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(
        {"success": False,
         "error": error.status_code,
         "message": error.error['description']
         }), error.status_code
