"""
query_builder.py
====================================
The module contains helper functions to build SQL query.
For example, for the where clause, if there are multiple constraints, we can
connect them using connect_with_and / connect_with_or defined in this file.

"""


def connect(connector, *args):
    """Connect the strings in args with connector. Make sure there's no
    additional connector."""
    args = args[0]
    if len(args) == 1 and args[0] == tuple([]):
        return ""
    L = ["(" + val + ")" for val in args if val.strip()
         != ""]  # remove empty values
    if len(L) == 0:
        return ""
    elif len(L) == 1:
        return L[0]
    else:
        return (" %s " % connector).join(L)


def connect_with_and(*args):
    """Connect the strings in args with AND. Make sure there's no additional
    connector."""
    return connect("AND", args)


def connect_with_or(*args):
    """Connect the strings in args with OR. Make sure there's no additional
    connector."""
    return connect("OR", args)
