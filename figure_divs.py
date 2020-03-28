#!/usr/bin/env python
r"""

Extended figures for LaTeX. Enables setting short captions, float placement and width factor.

Usage:
 
- Extended attributes are set like standard attributes:
    ```markdown
    ![Erträge von Food-Trucks [vgl. @Perez_PythonEcosystem_2011, 13]](../assets/ex1_food_truck_profit.pdf){.ext #ref_a_figure short="This is a short figure caption" placement="htbp" width="0.7"}
    ```

"""

from enum import Enum
from jinja2tex import latex_env
import panflute as pf

LATEX_INCLUDEGRAPHICS = USE_TERM = latex_env.from_string(
    r"""\begin{figure}<% if placement %>[<< placement >>]<% endif %>
<% if identifier %>\hypertarget{<< identifier >>}{%<% endif %>
\centering
\includegraphics<% if width %>[width=<< width >>\textwidth]<% endif %>{<< path >>}
\caption<% if short_caption %>[<< short_caption >>]<% endif %>{<< caption >>}<% if identifier %>\label{<< identifier >>}<% endif %>
<% if identifier %>}<% endif %>
\end{figure}""")

LATEX_INPUT = USE_TERM = latex_env.from_string(
    r"""\begin{figure}<% if placement %>[<< placement >>]<% endif %>
<% if identifier %>\hypertarget{<< identifier >>}{%<% endif %>
\centering
\input{<< path >>}
\caption<% if short_caption %>[<< short_caption >>]<% endif %>{<< caption >>}<% if identifier %>\label{<< identifier >>}<% endif %>
<% if identifier %>}<% endif %>
\end{figure}""")


class LaTeXImage(object):

    __slots__ = ['image', 'id']

    def __init__(self, image):
        self.image = image

    def render(self):
        short_caption = self.image.attributes.get('short')
        if short_caption:
            short_caption = pf.convert_text(short_caption,
                                            extra_args=['--biblatex'],
                                            input_format='markdown',
                                            output_format='latex')

        placement = self.image.attributes.get('placement', '')
        identifier = self.image.identifier
        width = self.image.attributes.get('width')
        if width:
            width = width.replace('%', '')
            width = '{0:.2f}'.format(float(width) / 100)

        path = self.image.url

        converted_caption = pf.convert_text(pf.Plain(*self.image.content),
                                            extra_args=['--biblatex'],
                                            input_format='panflute',
                                            output_format='latex')

        values = {
            'placement': placement,
            'width': width,
            'path': path,
            'short_caption': short_caption,
            'caption': converted_caption,
            'identifier': identifier
        }
        # don't use includegraphics on PGF files
        if self.image.url.endswith('.pgf'):
            tex = LATEX_INPUT.render(values)
        else:
            tex = LATEX_INCLUDEGRAPHICS.render(values)
        return tex


def action(pandoc_image, doc):
    if not isinstance(pandoc_image, pf.Image) or not doc.format == 'latex':
        return None

    image = LaTeXImage(pandoc_image)
    return pf.RawInline(image.render(), format='latex')


def main(doc=None):
    return pf.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
