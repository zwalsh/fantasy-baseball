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

        for tr in transitions:
            msg += "\n" + self.transition_message(tr)

        if len(msg) > 140:
            msg = msg[0:137] + "..."

        self.client.send_message(msg)

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
