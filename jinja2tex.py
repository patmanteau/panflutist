import jinja2, os

# latex_env = jinja2.Environment(
#         block_start_string = r'\BLOCK{',
#         block_end_string = '}',
#         variable_start_string = r'\VAR{',
#         variable_end_string = '}',
#         comment_start_string = r'\#{',
#         comment_end_string = '}',
#         line_statement_prefix = '%%',
#         line_comment_prefix = '%#',
#         trim_blocks = True,
#         autoescape = False,
#         loader = jinja2.FileSystemLoader(os.path.abspath('.'))
#     )

# I prefer a more concise style
latex_env = jinja2.Environment(
    block_start_string = '<%',
    block_end_string = '%>',
    variable_start_string = '<<',
    variable_end_string = '>>',
    comment_start_string = '<#',
    comment_end_string = '#>',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)
