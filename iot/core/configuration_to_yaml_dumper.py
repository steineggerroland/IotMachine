from collections import OrderedDict
from typing import List

from yaml import Dumper, Node


class ConfigDumpers:

    def configuration_dumper(dumper: Dumper, c) -> Node:
        to_dict = {'mqtt': c.mqtt,
                   'things': [thing for thing in c.things]}
        if c.time_series: to_dict['time_series'] = c.time_series
        if c.calendars_config and (c.calendars_config.categories or c.calendars_config.calendars): to_dict['calendars'] = c.calendars_config
        if c.flaskr: to_dict['flaskr'] = c.flaskr
        return dumper.represent_dict(
            _sort_keys(OrderedDict(to_dict), ['mqtt', 'time_series', 'things', 'calendars', 'flaskr']).items())

    def time_series_dumper(dumper: Dumper, ts) -> Node:
        dict__ = ts.__dict__
        _remove_none(dict__)
        return dumper.represent_dict(
            _sort_keys(OrderedDict(dict__), ['url', 'username', 'password', 'bucket_name']).items())

    def mqtt_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        to_dict = OrderedDict(dict__)
        del to_dict['has_credentials']
        return dumper.represent_dict(_sort_keys(to_dict, ['url', 'port', 'username', 'password', 'client_id']).items())

    def measure_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        return dumper.represent_dict(_sort_keys(OrderedDict(dict__), ['type', 'path']).items())

    def mqtt_measure_source_dumper(dumper: Dumper, o) -> Node:
        to_dict = {'mqtt_topic': o.mqtt_topic}
        if len(o.measures) == 1:
            to_dict = to_dict | o.measures[0].__dict__
        else:
            to_dict['measures'] = [m for m in o.measures]
        _remove_none(to_dict)
        return dumper.represent_dict(
            _sort_keys(OrderedDict(to_dict), ['mqtt_topic', 'type', 'path', 'measures', 'topic', 'subject']).items())

    def url_conf_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        return dumper.represent_dict(_sort_keys(OrderedDict(dict__),
                                                ['application', 'name', 'url', 'username', 'password',
                                                 'update_cron']).items())

    def referenced_url_dumper(dumper: Dumper, o) -> Node:
        return dumper.represent_dict(OrderedDict({
            'application': o.application,
            'reference_name': o.name
        }).items())

    def caldav_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        return dumper.represent_dict(_sort_keys(OrderedDict(dict__),
                                                ['name', 'url', 'username', 'password',
                                                 'update_cron', 'color_hex']).items())

    def referenced_caldav_dumper(dumper: Dumper, o) -> Node:
        return dumper.represent_dict(OrderedDict({
            'application': o.application,
            'reference_name': o.name
        }).items())

    def category_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        return dumper.represent_dict(_sort_keys(OrderedDict(dict__), ['name', 'color_hex']).items())

    def calendars_dumper(dumper: Dumper, o) -> Node:
        return dumper.represent_dict(OrderedDict({'categories': [cat for cat in o.categories],
                                                  'caldav': [cal for cal in o.calendars]}).items())

    def sources_dumper(dumper: Dumper, o) -> Node:
        return dumper.represent_list([source for source in o.list])

    def planned_notification_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        return dumper.represent_dict(
            _sort_keys(OrderedDict(dict__), ['mqtt_topic', 'subject', 'cron_expression']).items())

    def destinations_dumper(dumper: Dumper, o) -> Node:
        return dumper.represent_dict(
            OrderedDict({'planned_notifications': [planned_notification for planned_notification in
                                                   o.planned_notifications]}).items())

    def range_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        return dumper.represent_dict(_sort_keys(OrderedDict(dict__), ['lower', 'upper']).items())

    def thresholds_dumper(dumper: Dumper, o) -> Node:
        dict__ = dict(o.__dict__)
        _remove_none(dict__)
        to_dict = OrderedDict(dict__)
        to_dict['optimal'] = o.optimal
        return dumper.represent_dict(_sort_keys(to_dict, ['optimal', 'critical_lower', 'critical_upper']).items())

    def iot_thing_dumper(dumper: Dumper, o) -> Node:
        to_dict = OrderedDict({'name': o.name, 'type': o.type})
        if o.sources and o.sources.list:
            to_dict['sources'] = o.sources
        if o.destinations and o.destinations.planned_notifications:
            to_dict['destinations'] = o.destinations
        if o.humidity_thresholds:
            to_dict['humidity_thresholds'] = o.humidity_thresholds
        if o.temperature_thresholds:
            to_dict['temperature_thresholds'] = o.temperature_thresholds
        return dumper.represent_dict(_sort_keys(to_dict,
                                                ['name', 'type', 'temperature_thresholds', 'humidity_thresholds',
                                                 'sources', 'destinations']).items())


def _sort_keys(d: OrderedDict, a: List[str]) -> OrderedDict:
    for key in a:
        if key in d:
            d.move_to_end(key)
    return d


def _remove_none(obj):
    if type(obj) is dict:
        none_keys = []
        for key in obj.keys():
            if obj[key] is None:
                none_keys.append(key)
            else:
                _remove_none(obj[key])
        for k in none_keys:
            del obj[k]
    elif type(obj) is list:
        for o in obj:
            _remove_none(o)
