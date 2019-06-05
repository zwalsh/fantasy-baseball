from functools import reduce


class Trade:

    def __init__(self, from_team, to_team, send_players, receive_players):
        """
        Represents a trade between two teams. In the trade, the send_players would move from the from_team
        to the to_team, and vice verse for the receive_players.
        :param str from_team: the name of the team originating the trade
        :param str to_team: the name of the other team in the trade
        :param list send_players: the players to be sent by the originator
        :param list receive_players: the players to be received by the originator
        """
        self.from_team = from_team
        self.to_team = to_team
        self.send_players = send_players
        self.receive_players = receive_players

    def __str__(self):
        send_lasts = Trade.last_names(self.send_players)
        recv_lasts = Trade.last_names(self.receive_players)
        return f"{self.from_team} -> {self.to_team}, {send_lasts} <-> {recv_lasts}"

    @staticmethod
    def last_names(players):
        player_names = map(lambda p: p.last, players)
        return reduce(lambda acc, name: acc + " " + name if acc is not None else name, player_names)
