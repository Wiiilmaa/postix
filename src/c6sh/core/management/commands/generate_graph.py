import math
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, time, timedelta

import numpy as np
import pylab as plt
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils.timezone import get_current_timezone, now

from c6sh.core.models import CashdeskSession, TransactionPosition


def dtf(d):
    return d.hour + d.minute / 60.0


def opensessions(x, sessions, dt):
    tz = get_current_timezone()
    dt = datetime.combine(dt, time(hour=int(math.floor(x)), minute=int((x - math.floor(x)) * 60), second=0, tzinfo=tz))
    op = set([s['cashdesk'] for s in sessions if s['start'] <= dt and s['end'] >= dt])
    return len(op)


class Command(BaseCommand):
    help = 'Generate time graphs'

    def handle(self, *args, **kwargs):
        tz = get_current_timezone()
        sessions = CashdeskSession.objects.filter(
            cashdesk__name__startswith="Kasse"
        ).values('id', 'start', 'end', 'cashdesk')
        firststart = CashdeskSession.objects.order_by('start').first().start.date()
        lastend = CashdeskSession.objects.order_by('-end').first().end.date()
        days = (lastend - firststart).days + 1

        fig, axs = plt.subplots(math.ceil(days / 2), 2, figsize=(11.69, 8.27), sharey=True)
        for i in range(days):
            sp = axs[i // 2, i % 2]
            x = np.linspace(0, 24, 300)[:-1]
            day = firststart + timedelta(days=i)

            d = TransactionPosition.objects.filter(
                transaction__datetime__lt=firststart + timedelta(days=i + 1),
                transaction__datetime__gt=firststart + timedelta(days=i)
            ).values('transaction__datetime', 'preorder_position')
            h = sp.hist([
                [dtf(p['transaction__datetime'].astimezone(tz)) for p in d if p['preorder_position']],
                [dtf(p['transaction__datetime'].astimezone(tz)) for p in d if not p['preorder_position']]
            ], label=[
                'Presale transactions',
                'Cash transactions'
            ], bins=np.arange(0, 24.5, 0.5), histtype='barstacked')
            sp.set_title(day.strftime("%Y-%m-%d"))
            ax2 = sp.twinx()
            ax2.plot(x, [opensessions(x, sessions, firststart + timedelta(days=i)) for x in x],
                     label='Open cashdesks', color='r')
            ax2.set_ylim(0, 6)
            if i == 0:
                ax2.legend(loc='upper left')
            elif i == 3:
                ax2.set_ylabel('Open cashdesks')
            sp.set_xlim(0, 24)
            sp.set_xticks(range(0, 25, 2))

        axs[1, 1].legend(loc='upper left')
        axs[1, 0].set_ylabel(u'Number of Transactions')
        axs[2, 0].set_xlabel(u'Time of day')
        fig.tight_layout()
        fig.suptitle('Cashdesk transactions 33c3')
        plt.savefig('transactions.svg')
        plt.savefig('transactions.png')
