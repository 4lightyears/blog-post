from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from webargs.flaskparser import use_kwargs
from webargs import fields

from models.post import Post
from schemas.post import PostPaginationSchema, PostSchema
from caching import cache, clear_cache

post_schema = PostSchema()
post_list_schema = PostSchema(many=True)
post_pagination_schema = PostPaginationSchema()


arguments = {
    "page": fields.Int(missing=1),
    "per_page": fields.Int(missing=2),
    "order": fields.Str(missing='desc')
}

class PostListResource(Resource):

    @use_kwargs(arguments, location="query")
    @cache.cached(timeout=60, query_string=True)
    def get(self, page, per_page, order):
        print('Querying database...')
        if order not in ['asc', 'desc']:
            order = 'desc'
        paginated_posts = Post.get_all_posts(page=page, per_page=per_page, order=order)
        return post_pagination_schema.dump(paginated_posts), HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        try:
            data = post_schema.load(data=json_data)
        except ValidationError as exc:
            return {'message': 'validation error', 'errors': exc}, HTTPStatus.BAD_REQUEST

        post = Post(**data)
        post.user_id = current_user
        post.save()

        return post_schema.dump(post), HTTPStatus.CREATED


class PostResource(Resource):

    @jwt_required
    def get(self, id):
        post = Post.get_by_post_id(id=id)
        if not post:
            return {'message': 'not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if post.user_id != current_user:
            return {'message': 'Access not allowed.'}, HTTPStatus.FORBIDDEN

        return post_schema.dump(post), HTTPStatus.OK

    @jwt_required
    def patch(self, id):
        json_data = request.get_json()
        try:
            data = post_schema.load(data=json_data, partial=('name',))
        except ValidationError as exc:
            return {'message': 'validation error', 'errors': exc}, HTTPStatus.BAD_REQUEST
        post = Post.get_by_post_id(id)
        if post is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user != post.user_id:
            return {'message': 'access not allowed.'}, HTTPStatus.FORBIDDEN

        post.body = data['body'] or post.body

        post.save()
        clear_cache('/posts')
        return post_schema.dump(post), HTTPStatus.OK

    @jwt_required
    def delete(self, id):
        post = Post.get_by_post_id(id)
        if post is None:
            return {'message': 'Not found.'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user != post.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        post.delete()
        clear_cache('/posts')
        return {}, HTTPStatus.NO_CONTENT
