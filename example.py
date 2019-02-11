from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting

lib = MidiLibrary("midifiles")

# define a small test-specification:
TEST_SPECIFICATION = {
    "PITCH_ERROR_TESTS": {
        MidiLibrary.TEST_DESCRIPTION: "Randomly selected notes are modified in their heights.",
        MidiLibrary.PITCH_ERROR_SETTING: {              # This test has pitch errors
            MidiLibrary.PITCH_DEVIATION: 0.25,          # The deviation around a changed note is 0.25
            MidiLibrary.CHANGE_PROBABILITY: 0.1         # Change 10% of the notes
        }
    },

    # Add a test that has pitch errors and is transposed
    "TRANSPOSED_AND_PITCH_ERROR_QUERIES": {
        MidiLibrary.TEST_DESCRIPTION: "A combined test of transposed and randomly selected notes changed in height.",
        MidiLibrary.TRANSPOSED_QUERIES_SETTINGS: {      # This specifies the transposition part in the test
            MidiLibrary.LIMIT_MIN: -20,                 # Transpose at maximum 20 notes down
            MidiLibrary.LIMIT_MAX: 20                   # Transpose at maximum 20 notes up
        },
        MidiLibrary.PITCH_ERROR_SETTING: {              # This specifies the pitch errors
            MidiLibrary.PITCH_DEVIATION: 0.4,           # A changed note will have a deviation of 0.4 around its value
            MidiLibrary.CHANGE_PROBABILITY: 0.1         # 10% of the notes are changed
        }
    },

    # Add another test that hat duration and pitch errors
    "DURATION_AND_PITCH_ERROR_QUERIES": {
        MidiLibrary.TEST_DESCRIPTION: "A combined test where randomly selected notes are changed in pitch and length",
        MidiLibrary.PITCH_ERROR_SETTING: {              # This specifies the pitch errors
            MidiLibrary.PITCH_DEVIATION: 0.25,          # A changed note will have a deviation of 0.25 around its value
            MidiLibrary.CHANGE_PROBABILITY: 0.2         # 10% of the notes are changed
        },
        MidiLibrary.CHANGED_NOTE_DURATION_SETTING: {    # This specifies the note duration changes
            MidiLibrary.DURATION_DEVIATION: 0.2,        # the note-lengths will be multiplied by 1 + uniform(-0.2, 0.2)
            MidiLibrary.CHANGE_PROBABILITY: 1.0         # All notes will be changed
        }
    }
}

# Create queries out of the specified
lib.create_test_samples(sample_size=None,               # Use all samples in the folder
                        queries_per_sample=2,           # Create 2 queries per sample
                        min_query_length=5,             # Minimum length of a query can be 5 notes
                        max_query_length=50,            # Maximum length of a query can be 50 notes
                        test_dict=TEST_SPECIFICATION,   # This specifies what tests to create
                        verbose=False,                  # No additional outputs in the command line
                        QUERIES_WITH_NO_CHANGES={       # As additional parameters, further tests can be specified
                            MidiLibrary.TEST_DESCRIPTION: "A test with only truncated queries and no other changes"
                        },
                        FAST_QUERIES={
                            MidiLibrary.TEST_DESCRIPTION: "Test very fast queries",
                            MidiLibrary.TEMPO_CHANGE_SETTING: {
                                MidiLibrary.LIMIT_MIN: 2,  # speed up factor of in between 2 and 4
                                MidiLibrary.LIMIT_MAX: 4
                            }
                        })

# After test creation, lets print a short summary
lib.print_test_specification(name=None,                 # None means print all specified tests
                             pretty=True)               # Use a pretty formatting

# Now store the test settings in a folder
lib.save_test_samples("Example_Tests")


# Create a new library and load the samples from the previous library
newlib = MidiLibrary("midifiles")
newlib.load_test_samples("Example_Tests")

# After loading, no additional test-specifications have to be called, since they are stored in the directory alongside
# the midi-files

# Create a Fingerprint test, Parameters are used for HashType 3
fp_test = FingerPrinting(lib, **FingerPrinting.PARAM_SETTING_3)

# Do the evaluation, e.g. perform all tests
fp_test.evaluate(verbose=False)

# print a short summary of the test-results
fp_test.print_results()

