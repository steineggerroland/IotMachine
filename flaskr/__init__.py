import os

import yamlenv
from flask import Flask, request
from flask_babel import Babel
from flask_bootstrap import Bootstrap5

from flaskr.views import VirtualEntities
from iot.infrastructure.machine.appliance_depot import ApplianceDepot
from iot.infrastructure.register_of_persons import RegisterOfPersons
from iot.infrastructure.room_catalog import RoomCatalog


def create_app(default_config_file_name: str, appliance_depot: ApplianceDepot, room_catalog: RoomCatalog,
               register_of_persons: RegisterOfPersons, config: dict = None):
    app = Flask(__name__)

    app.config.from_file(default_config_file_name, load=yamlenv.load)
    app.config.from_mapping(config)

    app.appliance_depot = appliance_depot
    app.room_catalog = room_catalog
    app.register_of_persons = register_of_persons

    app.add_url_rule(
        "/virtual-entities/",
        view_func=VirtualEntities.ListView.as_view("ve_list")
    )

    def locale_selector():
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    @app.context_processor
    def utility_processor():
        return dict(lang=locale_selector())

    babel = Babel(app, default_translation_directories="../translations",
                  locale_selector=locale_selector)

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'sketchy'
    bootstrap = Bootstrap5(app)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
