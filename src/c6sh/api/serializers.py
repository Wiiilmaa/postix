from c6sh.core.models import Preorder, PreorderPosition, Transaction, TransactionPosition
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


class TransactionPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionPosition
        fields = ('type', 'value', 'tax_rate', 'tax_value', 'product',
                  'reverses', 'listentry', 'preorder_position',
                  'items', 'authorized_by')


class TransactionSerializer(serializers.ModelSerializer):
    positions = TransactionPositionSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ('datetime', 'session', 'cash_given', 'positions')