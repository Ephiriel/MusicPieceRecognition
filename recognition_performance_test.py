import matching_algorithms as ma
from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting
import numpy as np


def main():

    def store_results(results, test_n, mrr, top, top5, avg_time_query):
        for idx, key in enumerate(results):
            mrr[test_n, idx] = results[key][2]
            top[test_n, idx] = results[key][1][0]
            top5[test_n, idx] = results[key][1][1] + results[key][1][0]
            avg_time_query[test_n, idx] = results[key][3][0]

    empty_names = ["", "", "", "", ""]
    star = ["*", "*", "*", "*", ""]
    algo_names = ["SW", "DTW", "FP Hash 1", "FP Hash 2", "FP Hash 3"]
    test_names = []

    for key in MidiLibrary._DEFAULT_TEST_SPECIFICATION:
        test_names.append(key)

    ml = MidiLibrary("nottingham-dataset-master/MIDI/melody")
    path = "recognition_performance_test_queries"
    # ml.create_test_samples(None, 2, 15, 30)
    # ml.save_test_samples(path)
    ml.load_test_samples(path)

    mrr = np.zeros((5, len(test_names)))
    top = np.zeros((5, len(test_names)))
    top5 = np.zeros((5, len(test_names)))
    avg_time_query = np.zeros((5, len(test_names)))

    test_n = 0
    search = ma.SmithWaterman(ml)
    search.evaluate(verbose=True)

    store_results(search.results, test_n, mrr, top, top5, avg_time_query)
    print("MRR:", mrr[test_n])
    print("ACC:", top[test_n])
    print("TOP5:", top5[test_n])
    print("AVG:", avg_time_query[test_n])

    test_n = 1
    search = ma.DTW(ml)
    search.evaluate(verbose=True)

    store_results(search.results, test_n, mrr, top, top5, avg_time_query)
    print("MRR:", mrr[test_n])
    print("ACC:", top[test_n])
    print("TOP5:", top5[test_n])
    print("AVG:", avg_time_query[test_n])

    test_n = 2
    search = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_1)
    search.evaluate(verbose=True)

    store_results(search.results, test_n, mrr, top, top5, avg_time_query)
    print("MRR:", mrr[test_n])
    print("ACC:", top[test_n])
    print("TOP5:", top5[test_n])
    print("AVG:", avg_time_query[test_n])

    test_n = 3
    search = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_2)
    search.evaluate(verbose=True)

    store_results(search.results, test_n, mrr, top, top5, avg_time_query)
    print("MRR:", mrr[test_n])
    print("ACC:", top[test_n])
    print("TOP5:", top5[test_n])
    print("AVG:", avg_time_query[test_n])

    test_n = 4
    search = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_3)
    search.evaluate(verbose=True)

    store_results(search.results, test_n, mrr, top, top5, avg_time_query)
    print("MRR:", mrr[test_n])
    print("ACC:", top[test_n])
    print("TOP5:", top5[test_n])
    print("AVG:", avg_time_query[test_n])

    strp = "{}&{:s}&{:.3f}&{:.3f}&{:.3f}&{:.3f}\\\\{:s}"
    for test_number, name in enumerate(test_names):
        print("\\hline")
        empty_names[2] = name
        for idx, algo_name in enumerate(algo_names):
            print(strp.format(empty_names[idx], algo_name, mrr[idx, test_number], top[idx, test_number],
                              top5[idx, test_number], avg_time_query[idx, test_number], star[idx]))

    print("MRR:", mrr)
    print("ACC:", top)
    print("TOP5:", top5)
    print("AVG:", avg_time_query)


if __name__ == '__main__':
    main()

