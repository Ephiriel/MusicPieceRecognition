#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 15:07:38 2017

@author: andreas
"""

import argparse
import numpy as np

from madmom.audio.signal import SignalProcessor
from madmom.features.notes import (RNNPianoNoteProcessor,
                                   NotePeakPickingProcessor)


class Transcriptor:
    def __init__(self):

        self.p = argparse.ArgumentParser()

        SignalProcessor.add_arguments(self.p, norm=False, gain=1, start=True, stop=True)
        NotePeakPickingProcessor.add_arguments(self.p, threshold=0.35, smooth=0.09,
                                               combine=0.05)

        self.args = self.p.parse_args()
        self.args.fps = 100
        self.args.pre_max = 1. / self.args.fps
        self.args.post_max = 1. / self.args.fps

        self.rnn_processor = RNNPianoNoteProcessor(**vars(self.args))
        self.peak_picker = NotePeakPickingProcessor(**vars(self.args))

    def process_file(self, input):
        """ Transform input to a note and duration list.
        The output is a 2 column table."""
        activations = self.rnn_processor.process(input)
        notes = self.peak_picker(activations)
        if notes.shape[0] < 3:
            raise Exception("Not enough notes in query detected")
        retval = np.zeros(notes.shape)
        retval[:, 0] = notes[:, 1]
        retval[:, 1] = notes[:, 0]

        return retval



