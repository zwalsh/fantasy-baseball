from pathlib import Path


class EspnSessionStore:

    def __init__(self):
        """
        Provides an interface for file-system storage of session cookies
        """
        self.sessions_dir = Path("espn/sessions")
        if not self.sessions_dir.exists() or not self.sessions_dir.is_dir():
            self.sessions_dir.mkdir()

    def store_session(self, key, session):
        session_path = self.sessions_dir / key
        session_file = session_path.open("w+")
        session_file.truncate()
        session_file.write(session)
        session_file.close()

    def retrieve_session(self, key):
        session_path = self.sessions_dir / key
        if session_path.is_file():
            stored_session = session_path.read_text()
            if len(stored_session) > 0:
                return stored_session
        return None
