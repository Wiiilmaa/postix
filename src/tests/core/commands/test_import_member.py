import pytest
import tempfile

from django.core.management import call_command

from postix.core.models import ListConstraint


@pytest.yield_fixture
def sample_member_file_ccc():
    with tempfile.NamedTemporaryFile() as t:
        t.write(b"""chaos_number	first_name	last_name	state
2			bezahlt
4	A	B	Verzug
5	C	D	bezahlt
8	E	F	bezahlt
11	G	H	ruhend
14	I	J	ruhend
23	K	L	bezahlt
""")
        t.seek(0)
        yield t.name


@pytest.mark.django_db
def test_member_import_ccc(sample_member_file_ccc):
    call_command('import_member', sample_member_file_ccc)
    lc = ListConstraint.objects.get(confidential=True, name='Mitglieder')
    assert set((e.identifier, e.name) for e in lc.entries.all()) == {
        ('2', ' '),
        ('4', 'A B'),
        ('5', 'C D'),
        ('8', 'E F'),
        ('11', 'G H'),
        ('14', 'I J'),
        ('23', 'K L'),
    }
