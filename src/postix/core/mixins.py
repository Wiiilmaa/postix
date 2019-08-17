from typing import Dict


class Exportable:
    """Returns data for the settings export."""

    @property
    def data(self) -> Dict:
        return {
            field.name: getattr(self, field.name, None)
            for field in self._meta.fields
        }
