import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
# from db import items, stores
from flask_jwt_extended import jwt_required, get_jwt

from db import db
from sqlalchemy.exc import SQLAlchemyError
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description="Operation on items")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get (self, item_id):
        item = ItemModel.query.get_or_404(item_id)  # get_or_404, works only with flask sqlalchemy
        return item

    @jwt_required(fresh=True)
    def delete (self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort (401, message="Admin privilege needed to delete items.")
        item = ItemModel.query.get_or_404(item_id)  # works only with flask sqlalchemy
        db.session.delete(item)
        db.session.commit()

        return {"message" : "Item deleted successfully"}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(202, ItemSchema)
    def put (self, item_data, item_id):
        #
        # The below line was commented because data type validation
        # using marshmallow was added. It is to be noted that,
        # marshmallow will validate the input json and the pass it to the 
        # method. Also it goes as second parameter after self.
        #
        # item_data = request.get_json()
        # check that name, price and store_id is present
        
        # check that item_id exists
        item = ItemModel.query.get(item_id)
        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
        else:
            item = ItemModel(**item_data, id=item_id)
        db.session.add(item)
        db.session.commit()

        return item



@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))           # if returning a list
    def get(self):
        return ItemModel.query.all()          # get all rows


    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        #
        # The below line was commented because data type validation
        # using marshmallow was added. It is to be noted that,
        # marshmallow will validate the input json and the pass it to the 
        # method.
        #
        # 
        
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, 
                  message="Error occured while inserting data to item table.")


        return item, 201


