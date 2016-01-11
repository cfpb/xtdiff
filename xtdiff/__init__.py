# -*- coding: utf-8 -*-
"""
Python xtdiff

This implements "Change detection in hierarchically structured
information", by Sudarshan S. Chawathe, Anand Rajaraman, Hector
Garcia-Molina, and Jennifer Widom.

Chawathe, Sudarshan S., Anand Rajaraman, Hector Garcia-Molina, and
Jennifer Widom. "Change detection in hierarchically structured
information." In ACM SIGMOD Record, vol. 25, no. 2, pp. 493-504. ACM,
1996.
"""

from .diff import diff, transform, simplematch, fastmatch
from .diff import INSERT, UPDATE, MOVE, DELETE, Match
from .xsl import toxsl, xsldiff

__all__ = ['diff', 'transform', 'simplematch', 'fastmatch',
           'INSERT', 'UPDATE', 'MOVE', 'DELETE', 'Match',
           'toxsl', 'xsldiff']
