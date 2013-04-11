#!/usr/bin/env python
# -*- coding: utf-8 -*-  
#feedback: tomasz.czerwinski@nsn.com

import os
import sys
import re
import time
from operator import itemgetter

class Lexer:
    """Lexical analisis base class"""

    def __init__(self, log='', patterns=None, verbose=False):

        self.patterns = patterns 
        self.verbose = verbose
        self.log = log

    def mems(self):

        markers = {}
        index = 0

        self.stream = self.log.upper().split()
  
        for word in reversed(self.stream):
            index += 1 
            for key in self.patterns.keys():
                if re.compile(self.patterns[key]).match(word):
                    markers[key] = index
                    break 

        self.mems = sorted(markers.items(),key=itemgetter(1))

    def parse(self):

        self.mems()

        index = 0 
        container =  {}
        tmp = []
        logReversed = self.log.split()
        logReversed.reverse() 
 
        for mem in self.mems:
            for i in range(index, mem[1]):
               tmp.append(logReversed[i])

            index = mem[1]
            tmp.reverse()
            container[mem[0]] = tmp
            tmp = []

        if self.verbose:
            print container

        return container
