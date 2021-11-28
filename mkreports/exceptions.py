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
