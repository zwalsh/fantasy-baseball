import traceback

import sys

from lineup_slot import LineupSlot


class Notifier:
    def __init__(self, client):
        self.client = client

    def notify_set_lineup(self, team_name, plate_appearances, transitions):
        """
        Sends a message to the client detailing that a lineup has been set for the given team name,
        achieving the given projected plate appearances, with the given transitions.

        :param str team_name:
        :param list transitions:
        :param float plate_appearances:
        :return:
        """
        msg = f"{team_name}: proj. {plate_appearances:.02f} PA"

        for tr in sorted(transitions, key=Notifier.transition_sort_value):
            msg += "\n" + self.transition_message(tr)

        if len(msg) > 140:
            msg = msg[0:137] + "..."

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

        if len(msg) > 140:
            msg = msg[:137] + "..."

        self.client.send_message(msg)

    @staticmethod
    def transition_sort_value(transition):
        """
        Gives a value to a transition so that it may be sorted. Benched players come first,
        started players come second, swapped come last.
        :param LineupTransition transition: the transition to be given a sort value
        :return int: a value representing whether the transition should come sooner or later
        """
        if transition.to_slot == LineupSlot.BENCH:
            return 0
        elif transition.from_slot == LineupSlot.BENCH:
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
