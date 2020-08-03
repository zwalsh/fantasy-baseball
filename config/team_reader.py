import logging
from json import JSONDecodeError
import json

from config.team_config import EspnTeamConfig

LOGGER = logging.getLogger("config.team_reader")


def all_teams(directory):
    """
    Looks on the filesystem and returns all EspnTeamConfigs it can find.

    They should be stored on disk in the given directory as JSON text files
    with all the fields of the EspnTeamConfig as keys.

    :param Path directory: the directory in which to look for the EspnTeamConfigs
    :return list: all EspnTeamConfigs present on the filesystem
    """
    files = filter(lambda child: child.is_file(), directory.iterdir())
    configs = []
    for file in files:
        try:
            config = read_json(file.read_text())
            configs.append(config)
        except JSONDecodeError:
            LOGGER.error(
                "could not deserialize config file %(filename)s",
                {"filename": file.name},
            )
            continue
        except KeyError as e:
            error_info = {"filename": file.name, "msg": str(e)}
            LOGGER.error(
                "could not convert the JSON in config file %(filename)s to an EspnTeamConfig: "
                "missing key %(msg)s",
                error_info,
            )
            continue
        except ValueError as e:
            error_info = {"filename": file.name, "msg": str(e)}
            LOGGER.error(
                "could not convert the JSON in config file %(filename)s to an EspnTeamConfig: "
                "%(msg)s",
                error_info,
            )
            continue

    return configs


def read_json(file_contents):
    """
    Reads the contents of a file and converts it into an EspnTeamConfig. Assumes that the input is a JSON string.
    Converts the input into an EspnTeamConfig, returning None if the string does not meet the specifications.
    :param str file_contents: JSON-encoded string representing an EspnTeamConfig
    :return EspnTeamConfig: the configuration encoded by the input
    """
    config_dict = json.loads(file_contents)
    username = str(config_dict["username"])
    league_id = int(config_dict.get("league_id"))
    team_id = int(config_dict.get("team_id"))

    return EspnTeamConfig(username, league_id, team_id)
