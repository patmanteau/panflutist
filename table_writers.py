#!/usr/bin/env python

r"""

Extended tables. Enables setting short captions, float placement and table width factor.

Usage:
 
- Wrap tables in a Div of class `ext` and set attributes like so:
    ```markdown
    ::: {.ext short="This is a short table caption" placement="htbp" width="0.7"}
    ---------------------------------------------------------------------------
    Column 1            Column 2                Column 3
    --------------      -------------------     -------------------
    Row 1               0,1                     0,2

    Row 2               0,3                     0,3

    Row 3               0,4                     0,4      

    Row 4               0,5                     0,6

    ---------------------------------------------------------------------------
    Table: This is the table caption. Suspendisse blandit dolor sed tellus venenatis, venenatis fringilla turpis pretium. \label{ref_a_table}
    :::
    ```

"""

from enum import Enum
from string import Template # using .format() is hard because of {} in tex
import panflute as pf

LATEX_CELL_TMPL = Template(r"""\begin{minipage}[$outer_alignment]{$cell_width\columnwidth}$cell_alignment
$body\strut
\end{minipage}""")

LATEX_TABLE_TMPL = Template(r"""\begin{longtable}[$placement]{@{}$col_descriptor@{}}
\caption$short_caption{$caption}\endlastfoot
\toprule
$header
\midrule
\endfirsthead
\toprule
$header
\midrule
\endhead
$body
\bottomrule
\end{longtable}""")

class OuterAlignment(Enum):
    TOP = r't'
    CENTER = r'c'
    BOTTOM = r'b'


class HtmlWriter(object):

    __slots__ = [
        'table',
        'table_width'
    ]

class LatexWriter(object):

    __slots__ = [
        'table',
        'table_width'
    ]

    TABULAR_ALIGNMENT = {
        'AlignDefault': r'l',
        'AlignLeft': r'l',
        'AlignRight': r'r',
        'AlignCenter': r'c'
    }

    CELL_ALIGNMENT = {
        'AlignDefault': r'\raggedright',
        'AlignLeft': r'\raggedright',
        'AlignRight': r'\raggedleft',
        'AlignCenter': r'\centered'
    }

    def __init__(self, table, table_width=0.9):
        self.table = table
        self.table_width = table_width

    def write_cell(self, cell, width, align='AlignDefault', outer_align=OuterAlignment.TOP):
        tex = LATEX_CELL_TMPL.safe_substitute({
            'outer_alignment': outer_align.value,
            'cell_width': width * self.table_width,
            'cell_alignment': self.CELL_ALIGNMENT[align],
            'body': pf.stringify(cell)
        })
        return tex

    def write_row(self, row, outer_align=OuterAlignment.TOP):
        cells = []
        for (i, cell) in enumerate(row.content):
            cell = self.write_cell(cell, self.table.width[i], self.table.alignment[i], outer_align)
            cells.append(cell)

        tex = ' & '.join(cells) + '\\tabularnewline'
        return tex

    def write_table(self):
        # Process extended table attributes first so cell width gets calculated correctly
        short_caption = ''
        placement = ''
        if isinstance(self.table.parent, pf.Div) and 'ext' in self.table.parent.classes:
            short_caption = self.table.parent.attributes.get('short')
            short_caption = '[{}]'.format(short_caption) if short_caption else ''
            placement = self.table.parent.attributes.get('placement', '')
            width = self.table.parent.attributes.get('width')
            if width:
                self.table_width = float(width)

        col_desc = ''.join([self.TABULAR_ALIGNMENT[a] for a in self.table.alignment])
        body = ''.join([self.write_row(row) for row in self.table.content])
        caption = ''.join([pf.stringify(el) for el in self.table.caption.list])
        header = self.write_row(self.table.header, outer_align=OuterAlignment.BOTTOM)
        
        tex = LATEX_TABLE_TMPL.safe_substitute({
            'placement': placement,
            'short_caption': short_caption,
            'col_descriptor': col_desc,
            'header': header,
            'body': body,
            'caption': caption
        })
        return tex


def action(table, doc):
    if not isinstance(table, pf.Table) or not doc.format == 'latex':
        return table
    
    writer = LatexWriter(table, 0.9)
    return pf.RawBlock(writer.write_table(), format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc) 

if __name__ == '__main__':
    main()
