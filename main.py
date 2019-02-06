from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting
from matching_algorithms import SmithWaterman, DTW


def main():
    ml = MidiLibrary("nottingham-dataset-master/MIDI/melody")
    ml.create_test_samples(None, 2, 15, 30)
    ml.save_test_samples("performance_test_queries")

    sw = SmithWaterman(ml)
    sw.evaluate(verbose=True)

    dtw = DTW(ml)
    dtw.evaluate(verbose=True)

    fp1 = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_1)
    fp1.evaluate(verbose=True)

    fp2 = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_2)
    fp2.evaluate(verbose=True)

    fp3 = FingerPrinting(ml, **FingerPrinting.PARAM_SETTING_3)
    fp3.evaluate(verbose=True)


if __name__ == '__main__':
    main()

