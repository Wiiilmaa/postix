from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import DetailView
from django.views.generic.list import ListView

from ...core.models import Cashdesk, CashdeskSession, ItemMovement, User
from ..forms import ItemMovementFormSetHelper, get_form_and_formset
from ..report import generate_report
from .utils import BackofficeUserRequiredMixin, backoffice_user_required


@backoffice_user_required
def new_session(request):
    form, formset = get_form_and_formset()

    if request.method == 'POST':
        form, formset = get_form_and_formset(request=request)

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
                        ItemMovement.objects.create(
                            item=item,
                            session=session,
                            amount=amount,
                            backoffice_user=request.user,
                        )
                messages.success(request, 'Session wurde angelegt.'.format(session.pk, session.cashdesk))
                return redirect('backoffice:main')

        else:
            messages.error(request, 'Session konnte nicht angelegt werden: Bitte Daten korrigieren.')

    elif request.method == 'GET':
        param = request.GET.get('desk')
        if param:
            try:
                desk = Cashdesk.objects.get(pk=int(param))
                form, _ = get_form_and_formset(initial_form={'cashdesk': desk})
            except:
                pass

    return render(request, 'backoffice/new_session.html', {
        'form': form,
        'formset': formset,
        'helper': ItemMovementFormSetHelper(),
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


class ReportListView(LoginRequiredMixin, BackofficeUserRequiredMixin, ListView):
    """ list of old sessions """
    model = CashdeskSession
    template_name = 'backoffice/report_list.html'
    context_object_name = 'sessions'
    paginate_by = 25

    def get_queryset(self):
        return CashdeskSession.objects.filter(end__isnull=False).order_by('-end')


class SessionDetailView(BackofficeUserRequiredMixin, DetailView):
    queryset = CashdeskSession.objects.all()
    template_name = 'backoffice/session_detail.html'
    context_object_name = 'session'


@backoffice_user_required
def resupply_session(request, pk):
    """ Nice To Have: show approximate current amounts of items? """
    _, formset = get_form_and_formset()
    session = get_object_or_404(CashdeskSession, pk=pk)

    if request.method == 'POST':
        _, formset = get_form_and_formset(request=request)

        if formset.is_valid():
            for f in formset:
                item = f.cleaned_data.get('item')
                amount = f.cleaned_data.get('amount')
                if item and amount:
                    ItemMovement.objects.create(
                        item=item,
                        session=session,
                        amount=amount,
                        backoffice_user=request.user
                    )
            messages.success(request, 'Produkte wurden der Kasse hinzugefügt.')
            return redirect('backoffice:session-detail', pk=pk)

        elif formset.errors:
            messages.error(request, 'Fehler: Bitte Daten prüfen und korrigieren.')

    return render(request, 'backoffice/resupply_session.html', {
        'formset': formset,
        'helper': ItemMovementFormSetHelper(),
        'cashdesk': session.cashdesk,
        'cashier': session.user,
    })
    pass


@backoffice_user_required
def end_session(request, pk):
    session = get_object_or_404(CashdeskSession, pk=pk)
    items_in_session = session.get_item_set()
    cash_total = session.get_cash_transaction_total()

    if request.method == 'POST':
        form, formset = get_form_and_formset(request=request, extra=0)
        if form.is_valid() and formset.is_valid():
            for f in formset:
                item = f.cleaned_data.get('item')
                amount = f.cleaned_data.get('amount')
                if item and amount and amount:
                    ItemMovement.objects.create(
                        item=item,
                        session=session,
                        amount=-amount,
                        backoffice_user=request.user
                    )

            if session.end:
                # This is not optimal, but our data model does not have a way of tracking
                # cash movement over time.
                # TODO: Maybe we should at least adjust the backoffice user responsible.
                session.cash_after += form.cleaned_data.get('cash_before')
                session.save()
            else:
                session.end = now()
                session.backoffice_user_after = request.user
                session.cash_after = form.cleaned_data.get('cash_before')
                session.save()
                messages.success(request, 'Session wurde beendet.')

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
            initial_form={'cashdesk': session.cashdesk, 'user': session.user},
            initial_formset=[{'item': item} for item in items_in_session],
        )

    for f, item_data in zip(formset, session.get_current_items()):
        f.product_label = item_data

    return render(request, 'backoffice/end_session.html', {
        'session': session,
        'form': form,
        'formset': formset,
        'cash': {'initial': session.cash_before, 'transactions': cash_total},
    })


@backoffice_user_required
def session_report(request, pk):
    session = get_object_or_404(CashdeskSession, pk=pk)
    report_path = session.get_report_path()

    if not report_path:
        report_path = generate_report(session)

    response = HttpResponse(content=default_storage.open(report_path, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename=sessionreport-{}.pdf'.format(session.pk)
    return response


@backoffice_user_required
def edit_session(request):
    pass
