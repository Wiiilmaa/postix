from decimal import Decimal

import pytest

from postix.core.models import Cashdesk, Preorder, PreorderPosition, Product
from postix.core.utils.pretix_import import import_pretix_data


@pytest.fixture
def normal_pretix_data():
    return {"event": {
        "categories": [
            {
                "name": "Tickets",
                "id": 15
            },
        ],
        "organizer": {
            "slug": "orga",
            "name": "Orga"
        },
        "orders": [
            {
                "user": "user1@gmail.com",
                "total": "100.00",
                "status": "p",
                "datetime": "2017-12-17T13:37:27Z",
                "positions": [
                    {
                        "attendee_email": None,
                        "price": "100.00",
                        "item": 232,
                        "answers": [
                            {
                                "answer": "Cool",
                                "question": 10
                            },
                            {
                                "answer": "31",
                                "question": 11
                            },
                        ],
                        "secret": "xxxx",
                        "attendee_name": "User One",
                        "addon_to": None,
                        "id": 37950,
                        "variation": None
                    },
                ],
                "code": "DQFEF",
                "fees": []
            },
            {
                "user": "user2@hotmail.de",
                "total": "100.00",
                "status": "n",
                "datetime": "2017-12-16T14:51:51Z",
                "positions": [
                    {
                        "attendee_email": None,
                        "price": "100.00",
                        "item": 232,
                        "answers": [
                        ],
                        "secret": "yyyy",
                        "attendee_name": "User Two",
                        "addon_to": None,
                        "id": 37836,
                        "variation": None
                    },
                    {
                        "attendee_email": None,
                        "price": "100.00",
                        "item": 232,
                        "answers": [
                        ],
                        "secret": "zzzz",
                        "attendee_name": "User Three",
                        "addon_to": None,
                        "id": 37837,
                        "variation": None
                    },
                ],
                "code": "9SAR3",
                "fees": []
            },
        ],
        "questions": [
            {
                "question": "How do you like chocolate?",
                "type": "S",
                "id": 10
            },
            {
                "question": "How old are you?",
                "type": "S",
                "id": 11
            },
        ],
        "items": [
            {
                "tax_rate": "19.00",
                "category": 15,
                "price": "100.00",
                "active": True,
                "admission": True,
                "name": "Standard ticket",
                "variations": [],
                "id": 232,
                "tax_name": "VAT"
            },
        ],
        "quotas": [
            {
                "items": [
                    232
                ],
                "variations": [],
                "size": 100,
                "id": 36
            },
        ],
        "slug": "conf",
        "name": "Conference"
    }}


@pytest.mark.django_db
def test_pretix_import_regular(normal_pretix_data):
    assert Preorder.objects.count() == 0
    assert PreorderPosition.objects.count() == 0
    assert Cashdesk.objects.count() == 0
    assert Product.objects.count() == 0

    import_pretix_data(normal_pretix_data, add_cashdesks=5, questions=['10', ])

    assert Product.objects.count() == 1
    assert Preorder.objects.count() == 2
    assert PreorderPosition.objects.count() == 3
    assert Cashdesk.objects.count() == 5

    product = Product.objects.first()
    assert product.name == 'Standard ticket'
    assert product.price == Decimal('100.00')
    assert product.tax_rate == Decimal('19.00')

    assert PreorderPosition.objects.exclude(information='').count() == 1
