from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import DetailView
from django.views.generic.list import ListView

from ...core.models import Cashdesk, CashdeskSession, Item, ItemMovement, TransactionPositionItem, User
from .utils import BackofficeUserRequiredMixin, backoffice_user_required


class NewSessionItemForm(forms.Form):
    """ This is basically only used in the formset below.
    Normally you would use a modelformset, but the Form helper class is
    required to correct some crispy_forms behaviour for now. """
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('-initial_stock'), label='Produkt')
    amount = forms.IntegerField(label='Anzahl')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.tag = 'td'
        self.helper.form_show_labels = False


class NewSessionItemFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = 'bootstrap/table_inline_formset.html'
        self.form_id = 'session-items'
        self.form_tag = False


class SessionBaseForm(forms.Form):
    cashdesk = forms.ModelChoiceField(queryset=Cashdesk.objects.filter(is_active=True).order_by('name'), label='Kasse')
    user = forms.CharField(max_length=254, label='Engel')
    cash_before = forms.DecimalField(max_digits=10, decimal_places=2, label='Bargeld')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


@backoffice_user_required
def new_session(request):
    form = SessionBaseForm(prefix='data')
    NewSessionFormSet = forms.formset_factory(NewSessionItemForm)
    formset = NewSessionFormSet(prefix='items')

    if request.method == 'POST':
        form = SessionBaseForm(request.POST, prefix='data')
        formset = NewSessionFormSet(request.POST, prefix='items')

        if form.is_valid() and formset.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['user'])
            except User.DoesNotExist:
                form.add_error('user', 'Engel existiert nicht.')
            else:
                session = CashdeskSession.objects.create(
                    cashdesk=form.cleaned_data['cashdesk'],
                    user=user,
                    start=now(),
                    cash_before=form.cleaned_data['cash_before'],
                    backoffice_user_before=request.user,
                )
                for f in formset:
                    item = f.cleaned_data.get('item')
                    amount = f.cleaned_data.get('amount')
                    if item and amount and amount > 0:
                        ItemMovement.objects.create(item=item, session=session, amount=amount)
                    # TODO: error handling, don't fail silently
                messages.success(request, 'Session wurde angelegt.'.format(session.pk, session.cashdesk))
                return redirect('backoffice:main')

        else:
            messages.error(request, 'Session konnte nicht angelegt werden: Bitte Daten korrigieren.')

    elif request.method == 'GET':
        param = request.GET.get('desk')
        if param:
            try:
                desk = Cashdesk.objects.get(pk=int(param))
                form = SessionBaseForm(prefix='data', initial={'cashdesk': desk})
            except:
                pass

    return render(request, 'backoffice/new_session.html', {
        'form': form,
        'formset': formset,
        'helper': NewSessionItemFormSetHelper(),
        'user_list': User.objects.values_list('username', flat=True),
    })


class SessionListView(LoginRequiredMixin, BackofficeUserRequiredMixin, ListView):
    """ implements only a list of active sessions for now. Ended sessions will
    be visible in the reports view """
    model = CashdeskSession
    template_name = 'backoffice/session_list.html'
    context_object_name = 'cashdesks'

    def get_queryset(self):
        return Cashdesk.objects.filter(is_active=True).order_by('name')


class SessionDetailView(BackofficeUserRequiredMixin, DetailView):
    queryset = CashdeskSession.objects.all()
    template_name = 'backoffice/session_detail.html'
    context_object_name = 'session'


@backoffice_user_required
def resupply_session(request, pk):
    """ todo: show approximate current amounts of items? """
    formset = NewSessionFormSet(prefix='items')
    session = get_object_or_404(CashdeskSession, pk=pk)

    if request.method == 'POST':
        formset = NewSessionFormSet(request.POST, prefix='items')

        if formset.is_valid():
            for f in formset:
                item = f.cleaned_data.get('item')
                amount = f.cleaned_data.get('amount')
                if item and amount:
                    ItemMovement.objects.create(item=item, session=session, amount=amount)
                # TODO: error handling, don't fail silently
            messages.success(request, 'Produkte wurden der Kasse hinzugefügt.')

        elif formset.errors:
            messages.error(request, 'Fehler: Bitte Daten prüfen und korrigieren.')

    return render(request, 'backoffice/resupply_session.html', {
        'formset': formset,
        'helper': NewSessionItemFormSetHelper(),
        'cashdesk': session.cashdesk,
        'cashier': session.user,
    })
    pass


@backoffice_user_required
def end_session(request, pk):
    NewSessionFormSet = forms.formset_factory(NewSessionItemForm, extra=0)
    session = get_object_or_404(CashdeskSession, pk=pk)
    items_in_session = set(ItemMovement.objects.filter(session=session).values_list('item', flat=True))
    items_in_session = [Item.objects.get(pk=pk) for pk in items_in_session]
    cash_total = session.transactions.aggregate(total=Sum('cash_given'))['total'] or 0

    if request.method == 'POST':
        form = SessionBaseForm(request.POST, prefix='data')
        formset = NewSessionFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            session.end = now()
            session.cash_after = form.data.get('cash_before')
            session.save()
            # TODO: add ItemMovement instances per item
            messages.success(request, 'Session wurde beendet.')
            return redirect('backoffice:main')
        else:
            print(form.errors, formset.errors)
            messages.error(request, 'Session konnte nicht beendet werden: Bitte Daten korrigieren.')

    elif request.method == 'GET':
        form = SessionBaseForm(prefix='data', initial={'cashdesk': session.cashdesk, 'user': session.user})
        formset = NewSessionFormSet(prefix='items', initial=[{'item': item} for item in items_in_session])

    for f, item in zip(formset, items_in_session):
        f.product_label = {
            'product': item,
            'initial': ItemMovement.objects\
                .filter(item=item, session=session)\
                .aggregate(total=Sum('amount'))['total'],
            'transactions': TransactionPositionItem.objects\
                .filter(item=item, position__transaction__session=session)\
                .aggregate(total=Sum('amount'))['total'] or 0,
        }

    return render(request, 'backoffice/end_session.html', {
        'session': session,
        'form': form,
        'formset': formset,
        'cash': {'initial': session.cash_before, 'transactions': cash_total},
    })


@backoffice_user_required
def edit_session(request):
    pass
