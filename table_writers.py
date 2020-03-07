#!/usr/bin/env python

r"""

Panflute filter to have captions below longtables for LaTeX. 

"""

from enum import Enum
from string import Template # using .format() is hard because of {} in tex
import panflute as pf

TABLE_WIDTH = 0.9

LATEX_CELL_TMPL = Template(r"""\begin{minipage}[$outer_alignment]{$cell_width\columnwidth}$cell_alignment
$body\strut
\end{minipage}""")

LATEX_TABLE_TMPL = Template(r"""\begin{longtable}[]{@{}$col_descriptor@{}}
\caption{$caption}\endlastfoot
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

def write_cell(cell, width, align='AlignDefault', outer_align=OuterAlignment.TOP):
    tex = LATEX_CELL_TMPL.safe_substitute({
        'outer_alignment': outer_align.value,
        'cell_width': width * TABLE_WIDTH,
        'cell_alignment': CELL_ALIGNMENT[align],
        'body': pf.stringify(cell)
    })
    return tex

def write_row(row, table, outer_align=OuterAlignment.TOP):
    cells = []
    for (i, cell) in enumerate(row.content):
        cell = write_cell(cell, table.width[i], table.alignment[i], outer_align)
        cells.append(cell)

    tex = ' & '.join(cells) + '\\tabularnewline'
    return tex

def write_table(table, doc):
    col_desc = ''.join([TABULAR_ALIGNMENT[a] for a in table.alignment])
    body = ''.join([write_row(row, table) for row in table.content])
    caption = ''.join([pf.stringify(el) for el in table.caption.list])
    header = write_row(table.header, table, outer_align=OuterAlignment.BOTTOM)

    tex = LATEX_TABLE_TMPL.safe_substitute({
        'col_descriptor': col_desc,
        'header': header,
        'body': body,
        'caption': caption
    })
    return tex


def action(table, doc):
    if not isinstance(table, pf.Table) or not doc.format == 'latex':
        return None
    
    return pf.RawBlock(write_table(table, doc), format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc) 

if __name__ == '__main__':
    main()
