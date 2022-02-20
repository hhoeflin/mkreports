"""
All Exception classes that we are using in the package.
"""


class ReportExistsError(Exception):
    """Report already exists."""

    pass


class ReportNotExistsError(Exception):
    """The given path for a report does not exist."""

    pass


class ReportNotValidError(Exception):
    """The given path does not represent a valid report."""

    pass


class PageNotExistsError(Exception):
    """The page does not exist."""

    pass


class TrackerIncompleteError(Exception):
    """The tracker has not yet completed."""

    pass


class TrackerEmptyError(Exception):
    """The tracker is empty."""

    pass


class TrackerActiveError(Exception):
    """The tracker is active and it should not be."""

    pass


class TrackerNotActiveError(Exception):
    """The tracker is not active and it should be active."""

    pass


class CannotTrackError(Exception):
    """Tracking is not possible."""

    pass


class IncorrectSuffixError(Exception):
    """An incorrect suffix was given."""

    pass


class ContextActiveError(Exception):
    """The code-context is active and it should not be."""

    pass
