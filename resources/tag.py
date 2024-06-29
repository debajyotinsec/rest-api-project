import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
# from db import stores
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema


blp = Blueprint("Tags", __name__, description="Operation on tags")

@blp.route("/store/<string:store_id>/tags")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        
        return store.tags.all()


    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        
        # check if the tag for the store already exists.
        if TagModel.query.filter(TagModel.store_id == store_id, \
                                 TagModel.name == tag_data["name"]).first():
            abort(400,
                  message = "Tag name already exists for this store")
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort (500,
                   message=str(e))

        return tag


@blp.route("/tags/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    

    @blp.response(202, description="Deletes a tag if no item is assigned to it.",
                  example={"message" : "Tag deleted successfully."})
    @blp.alt_response(404, description="Tag id not found.")
    @blp.alt_response(400, description="Tag assigned to multiple items, delete not performed.")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message" : "Tag deleted successfully."}
        abort (400,
               message="Issue with tag deletion.")
    

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagstoItems(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag  = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except:
            abort (500,
                  message= "Insert in LinkTagstoItems.post method.")

        return tag

    @blp.response(202, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag  = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.delete(item)
            db.session.commit()
        except:
            abort (500,
                  message= "Delete in LinkTagstoItems.post method.")

        return {"message" :"Item removed from tag", 
                "item" : item, 
                "tag":tag
                }

