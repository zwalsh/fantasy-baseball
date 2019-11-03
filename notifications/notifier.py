import sys

from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat


class Notifier:
    def __init__(self, client):
        self.client = client

    def notify_set_lineup(self, team_name, lineup_total, transitions, scoring_settings):
        """
        Sends a message to the client detailing that a lineup has been set for the given team name,
        achieving the given projected stats, with the given transitions.

        :param str team_name:
        :param LineupTotal lineup_total:
        :param list transitions:
        :param list scoring_settings:
        :return:
        """
        stats = lineup_total.stats
        plate_appearances = stats.value_for_stat(BaseballStat.PA)
        msg = f"{team_name}: {plate_appearances:.02f}PA\n"

        for setting in scoring_settings:
            if setting.stat.is_hitting_stat():
                val = stats.value_for_stat(setting.stat)
                msg += f"{val:.02f}{setting.stat.name} "

        for tr in sorted(transitions, key=Notifier.transition_sort_value):
            msg += "\n" + self.transition_message(tr)

        self.client.send_message(msg)

    def error_occurred(self):
        """
        Notifies the client of the last exception that occurred during the execution of the script
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        name = exc_type.__name__
        file = exc_traceback.tb_frame.f_code.co_filename
        line = exc_traceback.tb_lineno
        msg = f"error occured: {name} [{file}:{line}] {exc_value}"
        self.client.send_message(msg)

    def notify_new_trade(self, trade):
        """
        Notifies the client of the new trade in the user's league.
        :param Trade trade: the trade to notify the user about
        """
        msg = f"new trade proposed: {trade}"
        self.client.send_message(msg)

    @staticmethod
    def transition_sort_value(transition):
        """
        Gives a value to a transition so that it may be sorted. Benched players come first,
        started players come second, swapped come last.
        :param LineupTransition transition: the transition to be given a sort value
        :return int: a value representing whether the transition should come sooner or later
        """
        if transition.to_slot == BaseballSlot.BENCH:
            return 0
        elif transition.from_slot == BaseballSlot.BENCH:
            return 1
        else:
            return 2

    @staticmethod
    def transition_message(transition):
        """
        Creates the message to send to a user for a LineupTransition
        :param LineupTransition transition: the transition that is happening
        :return str: the appropriate string to send to a user
        """
        last = transition.player.last
        fr = transition.from_slot
        to = transition.to_slot
        return f"{last}: {fr}->{to}"
