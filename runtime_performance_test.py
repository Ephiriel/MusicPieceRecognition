import matching_algorithms as ma
from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting
import numpy as np
import os
import shutil
import random


def main():
    def select_subsamples(from_dir, to_dir, chosen_files):
        dirlist = os.listdir(from_dir)

        os.mkdir(to_dir)

        for idx in chosen_files:
            file = dirlist[idx]
            shutil.copyfile(from_dir + "/" + file, to_dir + "/" + file)

    from_dir = "nottingham-dataset-master/MIDI/melody"
    to_dir = "part_{}"
    chosen_files = random.sample(range(1033), 1000)

    # Create partial databases
    for i in range(100, 1001, 100):
        select_subsamples(from_dir, to_dir.format(i), chosen_files[0:i])

    def store_results(result, test_n, idx, avg_time, min_time, max_time, median_time):
        avg_time[test_n, idx] = result[3][0]
        min_time[test_n, idx] = result[3][1]
        max_time[test_n, idx] = result[3][5]
        median_time[test_n, idx] = result[3][3]

    empty_names = ["", "", "", "", ""]
    star = ["*", "*", "*", "*", ""]
    algo_names = ["SW", "DTW", "FP Hash 1", "FP Hash 2", "FP Hash 3"]
    test_names = []
    n_of_queries = [100, 200, 200, 400, 400, 400, 400, 400, 400, 400]
    n_per_q = [4, 2, 2, 1, 1, 1, 1, 1, 1, 1]

    for length in range(100, 1001, 100):
        test_names.append(str(length))

    avg_time = np.zeros((5, len(test_names)))
    min_time = np.zeros((5, len(test_names)))
    max_time = np.zeros((5, len(test_names)))
    median_time = np.zeros((5, len(test_names)))

    Test = {"UNCHANGED_QUERIES": {MidiLibrary.TEST_DESCRIPTION: "Test using unmodified queries"}}

    for idx, test_name in enumerate(test_names):
        ml = MidiLibrary("part_" + test_name)
        ml.create_test_samples(n_of_queries[idx], n_per_q[idx], 20, 20, test_dict=Test, choose_random_samples=False)

        print("SW", test_name)
        search = ma.SmithWaterman(ml)
        search.evaluate(verbose=True)
        store_results(search.results["UNCHANGED_QUERIES"], 0, idx, avg_time, min_time, max_time, median_time)

        print("DTW", test_name)
        search = ma.DTW(ml)
        search.evaluate(verbose=True)
        store_results(search.results["UNCHANGED_QUERIES"], 1, idx, avg_time, min_time, max_time, median_time)

        print("Fingerprint Hash 1", test_name)
        search = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_1)
        search.evaluate(verbose=True)
        store_results(search.results["UNCHANGED_QUERIES"], 2, idx, avg_time, min_time, max_time, median_time)

        print("Fingerprint Hash 2", test_name)
        search = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_2)
        search.evaluate(verbose=True)
        store_results(search.results["UNCHANGED_QUERIES"], 3, idx, avg_time, min_time, max_time, median_time)

        print("Fingerprint Hash 3", test_name)
        search = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_3)
        search.evaluate(verbose=True)
        store_results(search.results["UNCHANGED_QUERIES"], 4, idx, avg_time, min_time, max_time, median_time)

    strp = "{}&{:s}&{:.3f}&{:.3f}&{:.3f}&{:.3f}\\\\{:s}"
    for test_number, name in enumerate(test_names):
        print("\\hline")
        empty_names[2] = name
        for idx, algo_name in enumerate(algo_names):
            print(strp.format(empty_names[idx], algo_name, avg_time[idx, test_number], min_time[idx, test_number],
                              max_time[idx, test_number], median_time[idx, test_number], star[idx]))

    print("MEAN=", avg_time)
    print("MIN=", min_time)
    print("MAX=", max_time)
    print("MEDIAN=", median_time)


if __name__ == '__main__':
    main()
