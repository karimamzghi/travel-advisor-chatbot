from app.conversation import ConversationState


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}

    def get_or_create(
        self,
        session_id: str,
    ) -> ConversationState:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationState()

        return self._sessions[session_id]

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None


session_store = InMemorySessionStore()
