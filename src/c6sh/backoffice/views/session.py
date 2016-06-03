from crispy_forms.helper import FormHelper
from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.views.generic import DetailView
from django.views.generic.list import ListView

from ...core.models import Cashdesk, CashdeskSession, Item, ItemMovement, User
from .utils import BackofficeUserRequiredMixin, backoffice_user_required


class NewSessionItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('-initial_stock'), label='Produkt')
    amount = forms.IntegerField(min_value=0, label='Anzahl')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.tag = 'td'
        self.helper.form_show_labels = False


NewSessionFormSet = forms.formset_factory(NewSessionItemForm)


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
    session = get_object_or_404(CashdeskSession, pk=pk)


@backoffice_user_required
def edit_session(request):
    pass
