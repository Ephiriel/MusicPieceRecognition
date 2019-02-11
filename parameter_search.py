import matching_algorithms as ma
from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting
import FingerPrintingTest
import matplotlib.pyplot as plt


def main():
    # ml = MidiLibrary("midifiles")
    # ml = MidiLibrary("midi_startup")
    # ml = MidiLibrary("mixed_midis")
    # ml = MidiLibrary("full_midis")
    ml = MidiLibrary("nottingham-dataset-master/MIDI/melody")

    path = "parameter_search"
    # ml.create_test_samples(None, 1, 15, 30, test_dict=queries)
    # ml.save_test_samples(path)
    ml.load_test_samples(path)
    queries = {
        "UNCHANGED_QUERIES": {MidiLibrary.TEST_DESCRIPTION: "Test using unmodified queries"},
        "COMBINED_ERROR_QUERY": {
            MidiLibrary.TEST_DESCRIPTION: "A combined test where all manipulations are applied to the queries",
            MidiLibrary.TRANSPOSED_QUERIES_SETTINGS: {
                MidiLibrary.LIMIT_MIN: -128,
                MidiLibrary.LIMIT_MAX: 128
            },
            MidiLibrary.PITCH_ERROR_SETTING: {
                MidiLibrary.PITCH_DEVIATION: 0.5,
                MidiLibrary.CHANGE_PROBABILITY: 0.1
            },
            MidiLibrary.TEMPO_CHANGE_SETTING: {
                MidiLibrary.LIMIT_MIN: 0.5,
                MidiLibrary.LIMIT_MAX: 2
            },
            MidiLibrary.CHANGED_NOTE_DURATION_SETTING: {
                MidiLibrary.DURATION_DEVIATION: 0.15,
                MidiLibrary.CHANGE_PROBABILITY: 1.0
            },
            MidiLibrary.ADD_OR_REMOVE_NOTE_SETTING: {
                MidiLibrary.ADD_PROBABILITY: 0.1,
                MidiLibrary.REMOVE_PROBABILITY: 0.1,
                MidiLibrary.PITCH_DEVIATION: 0.5,
                MidiLibrary.DURATION_DEVIATION: 0.15
            }
        }
    }

    f_max_settings = None
    a_max_settings = None
    f_noerr = None
    a_noerr = None
    fastest = 999
    no_err_fastest = 999
    most_accurate = 0
    no_err_acc = 0

    setting_result = dict()

    for tdr_res, tdr_mask in [(8, 0x07), (16, 0x0F), (32, 0x1F), (64, 0x3F), (128, 0x7F), (256, 0xFF)]:
        for tdr_range in [16]:
            for n1 in range(2, 5):
                for n2 in range(2, 5):
                    for n3 in range(1, 2):
                        for perc in (99,):
                            setting = {
                                FingerPrinting.N_OF_NOTES: 3,
                                FingerPrinting.FINGERPRINT_PER_NOTES: (n1, n2),
                                FingerPrinting.NOTE_DISTANCE: 0.05,
                                FingerPrinting.PITCH_DIFF: 24,
                                FingerPrinting.VERIFICATION_TIME_WINDOW: 0.5,
                                FingerPrinting.TDR_HASH_TYPE: 2,
                                FingerPrinting.TDR_RESOLUTION: tdr_res,
                                FingerPrinting.TDR_WINDOW: 0.25,
                                FingerPrinting.TDR_MASK: tdr_mask,
                                FingerPrinting.TDR_RANGE: tdr_range,
                                FingerPrinting.USE_VERIFICATION: True,
                                FingerPrinting.ELIMINATE_TOP_PERCENTILE: perc
                            }
                            print("tdr_res:", tdr_res, "tdr_range:", tdr_range, "(", n1, n2, n3, ")", perc)
                            fp = FingerPrinting(ml, **setting)
                            fp.evaluate(verbose=False)

                            print(
                                "========================================================"
                                "========================================================")
                            print(
                                "========================================================"
                                "========================================================")
                            print(
                                "========================================================"
                                "========================================================")

                            setting_result[(n1, n2, n3)] = (fp.results["COMBINED_ERROR_QUERY"][2],
                                                            fp.results["COMBINED_ERROR_QUERY"][3][0],
                                                            fp.results["UNCHANGED_QUERIES"][2],
                                                            fp.results["UNCHANGED_QUERIES"][3][0],
                                                            tdr_res, tdr_range, n1, n2, n3)

                            if fp.results["COMBINED_ERROR_QUERY"][2] > most_accurate:
                                most_accurate = fp.results["COMBINED_ERROR_QUERY"][2]
                                a_max_settings = (tdr_res, tdr_range, n1, n2, n3)
                            if fp.results["COMBINED_ERROR_QUERY"][3][0] < fastest:
                                fastest = fp.results["COMBINED_ERROR_QUERY"][3][0]
                                f_max_settings = (tdr_res, tdr_range, n1, n2, n3)
                            if fp.results["UNCHANGED_QUERIES"][2] > no_err_acc:
                                no_err_acc = fp.results["UNCHANGED_QUERIES"][2]
                                a_noerr = (tdr_res, tdr_range, n1, n2, n3)
                            if fp.results["UNCHANGED_QUERIES"][3][0] < no_err_fastest:
                                no_err_fastest = fp.results["UNCHANGED_QUERIES"][3][0]
                                f_noerr = (tdr_res, tdr_range, n1, n2, n3)

    print("fastest:", f_max_settings, fastest)
    print("accur:", a_max_settings, most_accurate)

    print("No Err fastest:", f_noerr, no_err_fastest)
    print("No Err accur:", a_noerr, no_err_acc)


if __name__ == '__main__':
    main()
