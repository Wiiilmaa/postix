from c6sh.core.models import Preorder, PreorderPosition, Transaction, TransactionPosition
from rest_framework import serializers


class PreorderPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreorderPosition
        fields = ('id', 'preorder', 'secret', 'product')


class PreorderSerializer(serializers.ModelSerializer):
    positions = PreorderPositionSerializer(many=True, read_only=True)

    class Meta:
        model = Preorder
        fields = ('id', 'order_code', 'is_paid', 'warning_text', 'positions')


class TransactionPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionPosition
        fields = ('id', 'type', 'value', 'tax_rate', 'tax_value', 'product',
                  'reverses', 'listentry', 'preorder_position',
                  'items', 'authorized_by')


class TransactionSerializer(serializers.ModelSerializer):
    positions = TransactionPositionSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ('id', 'datetime', 'session', 'cash_given', 'positions')