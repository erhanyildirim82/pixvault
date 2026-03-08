"""
event_group.py — Etkinlik gruplama veri modeli.
"""

from dataclasses import dataclass, field
from datetime import date


TURKISH_MONTHS = {
    1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan',
    5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos',
    9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık',
}


@dataclass
class EventGroup:
    name: str
    dates: list[date] = field(default_factory=list)

    @property
    def folder_name(self) -> str:
        """Örnek: 'Kayak Tatili [15-17 Aralık]'"""
        if not self.dates:
            return self.name
        sorted_dates = sorted(self.dates)
        first = sorted_dates[0]
        last = sorted_dates[-1]
        month_name = TURKISH_MONTHS[first.month]
        if first == last:
            date_str = f'{first.day} {month_name}'
        elif first.month == last.month:
            date_str = f'{first.day}-{last.day} {month_name}'
        else:
            last_month = TURKISH_MONTHS[last.month]
            date_str = f'{first.day} {month_name}-{last.day} {last_month}'
        return f'{self.name} [{date_str}]'

    def contains_date(self, d: date) -> bool:
        return d in self.dates

    def overlaps_range(self, start: date, end: date) -> bool:
        return any(start <= d <= end for d in self.dates)
