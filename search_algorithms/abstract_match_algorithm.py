from abc import ABC, abstractmethod
from library.midilibrary import MidiLibrary
import numpy as np
from search_algorithms.timemeasure import MeasureTime


class AbstractMatchClass(ABC):
    """Provides the evaluation-method for each algorithm to test its results"""

    def __init__(self, database: MidiLibrary):
        """Each matcher gets the database"""
        super().__init__()
        self.database = database

        self.results = {}

        self.ranking_array = (1, 5, 10, 20, 50, 100)

        self.timestamp_level = 0

        self._durations = MeasureTime()

    @abstractmethod
    def search(self, query, query_name="", evaluate=True, get_top_x=1):
        """This function does the actual matching
        it has to return a dictionary, where for each element in the database, the dict contains:
        [key, (score, rank, start_of_best_match)] where:
        key is the name of the file,
        confidence is, how "sure" the algorithm is about this file beeing the query
        rank is the position, e.g. what place the confidence is at
        start_of_best_match gives the time, where the match started in the file
        pass
        If evaluate=False, the return value is a tuple of (name, score, position) of the best matching
        database item.
        get_top_x determines the size of the results, if evaluate = False
        query_name: optional give a name to the query, if query is no MidiFile-Object
        """

    @abstractmethod
    def get_algorithm_name(self):
        pass

    def evaluate(self, verbose=False, partial_test_selection: list = None):
        """Evaluate the algorithm on the database, where sample_size samples are picked from the database,
        or if no parameter specified, the whole database will be used once as a sample.

        The tests to run are defined in the database class.
        """
        # init test-samples
        ts = MeasureTime(True)

        if not self.database.queries_created:
            return

        self.timestamp(ts, "EVAL Start", 0)

        if partial_test_selection is not None:
            test_keys = partial_test_selection
        else:
            test_keys = self.database.evaluation_queries.keys()

        for test_name in test_keys:
            self.results[test_name] = self._test(test_name, verbose=verbose)
            self.timestamp(ts, test_name, 0)

        print("Time for evaulation hh:mm:ss:ms : {}:{:2}:{:2.3f}".format(int(ts.get_whole_time_span() / 3600),
                                                                         int((ts.get_whole_time_span() % 3600) / 60),
                                                                         int((ts.get_whole_time_span() % 60)) +
                                                                         ts.get_whole_time_span() - int(
                                                                             ts.get_whole_time_span())))
        self.print_results()

    def _test(self, test_name, verbose=True, ts_name="Default"):
        """
        Perform a test specified by test_name by calling search for every query in the evaluation_query-dictionary
        found unter the test_name key
        :param test_name: String, name of the test to be evaluated
        :param verbose: Print additional information, like test specification and progress
        :param ts_name: Name of the timestamp for performance measurement
        :return: tuple (results, ranks, mrr, avg_time)
            results: list of tuples(score, rank, nr_of_notes) where each tuple represents the result the searched item
            ranks: list of list, where each item in the sublist returns the score, how many results where in the top x,
            specified by self.ranking_array
            mrr: mean reciprocal rank for this test
            avg_time: average time per query
        """
        ts = MeasureTime(True)

        queries = self.database.evaluation_queries[test_name]

        results = []
        self._print_v(verbose, "Starting test:")

        self.timestamp(ts, "{} Start".format(ts_name))

        if verbose:
            self.database.print_test_specification(test_name)

        self._durations.reset()

        # print progress
        self._print_v(self.timestamp_level == 0 and verbose,
                      "|------------------------------------------------"
                      "100%"
                      "------------------------------------------------|")
        self._print_v(self.timestamp_level == 0 and verbose, "|", end="")

        # call search for every query specified for this test
        for idx, query in enumerate(queries):
            self._print_v(
                self.timestamp_level == 0 and verbose, "\r" + "|" + "=" * (1 + int(idx / len(queries) * 100 + 0.5)), end="")

            try:
                (score, _), rank, _ = self.search(query, evaluate=True)[query.name]
            except KeyError:
                score = 0
                rank = 0xFFFFFFFF

            self.timestamp(ts, "{} Query {}".format(ts_name, idx))
            self.timestamp(self._durations, "", 0)
            results.append([score, rank, query.get_nr_of_notes()])

        self._print_v(self.timestamp_level == 0 and verbose, "|")

        # calculate the results for the test
        ranks, mrr, avg_time = self._calculate_results(results=results, verbose=verbose)

        self.timestamp(ts, "{} Results".format(ts_name))

        return results, ranks, mrr, avg_time

    @staticmethod
    def _print_v(verbose, text, end="\n"):
        if verbose:
            print(text, end=end, flush=True)

    def _calculate_statistics(self, results):
        """Calculates statistics for results matrix"""
        avg = np.average(results, axis=0)
        minimum = np.min(results, axis=0)
        _25_quartile = np.percentile(results, 25, axis=0)
        median = np.median(results, axis=0)
        _75_quartile = np.percentile(results, 75, axis=0)
        maximum = np.max(results, axis=0)

        length = results.shape[0]

        # Calculate rank-list
        # Calculates how many results are in top x rank
        ranks = [(results[:, 1] == self.ranking_array[0]).sum() / length]
        for i in range(1, len(self.ranking_array)):
            ranks.append(
                ((int(self.ranking_array[i - 1]) < results[:, 1]) & (
                        results[:, 1] <= int(self.ranking_array[i]))).sum() / length)

        ranks = np.array(ranks)

        # MRR calculation = (1/N_of-queries) * sum(1/ranks)
        mrr = (1 / results[:, 1]).sum() / length

        return avg, minimum, _25_quartile, median, _75_quartile, maximum, ranks, mrr

    def _calculate_results(self, results, verbose=True):
        """
        Calculates and prints (if verbose=True) the results of a test
        :param results: List of tuples as returned by _test()-Method
        :param verbose: Print test restults
        :return: ranks-list, mrr for this test, and query time stats
        """
        results = np.matrix(results)
        avg, minima, quartile_25, median, quartile_75, maxima, ranks, mrr = \
            self._calculate_statistics(results)

        if verbose:
            print()
            print(
                "Using {:d} queries with query-length ranging from {:5d} to {:5d}, Avg: {:5.2f}, ".format(
                    results.shape[0],
                    int(minima[
                            0, 2]),
                    int(maxima[
                            0, 2]),
                    avg[0, 2]))
            print("MRR: {:0.3f} | Average time/query {:0.5f}s".format(mrr, self._durations.get_average_timediff()))
            print("MinTime: {:0.3f}, 25_Quantile: {:0.3f}, Median: {:0.3f}, 75_Quantile: {:0.3f}, MaxTime: {:0.3f}"
                  .format(*self._durations.get_time_stats()[1:]))
            print("Average ranking position over all samples were:")
            format_string = "<={:3d}: {:5.3f}"
            sum_ = 0
            for idx, val in enumerate(self.ranking_array):
                sum_ += ranks[idx]
                print(format_string.format(val, sum_))
            print("-------------------------------------------------------------------------")
            print("Results based on Query length:")

            len_format_string = "Len={:5d} MRR={:0.3f} " \
                                "1:{:0.3f} <=5:{:0.3f} <=10:{:0.3f} <=20:{:0.3f} <=50:{:0.3f} <=100:{:0.3f}"

            for length in range(int(minima[0, 2]), int(maxima[0, 2]) + 1):
                r = results[np.where(results[:, 2] == length)[0]]
                if r.shape[0] > 0:
                    avg, minimum, _25_quartile, median, _75_quartile, maximum, l_ranks, l_mrr = \
                        self._calculate_statistics(r)
                    print(len_format_string.format(length, l_mrr, l_ranks[0], l_ranks[1], l_ranks[2], l_ranks[3],
                                                   l_ranks[4], l_ranks[5]))
            print("===================================================================================================")
        return ranks, mrr, self._durations.get_time_stats()

    def timestamp(self, meas: MeasureTime, name, level=1):
        """
        Store a timestamp
        :param meas: MeasureTime object
        :param name: timestamp name, to identify it later
        :param level: take timestamp only if level is larger then timestamp_level of class
        :return: None
        """
        if level <= self.timestamp_level:
            meas.timestamp(name)

    def print_results(self):
        """
        Prints a summary of the results currently stored in the self.results dictionary.
        Each specified test gets an entry in the self.results-dictionary after it is evaluated
        :return: None
        """
        avg_mrr = 0.0
        avg_qt = 0.0
        samples = 0
        print("MRR Results:")
        print("{:36s}\t{:5s}\t{:5s}\t{:5s}\t{:5s}".format("Test", "MRR", "Avg Time/Query", "Accuracy", "Result in top 5"))
        for result_name in self.results:
            (_, ranks, mrr, (tmean, _, _, _, _, _)) = self.results[result_name]
            avg_mrr += mrr
            avg_qt += tmean
            samples += 1
            print("{:33s}:\t{:0.3f}\t{:0.3f}\t{:0.3f}\t{:0.3f}".format(result_name, mrr,
                                                                          tmean, ranks[0], ranks[0] + ranks[1]))

        print("Average MRR:\t{:.3f}\nAverage Time/Query:\t{:.3f}".format(avg_mrr / samples, avg_qt / samples))
        print()
        # print("Ranks:")
        # for result_name in self.results:
        #     (_, ranks, _, _) = self.results[result_name]
        #     print("{:33s}".format(result_name))
        #
        #     format_string = "<={:3d}: {:5.3f}"
        #     sum_ = 0
        #     for idx2, val in enumerate(self.ranking_array):
        #         sum_ += ranks[idx2]
        #         print(format_string.format(val, sum_))
