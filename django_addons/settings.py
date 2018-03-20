# -*- coding: utf-8 -*-
import importlib.util
import os
import shutil
from . import utils
from .utils import global_settings
from .exceptions import ImproperlyConfigured
from pprint import pformat
import six
from six.moves import UserDict
from functools import partial


def save_settings_dump(settings, path):
    to_dump = {key: value for key, value in settings.items() if key == key.upper()}
    with open(path, 'w+') as fobj:
        fobj.write(
            pformat(
                to_dump,
                indent=4,
            )
        )


def count_str(number):
    return '{0:05d}'.format(number)


class SettingsDictWrapper(UserDict):
    """
    hack to get around detecting if an altered setting was actually explicitly
    set or just happens to be the same as the django default.
    """
    def __init__(self, wrapped, watched_keys):
        self.data = wrapped
        self._watched_keys = watched_keys
        self.altered_keys = set()
        # register any already set settings as altered keys, if necessary
        for key, value in self.data.items():
            if key in self._watched_keys:
                self[key] = value

    def __setitem__(self, key, value):
        if key in self._watched_keys:
            self.altered_keys.add(key)
        self.set(key, value)

    def set(self, key, value):
        UserDict.__setitem__(self, key, value)

    def update(self, *args, **kwargs):
        if six.PY3:
            UserDict.update(self, *args, **kwargs)
        else:
            self._update_py2(*args, **kwargs)

    def _update_py2(*args, **kwargs):
        # copied from python2 standardlib UserDict.update() and altered a little
        # (see commented out lines below)
        if not args:
            raise TypeError("descriptor 'update' of 'UserDict' object "
                            "needs an argument")
        self = args[0]
        args = args[1:]
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            dict = args[0]
        elif 'dict' in kwargs:
            dict = kwargs.pop('dict')
            import warnings
            warnings.warn("Passing 'dict' as keyword argument is deprecated",
                          PendingDeprecationWarning, stacklevel=2)
        else:
            dict = None
        if dict is None:
            pass
        # elif isinstance(dict, UserDict):
        #     self.data.update(dict.data)
        # elif isinstance(dict, type({})) or not hasattr(dict, 'items'):
        elif not hasattr(dict, 'items'):
            # this case is not covered for altered state tracking
            self.data.update(dict)
        else:
            for k, v in dict.items():
                self[k] = v
        if len(kwargs):
            # self.data.update(kwargs)
            for k, v in kwargs.items():
                self[k] = v

    def update_without_tracking_altered_state(self, a_dict):
        for key, value in a_dict.items():
            self.set(key, value)


def load(settings, **kwargs):
    global_debug = utils.boolean_ish(os.environ.get('DJANGO_ADDONS_DEBUG', False))
    # fallback to global debug flag
    debug = kwargs.get('debug', global_debug)

    settings = SettingsDictWrapper(
        settings,
        watched_keys=global_settings.keys(),
    )
    env = partial(utils.djsenv, settings=settings)
    settings['BASE_DIR'] = env(
        'BASE_DIR',
        os.path.dirname(os.path.abspath(settings['__file__']))
    )

    settings['ADDONS_CONFIG_DIR'] = env(
        'ADDONS_CONFIG_DIR',
        os.path.join(settings['BASE_DIR'], 'addons-config')
    )
    # settings['ADDONS_DEV_DIR'] = env(
    #     'ADDONS_DEV_DIR',
    #     os.path.join(settings['BASE_DIR'], 'addons-dev')
    # )
    # utils.mkdirs(settings['ADDONS_DEV_DIR'])
    utils.mkdirs(settings['ADDONS_CONFIG_DIR'])

    if debug:
        # TODO: .debug is not multi-process safe!
        debug_path = os.path.join(settings['ADDONS_CONFIG_DIR'], '.debug')
        shutil.rmtree(debug_path, ignore_errors=True)
        utils.mkdirs(debug_path)

    def dump(obj, count, name):
        if not debug:
            # do nothing if debug is not turned on
            return 0
        dump_name = '{}-{}.dump'.format(count_str(count), name)
        dump_path = os.path.join(debug_path, dump_name)
        save_settings_dump(obj, dump_path)
        return count + 1

    debug_count = 0
    debug_count = dump(settings, debug_count, 'initial')

    # load global defaults
    for key, value in global_settings.items():
        if key not in settings:
            # SettingsDictWrapper.set skips the default settings change
            # recording
            settings.set(key, value)

    debug_count = dump(settings, debug_count, 'load-globals')

    # normalise tuple settings to lists
    for key, value in settings.items():
        if isinstance(value, tuple):
            settings.set(key, list(value))

    debug_count = dump(settings, debug_count, 'normalise')

    # add Addon default settings if they are not there yet
    settings.setdefault('ADDON_URLS', [])
    settings.setdefault('ADDON_URLS_I18N', [])
    settings.setdefault('INSTALLED_APPS', [])
    # load Addon settings
    if not (settings['INSTALLED_ADDONS'] and settings['ADDONS_CONFIG_DIR']):
        return
    for addon_name in settings['INSTALLED_ADDONS']:
        load_addon_settings(
            addon_name=addon_name,
            settings=settings,
        )
        debug_count = dump(settings, debug_count, addon_name)


def load_addon_settings(addon_name, settings):
    # print(f'load addon settings "{addon_name}"')
    addon_config_module_name = f'{addon_name}.addon_config'
    addon_config_spec = importlib.util.find_spec(addon_config_module_name)
    print(f'{addon_name} --> CONFIG spec {addon_config_spec}')
    if not addon_config_spec:
        raise ImproperlyConfigured(
            f'{addon_config_module_name}'
        )
    # if addon_name == 'django_addon':
    #     import ipdb; ipdb.set_trace()
    addon_config_module = importlib.import_module(addon_config_module_name)
    # addon_config_module = importlib.util.module_from_spec(addon_config_spec)
    # print(f'{addon_name} --> CONFIG mod {addon_config_module}')
    # addon_config_spec.loader.exec_module(addon_config_module)
    # print(f'{addon_name} --> CONFIG mod loaded')
    config_json_path = os.path.join(
        settings['ADDONS_CONFIG_DIR'],
        f'{addon_name}.json',
    )
    if os.path.exists(config_json_path):
        config = utils.json_from_file(config_json_path)
    else:
        config = {}

    addon_form_module_name = f'{addon_name}.addon_form'
    addon_form_spec = importlib.util.find_spec(addon_form_module_name)
    print(f'{addon_name} --> FORM spec {addon_form_spec}')
    if addon_form_spec:
        addon_form_module = importlib.import_module(addon_form_module_name)
        # addon_form_module = importlib.util.module_from_spec(addon_form_spec)
        # print(f'{addon_name} --> FORM mod {addon_form_module}')
        # addon_form_spec.loader.exec_module(addon_form_module)
        # print(f'{addon_name} --> FORM mod loaded')
        Form = addon_form_module.Form
        for field_name, field in Form._fields:
            if field_name not in config:
                config[field_name] = field.initial
        form = Form(data=config)
        if not form.is_valid():
            raise ImproperlyConfigured(
                f'{addon_form_module} validation error: ' + ', '.join([
                    f'{field}: {error}' for field, error in form.errors.items()
                ])
            )
        formdata = form.cleaned_data
    else:
        formdata = {}
    # load() must alter settings in-place.
    addon_config_module.load(
        formdata=formdata,
        settings=settings,
    )

    # remove duplicates
    settings['INSTALLED_APPS'] = utils.remove_duplicates(settings['INSTALLED_APPS'])
    if 'MIDDLEWARE' in settings:
        settings['MIDDLEWARE'] = utils.remove_duplicates(settings['MIDDLEWARE'])
