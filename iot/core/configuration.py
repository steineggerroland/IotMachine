import yamlenv


class IncompleteConfiguration(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class TimeSeriesConfig:
    def __init__(self, url: str, username: str, password: str, bucket_name: str):
        self.url = url
        self.username = username
        self.password = password
        self.bucket_name = bucket_name


class MqttConfiguration:
    def __init__(self, url: str, client_id: str, port: int = 1883, credentials: str | None = None):
        self.url = url
        self.port = port if port is not None else 1883
        if credentials is not None:
            self.username = credentials['username']
            self.password = credentials['password']
            self.has_credentials = True
        else:
            self.has_credentials = False
        self.client_id = client_id

    def __str__(self):
        if self.has_credentials:
            return f"mqtt ({self.url}:{self.port}, {self.username}:<pw len {len(self.password)}>)"
        return f"mqtt ({self.url}:{self.port})"


class Measure:
    def __init__(self, source_type: str, path: None | str = None):
        self.type = source_type
        self.path = path


class Source:
    def __init__(self, topic: str, measures: [Measure]):
        self.topic = topic
        self.measures = measures

    def __eq__(self, other):
        if not isinstance(other, Source) or self.topic != other.topic:
            return False
        for measure in self.measures:
            if not any(vars(measure) == vars(other_measure) for other_measure in other.measures):
                return False
        return True


class Sources:
    def __init__(self, sources: [Source]):
        self.list = sources


class PlannedNotification:
    def __init__(self, mqtt_topic: str, cron_expression: str):
        self.mqtt_topic = mqtt_topic
        self.cron_expression = cron_expression

    def __eq__(self, other):
        if not isinstance(other, PlannedNotification):
            return False
        return self.mqtt_topic == other.mqtt_topic and self.cron_expression == other.cron_expression


class Destinations:
    def __init__(self, planned_notifications: list[PlannedNotification]):
        self.planned_notifications = planned_notifications


class RangeConfig:
    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper


class ThresholdsConfig:
    def __init__(self, optimal: RangeConfig, critical_lower: float, critical_upper: float):
        self.optimal = optimal
        self.critical_lower = critical_lower
        self.critical_upper = critical_upper


class IotThingConfig:
    def __init__(self, name: None | str = None, thing_type: None | str = None,
                 temperature_thresholds: None | ThresholdsConfig = None,
                 humidity_thresholds: None | ThresholdsConfig = None,
                 sources: None | Sources = None,
                 destinations: None | Destinations = None):
        self.name = name
        self.type = thing_type
        self.temperature_thresholds = temperature_thresholds
        self.humidity_thresholds = humidity_thresholds
        self.sources = sources
        self.destinations = destinations

    def __str__(self):
        return f"{self.name} ({self.type}, {self.sources}, {self.destinations})"


class Configuration:
    def __init__(self, mqtt: MqttConfiguration, things: [IotThingConfig], time_series: TimeSeriesConfig | None):
        self.mqtt = mqtt
        self.things = things
        self.time_series = time_series

    def __str__(self):
        return f"{self.mqtt}, {self.things}, {self.time_series}"


def load_configuration(config_path):
    conf_file = None
    try:
        conf_file = open(config_path)
        conf_dict = yamlenv.load(conf_file)

        config = _read_configuration(conf_dict)
        return config
    except FileNotFoundError as e:
        raise Exception(f'Configuration file is missing. File "{config_path}" is needed.') from e
    finally:
        if conf_file:
            conf_file.close()


def _read_mqtt_configuration(conf_dict):
    mqtt_dict = conf_dict['mqtt']
    _verify_keys(mqtt_dict, ['url'], 'mqtt')
    return MqttConfiguration(mqtt_dict['url'],
                             mqtt_dict['clientId'] if 'clientId' in mqtt_dict else f"iot-things-client",
                             mqtt_dict['port'] if 'port' in mqtt_dict else None,
                             credentials=_read_mqtt_credentials(mqtt_dict))


def _read_mqtt_credentials(mqtt_dict):
    if 'username' in mqtt_dict and 'password' in mqtt_dict:
        return {'username': mqtt_dict['username'], 'password': mqtt_dict['password']}
    return None


def _read_destination_configuration(thing_dict):
    if 'destinations' not in thing_dict or 'scheduled_updates' not in thing_dict['destinations']:
        return Destinations([])
    planned_notifications = []
    for entry in thing_dict['destinations']['scheduled_updates']:
        _verify_keys(entry, ['topic', 'cron'], 'things[].destinations.scheduled_updates[]')
        planned_notifications.append(PlannedNotification(entry['topic'], entry['cron']))
    return Destinations(planned_notifications)


def _read_sources_configuration(thing_dict):
    if 'sources' not in thing_dict:
        return Sources([])
    sources = []
    if thing_dict['sources']:
        for source in thing_dict['sources']:
            measures = []
            _verify_keys(source, ['topic'], "things[].sources[]")
            if 'measures' in source:
                for measure in source['measures']:
                    _verify_keys(measure, ['type'], "things[].sources[].measures[]")
                    measures.append(Measure(source_type=measure['type'],
                                            path=measure['path'] if 'path' in measure else None))
            else:
                _verify_keys(source, ['type'], "things[].sources[]")
                measures.append(Measure(source_type=source['type'], path=source['path'] if 'path' in source else None))
            sources.append(Source(topic=source['topic'], measures=measures))

    return Sources(sources)


def _read_thresholds_config(thresholds_config: dict, prefix) -> ThresholdsConfig:
    _verify_keys(["optimal", "critical_lower", "critical_upper"], thresholds_config, prefix)
    _verify_keys(["lower", "upper"], thresholds_config['optimal'], f"{prefix}.optimal")
    return ThresholdsConfig(RangeConfig(thresholds_config['optimal']['lower'], thresholds_config['optimal']['upper']),
                            thresholds_config['critical_lower'], thresholds_config['critical_upper'])


def _read_temperature_thresholds_configuration(thing_config: dict) -> None | ThresholdsConfig:
    if "temperature_thresholds" in thing_config:
        return _read_thresholds_config(thing_config['temperature_thresholds'], "things[].temperature_thresholds")
    else:
        return None


def _read_humidity_thresholds_configuration(thing_config: dict) -> None | ThresholdsConfig:
    if "humidity_thresholds" in thing_config:
        return _read_thresholds_config(thing_config['humidity_thresholds'], "things[].humidity_thresholds")
    else:
        return None


def _read_thing(thing_config):
    _verify_keys(thing_config, ["name", "type"], "things[]")
    return IotThingConfig(thing_config['name'], thing_config['type'],
                          _read_temperature_thresholds_configuration(thing_config),
                          _read_humidity_thresholds_configuration(thing_config),
                          _read_sources_configuration(thing_config),
                          _read_destination_configuration(thing_config))


def _read_things(conf_dict):
    _verify_keys(conf_dict, ["things"])
    return [_read_thing(thing_config) for thing_config in conf_dict['things']]


def _read_time_series_config(time_series_config):
    _verify_keys(time_series_config, ['url', 'username', 'password', 'bucket_name'], 'time_series')
    return TimeSeriesConfig(time_series_config['url'], time_series_config['username'], time_series_config['password'],
                            time_series_config['bucket_name'])


def _read_configuration(conf_dict):
    return Configuration(_read_mqtt_configuration(conf_dict),
                         _read_things(conf_dict),
                         _read_time_series_config(conf_dict['time_series']) if 'time_series' in conf_dict else None)


def _verify_keys(yaml_dict, keys, prefix=None):
    for key in keys:
        if key not in yaml_dict:
            raise IncompleteConfiguration(f"Config is missing key '{prefix + '.' if prefix else ''}{key}'")
