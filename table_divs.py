#!/usr/bin/env python

r"""

Extended tables. Enables setting short captions, float placement and table width factor.

Usage:
 
- Wrap tables in a Div of class `ext` and set attributes like so:
    ```markdown
    ::: {.divtable #tbl:a_table short="This is a short table caption" placement="htbp" width="0.7"}
    ---------------------------------------------------------------------------
    Column 1            Column 2                Column 3
    --------------      -------------------     -------------------
    Row 1               0,1                     0,2

    Row 2               0,3                     0,3

    Row 3               0,4                     0,4      

    Row 4               0,5                     0,6

    ---------------------------------------------------------------------------
    Table: This is the table caption. Suspendisse blandit dolor sed tellus venenatis, venenatis fringilla turpis pretium.
    :::
    ```

"""

from decimal import Decimal
from enum import Enum
from jinja2tex import latex_env
import panflute as pf

# fix for broken citations
from figure_divs import my_stringify

class VerticalAlignment(Enum):
    TOP = r't'
    CENTER = r'c'
    BOTTOM = r'b'

class Alignment(Enum):
    DEFAULT = 'AlignDefault'
    LEFT = 'AlignLeft'
    RIGHT = 'AlignRight'
    CENTER = 'AlignCenter'

class HtmlWriter(object):

    __slots__ = [
        'table',
        'table_width'
    ]

class LatexTableCell(object):

    LATEX_ALIGNMENT = {
        'AlignDefault': r'\raggedright',
        'AlignLeft': r'\raggedright',
        'AlignRight': r'\raggedleft',
        'AlignCenter': r'\centered'
    }

    __slots__ = [
        'content',
        'width',
        'align',
        'valign'
    ]

    def __init__(self, content, width, scale=1.0, align=Alignment.DEFAULT, valign=VerticalAlignment.TOP):
        raw_content = pf.stringify(content)
        self.content = pf.convert_text(raw_content, extra_args=['--biblatex'], input_format='markdown', output_format='latex')
        self.width = scale * width
        self.align = self.LATEX_ALIGNMENT[align]
        self.valign = valign.value

    
class LatexTableRow(object):
    ROW_TMPL = latex_env.from_string(r"""
""")

    __slots__ = [
        'cells'
    ]

    def __init__(self, row, scale, valign, parent):
        self.cells = [LatexTableCell(
            cell,
            parent.width[i],
            scale,
            parent.alignment[i],
            valign
        ) for (i, cell) in enumerate(row.content)]
        
class LatexTable(object):
    TABLE_TMPL = latex_env.from_string(
r"""<% macro make_row(row) -%>
<%- for cell in row.cells -%>
\begin{minipage}[<< cell.valign >>]{<< cell.width >>\columnwidth}<< cell.align >>
<< cell.content >>\strut
\end{minipage}<% if not loop.last %> & <% else %>\tabularnewline<% endif %>
<% endfor -%>
<%- endmacro %>
\begin{longtable}<% if table.placement %>[<< table.placement >>]<% endif %>{@{}<< table.col_descriptor >>@{}}
\caption<% if table.short_caption %>[<< table.short_caption >>]<% endif %>{<< table.caption >>}
<%- if table.identifier %>\label{<< table.identifier >>}<% endif -%>\endlastfoot
\toprule
<< make_row(table.header) ->>
\midrule
\endfirsthead
\toprule
<< make_row(table.header) ->>
\midrule
\endhead
<% for row in table.rows -%>
<< make_row(row) >>
<%- endfor -%>
\bottomrule
\end{longtable}"""
)

    __slots__ = [
        'table',
        'scale',
        'header',
        'caption',
        'identifier',
        'short_caption',
        'placement',
        'col_descriptor',
        'rows'
    ]

    TABULAR_ALIGNMENT = {
        'AlignDefault': r'l',
        'AlignLeft': r'l',
        'AlignRight': r'r',
        'AlignCenter': r'c'
    }

    def __init__(self, table):
        self.table = table
        self.scale = float(table.parent.attributes.get('width', 1))
        self.short_caption = table.parent.attributes.get('short')
        self.placement = table.parent.attributes.get('placement')
        self.col_descriptor = ''.join([self.TABULAR_ALIGNMENT[a] for a in table.alignment])
        
        raw_caption = ''.join([my_stringify(el) for el in table.caption.list])
        self.caption = pf.convert_text(raw_caption, extra_args=['--biblatex', '--filter=tools/panflutist/reference_spans.py'], input_format='markdown', output_format='latex')
        self.identifier = table.parent.identifier

        self.header = LatexTableRow(table.header, self.scale, VerticalAlignment.BOTTOM, table)
        self.rows = [LatexTableRow(row, self.scale, VerticalAlignment.TOP, table) for row in table.content]

    def render(self):
        return self.TABLE_TMPL.render(table=self)

    @staticmethod
    def parse_table(table):
        if isinstance(table.parent, pf.Div) and 'divtable' in table.parent.classes:
            return LatexTable(table)
            

def action(pandoc_table, doc):
    if not isinstance(pandoc_table, pf.Table) or not doc.format == 'latex':
        return pandoc_table
    
    table = LatexTable.parse_table(pandoc_table)
    return pf.RawBlock(table.render(), format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc) 

if __name__ == '__main__':
    main()
