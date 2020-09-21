class MatcherSettingValue:

    def __init__(self, value, description='', default=False):
        self.description = description
        self.value = value
        self.default = default


class MatcherSetting:

    def __init__(self, name, options, value=None, description=''):
        self.name = name
        self.description = description
        self.value = value
        self.options = options

    def get_options(self):
        return self.options

    def set_value(self, value: MatcherSettingValue):
        self.value = value

    def get_value(self):
        if self.value is None:
            return self.get_default()
        else:
            return self.value

    def get_default(self):
        for option in self.options:
            if option.default:
                return option


class MatcherConfig:

    def __init__(self, settings):
        self.settings = MatcherConfig._settings_to_dict(settings)

    @staticmethod
    def _settings_to_dict(settings):
        _result = dict()
        for setting in settings:
            _result[setting.name] = setting
        return _result

    def add_setting(self, setting: MatcherSetting):
        self.settings[setting.name] = setting

    def get_settings(self):
        _settings = []
        for setting in self.settings:
            _settings.append(setting)
        return _settings

    def get_setting(self, name):
        return self.settings.get(name)
