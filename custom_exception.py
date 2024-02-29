class SpotifyGestureError(Exception):
    """generic custom expression for any Gesture control spotify control error"""
class SessionDataNotFound(SpotifyGestureError):
    """Raises exception for session data not found"""

class TokenInfoNotFound(SpotifyGestureError):
    """Token information not found"""