import logging.config

from config import logging_config, notifier_config


class Task:

    @staticmethod
    def create(username):
        """
        Creates a Task, initializing whatever dependencies may be necessary. Each subclass must implement this
        method for itself, and it should be used instead of __init__.
        :param str username: the username of the ESPN user that this Task is being run for
        :return Task: the created Task
        """
        raise NotImplementedError("")

    def run(self):
        """
        This executes the actual behavior of the Task. Is called by the execute method of the parent Task class.

        Should be overridden in every Task implementation.
        """
        raise NotImplementedError("Parent Task class does not implement any specific behavior")

    def execute(self):
        """
        Executes this Task in a controlled manner. Calls the method run(), logging and notifying in the event
        of an error.
        """
        logging.config.dictConfig(logging_config.config_dict())

        logger = logging.getLogger()
        logger.info("starting up %(task)s with user %(user)s", {"user": self.username, "task": type(self).__name__})
        notifier = notifier_config.current_notifier(self.username)

        try:
            self.run()
        except Exception as e:
            logger.exception(e)
            notifier.error_occurred()
            raise e
