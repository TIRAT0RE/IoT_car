from marshmallow import Schema, fields

class ParkingSchema(Schema):
    empty_count = fields.Number()
    longitude = fields.Number()
    latitude = fields.Number()