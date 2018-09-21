from .config import Config

def merge_to_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

def conf_api(params):
        if 'api_key' in params:
            Config.api_key = params.pop('api_key')