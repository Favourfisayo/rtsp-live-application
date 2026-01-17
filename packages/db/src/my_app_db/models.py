from mongoengine import Document, StringField, FloatField, IntField, BooleanField, DateTimeField
from datetime import datetime

class Overlay(Document):
    type = StringField(required=True, choices=('text', 'image'))
    content = StringField(required=True)
    x = FloatField(required=True, default=0.0)
    y = FloatField(required=True, default=0.0)
    width = FloatField(required=True, default=100.0)
    height = FloatField(required=True, default=100.0)
    zIndex = IntField(required=True, default=1)
    visible = BooleanField(required=True, default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'overlays'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(Overlay, self).save(*args, **kwargs)
