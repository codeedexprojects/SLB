# fields.py
from rest_framework import serializers
from datetime import datetime

class CustomDateField(serializers.DateField):
    def to_representation(self, value):
        return value.strftime('%d-%m-%Y')

    def to_internal_value(self, data):
        try:
            return datetime.strptime(data, '%d-%m-%Y').date()
        except ValueError:
            self.fail('invalid', format='dd-mm-yyyy')
