from c6sh.core.models import (
    ListConstraintEntry, PreorderPosition, TransactionPosition,
)


def is_redeemed(obj) -> bool:

    if isinstance(obj, ListConstraintEntry):
        positions = TransactionPosition.objects.filter(listentry=obj)
    elif isinstance(obj, PreorderPosition):
        positions = TransactionPosition.objects.filter(preorder_position=obj)
    else:  # noqa
        raise TypeError('Expected ListConstraintEntry or PreorderPosition object.')

    positives = positions.filter(type='redeem')
    negatives = positions.filter(type='reverse')

    if positives.exists():
        return positives.count() > negatives.count()

    return False
