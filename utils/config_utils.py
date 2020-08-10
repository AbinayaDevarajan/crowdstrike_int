import yaml

class ConfigurationReader:
    def __init__(self, config_file, config_type="yaml"):
        self.config_file = config_file
        self.configuration = None

    '''
        read_config_file: To read the YAML configuration file.
        This will take in the configuration file and assign the python dictionary
        to the member variable configuration.

    '''

    def read_config_file(self):
        try:
            with open(self.config_file, 'r') as ymlfile:
                self.configuration = yaml.load(ymlfile, Loader=yaml.FullLoader)
        except (yaml.YAMLError, yaml.MarkedYAMLError) as e:
            raise Exception(
                'Your settings file(s) contain invalid YAML syntax! Please fix and restart!, {}'.
                format(str(e))
            )
    '''
        This module will return the configuration attributes: configured
        in the YAML file.
    '''

    def __get_configuration_attributes__(
        self, configuration_part, fetch_fields=True
    ):
        try:
            return self.configuration[configuration_part]
        except KeyError as e:
            raise Exception(
                'Your configuration settings file(s) contains improper configuration '
                ', Please fix and restart!, {}'.format( str(e)
                )
            )

    def get_ftp_server_config(self):
        try:
            return self.configuration["ftp_server"]
        except KeyError:
            raise Exception(
                'The FTP server configurations are not configured, please configure dcm_user in yml file'
            )
