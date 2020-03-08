#!/usr/bin/env python

r"""

Extended figures for LaTeX. Enables setting short captions, float placement and width factor.

Usage:
 
- Extended attributes are set like standard attributes:
    ```markdown
    ![Erträge von Food-Trucks [vgl. @Perez_PythonEcosystem_2011, 13]](../assets/ex1_food_truck_profit.pdf){.ext #ref_a_figure short="This is a short figure caption" placement="htbp" width="0.7"}
    ```

"""


"""
Image

:param args: text with the image description
:type args: :class:`Inline`
:param url: URL or path of the image
:type url: ``str``
:param title: Alt. title
:type title: ``str``
:param identifier: element identifier (usually unique)
:type identifier: :class:`str`
:param classes: class names of the element
:type classes: :class:`list` of :class:`str`
:param attributes: additional attributes
:type attributes: :class:`dict`
:Base: :class:`Inline`
"""

from enum import Enum
from string import Template # using .format() is hard because of {} in tex
import panflute as pf

LATEX_CELL_TMPL = Template(r"""\begin{minipage}[$outer_alignment]{$cell_width\columnwidth}$cell_alignment
$body\strut
\end{minipage}""")

"""
\begin{figure}
\hypertarget{ref_a_figure}{%
\centering
\includegraphics[width=1\textwidth,height=\textheight]{../assets/ex1_food_truck_profit.pdf}
\caption{Erträge von Food-Trucks in Abhängigkeit von der Stadtgröße
\autocite[vgl.][13]{Perez_PythonEcosystem_2011}}\label{ref_a_figure}
}
\end{figure}"""

LATEX_INCLUDEGRAPHICS_TMPL = Template(r"""\begin{figure}[$placement]
$hypertarget_open
\centering
\includegraphics$width{$path}
\caption$short_caption{$caption}$label
$hypertarget_close
\end{figure}""")

LATEX_INPUT_TMPL = Template(r"""\begin{figure}[$placement]
$hypertarget_open
\centering
\input{$path}
\caption$short_caption{$caption}$label
$hypertarget_close
\end{figure}""")

class LaTeXWriter(object):

    __slots__ = [
        'image',
        'id'
    ]

    def __init__(self, image):
        self.image = image

    def write_image(self):
        short_caption = self.image.attributes.get('short')
        short_caption = '[{}]'.format(short_caption) if short_caption else ''
            
        placement = self.image.attributes.get('placement', '')
        width_percent = self.image.attributes.get('width')
        identifier = self.image.identifier
        if width_percent:
            width_percent = width_percent.replace('%', '')
            width = '{0:.2f}'.format(float(width_percent) / 100)
            width = Template(r'[width=$width\textwidth]').safe_substitute(width=width)

        hypertarget_open = Template(r'\hypertarget{$id}{%').safe_substitute(id=identifier) if identifier else ''
        hypertarget_close = '}' if identifier else ''
        label = Template(r'\label{$id}').safe_substitute(id=identifier) if identifier else ''

        path = self.image.url
        
        # write citations ourself, something is awry between panflute and me
        def _write_element(el):
            return pf.stringify(el)

        def _write_cite(cite):
            return pf.stringify(pf.Plain(*cite.content))

        def my_stringify(el):
            if isinstance(el, pf.Cite):
                return _write_cite(el)
            else:
                return _write_element(el)

        caption = ''.join([my_stringify(el) for el in self.image.content])
        converted_caption = pf.convert_text(caption, extra_args=['--biblatex'], input_format='markdown', output_format='latex')
        
        values = {
            'placement': placement,
            'hypertarget_open': hypertarget_open,
            'width': width,
            'path': path,
            'hypertarget_close': hypertarget_close,
            'short_caption': short_caption,
            'caption': converted_caption,
            'label': label
        }
        # don't use includegraphics on PGF files
        if self.image.url.endswith('.pgf'):
            tex = LATEX_INPUT_TMPL.safe_substitute(values)            
        else:
            tex = LATEX_INCLUDEGRAPHICS_TMPL.safe_substitute(values)
        return tex


def action(image, doc):
    if not isinstance(image, pf.Image) or not doc.format == 'latex':
        return None
    
    writer = LaTeXWriter(image)
    return pf.RawInline(writer.write_image(), format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc) 

if __name__ == '__main__':
    main()
