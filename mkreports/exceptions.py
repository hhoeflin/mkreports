"""
All Exception classes that we are using in the package.
"""


class ReportExistsError(Exception):
    pass


class ReportNotExistsError(Exception):
    pass


class ReportNotValidError(Exception):
    pass


class PageNotExistsError(Exception):
    pass


class TrackerIncompleteError(Exception):
    pass


class TrackerEmptyError(Exception):
    pass


class TrackerActiveError(Exception):
    pass


class TrackerNotActiveError(Exception):
    pass


class CannotTrackError(Exception):
    pass


class IncorrectSuffixError(Exception):
    pass


class ContextActiveError(Exception):
    pass
