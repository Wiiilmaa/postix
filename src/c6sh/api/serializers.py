from c6sh.core.models import Preorder, PreorderPosition
from rest_framework import serializers


class PreorderPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreorderPosition
        fields = ('preorder', 'secret', 'product')


class PreorderSerializer(serializers.ModelSerializer):
    positions = PreorderPositionSerializer(many=True, read_only=True)

    class Meta:
        model = Preorder
        fields = ('order_code', 'is_paid', 'warning_text', 'positions')
