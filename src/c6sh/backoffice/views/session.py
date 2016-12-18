from typing import Union

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import DetailView
from django.views.generic.list import ListView

from .. import checks
from ...core.models import Cashdesk, CashdeskSession, ItemMovement, User
from ..forms import ItemMovementFormSetHelper, get_form_and_formset
from ..report import generate_report
from .utils import BackofficeUserRequiredMixin, backoffice_user_required


@backoffice_user_required
def new_session(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    form, formset = get_form_and_formset(initial_form={'backoffice_user': request.user})

    if request.method == 'POST':
        form, formset = get_form_and_formset(request=request)

        if form.is_valid() and formset.is_valid():
            session = CashdeskSession.objects.create(
                cashdesk=form.cleaned_data['cashdesk'],
                user=form.cleaned_data['user'],
                start=now(),
                cash_before=form.cleaned_data['cash_before'],
                backoffice_user_before=form.cleaned_data['backoffice_user'],
            )
            for f in formset:
                item = f.cleaned_data.get('item')
                amount = f.cleaned_data.get('amount')
                if item and amount and amount > 0:
                    ItemMovement.objects.create(
                        item=item,
                        session=session,
                        amount=amount,
                        backoffice_user=form.cleaned_data['backoffice_user'],
                    )
            messages.success(request, 'Session wurde angelegt.'.format(session.pk, session.cashdesk))
            return redirect('backoffice:main')

        else:
            messages.error(request, 'Session konnte nicht angelegt werden: Bitte Daten korrigieren.')

    elif request.method == 'GET':
        param = request.GET.get('desk')
        if param:
            try:
                initial_form = {
                    'cashdesk': Cashdesk.objects.get(pk=int(param)),
                    'backoffice_user': request.user,
                }
                form, _ = get_form_and_formset(initial_form=initial_form)
            except:
                pass

    return render(request, 'backoffice/new_session.html', {
        'form': form,
        'formset': formset,
        'helper': ItemMovementFormSetHelper(),
        'users': User.objects.values_list('username', flat=True),
        'backoffice_users': User.objects.filter(is_backoffice_user=True).values_list('username', flat=True),
    })


class SessionListView(LoginRequiredMixin, BackofficeUserRequiredMixin, ListView):
    """ implements only a list of active sessions for now. Ended sessions will
    be visible in the reports view """
    model = CashdeskSession
    template_name = 'backoffice/session_list.html'
    context_object_name = 'cashdesks'

    def get_queryset(self) -> QuerySet:
        return Cashdesk.objects.filter(is_active=True).order_by('name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx['check_errors'] = checks.all_errors()
        return ctx


class ReportListView(LoginRequiredMixin, BackofficeUserRequiredMixin, ListView):
    """ list of old sessions """
    model = CashdeskSession
    template_name = 'backoffice/report_list.html'
    context_object_name = 'sessions'
    paginate_by = 25

    def get_queryset(self) -> QuerySet:
        return CashdeskSession.objects.filter(end__isnull=False).order_by('-end')


class SessionDetailView(BackofficeUserRequiredMixin, DetailView):
    queryset = CashdeskSession.objects.all()
    template_name = 'backoffice/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['url'] = self.request.build_absolute_uri('/')
        return ctx


@backoffice_user_required
def resupply_session(request: HttpRequest, pk: int) -> Union[HttpResponse, HttpResponseRedirect]:
    """ TODO: show approximate current amounts of items? """
    session = get_object_or_404(CashdeskSession, pk=pk)
    initial_form = {
        'cashdesk': session.cashdesk,
        'user': session.user,
        'backoffice_user': request.user,
        'cash_before': 0,
    }
    form, formset = get_form_and_formset(initial_form=initial_form)

    if request.method == 'POST':
        form, formset = get_form_and_formset(request=request)

        if formset.is_valid() and form.is_valid():
            for f in formset:
                item = f.cleaned_data.get('item')
                amount = f.cleaned_data.get('amount')
                if item and amount:
                    ItemMovement.objects.create(
                        item=item,
                        session=session,
                        amount=amount,
                        backoffice_user=form.cleaned_data['backoffice_user'],
                    )
            messages.success(request, 'Produkte wurden der Kasse hinzugefügt.')
            return redirect('backoffice:session-detail', pk=pk)

        elif formset.errors:
            print(formset.errors)
            print(form.errors)
            messages.error(request, 'Fehler: Bitte Daten prüfen und korrigieren.')

    form.fields['user'].widget.attrs['readonly'] = True
    form.fields['cashdesk'].widget.attrs['readonly'] = True
    form.fields['cash_before'].widget = forms.HiddenInput()

    return render(request, 'backoffice/resupply_session.html', {
        'formset': formset,
        'helper': ItemMovementFormSetHelper(),
        'form': form,
        'backoffice_users': User.objects.filter(is_backoffice_user=True).values_list('username', flat=True),
    })
    pass


@backoffice_user_required
def end_session(request: HttpRequest, pk: int) -> Union[HttpRequest, HttpResponseRedirect]:
    session = get_object_or_404(CashdeskSession, pk=pk)
    items_in_session = session.get_item_set()
    cash_total = session.get_cash_transaction_total()

    if request.method == 'POST':
        form, formset = get_form_and_formset(request=request, extra=0)
        if form.is_valid() and formset.is_valid():
            if session.end:
                # This is not optimal, but our data model does not have a way of tracking
                # cash movement over time.
                # TODO: Maybe we should at least adjust the backoffice user responsible.
                session.cash_after += form.cleaned_data.get('cash_before')
                session.save(update_fields=['cash_after'])
            else:
                session.end = now()
                session.backoffice_user_after = request.user
                session.cash_after = form.cleaned_data.get('cash_before')
                session.save(update_fields=['backoffice_user_after', 'cash_after', 'end'])
                messages.success(request, 'Session wurde beendet.')

            # It is important that we do this *after* we set session.end as the date of this movement
            # will be used in determining this as the final item takeout *after* the session.
            for f in formset:
                item = f.cleaned_data.get('item')
                amount = f.cleaned_data.get('amount')
                if item and amount and amount:
                    ItemMovement.objects.create(
                        item=item,
                        session=session,
                        amount=-amount,
                        backoffice_user=form.cleaned_data['backoffice_user'],
                    )

            generate_report(session)
            return redirect('backoffice:session-report', pk=pk)
        else:
            messages.error(request, 'Session konnte nicht beendet werden: Bitte Daten korrigieren.')

    elif request.method == 'GET':
        if session.end:
            msg = 'Diese Session wurde bereits ausgezählt und abgeschlossen. '\
                  'Wenn du dieses Formular ausfüllst, wird ein zweiter, korrigierter '\
                  'Report erstellt.'
            messages.warning(request, msg)

        form, formset = get_form_and_formset(
            extra=0,
            initial_form={'cashdesk': session.cashdesk, 'user': session.user, 'backoffice_user': request.user},
            initial_formset=[{'item': item} for item in items_in_session],
        )

    for f, item_data in zip(formset, session.get_current_items()):
        f.product_label = item_data

    return render(request, 'backoffice/end_session.html', {
        'session': session,
        'form': form,
        'formset': formset,
        'cash': {'initial': session.cash_before, 'transactions': cash_total},
        'backoffice_users': User.objects.filter(is_backoffice_user=True).values_list('username', flat=True),
    })


@backoffice_user_required
def session_report(request: HttpRequest, pk: int) -> Union[HttpResponse, HttpResponseRedirect]:
    session = get_object_or_404(CashdeskSession, pk=pk)
    report_path = session.get_report_path()

    if not report_path:
        report_path = generate_report(session)

    response = HttpResponse(content=default_storage.open(report_path, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename=sessionreport-{}.pdf'.format(session.pk)
    return response
