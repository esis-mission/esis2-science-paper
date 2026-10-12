import pylatex

__all__ = [
    "preamble",
]


def preamble() -> list[pylatex.base_classes.LatexObject]:
    """
    Custom LaTeX commands used throughout the article.
    """
    return [
        pylatex.NoEscape(r"""
\makeatletter
\newcommand{\acposs}[1]{%
 \expandafter\ifx\csname AC@#1\endcsname\AC@used
   \acs{#1}'s%
 \else
   \aclu{#1}'s (\acs{#1}'s)%
 \fi
}
\newcommand{\Acposs}[1]{%
 \expandafter\ifx\csname AC@#1\endcsname\AC@used
   \acs{#1}'s%
 \else
   \Aclu{#1}'s (\acs{#1}'s)%
 \fi
}
\makeatother"""),
        # The two flights of ESIS. LaTeX command names cannot contain digits,
        # and the box keeps the number on the same line as the name.
        pylatex.NoEscape(r"\newcommand{\ESISone}{\mbox{ESIS-1}}"),
        pylatex.NoEscape(r"\newcommand{\ESIStwo}{\mbox{ESIS-2}}"),
        pylatex.NoEscape(r"\newcommand{\HeII}{He\,\textsc{ii}}"),
        pylatex.NoEscape(r"\newcommand{\NeVII}{Ne\,\textsc{vii}}"),
        pylatex.NoEscape(r"\newcommand{\OV}{O\,\textsc{v}}"),
        pylatex.NoEscape(r"\newcommand{\SiIV}{Si\,\textsc{iv}}"),
        pylatex.NoEscape(r"\newcommand{\SiXII}{Si\,\textsc{xii}}"),
        pylatex.NoEscape(r"\newcommand{\ie}{i.e.}"),
        pylatex.NoEscape(r"\newcommand{\eg}{e.g.}"),
        # A colored comment macro for each author.
        pylatex.NoEscape(r"\newcommand{\jake}[1]{{{\color{purple} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\genevieve}[1]{{{\color{magenta} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\charles}[1]{{{\color{teal} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\amy}[1]{{{\color{red} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\will}[1]{{{\color{olive} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\roy}[1]{{{\color{blue} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\adrian}[1]{{{\color{brown} #1}}}"),
        # The sections which are not written yet are drafted as a list of
        # what each will contain, set apart from the prose so that a reader
        # of the draft can tell the plan from the article.
        pylatex.NoEscape(r"""
\newenvironment{outline}
  {\par\color{gray}\small\noindent\textbf{Outline.}\begin{itemize}}
  {\end{itemize}}"""),
    ]
