import unittest
from unittest.mock import Mock

from iot.core.configuration import IotThingConfig, UrlConf, Sources
from iot.infrastructure.person_service import PersonService


class PersonServiceCase(unittest.TestCase):
    def test_constructor(self):
        name = "mika"
        service = PersonService(Mock(),
                                IotThingConfig(name, sources=Sources([UrlConf("calendar", "calendar.url")])))
        self.assertEqual(name, service.person.name)
        self.assertEqual(1, len(service.person.calendars))
        self.assertListEqual([], service.person.calendars[0].appointments)


if __name__ == '__main__':
    unittest.main()