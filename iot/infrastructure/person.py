from datetime import datetime, timedelta
from functools import reduce
from typing import List

from iot.infrastructure.thing import Thing
from iot.infrastructure.time.calendar import Calendar


class Person(Thing):
    def __init__(self, name: str, calendars: List[Calendar] = (), last_updated_at: datetime = datetime.now(),
                 last_seen_at: None | datetime = None):
        super().__init__(name, last_updated_at, last_seen_at, online_delta_in_seconds=60 * 10)
        self.calendars = calendars

    def get_appointments_for(self, start: datetime, delta: timedelta):
        return list(reduce(lambda a, b: a + b, map(lambda c: c.find_appointments(start, delta), self.calendars), []))

    def to_dict(self):
        return {"name": self.name,
                "calendars": list(map(lambda c: c.to_dict(), self.calendars)),
                "online_status": self.online_status(),
                "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at is not None else None,
                "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at is not None else None}

    def set_calendars(self, calendars):
        now = datetime.now()
        return Person(self.name, calendars, now, now)
