from ..models import PreorderPosition


class FlowError(Exception):

    def __init__(self, msg, type="error", missing_field=None):
        self.message = msg
        self.type = type
        self.missing_field = missing_field

    def __str__(self):
        return self.message


def redeem_preorder_ticket(**kwargs):
    if 'secret' not in kwargs:
        raise FlowError('No secret has been given.')

    try:
        pp = PreorderPosition.objects.get(secret=kwargs.get('secret'))
    except PreorderPosition.DoesNotExist:
        raise FlowError('No ticket found with the given secret.')

    if not pp.preorder.is_paid:
        raise FlowError('Ticket has not been paid for.')

    if pp.preorder.warning_text and 'warning_acknowledged' not in kwargs:
        raise FlowError(pp.preorder.warning_text, type='confirmation',
                        missing_field='warning_acknowledged')

    if
