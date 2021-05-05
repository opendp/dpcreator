"""

"""

def get_websocket_id(request):
    """Create a websocket_id based on the logged in user"""
    if not request.user.is_authenticated:
        return None

    return f'ws_{request.user.object_id}'