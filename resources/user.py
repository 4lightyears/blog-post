from http import HTTPStatus
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional
from marshmallow import ValidationError
from webargs.flaskparser import use_kwargs
from webargs import fields

from models.user import User
from models.post import Post

from schemas.user import UserSchema
from schemas.post import PostSchema, PostPaginationSchema

user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))

post_list_schema = PostSchema(many=True)
post_pagination_schema = PostPaginationSchema()


class CreateUserResource(Resource):

    def post(self):
        json_data = request.get_json()
        try:
            data = user_schema.load(data=json_data)
        except ValidationError as exc:
            return {'message': 'validation error', 'errors': exc}, HTTPStatus.BAD_REQUEST

        if User.get_by_username(data.get('username')):
            return {'message': 'username already taken.'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(data.get('email')):
            return {'message': 'email already taken.'}, HTTPStatus.BAD_REQUEST

        user = User(**data)
        user.save()
        return user_schema.dump(user), HTTPStatus.CREATED


class UserResource(Resource):

    @jwt_optional
    def get(self, username):
        """if jwt_token is accessed, then this returns the email too else only the username and id"""
        user = User.get_by_username(username)
        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_public_schema.dump(user)
        print('data is of type', type(data))
        return data, HTTPStatus.OK


class MeResource(Resource):

    @jwt_required
    def get(self):
        user = User.get_by_id(get_jwt_identity())
        return user_schema.dump(user), HTTPStatus.OK


class UserPostListResource(Resource):

    @jwt_optional
    @use_kwargs({'page': fields.Int(missing=1), 'per_page': fields.Int(missing=4)}, location="query")
    def get(self, username, page, per_page):
        user = User.get_by_username(username)
        if user is None:
            return {'message': 'user not found.'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        posts = Post.get_all_posts_by_user(user.id, page, per_page, order)
        return post_pagination_schema.dump(posts), HTTPStatus.OK







