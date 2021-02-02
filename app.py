# import from packages
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate

# imports from manually created files
from resources.user import CreateUserResource, UserResource, MeResource, UserPostListResource
from resources.post import PostListResource, PostResource
from resources.token import TokenResource, RefreshResource, RevokeAccessResource, blacklist
from database import db
from jwt_manage import jwt
from caching import cache


def create_app():
    app = Flask(__name__)

    DEBUG = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://varun_reviewbook:sharma@localhost/restaurants_data'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'topsecret'
    app.config['JWT_ERROR_MESSAGE'] = 'message'
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 10 * 60

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    migrate = Migrate(app, db)

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in blacklist

    api = Api(app)
    api.add_resource(PostListResource, '/posts')
    api.add_resource(PostResource, '/posts/<int:id>')

    api.add_resource(CreateUserResource, '/users')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(MeResource, '/me')
    api.add_resource(UserPostListResource, '/users/<string:username>/posts')

    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeAccessResource, '/revoke')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
