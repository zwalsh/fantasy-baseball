import logging

from pushed import Pushed

LOGGER = logging.getLogger("notifications.client.pushed")


class PushedClient:
    def __init__(self, user, pushed_id, app_key, app_secret):
        """
        Represents a PushedClient that can be used to push message to a Pushed app client
        :param str pushed_id: the pushed id of the client that this will push to
        """
        self.user = user
        self.pushed_id = pushed_id
        self.pushed = Pushed(app_key, app_secret)

    def send_message(self, content, content_url=None):
        """
        Sends a push notification to the client with the given message content. If a URL is given,
        opening that push will direct the user to the given URL.
        :param str content: the message text
        :param str content_url: Optional - the URL that the user will be redirected to if they open the notification
        """
        LOGGER.info(
            "sending message: %(content)s to user: %(user)s",
            {"content": content, "user": self.user},
        )
        if len(content) > 140:
            content = content[:137] + "..."
        self.pushed.push_pushed_id(content, self.pushed_id, content_url)
