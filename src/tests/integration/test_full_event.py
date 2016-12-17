import json

import pytest
from c6sh.core.models import Item, Product, ProductItem, ItemMovement, Cashdesk, CashdeskSession, EventSettings, Preorder
from django.utils.crypto import get_random_string
from tests.factories import user_factory, cashdesk_session_before_factory


@pytest.mark.django_db
class TestFullEvent:

    def _setup_base(self):
        s = EventSettings.get_solo()
        s.initialized = True
        s.receipt_address = "Foo"
        s.save()

        self.session = cashdesk_session_before_factory(create_items=False)
        self.troubleshooter = user_factory(troubleshooter=True, superuser=False, password='123')
        self.backoffice_user = user_factory(troubleshooter=True, backoffice=True, password='123')
        self.cashier1 = user_factory(password='123')
        self.cashier2 = user_factory(password='123')

        self.item_full = Item.objects.create(name='Wristband red', description='Full pass', initial_stock=200)
        self.item_d1 = Item.objects.create(name='Wristband 1', description='Day 1', initial_stock=100)
        self.item_d2 = Item.objects.create(name='Wristband 2', description='Day 2', initial_stock=100)
        self.prod_full = Product.objects.create(name='Full pass', price=100, tax_rate=19)
        self.prod_d1 = Product.objects.create(name='Day pass Day 1', price=35, tax_rate=19)
        self.prod_d2 = Product.objects.create(name='Day pass Day 2', price=35, tax_rate=19)
        ProductItem.objects.create(product=self.prod_full, item=self.item_full, amount=1)
        ProductItem.objects.create(product=self.prod_d1, item=self.item_d1, amount=1)
        ProductItem.objects.create(product=self.prod_d2, item=self.item_d2, amount=1)
        self.desk1 = Cashdesk.objects.create(name='Desk 1', ip_address='10.1.1.1')
        self.desk2 = Cashdesk.objects.create(name='Desk 2', ip_address='10.1.1.2')
        #ItemMovement.objects.create(session=session, item=item_1d, amount=10, backoffice_user=buser)

    def _simulate_preorder(self, client, product):
        secret = get_random_string(32)
        p = Preorder.objects.create(order_code=get_random_string(12), is_paid=True)
        p.positions.create(secret=secret, product=product)
        resp = client.post('/api/transactions/', json.dumps({
            "positions": [
                {"product": product.pk,
                 "price": "0.00",
                 "secret": secret,
                 "type": "redeem",
                 "_title": product.name}
            ]
        }), content_type="application/json")
        c = json.loads(resp.content.decode('utf-8'))
        assert c['success']
        return c['id']

    def _simulate_sale(self, client, product):
        resp = client.post('/api/transactions/', json.dumps({
            "positions": [
                {"product": product.pk,
                 "price": str(product.price),
                 "type": "sell",
                 "_title": product.name}
            ]
        }), content_type="application/json")
        c = json.loads(resp.content.decode('utf-8'))
        assert c['success']
        return c['id']

    def _simulate_reverse(self, client, tid):
        resp = client.post('/api/transactions/{}/reverse/'.format(tid))
        c = json.loads(resp.content.decode('utf-8'))
        assert c['success']
        return c['id']

    def _simulate_session(self, full_sales, full_preorders, full_reversals, full_preorder_reversals,
                          d1_sales, d1_preorders, d1_reversals, d1_preorder_reversals,
                          d2_sales, d2_preorders, d2_reversals, d2_preorder_reversals,
                          user, cashdesk, client, buser):
        client.login(username=self.backoffice_user.username, password='123')
        client.post('/backoffice/session/new/', {
            'session-cashdesk': cashdesk.pk,
            'session-user': user.username,
            'session-backoffice_user': buser.username,
            'session-cash_before': '300.00',
            'items-TOTAL_FORMS': '3',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-item': self.item_full.pk,
            'items-0-amount': '100',
            'items-1-item': self.item_d1.pk,
            'items-1-amount': '50',
            'items-2-item': self.item_d2.pk,
            'items-2-amount': '50',
        }, follow=True)
        session = CashdeskSession.objects.filter(user=user, cashdesk=cashdesk).order_by('id').last()
        assert session is not None
        client.login(username=self.cashier1.username, password='123')

        for i in range(full_sales):
            tid = self._simulate_sale(client, self.prod_full)
            if i < full_reversals:
                self._simulate_reverse(client, tid)
        for i in range(d1_sales):
            tid = self._simulate_sale(client, self.prod_d1)
            if i < d1_reversals:
                self._simulate_reverse(client, tid)
        for i in range(d2_sales):
            tid = self._simulate_sale(client, self.prod_d2)
            if i < d2_reversals:
                self._simulate_reverse(client, tid)
        for i in range(full_preorders):
            tid = self._simulate_preorder(client, self.prod_full)
            if i < full_preorder_reversals:
                self._simulate_reverse(client, tid)
        for i in range(d1_preorders):
            tid = self._simulate_preorder(client, self.prod_d1)
            if i < d1_preorder_reversals:
                self._simulate_reverse(client, tid)
        for i in range(d2_preorders):
            tid = self._simulate_preorder(client, self.prod_d2)
            if i < d2_preorder_reversals:
                self._simulate_reverse(client, tid)

        client.login(username=self.backoffice_user.username, password='123')
        r = client.post('/backoffice/session/{}/end/'.format(session.pk), {
            'session-cashdesk': cashdesk.pk,
            'session-user': user.username,
            'session-backoffice_user': buser.username,
            'session-cash_before': (
                ((d1_sales - d1_reversals) * self.prod_d1.price) +
                ((d2_sales - d2_reversals) * self.prod_d2.price) +
                ((full_sales - full_reversals) * self.prod_full.price)
            ),
            'items-TOTAL_FORMS': '3',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-item': self.item_full.pk,
            'items-0-amount': 50 - full_sales + full_reversals - full_preorders + full_preorder_reversals,
            'items-1-item': self.item_d1.pk,
            'items-1-amount': 50 - d1_sales + d1_reversals - d1_preorders + d1_preorder_reversals,
            'items-2-item': self.item_d2.pk,
            'items-2-amount': 50 - d2_sales + d2_reversals - d2_preorders + d2_preorder_reversals,
        }, follow=True)
        session.refresh_from_db()
        assert session.end

    def test_full(self, client):
        self._setup_base()
        self._simulate_session(full_sales=20, full_preorders=60, full_reversals=3, full_preorder_reversals=2,
                               d1_sales=5, d1_preorders=10, d1_reversals=0, d1_preorder_reversals=1,
                               d2_sales=20, d2_preorders=30, d2_reversals=3, d2_preorder_reversals=4,
                               user=self.cashier1, cashdesk=self.desk1, client=client, buser=self.backoffice_user)
