import unittest
from pathlib import Path

from iot.core import configuration
from iot.core.configuration import PlannedNotification, IncompleteConfiguration, Source, Measure

DIR = Path(__file__).parent


class ConfigurationTest(unittest.TestCase):
    def test_complete_config(self):
        config = configuration.load_configuration(DIR / "complete_test_config.yaml")
        self.assertEqual("my.machine.local", config.mqtt.url)
        self.assertEqual(1337, config.mqtt.port)
        self.assertEqual("user", config.mqtt.username)
        self.assertTrue(config.mqtt.has_credentials)
        self.assertEqual("my-secret", config.mqtt.password)
        self.assertEqual("my-client", config.mqtt.client_id)

        self.assertEqual("influxdb.url", config.time_series.url)
        self.assertEqual("influxdb", config.time_series.username)
        self.assertEqual("secret", config.time_series.password)
        self.assertEqual("bucket_to_save_to", config.time_series.bucket_name)

        self.assertEqual("super_thing", config.things[0].name)
        self.assertEqual("dryer", config.things[0].type)
        self.assertIn(Source('consumption/topic', [Measure(source_type='consumption')]), config.things[0].sources.list)
        self.assertIn(Source('loading/topic', [Measure(source_type='loading')]), config.things[0].sources.list)
        self.assertIn(Source('unloading/topic', [Measure(source_type='unloading')]), config.things[0].sources.list)

        self.assertIn(PlannedNotification('update/every-second/topic', '*/1 * * * * *'),
                      config.things[0].destinations.planned_notifications)
        self.assertIn(PlannedNotification('update/every-15-minutes/topic', '* */15 * * * *'),
                      config.things[0].destinations.planned_notifications)

        self.assertEqual("Kitchen", config.things[1].name)
        self.assertEqual("room", config.things[1].type)
        self.assertEqual("kitchen/sensor/temperature", config.things[1].sources.list[0].topic)
        self.assertEqual("temperature", config.things[1].sources.list[0].measures[0].type)
        self.assertEqual("$.update.temperature", config.things[1].sources.list[0].measures[0].path)

        self.assertEqual("Bathroom", config.things[2].name)
        self.assertEqual("room", config.things[2].type)
        self.assertEqual(15, config.things[2].temperature_thresholds.critical_lower)
        self.assertEqual(20, config.things[2].temperature_thresholds.optimal.lower)
        self.assertEqual(22, config.things[2].temperature_thresholds.optimal.upper)
        self.assertEqual(30, config.things[2].temperature_thresholds.critical_upper)
        self.assertEqual(50, config.things[2].humidity_thresholds.critical_lower)
        self.assertEqual(65, config.things[2].humidity_thresholds.optimal.lower)
        self.assertEqual(75, config.things[2].humidity_thresholds.optimal.upper)
        self.assertEqual(90, config.things[2].humidity_thresholds.critical_upper)
        self.assertEqual("bath/sensor/temperature", config.things[2].sources.list[0].topic)
        self.assertEqual("temperature", config.things[2].sources.list[0].measures[0].type)
        self.assertEqual("$.temperature", config.things[2].sources.list[0].measures[0].path)
        self.assertEqual("humidity", config.things[2].sources.list[0].measures[1].type)
        self.assertEqual("$.humidity", config.things[2].sources.list[0].measures[1].path)

    def test_min_config(self):
        min_config = configuration.load_configuration(DIR / "min_test_config.yaml")
        self.assertEqual("mqtt.local", min_config.mqtt.url)
        self.assertIsNotNone(min_config.mqtt.port)
        self.assertFalse(min_config.mqtt.has_credentials)
        self.assertIsNotNone(min_config.mqtt.client_id)

        self.assertEqual("super_washer", min_config.things[0].name)
        self.assertEqual("washing_machine", min_config.things[0].type)
        self.assertFalse(min_config.things[0].sources.list)
        self.assertFalse(min_config.things[0].destinations.planned_notifications)

        self.assertEqual("Dining room", min_config.things[1].name)
        self.assertEqual("room", min_config.things[1].type)
        self.assertFalse(min_config.things[1].sources.list)
        self.assertFalse(min_config.things[1].destinations.planned_notifications)

    def test_incomplete_sources_produce_errors(self):
        self.assertRaises(IncompleteConfiguration,
                          configuration.load_configuration, (DIR / "incomplete_loading_source_config.yaml"))
        self.assertRaises(IncompleteConfiguration,
                          configuration.load_configuration, (DIR / "incomplete_unloading_source_config.yaml"))
        self.assertRaises(IncompleteConfiguration,
                          configuration.load_configuration, (DIR / "incomplete_mqtt_config.yaml"))
        self.assertRaises(IncompleteConfiguration,
                          configuration.load_configuration, (DIR / "incomplete_thing_config.yaml"))
        self.assertRaises(IncompleteConfiguration,
                          configuration.load_configuration, (DIR / "incomplete_influxdb_config.yaml"))


if __name__ == '__main__':
    unittest.main()
