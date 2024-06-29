import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
# from db import stores
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema


blp = Blueprint("Stores", __name__, description="Operation on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store


    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        
        db.session.delete(store)
        db.session.commit()

        return {"message" : "Store deleted successfully."}


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()          # extract all rows

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        #
        # The below line was commented because data type validation
        # using marshmallow was added. It is to be noted that,
        # marshmallow will validate the input json and the pass it to the 
        # method. Also it goes as second parameter after self.
        #
        
        # store_data = request.get_json()
        
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(500,
                  message="Store name exists")
        except SQLAlchemyError:
            abort(500,
                  message="Error while inserting data to stores table.")


        return store, 201               # manually set return code 201, means accepted and processed


