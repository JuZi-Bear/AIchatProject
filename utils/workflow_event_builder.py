from datetime import datetime


def create_workflow_event(
    event_type,
    event_text,
    agent=None,
    status=None,
    message="",
    detail=None,
):
    """Create a stable workflow event dict for API/UI/platform consumers."""
    return {
        "event_type": str(event_type or ""),
        "event_text": str(event_text or ""),
        "agent": str(agent or ""),
        "status": str(status or ""),
        "message": str(message or ""),
        "detail": detail or {},
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def append_workflow_event(state, event):
    """Append one workflow event without assuming the state already has a list."""
    if state is None:
        state = {}

    workflow_events = state.setdefault("workflow_events", [])

    if not isinstance(workflow_events, list):
        workflow_events = []
        state["workflow_events"] = workflow_events

    workflow_events.append(event)
    return state


def append_workflow_event_from_parts(
    state,
    event_type,
    event_text,
    agent=None,
    status=None,
    message="",
    detail=None,
):
    event = create_workflow_event(
        event_type,
        event_text,
        agent=agent,
        status=status,
        message=message,
        detail=detail,
    )
    return append_workflow_event(state, event)
