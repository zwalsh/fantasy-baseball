import logging

LOGGER = logging.getLogger("notifications.client.dev")


class DevClient:

    def send_message(self, content, content_url=None):
        """
        Mimics a normal Notifications client, logging the message instead of sending it to Pushed.
        :param str content: the content of the notification
        :param str content_url: the URL attached to the notification
        """
        LOGGER.info("notified: %(content)s, url: %(url)s", {"content": content, "url": content_url})
