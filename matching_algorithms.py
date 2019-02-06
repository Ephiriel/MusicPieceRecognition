import numpy as np
from AbstractMatchAlgorithm import AbstractMatchClass
from midilibrary import MidiLibrary
from midifile import MidiFile
from midifile import NoteRepresentation
import librosa.sequence as sdtw
from timemeasure import MeasureTime


class SmithWaterman(AbstractMatchClass):
    def __init__(self, database: MidiLibrary, score_function=None):
        """
        :param database: Database to perform the search on
        :param score_function: Optional, if a separate scorefunction should be used
        """
        super().__init__(database)

        self.timestamp_level = 0

        self.MATCH_SCORE = 1
        self.MISSMATCH_SCORE = -1
        self.GAP_PENALTY = -2

        if score_function is None:
            self._score_function = self._score
        else:
            self._score_function = score_function

    def get_algorithm_name(self):
        return "Smith-Waterman local sequence alignment"

    def search(self, query: MidiFile, evaluate=True):
        """Performs the search, if evaluate=True, all results are returned
        """
        results = []
        dict_result = dict()

        best_result_score = None
        best_result_name = None
        best_result_start = None

        ts = MeasureTime(True)
        self.timestamp(ts, "SW Start", 2)

        qnotes, _, _ = query.get_notelist(note_representation=NoteRepresentation.RELATIVE)
        midifiles = self.database.get_midifiles()

        self.timestamp(ts, "SW init", 2)

        # call for every file in the database the sw algorithm and store the result
        for midifile in midifiles:
            dbnotes, _, _ = midifile.get_notelist(note_representation=NoteRepresentation.RELATIVE)
            score, start_idx = self._smith_waterman(qnotes, dbnotes)
            results.append((midifile.name, score, start_idx))

            # store highest score
            if best_result_score is None or score > best_result_score:
                best_result_name = midifile.name
                best_result_score = score
                best_result_start = start_idx

            self.timestamp(ts, "SW search", 2)

        if evaluate:
            # sort descending by max score -> highest score -> best match
            results.sort(key=lambda x: x[1], reverse=True)
            # for each list entry, store tuple with sorted result index
            for i, (name, score, start_idx) in enumerate(results):
                dict_result[name] = (score, i + 1, start_idx)

            self.timestamp(ts, "SW Evaluated", 2)

            return dict_result
        else:
            self.timestamp(ts, "SW Completed", 2)
            return best_result_name, best_result_score, best_result_start

    def _score(self, x, y):
        """
        Calculate the score of comparison x and y for SW
        :param x: Item on the X-axis
        :param y: Item on the Y-axis
        :return: score
        """

        # Only define constant match and mismatch score
        if x == y:
            return self.MATCH_SCORE
        else:
            return self.MISSMATCH_SCORE

    def _smith_waterman(self, query, midi):
        """
        Perform the smith waterman algorithm
        :param query:
        :param midi:
        :return:  highest score and idx of highest score
        """

        # the score matrix is one larger then the length of the inputs,
        # this simplifies the algorithm because no indexlimits have to be
        # checked
        scores = np.zeros((len(midi) + 1, len(query) + 1))
        for i, m in enumerate(midi, 1):
            for j, q in enumerate(query, 1):
                diagonal_score = scores[i - 1, j - 1] + self._score_function(m, q)
                left_score = scores[i - 1, j] + self.GAP_PENALTY
                top_score = scores[i, j - 1] + self.GAP_PENALTY

                scores[i, j] = max(0, diagonal_score, left_score, top_score)

        # the highest score in the matrix represents the best match
        max_idx = np.argmax(scores)
        # maximum possible score is when full query is found without gaps e.g. query_len * MATCH_SCORE
        max_score = np.max(scores) / (self.MATCH_SCORE * len(query))
        return max_score, max_idx


class DTW(AbstractMatchClass):
    def __init__(self, database: MidiLibrary, note_representation=NoteRepresentation.RELATIVE):
        super().__init__(database)

        self.timestamp_level = 0

        self.note_representation = note_representation

    def get_algorithm_name(self):
        return "DTW"

    def search(self, query: MidiFile, evaluate=True):
        results = []
        dict_result = dict()
        best_result_score = None
        best_result_name = None
        best_result_start = None

        ts = MeasureTime(True)
        self.timestamp(ts, "DTW Start")

        qnotes, _, _ = query.get_notelist(note_representation=self.note_representation)

        self.timestamp(ts, "DTW Query NoteList")

        midifiles = self.database.get_midifiles()

        self.timestamp(ts, "DTW Get MidiFiles")

        for midifile in midifiles:
            dbnotes, _, _ = midifile.get_notelist(note_representation=self.note_representation)

            self.timestamp(ts, "DTW DB NoteList")

            # https://librosa.github.io/librosa/generated/librosa.sequence.dtw.html?highlight=dtw#librosa.sequence.dtw
            dist_array = sdtw.dtw(np.array(qnotes), np.array(dbnotes), subseq=True,
                                  backtrack=False, global_constraints=False)

            self.timestamp(ts, "DTW Search")

            # smallest distance in the last row is the best match, the lower the distance, the better
            dist = np.nanmin(dist_array[-1, :])

            results.append((midifile.name, dist, -1))

            if best_result_score is None or dist < best_result_score:
                best_result_name = midifile.name
                best_result_score = dist
                best_result_start = -1

            self.timestamp(ts, "DTW Stat")

            # print(query.name, midifile.name, dist)
            #
            # plt.subplot(2, 1, 1)
            # plt.title(midifile.name)
            # lbrd.specshow(dist_array, x_axis='frames', y_axis='frames')
            # plt.plot(wp[:, 1], wp[:, 0], label='Optimal path', color='y')
            # plt.legend()
            # plt.subplot(2, 1, 2)
            # plt.plot(dist_array[-1, :] / wp.shape[0])
            # plt.title('Matching cost function')
            # plt.tight_layout()
            # plt.show()

        if evaluate:
            # sort descending by max score
            # lower score is better
            results.sort(key=lambda x: x[1], reverse=False)
            for i, (name, score, start_idx) in enumerate(results):
                dict_result[name] = (score, i + 1, start_idx)

            self.timestamp(ts, "DTW Evaluated")
            return dict_result
        else:
            self.timestamp(ts, "DTW Completed")
            return best_result_name, best_result_score, best_result_start
