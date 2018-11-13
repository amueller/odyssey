def pprint_ipynb(val):
    from odyssey.core.bigquery.BigQueryGithubEntry import BigQueryGithubEntry
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from IPython.display import HTML
    from pygments.formatters import HtmlFormatter
    import IPython

    if isinstance(val, BigQueryGithubEntry):
        val = val.code

    IPython.display.display(HTML('<style type="text/css">{}</style>{}'.format(
        HtmlFormatter().get_style_defs('.highlight'),
        highlight(val, PythonLexer(), HtmlFormatter()))))
