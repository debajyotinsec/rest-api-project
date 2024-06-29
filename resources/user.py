import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
# from db import items, stores

from blocklist import BLOCKLIST
from db import db
from sqlalchemy.exc import SQLAlchemyError
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users", __name__, description="Operation on users")

@blp.route("/register")
class UserRegister(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        # test_user_id = 1
        # user_entry = UserModel.query.get_or_404(test_user_id)
        # print ("user ----> ", user_entry)
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409,
                  message="User name not available. Use another.")
        

        user = UserModel(
            username = user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        # print ("User Model --->", user)
        
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort (410,
                   message="User data cannot be saved. Try later.")
        
        return {"message": "User added successfully"}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token" : access_token,
                    "refresh_token" : refresh_token}
        
        abort(401, 
               message = "Invalid credentials.")



@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token" : new_token}


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]      # or you can write get_jwt().get("jti")
        BLOCKLIST.add(jti)
        return {"message" : "Logout Successful"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        # print ("Input userid is --> ", user_id, flush=True)
        user = UserModel.query.get_or_404(user_id)
        # print ("user is ----> ", user, flush=True)
        # print ("user is ----> ", user.id, flush=True)
        # print ("user is ----> ", user.username, flush=True)
        # print ("user is ----> ", user.password, flush=True)
        return user
    

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort (411,
                   message="Issue in user deletion, try later.")
        return {"message" : "User deleted successfully"}, 203



