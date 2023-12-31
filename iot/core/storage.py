import json
import time
from pathlib import Path
from threading import Thread

from iot.core.timeseries_storage_in_memory import InMemoryTimeSeriesStorage
from iot.core.timeseries_storage_influxdb import InfluxDbTimeSeriesStorage
from iot.core.timeseries_types import ConsumptionMeasurement
from iot.infrastructure.thing import Thing
from iot.infrastructure.units import Temperature


class Storage:
    def __init__(self, db_path: Path, thing_names: [str], time_series_config):
        self.db_name = db_path
        self.things = {}
        db_file = None
        try:
            db_file = open(db_path)
            things_in_db = json.loads(db_file.read())
            for thing_name in thing_names:
                self.things[thing_name] = things_in_db[thing_name] \
                    if thing_name in things_in_db \
                    else {'type': 'thing', 'name': thing_name}
        except FileNotFoundError:
            for thing_name in thing_names:
                self.things[thing_name] = {'type': 'thing', 'name': thing_name}
        finally:
            if db_file:
                db_file.close()
        self._scheduled_snapshots_thread: Thread = Thread(target=self._scheduled_snapshots, daemon=True)
        if time_series_config:
            self.time_series_storage = InfluxDbTimeSeriesStorage(time_series_config)
        else:
            self.time_series_storage = InMemoryTimeSeriesStorage()

    def start(self):
        self._scheduled_snapshots_thread.start()
        self.time_series_storage.start()

    def shutdown(self, timeout=5):
        self._scheduled_snapshots_thread.join(timeout)
        self._save_snapshot_to_file()
        self.time_series_storage.shutdown()

    def _scheduled_snapshots(self):
        while True:
            time.sleep(60)
            self._save_snapshot_to_file()

    def _save_snapshot_to_file(self):
        with open(self.db_name, 'w') as db_file:
            json.dump(self.things, db_file)

    def load_thing(self, thing_name: str):
        return self.things[thing_name]

    def update_thing(self, thing: Thing):
        self.things[thing.name] = thing.to_dict()

    def append_power_consumption(self, watt: float, thing_name: str):
        self.time_series_storage.append_power_consumption(watt, thing_name)

    def get_power_consumptions_for_last_seconds(self, seconds: int, thing_name: str) -> [ConsumptionMeasurement]:
        return self.time_series_storage.get_power_consumptions_for_last_seconds(seconds, thing_name)

    def append_room_climate(self, temperature: Temperature, humidity: float, thing_name):
        self.time_series_storage.append_room_climate(temperature, humidity, thing_name)
