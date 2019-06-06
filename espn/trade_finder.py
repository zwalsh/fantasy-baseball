import logging

from espn.trade import Trade


LOGGER = logging.getLogger("espn.trade_finder")


def all_current_trades(api):
    """
    Returns all current trades in the league accessible by the given EspnApi.
    :param EspnApi api: the API access object that will be used to find all trades
    :return list: all of the Trades currently outstanding
    """
    all_info = api.all_info().json()
    pending = all_info.get("pendingTransactions", None)
    if pending is None:
        return set()
    trades = filter(is_trade, pending)
    return set(map(lambda t: trade_object_to_trade(t, api), trades))


def is_trade(transaction):
    return transaction["type"] == "TRADE_PROPOSAL"


def trade_object_to_trade(trade_object, api):
    """
    Takes a JSON object representing a Trade and fetches all the Players in the
    object, creating and returning the equivalent Python Trade object
    :param dict trade_object: the JSON response to translate
    :param EspnApi api: the API to use to fetch players
    :return Trade: the Trade that the JSON object represented
    """
    originator_id = trade_object["teamId"]
    other_id = None
    originator_players = []
    other_players = []
    items = trade_object["items"]
    for item in items:
        cur_team = item["fromTeamId"]
        player = api.player(item["playerId"])
        if cur_team == originator_id:
            originator_players.append(player)
        else:
            other_id = cur_team
            other_players.append(player)
    orig_name = api.team_name(originator_id)
    other_name = api.team_name(other_id)

    return Trade(orig_name, other_name, originator_players, other_players)
