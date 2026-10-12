"""
The sections of this article, each a factory function returning an
:class:`aastex.Section`.
"""

from ._s0_abstract import abstract
from ._s1_introduction import introduction
from ._s2_motivation import motivation
from ._s3_instrument import instrument
from ._s4_inversions import inversions
from ._s5_conclusions import conclusions

__all__ = [
    "abstract",
    "conclusions",
    "instrument",
    "introduction",
    "inversions",
    "motivation",
]
