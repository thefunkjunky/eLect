import json
import urllib

class DevelopmentConfig(object):
    try:
        with open("main_config_variables.json", 'r') as cfg_file:
            cfg_params = json.load(cfg_file)
    except Exception as e:
        print("Error loading main_config_variables.json configuration file.  Please run sql_connection_config_script.py")
        print("Exception: {}".format(e))
        sys.exit()

    DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
        cfg_params['user'],
        urllib.parse.quote(cfg_params['password']), # Encodes weird passwords with spaces and whatnot for urls
        cfg_params['host'],
        cfg_params['port'],
        cfg_params['dbname'])

    SECRET_KEY = cfg_params['secret_key']
    SERVER_IP = cfg_params['host']
    DEBUG = True


class TestingConfig(object):
    try:
        with open("test_config_variables.json", 'r') as cfg_file:
            cfg_params = json.load(cfg_file)
    except Exception as e:
        print("Error loading test_config_variables configuration file.  Please run sql_connection_config_script.py")
        print("Exception: {}".format(e))
        sys.exit()

    DATABASE_URI = "postgresql://{}:{}@{}:{}/{}".format(
        cfg_params['user'],
        urllib.parse.quote(cfg_params['password']), # Encodes weird passwords with spaces and whatnot for urls
        cfg_params['host'],
        cfg_params['port'],
        cfg_params['dbname'])

    SECRET_KEY = cfg_params['secret_key']
    SERVER_IP = cfg_params['host']
    DEBUG = True
