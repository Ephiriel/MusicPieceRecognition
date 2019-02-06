from AbstractMatchAlgorithm import AbstractMatchClass
from midilibrary import MidiLibrary
from midifile import MidiFile
import numpy as np
import matplotlib.pyplot as plt
import collections


class FingerPrinting(AbstractMatchClass):
    N_OF_NOTES = "N"
    FINGERPRINT_PER_NOTES = "n_i"
    NOTE_DISTANCE = "d"
    PITCH_DIFF = "pitch_diff"

    USE_VERIFICATION = "use_verification"
    VERIFICATION_TIME_WINDOW = "verification_time_window"

    ELIMINATE_TOP_PERCENTILE = "eliminate_percentile"

    TDR_HASH_TYPE = "hash type"
    TDR_RANGE = "tdr_range"
    TDR_RESOLUTION = "tdr_resolution"
    TDR_WINDOW = "tdr_window"
    TDR_MASK = "tdr_tdr_mask"

    PLOT_COMPARISON = "plot_comparison"

    # Default parameters for Fingerprint Creation
    DEFAULT_N = 4
    DEFAULT_N_I = (3, 2, 2)
    DEFAULT_D = 0.05
    DEFAULT_PITCH_DIFF = 24

    # Default parameter for Verification
    DEFAULT_VERIFICATION_TIME_WINDOW = 0.5

    # Default parameters for FingerPrint-Hash
    DEFAULT_HASH = 3
    DEFAULT_TDR_RANGE = 8.0
    DEFAULT_TDR_RESOLUTION = 256
    DEFAULT_TDR_WINDOW = 0.25
    DEFAULT_TDR_MASK = 0x000000FF
    DEFAULT_USE_VERIFICATION = False
    DEFAULT_PLOT_COMPARISON = False

    PARAM_SETTING_1 = {
        N_OF_NOTES: 3,
        FINGERPRINT_PER_NOTES: (5, 5),
        NOTE_DISTANCE: 0.05,
        PITCH_DIFF: 24,
        VERIFICATION_TIME_WINDOW: 0.5,
        TDR_HASH_TYPE: 1,
        TDR_RESOLUTION: 512,
        TDR_WINDOW: 0.25,
        TDR_MASK: 0x1FF,
        TDR_RANGE: 16.0,
        USE_VERIFICATION: False,
        ELIMINATE_TOP_PERCENTILE: None
    }

    PARAM_SETTING_2 = {
        N_OF_NOTES: 3,
        FINGERPRINT_PER_NOTES: (5, 5),
        NOTE_DISTANCE: 0.05,
        PITCH_DIFF: 24,
        VERIFICATION_TIME_WINDOW: 0.5,
        TDR_HASH_TYPE: 2,
        TDR_RESOLUTION: 512,
        TDR_WINDOW: 0.25,
        TDR_MASK: 0x1FF,
        TDR_RANGE: 16.0,
        USE_VERIFICATION: True,
        ELIMINATE_TOP_PERCENTILE: None
    }

    PARAM_SETTING_3 = {
        N_OF_NOTES: 4,
        FINGERPRINT_PER_NOTES: (3, 2, 2),
        NOTE_DISTANCE: 0.05,
        PITCH_DIFF: 24,
        VERIFICATION_TIME_WINDOW: 0.5,
        TDR_HASH_TYPE: 3,
        TDR_RESOLUTION: 16,
        TDR_WINDOW: 0.25,
        TDR_MASK: 0x1F,
        TDR_RANGE: 8.0,
        USE_VERIFICATION: False,
        ELIMINATE_TOP_PERCENTILE: 99
    }

    class QueryList(list):
        """
        List, that can hold a midifiles as a separate field.
        """
        def __init__(self, midifile, **kwargs):
            super().__init__(kwargs)
            self.midifile = midifile

    class FingerPrintList(list):
        """
        This FingerPrintList calculates automatically the diagonal score
        of the fingerprint-algorithm, when a matched fingerprint-pair is appended
        or removed.
        """
        def __init__(self, midifile, query_fingerprints, **kwargs):
            """
            Initialize function
            :param midifile: The midifile in the database
            :param query_fingerprints: fingerprints of the query
            :param kwargs: for super-class
            """
            super().__init__(kwargs)
            self.midifile = midifile
            self.query_fingerprints = query_fingerprints
            self.histogram = collections.Counter()
            self.max_score = -1

        def append(self, matched_pair):
            """
            Append new matched pair to the list
            :param matched_pair: tuple of 2: first item is the database-fingerprint second item is the query-fingerprint
            :return: None
            """
            super().append(matched_pair)

            mfp, qfp = matched_pair

            # calculate the speed ratio
            r = mfp.td12 / qfp.td12

            # Update the histogram-diagonal score
            hpos = int(round(mfp.pos1 - qfp.pos1 * r))
            self.histogram[hpos] += 1
            new_score = self.histogram[hpos]

            # update the maximum score, if a higher one is reached
            if new_score > self.max_score:
                self.max_score = new_score

        def remove(self, matched_pair):
            super().remove(matched_pair)

            mfp, qfp = matched_pair

            # calculate the speed ratio
            r = mfp.td12 / qfp.td12

            hpos = int(round(mfp.pos1 - qfp.pos1 * r))
            old_score = self.histogram[hpos]

            self.histogram[hpos] -= 1

            # Score needs to be reevaluated
            if old_score == self.max_score:
                self.max_score = -1  # clear max_score, so it has to be recalculated

        def get_score(self):
            """
            Returns the highest diagonal score of the histogram
            :return: Highest score
            """
            if self.max_score == -1:
                highest_score = self.histogram.most_common(1)
                if len(highest_score) > 0:
                    self.max_score = highest_score[0][1]
                    return self.max_score
                else:
                    return -1
            else:
                return self.max_score

    def __init__(self, database: MidiLibrary, **kwargs):
        """
        :param database: The database to perform the algorithm on
        :param kwargs: are holding custom parameters for the algorithm settings
        """
        super().__init__(database)

        np.random.seed(23)

        # Create Fingerprint-Database
        self._fingerprints = dict()

        # Use custom parameters
        self.N = kwargs.get(self.N_OF_NOTES, self.DEFAULT_N)
        self.n = kwargs.get(self.FINGERPRINT_PER_NOTES, self.DEFAULT_N_I)
        self.pitch_diff = kwargs.get(self.PITCH_DIFF, self.DEFAULT_PITCH_DIFF)
        self.d = kwargs.get(self.NOTE_DISTANCE, self.DEFAULT_D)
        self.verification_time_window = kwargs.get(self.VERIFICATION_TIME_WINDOW, self.DEFAULT_VERIFICATION_TIME_WINDOW)
        self.use_verification = kwargs.get(self.USE_VERIFICATION, self.DEFAULT_USE_VERIFICATION)
        self.percentile = kwargs.get(self.ELIMINATE_TOP_PERCENTILE, None)

        # Set settings for the FingerPrint Class
        self.FingerPrint.update_class_variables(kwargs.get(self.TDR_HASH_TYPE, self.DEFAULT_HASH),
                                                kwargs.get(self.TDR_RANGE, self.DEFAULT_TDR_RANGE),
                                                kwargs.get(self.TDR_RESOLUTION, self.DEFAULT_TDR_RESOLUTION),
                                                kwargs.get(self.TDR_WINDOW, self.DEFAULT_TDR_WINDOW),
                                                kwargs.get(self.TDR_MASK, self.DEFAULT_TDR_MASK))

        self.plot_compare_on_missmatch = kwargs.get(self.PLOT_COMPARISON, self.DEFAULT_PLOT_COMPARISON)

        # Create fingerprints for each midifile in the database
        for midifile in database.get_midifiles():
            if isinstance(midifile, MidiFile):
                for fp in self.create_fingerprints(midifile):
                    fplist = self._fingerprints.get(fp.hash, None)
                    # check if hash is already in the list
                    if fplist is None:
                        # create new list
                        self._fingerprints[fp.hash] = [fp]
                    else:
                        # otherwise append fingerprint to existing list
                        fplist.append(fp)

        if self.percentile is not None:
            lens = np.zeros(len(self._fingerprints))
            for idx, key in enumerate(self._fingerprints):
                lens[idx] = len(self._fingerprints[key])
            self.quantile = np.percentile(lens, self.percentile)
        else:
            self.quantile = None

    def create_fingerprints(self, query: MidiFile, remove_doubles=False):
        """
        Creates all fingerprints for a given query: MidiFile. Optionally, fingerprints with the
        same hashvalue are not stored.
        self.N determines the used events per fingerprint.
        self.n[] determines how many fingerprints per note in the midifile will be generated

        :param query: MidiFile from which fingerprints should be created
        :param remove_doubles: only unique fingerprints are generated if True
        :return: QueryList of fingerprints
        """
        prev_hashes = dict()
        fingerprints = self.QueryList(query)
        notes = query.notes[0]

        # First iterate over all notes
        for idx, e1 in enumerate(notes):
            # for each note, generate n1 follow up events
            idx2, evt2 = self._select_next_events(notes, idx, self.n[0])
            if evt2 is not None:
                # iterate all follow up events
                for offset2, e2 in enumerate(evt2):
                    # for each event selected for the second value, select n2 follow up events
                    idx3, evt3 = self._select_next_events(notes, idx2 + offset2, self.n[1])
                    if evt3 is not None:
                        # iterate over all selected events
                        for offset3, e3 in enumerate(evt3):
                            # generate fingerprint, if N=3
                            if self.N == 3:
                                fp = self.FingerPrint(query, e1, e2, e3, None)
                                if not remove_doubles or prev_hashes.get(fp.hash, True):
                                    fingerprints.append(fp)
                                    prev_hashes[fp.hash] = False
                            else:
                                # select next followup events if N=4
                                _, evt4 = self._select_next_events(notes, idx3 + offset3, self.n[2])
                                if evt4 is not None:
                                    for e4 in evt4:
                                        # generate fingerprint
                                        fp = self.FingerPrint(query, e1, e2, e3, e4)
                                        if not remove_doubles or prev_hashes.get(fp.hash, True):
                                            fingerprints.append(fp)
                                            prev_hashes[fp.hash] = False

        return fingerprints

    def _select_next_events(self, query, start_idx, n_events):
        """
        Select from the given query n_events, starting from start_idx+1.
        The selected events have to be self.d later positionwise then the
        start_idx position, and the first pitch-value has to be smaller then
        self.pitch_diff
        :param query: The midi eventlist
        :param start_idx: index where to start the selection
        :param n_events: number of events to select
        :return: the index of the first picked event and the list of all selected events
        """

        p, _, pos, _ = query[start_idx]
        try:
            idx = start_idx + 1

            p_next, _, pos_next, _ = query[idx]

            # iterate until position self.d and pitch_diff self.pitch_diff requirements are met
            while (abs(pos_next - pos) < self.d) or (abs(p_next - p) > self.pitch_diff):
                idx += 1
                p_next, _, pos_next, _ = query[idx]
        except IndexError:
            return -1, None

        return idx, query[idx:idx + n_events]

    def get_algorithm_name(self):
        return "FingerPrinting"

    def search(self, query: MidiFile, evaluate=True):
        dict_result = dict()

        q_fingerprints, matches, should_match = self.perform_query(query)

        # sort descending by max score
        results = sorted(matches, key=lambda itm: itm.get_score(), reverse=True)

        # make token verification on top 5%
        if self.use_verification:
            results = self._verify_results(results)

        for i, match in enumerate(results, 1):
            dict_result[match.midifile.name] = (0, i, 0)

        if self.plot_compare_on_missmatch and results[0].midifile.name != query.name:
            self._compare_plot(results[0], should_match)

        return dict_result

    def _verify_results(self, results):
        """
        Perform the verification step on the top 5 percont of the results list.
        Compare for earch fingerprint-match 10 notes if they are equal, if less 50%
        of the notes are equal, remove the fingerprint from the matched list
        :param results: result list
        :return: an updated result list
        """

        verified_results = []

        for cnt, matches in enumerate(results):
            if cnt > len(results) * 0.05:  # only check top 5 percent of results
                break

            verified_results.append(matches)

            # if isinstance(matches, self.FingerPrintList):
            for dbfp, qfp in matches:

                # in order to determine the correct position of a matching pitch value in
                # query and database file, calculate the pitch difference of the first matched
                # fingerprint-event and the ratio of the time difference of the first 2 events
                pitch_diff = qfp.p1 - dbfp.p1
                t_ratio = qfp.td12 / dbfp.td12
                t_diff = qfp.pos1 - dbfp.pos1 * t_ratio

                # start_idx is either 0 (start of the file, or the fingerprint-start - 5
                q_idx = max(0, qfp.idx1 - 5)
                db_idx = max(0, dbfp.idx1 - 5)

                compared_events = 0
                matched_events = 0

                query_notes = matches.query_fingerprints.midifile.notes[0]
                db_notes = matches.midifile.notes[0]

                # max matches are 10 or the length of the query - 3 fingerprint-tokens
                max_possible_matches = min(10, len(query_notes) - q_idx - 3, len(db_notes) - db_idx - 3)

                while compared_events < max_possible_matches:
                    # skip fingerprint-events
                    if not (db_idx == dbfp.idx1 or db_idx == dbfp.idx2 or db_idx == dbfp.idx3):
                        compared_events += 1

                        q_pitch, _, q_pos, _ = query_notes[q_idx]
                        db_pitch, _, db_pos, _ = db_notes[db_idx]
                        # check if pitch-values match
                        if q_pitch == db_pitch + pitch_diff:
                            equ_db_pos = db_pos * t_ratio
                            if (equ_db_pos + t_diff) - self.verification_time_window <= \
                                    q_pos \
                                    <= (equ_db_pos + t_diff) + self.verification_time_window:
                                matched_events += 1

                    q_idx += 1
                    db_idx += 1

                # < 80% of the events are matched
                if matched_events / max_possible_matches < 0.5:
                    matches.remove((dbfp, qfp))  # remove fingerprint from match

        verified_results.sort(key=lambda itm: itm.get_score(), reverse=True)
        return verified_results

    @staticmethod
    def _plot_query(matched_pairs: FingerPrintList):
        """
        Plots the matched pairs of fingerprints
        :param matched_pairs:
        :return:
        """
        x_pos = []
        y_pos = []

        for mfp, qfp in matched_pairs:
            x_pos.append(mfp.pos1)
            y_pos.append(qfp.pos1)

        f, arg = plt.subplots(2)
        arg[0].scatter(x_pos, y_pos, marker="x")
        arg[0].set_xlabel(matched_pairs.midifile.name)
        arg[0].set_ylabel(matched_pairs.query_fingerprints.midifile.name)

        x, y = zip(*sorted(matched_pairs.histogram.items()))
        arg[1].bar(x, y, width=1, align='center')
        arg[1].set_xlabel("seconds [s]")
        arg[1].set_ylabel("Matches")
        plt.show()

    @staticmethod
    def _compare_plot(matched_pairs_1: FingerPrintList, matched_pairs_2: FingerPrintList):
        """
        Plot a comparison of 2 fingerprintlists-pairs
        :param matched_pairs_1:
        :param matched_pairs_2:
        :return:
        """
        x_pos1 = []
        y_pos1 = []

        for mfp, qfp in matched_pairs_1:
            x_pos1.append(mfp.pos1)
            y_pos1.append(qfp.pos1)

        f, arg = plt.subplots(2, 2)
        arg[0, 0].scatter(x_pos1, y_pos1, marker="x")
        arg[0, 0].set_xlabel(matched_pairs_1.midifile.name)
        arg[0, 0].set_ylabel(matched_pairs_1.query_fingerprints.midifile.name)

        x, y = zip(*sorted(matched_pairs_1.histogram.items()))
        arg[1, 0].bar(x, y, width=1, align='center')
        arg[1, 0].set_xlabel("seconds [s]")
        arg[1, 0].set_ylabel("Matches")

        x_pos2 = []
        y_pos2 = []

        for mfp, qfp in matched_pairs_2:
            x_pos2.append(mfp.pos1)
            y_pos2.append(qfp.pos1)

        arg[0, 1].scatter(x_pos2, y_pos2, marker="x")
        arg[0, 1].set_xlabel(matched_pairs_2.midifile.name)
        arg[0, 1].set_ylabel(matched_pairs_2.query_fingerprints.midifile.name)

        x, y = zip(*sorted(matched_pairs_2.histogram.items()))
        arg[1, 1].bar(x, y, width=1, align='center')
        arg[1, 1].set_xlabel("seconds [s]")
        arg[1, 1].set_ylabel("Matches")
        plt.show()

    def get_hash_value_lengths(self):
        """
        Returns a numpy array that contains the amount of hash collisions for every hash stored.
        :return: np.array
        """
        lens = np.zeros(len(self._fingerprints))
        for idx, key in enumerate(self._fingerprints):
            lens[idx] = len(self._fingerprints[key])
        return lens

    def perform_query(self, query: MidiFile):
        """
        Search for the query by creating fingerprints of it
        and then, for each fingerprint ask for a dictionary entry.
        :param query:
        :return: the created fingerprints, a list of matched fingerprints and the "true" match for analysis
        """
        query_fingerprints = self.create_fingerprints(query, remove_doubles=True)
        matched_queries = dict()
        for fp in query_fingerprints:
            for hash_val in fp.get_hash_iterator():
                matched_fingerprint_list = self._fingerprints.get(hash_val, None)
                if matched_fingerprint_list is not None:
                    if self.quantile is None or len(matched_fingerprint_list) < self.quantile:
                        for mfp in matched_fingerprint_list:  # query all files with this fingerprint
                            matches = matched_queries.get(mfp.midifile.name, None)
                            # create a new fingerprintlist, if there is a fingerprint from a new file
                            if matches is None:
                                matches = self.FingerPrintList(mfp.midifile, query_fingerprints)
                                matched_queries[mfp.midifile.name] = matches

                            matches.append((mfp, fp))
                    break

        return query_fingerprints, list(matched_queries.values()), matched_queries[query.name]

    class FingerPrint(object):
        """
        Fingerprint-Class
        """
        TDR_HASH_1 = 1
        TDR_HASH_2 = 2
        TDR_HASH_3 = 3

        PARAM_INIT = False

        TDR_RANGE = 0
        TDR_RESOLUTION = 0
        TDR_WINDOW = 0
        TDR_DELTA_VALUE = 0
        TDR_MASK = 0
        TDR_HASH_TYPE = 0

        TDR_K = 0
        TDR_D = 0

        __slots__ = ("midifile", "name", "p1", "pos1", "idx1", "idx2", "idx3", "td12", "hash")

        def __init__(self, midifile, e1, e2, e3, e4):
            if not self.PARAM_INIT:
                raise Exception("Call Fingerprint.update_class_variables() first")

            object.__setattr__(self, "midifile", midifile)
            object.__setattr__(self, "name", midifile.name)
            object.__setattr__(self, "p1", e1[0])
            object.__setattr__(self, "pos1", e1[2])
            object.__setattr__(self, "idx1", e1[3])
            object.__setattr__(self, "idx2", e2[3])
            object.__setattr__(self, "idx3", e3[3])
            object.__setattr__(self, "td12", e2[2] - e1[2])

            td23 = e3[2] - e2[2]

            if td23 > self.td12:
                tdr = abs(td23 / self.td12)
            else:
                tdr = abs(self.td12 / td23)

            # use kx+d formula to fit (MAX_TDR_VALUES-MIN_TDR_VALUE) between MIN_TDR_FLOAT and MAX_TDR_FLOAT
            tdr = tdr * __class__.TDR_K + self.TDR_D

            if td23 > self.td12:
                tdr = self.TDR_RESOLUTION / 2 + tdr
            else:
                tdr = self.TDR_RESOLUTION / 2 - tdr

            tdr = int(max(min(tdr, self.TDR_RESOLUTION - 1), 0))

            h = None

            # create hash value according to self.TDR_HASH_TYPE
            if self.TDR_HASH_TYPE == self.TDR_HASH_1:
                h = int(((int(self.p1) & 0x7F) << 25) | ((int(e2[0]) & 0x7F) << 18) |
                                ((int(e3[0]) & 0x7F) << 11) | (tdr & self.TDR_MASK))
            elif self.TDR_HASH_TYPE == self.TDR_HASH_2:
                h = int(((int(e2[0] - self.p1) & 0xFF) << 24) | ((int(e3[0] - e2[0]) & 0xFF) << 16) |
                                (tdr & self.TDR_MASK))
            elif self.TDR_HASH_TYPE == self.TDR_HASH_3:
                h = int(((int(e2[0] - self.p1) & 0xFF) << 24) | ((int(e3[0] - e2[0]) & 0xFF) << 16) |
                                ((int(e4[0] - e3[0]) & 0xFF) << 8) | (tdr & self.TDR_MASK))

            object.__setattr__(self, "hash", h)

        def __setattr__(self, *args):
            raise AttributeError("Attributes of Immutable3 cannot be changed")

        def __delattr__(self, *args):
            raise AttributeError("Attributes of Immutable3 cannot be deleted")

        @staticmethod
        def update_class_variables(TDR_HASH_TYPE, TDR_RANGE, TDR_RESOLUTION, TDR_WINDOW, TDR_MASK):
            __class__.TDR_RANGE = TDR_RANGE
            __class__.TDR_RESOLUTION = TDR_RESOLUTION
            __class__.TDR_WINDOW = TDR_WINDOW
            __class__.TDR_DELTA_VALUE = int(TDR_RESOLUTION * TDR_WINDOW)
            __class__.TDR_MASK = TDR_MASK
            __class__.TDR_HASH_TYPE = TDR_HASH_TYPE

            __class__.TDR_K = (TDR_RESOLUTION / 2) / (TDR_RANGE - 1)
            __class__.TDR_D = - __class__.TDR_K

            __class__.PARAM_INIT = True

        def get_hash_iterator(self):
            """
            Returns a list of hashes where the tdr-range is adopted for each hash.
            :return: list of hashes
            """
            tdr = self.hash & self.TDR_MASK
            min_tdr = max(0, tdr - self.TDR_DELTA_VALUE)
            max_tdr = min(self.TDR_RESOLUTION - 1, tdr + self.TDR_DELTA_VALUE)

            part_hash = int(self.hash & (0xFFFFFFFF ^ self.TDR_MASK))
            hash_list = [self.hash]

            # add hashes in order, where they are closest to the original hash
            # so smaller differences are found faster
            # this assumes, that smaller tempo errors are more frequent than larger ones
            for tdr_offset in range(1, self.TDR_DELTA_VALUE + 1):
                if max_tdr >= tdr_offset + tdr:
                    hash_list.append(int(part_hash | int(tdr + tdr_offset)))
                if min_tdr <= tdr - tdr_offset:
                    hash_list.append(int(part_hash | int(tdr - tdr_offset)))

            return hash_list

        def __repr__(self):
            return self.name + "_" + str(self.pos1)

        def __str__(self):
            return self.name + "_" + str(self.pos1)

        def __hash__(self):
            return self.hash

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.hash == other.hash
            else:
                return False

        def __ne__(self, other):
            return not self.__eq__(other)

        def __lt__(self, other):
            if isinstance(other, self.__class__):
                return (self.pos1 - other.pos1) < 0
            else:
                return False

        def __le__(self, other):
            if isinstance(other, self.__class__):
                return (self.pos1 - other.pos1) <= 0
            else:
                return False

        def __gt__(self, other):
            if isinstance(other, self.__class__):
                return (self.pos1 - other.pos1) > 0
            else:
                return False

        def __ge__(self, other):
            if isinstance(other, self.__class__):
                return (self.pos1 - other.pos1) >= 0
            else:
                return False
