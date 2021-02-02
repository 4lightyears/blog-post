from flask import request
from flask_restful import Resource
from flask_jwt_extended import (jwt_required, create_access_token, create_refresh_token, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from http import HTTPStatus

from models.user import User
from encrypt import verify_pass

blacklist = set()


class TokenResource(Resource):

    def post(self):
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')

        user = User.get_by_email(email=email)

        if not user or not verify_pass(password, user.password):
            return {'message': 'email or password incorrect.'}, HTTPStatus.UNAUTHORIZED

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        return {'access-token': access_token, 'refresh-token': refresh_token}, HTTPStatus.OK


class RefreshResource(Resource):

    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)

        return {'access-token': access_token}, HTTPStatus.OK


class RevokeAccessResource(Resource):

    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)

        return {"message": "Successfully logged out"}, HTTPStatus.OK
