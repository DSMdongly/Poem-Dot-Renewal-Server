from flask import abort, Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from ..view import json_required, user_required
from ..model.poem import Poem
from ..model.user import User

api = Api(Blueprint(__name__, 'poem_api'))


@user_required
def author_required(fn):
    @wraps
    def wrapper(*args, **kwargs):
        poem = Poem.find_by_id(request.args['id'] or request.json['id'])
        user = User.find_by_id(get_jwt_identity())

        if poem is None:
            return abort(404)

        if user is None or user.id != poem.author_id:
            return abort(403)

        return fn(args, **kwargs)

    return wrapper


@api.resource('/poem')
class PoemService(Resource):
    @user_required
    @json_required({'title': str, 'content': str})
    def post(self):
        payload = request.json

        user = User.find_by_id(get_jwt_identity())

        poem = Poem(title=payload['title'],
                    content=payload['content'],
                    author_id=user.id)

        poem.save()

        return {
            'created': poem.id
        }, 201

    @user_required
    def get(self):
        user = User.find_by_id(get_jwt_identity())
        return user.poems

    @author_required
    @json_required({'title': str, 'content': str})
    def put(self):
        payload = request.json
        poem = Poem.find_by_id(payload['id'])

        poem.update(title=payload['title'],
                    content=payload['content'])

        return {
            'updated': poem.id,
        }

    @author_required
    @json_required({'id': int})
    def delete(self):
        payload = request.json

        poem = Poem.find_by_id(payload['id'])
        poem.remove()

        return {
            'deleted': poem.id
        }