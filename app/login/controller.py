from flask_restx import Resource, Namespace
from app.models import User
from app.extensions import db, bcrypt
from .requests import login_request
from flask_jwt_extended import create_access_token


login_ns = Namespace("api")


@login_ns.route("/login")
class Login(Resource):
    @login_ns.expect(login_request, validate=True)
    def post(self):
        request = login_ns.payload
        user = User.query.filter(User.email == request['email']).first()
        if not user:
            return {"message": "The user does not exists", "token": None}, 401
        if not bcrypt.check_password_hash(user.password, request['password']):
            return {"message": "The password is incorrect", "token": None}, 401
        return {"message": "User logged successfully", "token": create_access_token(user)}, 401
