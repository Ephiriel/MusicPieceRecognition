from typing import Any, Tuple

from search_algorithms.abstract_match_algorithm import AbstractMatchClass
from library.midilibrary import MidiLibrary
from library.midifile import MidiFile
import numpy as np
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

    SPLIT_QUERIES_LONGER_THAN = "long_query_split"
    SPLIT_QUERY_LENGTH = "split_query_length"
    SPLIT_QUERIES_SLIDING_WINDOW = "query_split_sliding_window"

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
    DEFAULT_TDR_RESOLUTION = 16
    DEFAULT_TDR_WINDOW = 0.25
    DEFAULT_TDR_MASK = 0x0000001F
    DEFAULT_SPLIT_QUERIES_LONGER_THAN = 20
    DEFAULT_SPLIT_QUERY_LENGTH = 20
    DEFAULT_SPLIT_QUERIES_SLIDING_WINDOW = 5

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
        ELIMINATE_TOP_PERCENTILE: None,
        SPLIT_QUERIES_LONGER_THAN: 25,
        SPLIT_QUERIES_SLIDING_WINDOW: 5,
        SPLIT_QUERY_LENGTH: 25
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
        ELIMINATE_TOP_PERCENTILE: None,
        SPLIT_QUERIES_LONGER_THAN: 20,
        SPLIT_QUERIES_SLIDING_WINDOW: 5,
        SPLIT_QUERY_LENGTH: 20
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
        ELIMINATE_TOP_PERCENTILE: 99,
        SPLIT_QUERIES_LONGER_THAN: 20,
        SPLIT_QUERIES_SLIDING_WINDOW: 5,
        SPLIT_QUERY_LENGTH: 20
    }

    class FingerPrintList(list):
        """
        This FingerPrintList calculates automatically the diagonal score
        of the fingerprint-algorithm, when a matched fingerprint-pair is appended
        or removed.
        """
        max_score: Tuple[Any, Any]

        class BinFingerPrintList(list):
            """ Stores all fingerprints for a bin, and stores the lowest start position and highest end position"""
            def __init__(self):
                super().__init__()
                self.end = None
                self.start = None

            def append(self, obj):
                super().append(obj)
                if self.end is None or self.end.max_pos < obj.max_pos:
                    self.end = obj
                if self.start is None or self.start.pos1 > obj.pos1:
                    self.start = obj

        def __init__(self, db_name, query_fingerprints, query_notes, query_name, **kwargs):
            """
            Initialize function
            :param midifile: The midifile in the database
            :param query_fingerprints: fingerprints of the query
            :param kwargs: for super-class
            """
            super().__init__(kwargs)
            self.db_name = db_name
            self.query_fingerprints = query_fingerprints
            self.query_name = query_name
            self.query_notes = query_notes
            self.histogram = collections.Counter()
            self.fps_in_bins = dict()
            self.query_fps_in_bins = dict()
            self.max_score = None

        def append(self, matched_pair):
            """
            Append new matched pair to the list
            :param matched_pair: tuple of 2: first item is the database-fingerprint second item is the query-fingerprint
            :return: None
            """

            super().append(matched_pair)

            mfp, qfp = matched_pair

            # calculate the speed ratio
            r = float(mfp.td12) / float(qfp.td12)

            # Update the histogram-diagonal score
            hpos = int(round(mfp.pos1 - qfp.pos1 * r))
            self.histogram[hpos] += 1
            bin_x = self.fps_in_bins.get(hpos, None)
            if bin_x is None:
                bin_x = self.BinFingerPrintList()
                self.fps_in_bins[hpos] = bin_x

            bin_x.append(mfp)

            bin_x = self.query_fps_in_bins.get(hpos, None)
            if bin_x is None:
                bin_x = self.BinFingerPrintList()
                self.query_fps_in_bins[hpos] = bin_x

            bin_x.append(qfp)

            new_score = self.histogram[hpos]

            # update the maximum score, if a higher one is reached
            if self.max_score is None or new_score > self.max_score[1]:
                self.max_score = (hpos, new_score)

        def remove(self, matched_pair):
            super().remove(matched_pair)

            mfp, qfp = matched_pair

            # calculate the speed ratio
            r = float(mfp.td12) / float(qfp.td12)

            hpos = int(round(mfp.pos1 - qfp.pos1 * r))
            old_score = self.histogram[hpos]

            self.histogram[hpos] -= 1

            # Score needs to be reevaluated
            if old_score == self.max_score[1]:
                self.max_score = None  # clear max_score, so it has to be recalculated

        def get_score(self):
            """
            Returns the highest diagonal score of the histogram
            :return: Highest score
            """
            if self.max_score is None:
                highest_score = self.histogram.most_common(1)
                if len(highest_score) > 0:
                    self.max_score = highest_score[0]
                else:
                    return (-1, -1)

            return self.max_score

        def get_top_bins(self, filter_factor):
            scores = np.array(self.histogram.most_common())
            return scores[scores[:, 1] > scores[:, 1].mean() * filter_factor]

        def __str__(self):
            return self.db_name + str(self.get_score()[1])

        def __repr__(self):
            return self.db_name + str(self.get_score()[1])

    def __init__(self, database: MidiLibrary, notify_init_status=None, **kwargs):
        """
        :param database: The database to perform the algorithm on
        :param kwargs: are holding custom parameters for the algorithm settings
        """
        super().__init__(database)

        np.random.seed(23)

        # Create Fingerprint-Database
        self._fingerprints = dict()
        self._in_db = set()

        # Use custom parameters
        self.N = kwargs.get(self.N_OF_NOTES, self.DEFAULT_N)
        self.n = kwargs.get(self.FINGERPRINT_PER_NOTES, self.DEFAULT_N_I)
        self.pitch_diff = kwargs.get(self.PITCH_DIFF, self.DEFAULT_PITCH_DIFF)
        self.d = kwargs.get(self.NOTE_DISTANCE, self.DEFAULT_D)
        self.verification_time_window = kwargs.get(self.VERIFICATION_TIME_WINDOW, self.DEFAULT_VERIFICATION_TIME_WINDOW)
        self.percentile = kwargs.get(self.ELIMINATE_TOP_PERCENTILE, None)
        self.split_queries_longer_than = kwargs.get(self.SPLIT_QUERIES_LONGER_THAN,
                                                    self.DEFAULT_SPLIT_QUERIES_LONGER_THAN)
        self.split_query_length = kwargs.get(self.SPLIT_QUERY_LENGTH, self.DEFAULT_SPLIT_QUERIES_LONGER_THAN)
        self.split_queries_sliding_window = kwargs.get(self.SPLIT_QUERIES_SLIDING_WINDOW,
                                                       self.DEFAULT_SPLIT_QUERIES_SLIDING_WINDOW)

        # Set settings for the FingerPrint Class
        self.FingerPrint.update_class_variables(kwargs.get(self.TDR_HASH_TYPE, self.DEFAULT_HASH),
                                                kwargs.get(self.TDR_RANGE, self.DEFAULT_TDR_RANGE),
                                                kwargs.get(self.TDR_RESOLUTION, self.DEFAULT_TDR_RESOLUTION),
                                                kwargs.get(self.TDR_WINDOW, self.DEFAULT_TDR_WINDOW),
                                                kwargs.get(self.TDR_MASK, self.DEFAULT_TDR_MASK))

        self.quantile = None

        self.create_fp_from_library(notify_init_status)

    def create_fp_from_library(self, notify_init_status=None):
        max_midi = self.database.get_length() - len(self._in_db)
        current = 0

        # Are there new items to add?
        if max_midi > 0:
            # Create fingerprints for each midifile in the database
            for midifile in self.database.get_midifiles():

                if notify_init_status is not None:
                    notify_init_status("fp", current, max_midi, midifile.name)

                if isinstance(midifile, MidiFile):
                    try:
                        if midifile.name not in self._in_db:
                            current += 1
                            self._in_db.add(midifile.name)

                            for fp in self.create_fingerprints(midifile.get_notes_for_fingerprints(), midifile.name)[0]:
                                fplist = self._fingerprints.get(fp.hash, None)
                                # check if hash is already in the list
                                if fplist is None:
                                    # create new list
                                    self._fingerprints[fp.hash] = [fp]
                                else:
                                    # otherwise append fingerprint to existing list
                                    fplist.append(fp)
                    except Exception as e:
                        if notify_init_status is not None:
                            notify_init_status("excpetion", -1, -1, "{} containts too few notes".format(midifile.name))
                        else:
                            print(e)

            if self.percentile is not None:
                lens = np.zeros(len(self._fingerprints))
                for idx, key in enumerate(self._fingerprints):
                    lens[idx] = len(self._fingerprints[key])
                self.quantile = np.percentile(lens, self.percentile)
            else:
                self.quantile = None

        if notify_init_status is not None:
            notify_init_status("fp", max_midi, max_midi, "")

    def create_fingerprints(self, query_notes, query_name, remove_doubles=False):
        """
        Creates all fingerprints for a given query: MidiFile. Optionally, fingerprints with the
        same hashvalue are not stored.
        self.N determines the used events per fingerprint.
        self.n[] determines how many fingerprints per note in the midifile will be generated

        :param query_notes: MidiFile from which fingerprints should be created
        :param query_name: MidiFile from which fingerprints should be created
        :param remove_doubles: only unique fingerprints are generated if True
        :return: List of fingerprints
        """
        prev_hashes = dict()
        fingerprints = []
        created = 0

        # First iterate over all notes
        for idx, e1 in enumerate(query_notes):
            # for each note, generate n1 follow up events
            idx2, evt2 = self._select_next_events(query_notes, idx, self.n[0])
            if evt2 is not None:
                # iterate all follow up events
                for offset2, e2 in enumerate(evt2):
                    # for each event selected for the second value, select n2 follow up events
                    idx3, evt3 = self._select_next_events(query_notes, idx2 + offset2, self.n[1])
                    if evt3 is not None:
                        # iterate over all selected events
                        for offset3, e3 in enumerate(evt3):
                            # generate fingerprint, if N=3
                            if self.N == 3:
                                fp = self.FingerPrint(query_name, e1, e2, e3, None)
                                created += 1
                                if not remove_doubles or prev_hashes.get(fp.hash, True):
                                    fingerprints.append(fp)
                                    prev_hashes[fp.hash] = False
                            else:
                                # select next followup events if N=4
                                _, evt4 = self._select_next_events(query_notes, idx3 + offset3, self.n[2])
                                if evt4 is not None:
                                    for e4 in evt4:
                                        # generate fingerprint
                                        fp = self.FingerPrint(query_name, e1, e2, e3, e4)
                                        created += 1
                                        if not remove_doubles or prev_hashes.get(fp.hash, True):
                                            fingerprints.append(fp)
                                            prev_hashes[fp.hash] = False

        return fingerprints, created

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

        p, pos = query[start_idx]
        try:
            idx = start_idx + 1

            p_next, pos_next = query[idx]

            # iterate until position self.d and pitch_diff self.pitch_diff requirements are met
            while (abs(pos_next - pos) < self.d) or (abs(p_next - p) > self.pitch_diff):
                idx += 1
                p_next, pos_next = query[idx]
        except IndexError:
            return -1, None

        return idx, query[idx:idx + n_events]

    def get_algorithm_name(self):
        return "FingerPrinting"

    def search(self, query, query_name="", evaluate=False, get_top_x=1):
        """This function does the actual matching
        it has to return a dictionary, where for each element in the database, the dict contains:
        [key, ((score, percent_score), rank, (start_of_best_match, end_of_best_match))] where:
        key is the name of the file,
        confidence is, how "sure" the algorithm is about this file beeing the query
        rank is the position, e.g. what place the confidence is at
        start_of_best_match gives the time, where the match started in the file
        pass
        If evaluate=False, the return value is a tuple of
        (name, (score, percent_score), (start_of_best_match, end_of_best_match)) of the best matching database item.
        get_top_x determines the size of the results, if evaluate = False
        query_name: optional give a name to the query, if query is no MidiFile-Object
        """

        if isinstance(query, MidiFile):
            query_name = query.name
            query_notes = query.get_notes_for_fingerprints()
        else:
            query_notes = query

        dict_result = dict()
        created_fingerprints = 0

        # create splitable windows, if split_queries_longer_than is none or < 0, don't split
        no_split = self.split_queries_longer_than is None or self.split_queries_longer_than < 0 or self.split_query_length >= query_notes.shape[0]
        if no_split:
            split_indexes = (0, )
        else:
            split_indexes = range(0, query_notes.shape[0] - self.split_query_length + 1, self.split_queries_sliding_window)

        matchdict = dict()

        for idx, split_idx in enumerate(split_indexes):
            if no_split or split_idx + self.split_query_length > query_notes.shape[0] - self.split_queries_sliding_window:
                split_end = query_notes.shape[0]
            else:
                split_end = split_idx + self.split_query_length

            # perform a query for every split and save all results in matchdict,
            split_query = query_notes[split_idx:split_end].copy()
            # adopt the starting position for all split queries, so they start from 0 time
            split_query[:, 1] = split_query[:, 1] - split_query[0, 1]

            fp, histograms, created, _ = self.perform_query(split_query, query_name)

            # count total amount of created fingerprints
            created_fingerprints += created

            # check every FingerPrintList from the performed query
            for hist in histograms:
                # create a list for every histogram in the result dictionary
                top_bins = matchdict.get(hist.db_name, None)
                if top_bins is None:
                    top_bins = []
                    matchdict[hist.db_name] = top_bins

                # Add for the top bins in each histogram an entry in the list
                # All bins above 1.25*bin_avg are added
                for bin_pos, score in hist.get_top_bins(filter_factor=1.25):
                    qfp = hist.query_fps_in_bins[bin_pos].start
                    mfp = hist.fps_in_bins[bin_pos].start

                    # Calculate a time ratio between the first matched query and database fingerprint
                    # to scale the query position for the final evaluation
                    r = float(mfp.td12) / float(qfp.td12)
                    y_pos = (qfp.pos1 + query_notes[split_idx, 1]) * r
                    x_pos = mfp.pos1
                    top_bins.append((x_pos, y_pos, score, hist.fps_in_bins[bin_pos]))

        results = []
        # Find for every database item a diagonal and calculate the maximum score (e.g. cluster
        # with highest score
        for name in matchdict:
            data = matchdict[name]
            clusters = self.find_diagonals(data)
            top_cluster = max(clusters, key=lambda cluster: cluster.score, default=self.Cluster())
            results.append((name, top_cluster, clusters))

        # sort after score, including partially used neighbors
        results = sorted(results, key=lambda itm: itm[1].score, reverse=True)

        ####################################################
        # UNCOMMENT to view some clusters of the top results as plots
        #
        # def plot_(name, query, clusters, top_score):
        #     import matplotlib.pyplot as plt
        #     for cluster in clusters:
        #         plt.scatter(cluster.to_numpy()[:, 0], cluster.to_numpy()[:, 1], marker="x", alpha=0.5)
        #     plt.scatter(top_score.to_numpy()[:, 0], top_score.to_numpy()[:, 1], marker="x", alpha=1)
        #     plt.title("db={} | q={} score={}".format(name, query, top_score.score))
        #     plt.show()
        #
        # for res in results[0:3]:
        #     plot_(query_name, res[0], res[2], res[1])
        ####################################################

        if evaluate:
            for i, (name, match, _) in enumerate(results, 1):
                dict_result[name] = (match.get_score(created_fingerprints), i, match.get_pos())
            return dict_result
        else:
            ranked_result = []
            for result in results[0:get_top_x]:
                ranked_result.append((result[0], result[1].get_score(created_fingerprints), result[1].get_pos()))
            return ranked_result

    def get_hash_value_lengths(self):
        """
        Returns a numpy array that contains the amount of hash collisions for every hash stored.
        :return: np.array
        """
        lens = np.zeros(len(self._fingerprints))
        for idx, key in enumerate(self._fingerprints):
            lens[idx] = len(self._fingerprints[key])
        return lens

    def perform_query(self, query_notes, query_name):
        """
        Search for the query by creating fingerprints of it
        and then, for each fingerprint ask for a dictionary entry.
        :param query_notes:
        :param query_name:
        :return: the created fingerprints, a list of matched fingerprints and the "true" match for analysis
        """
        query_fingerprints, created = self.create_fingerprints(query_notes, query_name, remove_doubles=True)
        matched_queries = dict()
        for fp in query_fingerprints:
            for hash_val in fp.get_hash_iterator():
                matched_fingerprint_list = self._fingerprints.get(hash_val, None)
                if matched_fingerprint_list is not None:
                    if self.quantile is None or len(matched_fingerprint_list) < self.quantile:
                        for mfp in matched_fingerprint_list:  # query all files with this fingerprint
                            matches = matched_queries.get(mfp.name, None)
                            # create a new fingerprintlist, if there is a fingerprint from a new file
                            if matches is None:
                                matches = self.FingerPrintList(mfp.name, query_fingerprints,
                                                               query_notes, query_name,
                                                               ignore_doubles=self.split_queries_longer_than is not None
                                                                              and self.split_queries_longer_than > 0)
                                matched_queries[mfp.name] = matches

                            matches.append((mfp, fp))
                    break

        should_match = matched_queries.get(query_name, None)

        return query_fingerprints, list(matched_queries.values()), created, should_match

    class Cluster(list):
        """
        Class for fingerprint clusters and a distance measure
        """
        def __init__(self):
            super().__init__()
            self.score = 0
            self.start = 0x7FFFFFFF
            self.end = 0

        def append(self, datapoint):
            """
            Append new datapoint to the list, tracks additionally the start and end position of
            the fingerprints.
            :param datapoint:
            :return:
            """
            super().append(datapoint[0:2])

            # Update score
            self.score += datapoint[2]

            # Update start and end positions.
            if self.start > datapoint[3].start.pos1:
                self.start = datapoint[3].start.pos1
            if self.end < datapoint[3].end.max_pos:
                self.end = datapoint[3].end.max_pos

        def calc_distance(self, other):
            """
            Calculate euclidean distance, weighted by the slope, e.g. the higher the slope away
            another datapoint is from the cluster
            :param other:
            :return:
            """
            lowest_distance = None
            closest_point = None

            for my_pos in self:
                for their_pos in other:
                    if my_pos[0] <= their_pos[0] and my_pos[1] <= their_pos[1]:
                        # calculate euclidean distance
                        dist = np.sqrt((my_pos[0]-their_pos[0])**2 + (my_pos[1]-their_pos[1])**2)

                        x_dist = their_pos[0] - my_pos[0]
                        y_dist = their_pos[1] - my_pos[1]

                        # Calculate slope that is always >= 1
                        slope = max(x_dist, y_dist) / max(min(x_dist, y_dist), 0.00001)

                        # weight distance by slope, the further away from 1, the more penalty.
                        dist *= slope

                        # track lowest distance between all datapoints
                        if lowest_distance is None or dist < lowest_distance:
                            lowest_distance = dist
                            closest_point = (my_pos[0], my_pos[1])

            return lowest_distance, closest_point

        def to_numpy(self):
            return np.array(self)

        def get_score(self, max_score):
            return self.score, self.score/max_score

        def get_pos(self):
            return self.start, self.end

    def find_diagonals(self, data: list):
        """ Search for diagonals in the data-list with the following constraints:
        New datapoints added to a new cluster have to be always in the top right of an existing cluster.
        (x_new > x_cluster, y_new > y_cluster)
        Slope: the slope between the new point and the closest clusterpoint has to be maximum 3
        If none of the conditions are met, a new cluster is added.
        For a new datapoint the cluster with the closest euclidean distance additionally weighted by the slope is chosen
        Finally, for all clusters the one with the highest score (e.g. most fingerprints in it, is chosen"""
        data.sort(key=lambda d: d[0])
        clusters = []
        for x, y, score, fps in data:
            lowest_distance, closest_cluster, closest_point = self.get_closest_cluster(clusters, x, y)
            # If no matching cluster for this datapoint is found, create a new one
            # but allow if datapoint is exactly on the same position as another point (e.g. distance=0)
            if closest_cluster is None or ((closest_point[0] >= x or closest_point[1] >= y) and (closest_point[0] != x or closest_point[1] != y)):
                closest_cluster = self.Cluster()
                clusters += [closest_cluster]
                closest_cluster.append((x, y, score, fps))
            else:
                # check the slope
                x_dist = x - closest_point[0]
                y_dist = y - closest_point[1]

                # calculate slope (always >= 1)
                slope = max(x_dist, y_dist) / max(min(x_dist, y_dist), 0.00001)

                # if the slope is larger then 3 create a new cluster, otherwise add to old
                if y_dist < 0 or x_dist < 0 or slope > 3:
                    new_cluster = self.Cluster()
                    clusters += [new_cluster]
                    new_cluster.append((x, y, score, fps))
                else:
                    closest_cluster.append((x, y, score, fps))
        return clusters

    @staticmethod
    def get_closest_cluster(clusters, x, y):
        """
        Get closest cluster for points x,y using single linkage (closest point IN cluster to (x,y)
        :param clusters: List of already existing clusters
        :param x:
        :param y:
        :return: distance, closest cluster and point
        """
        closest_distance = None
        closest_cluster = None
        closest_point = None

        for cluster in clusters:
            dst, closest_p_in_cluster = cluster.calc_distance([(x, y)])
            if dst is not None and closest_p_in_cluster is not None:
                if closest_distance is None or dst < closest_distance:
                    closest_distance = dst
                    closest_cluster = cluster
                    closest_point = closest_p_in_cluster

        return closest_distance, closest_cluster, closest_point

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

        __slots__ = ("name", "p1", "pos1", "td12", "hash", "max_pos")

        def __init__(self, name, e1, e2, e3, e4):
            if not self.PARAM_INIT:
                raise Exception("Call Fingerprint.update_class_variables() first")

            object.__setattr__(self, "name", name)
            object.__setattr__(self, "p1", e1[0])
            object.__setattr__(self, "pos1", e1[1])
            object.__setattr__(self, "td12", e2[1] - e1[1])
            object.__setattr__(self, "max_pos", e4[1] if self.TDR_HASH_TYPE == self.TDR_HASH_3 else e3[1])

            td23 = e3[1] - e2[1]

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


def main():
    db = MidiLibrary("../small_db")
    db.load_test_samples("../mylittlepownytest")
    fp_alg = FingerPrinting(db)
    fp_alg.evaluate(verbose=True)#, partial_test_selection=["10_COMBINED_ERROR_QUERY"])

    # db = MidiLibrary("../../StartUp-Midis/midi_startup_modified")
    # fp_alg = FingerPrinting(db)
    # query_path = "../../Rode Mic Soundfiles OKTAV - Melodien/10487 - Fascinating Rhythm.mp3"
    # from search_algorithms.transcribe_offline import Transcriptor
    # transc = Transcriptor()
    # mf = transc.process_file(query_path)
    # fp_alg.search(mf)

    # db = MidiLibrary("../../StartUp-Midis/midi_startup_modified")
    # fp_alg = FingerPrinting(db)
    # query_path = "../../StartUp-Midis/midi_startup_modified/Get Hold Of Yourself (Jamie Cullum) PVG.mid"
    # # from search_algorithms.transcribe_offline import Transcriptor
    # # transc = Transcriptor()
    # mf = MidiFile("Get Hold Of Yourself (Jamie Cullum) PVG.mid", query_path)
    # fp_alg.search(mf, evaluate=False)


if __name__ == '__main__':
    main()
