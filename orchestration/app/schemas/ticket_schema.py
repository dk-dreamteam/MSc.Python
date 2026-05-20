from marshmallow import fields, validate
from app.extensions import ma
from app.models.ticket import Ticket
from app.models.category import Category
from app.models.status import Status


class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True

    category_name = fields.String(attribute='category.name', dump_only=True)
    status_name = fields.String(attribute='status.name', dump_only=True)


class TicketCreateSchema(ma.Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=True, validate=validate.Length(min=1))
    category_id = fields.Integer(allow_none=True)
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    photo = fields.Field(load_only=True)


class TicketUpdateSchema(ma.Schema):
    title = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.String(validate=validate.Length(min=1))
    status_id = fields.Integer()
    admin_notes = fields.String()


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True


class StatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Status
        load_instance = True
