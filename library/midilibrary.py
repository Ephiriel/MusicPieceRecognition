from library.midifile import MidiFile
import os
import numpy as np
import copy


class MidiLibrary:
    """Class to manage a midi library."""
    QUERY_START_KEY = "#QSP_"
    QUERY_START_PATTERN = QUERY_START_KEY + "{:03d}_{}"
    QUERY_START_PATTERN_LENGTH = 9

    TEST_SPECIFICATION_FILE = 'test_specification.dict'

    # Keys for test dictionary
    PITCH_DEVIATION = "PITCH_DEVIATION"
    DURATION_DEVIATION = "DURATION_DEVIATION"
    CHANGE_PROBABILITY = "CHANGE_PROBABILITY"
    ADD_PROBABILITY = "ADD_PROBABILITY"
    REMOVE_PROBABILITY = "REMOVE_PROBABILITY"
    LIMIT_MIN = "LIMIT_MIN"
    LIMIT_MAX = "LIMIT_MAX"

    # Keys for test-set dictionary
    TEST_DESCRIPTION = "TEST_DESCRIPTION"
    TRANSPOSED_QUERIES_SETTINGS = "TRANSPOSED_QUERIES_SETTINGS"
    PITCH_ERROR_SETTING = "PITCH_ERROR_SETTING"
    TEMPO_CHANGE_SETTING = "TEMPO_CHANGE_LIMIT"
    CHANGED_NOTE_DURATION_SETTING = "CHANGED_NOTE_DURATION_SETTING"
    ADD_OR_REMOVE_NOTE_SETTING = "ADD_OR_REMOVE_NOTE_SETTING"

    _DEFAULT_TEST_SPECIFICATION = {
        "01_UNCHANGED_QUERIES": {TEST_DESCRIPTION: "Test using unmodified queries"},
        "02_TRANSPOSED_QUERIES": {
            TEST_DESCRIPTION: "Transpose the notes to different heights, randomly selected",
            TRANSPOSED_QUERIES_SETTINGS: {
                LIMIT_MIN: -128,
                LIMIT_MAX: 128
            }
        },
        "03_PITCH_ERROR_QUERIES_1": {
            TEST_DESCRIPTION: "Randomly selected notes are modified in their heights.",
            PITCH_ERROR_SETTING: {
                PITCH_DEVIATION: 0.4,
                CHANGE_PROBABILITY: 0.05
            }
        },
        "03_PITCH_ERROR_QUERIES_2": {
            TEST_DESCRIPTION: "Randomly selected notes are modified in their heights.",
            PITCH_ERROR_SETTING: {
                PITCH_DEVIATION: 0.5,
                CHANGE_PROBABILITY: 0.1
            }
        },
        "03_PITCH_ERROR_QUERIES_3": {
            TEST_DESCRIPTION: "Randomly selected notes are modified in their heights.",
            PITCH_ERROR_SETTING: {
                PITCH_DEVIATION: 0.6,
                CHANGE_PROBABILITY: 0.15
            }
        },
        "04_TEMPO_CHANGE_QUERIES": {
            TEST_DESCRIPTION: "Changed tempo of the query",
            TEMPO_CHANGE_SETTING: {
                LIMIT_MIN: 0.5,
                LIMIT_MAX: 2
            }
        },
        "05_CHANGED_NOTE_DURATION_QUERIES_1": {
            TEST_DESCRIPTION: "Randomly selected notes are modified in their length.",
            CHANGED_NOTE_DURATION_SETTING: {
                DURATION_DEVIATION: 0.05,
                CHANGE_PROBABILITY: 1.0
            }
        },
        "05_CHANGED_NOTE_DURATION_QUERIES_2": {
            TEST_DESCRIPTION: "Randomly selected notes are modified in their length.",
            CHANGED_NOTE_DURATION_SETTING: {
                DURATION_DEVIATION: 0.1,
                CHANGE_PROBABILITY: 1.0
            }
        },
        "05_CHANGED_NOTE_DURATION_QUERIES_3": {
            TEST_DESCRIPTION: "Randomly selected notes are modified in their length.",
            CHANGED_NOTE_DURATION_SETTING: {
                DURATION_DEVIATION: 0.2,
                CHANGE_PROBABILITY: 1.0
            }
        },
        "06_REMOVED_NOTES_QUERIES": {
            TEST_DESCRIPTION: "Randomly selected notes are removed from the queries.",
            ADD_OR_REMOVE_NOTE_SETTING: {
                ADD_PROBABILITY: 0.0,
                REMOVE_PROBABILITY: 0.1,
                PITCH_DEVIATION: 0.0,
                DURATION_DEVIATION: 0.0
            }
        },
        "07_ADDED_NOTES_QUERIES": {
            TEST_DESCRIPTION: "Randomly selected notes are added to the queries.",
            ADD_OR_REMOVE_NOTE_SETTING: {
                ADD_PROBABILITY: 0.1,
                REMOVE_PROBABILITY: 0.0,
                PITCH_DEVIATION: 0.7,
                DURATION_DEVIATION: 0.2,
            }
        },
        "08_ADDED_AND_REMOVED_NOTES_QUERIES": {
            TEST_DESCRIPTION: "Randomly selected notes are added to or removed from the queries.",
            ADD_OR_REMOVE_NOTE_SETTING: {
                ADD_PROBABILITY: 0.1,
                REMOVE_PROBABILITY: 0.1,
                PITCH_DEVIATION: 0.7,
                DURATION_DEVIATION: 0.2
            }
        },
        "09_COMBINED_ERROR_QUERY": {
            TEST_DESCRIPTION: "A combined test where all manipulations except for transposition are applied to the queries",
            PITCH_ERROR_SETTING: {
                PITCH_DEVIATION: 0.5,
                CHANGE_PROBABILITY: 0.1
            },
            TEMPO_CHANGE_SETTING: {
                LIMIT_MIN: 0.5,
                LIMIT_MAX: 2
            },
            CHANGED_NOTE_DURATION_SETTING: {
                DURATION_DEVIATION: 0.15,
                CHANGE_PROBABILITY: 1.0
            },
            ADD_OR_REMOVE_NOTE_SETTING: {
                ADD_PROBABILITY: 0.1,
                REMOVE_PROBABILITY: 0.1,
                PITCH_DEVIATION: 0.5,
                DURATION_DEVIATION: 0.15
            }
        },
        "10_COMBINED_ERROR_QUERY": {
            TEST_DESCRIPTION: "A combined test where all manipulations are applied to the queries",
            TRANSPOSED_QUERIES_SETTINGS: {
                LIMIT_MIN: -128,
                LIMIT_MAX: 128
            },
            PITCH_ERROR_SETTING: {
                PITCH_DEVIATION: 0.5,
                CHANGE_PROBABILITY: 0.1
            },
            TEMPO_CHANGE_SETTING: {
                LIMIT_MIN: 0.5,
                LIMIT_MAX: 2
            },
            CHANGED_NOTE_DURATION_SETTING: {
                DURATION_DEVIATION: 0.15,
                CHANGE_PROBABILITY: 1.0
            },
            ADD_OR_REMOVE_NOTE_SETTING: {
                ADD_PROBABILITY: 0.1,
                REMOVE_PROBABILITY: 0.1,
                PITCH_DEVIATION: 0.5,
                DURATION_DEVIATION: 0.15
            }
        }
    }

    def __init__(self, path, notify_init_status=None):
        """Initializes the library, if a path is a directory,
        load all midifiles in that directory
        if path specifies a midifile, only that file is loaded.
        :param path: Path to a folder containing midi-files"""
        self._database = dict()

        self._load_library(path, notify_init_status)
        self.test_specification = {}

        self.evaluation_queries = dict()
        self.queries_created = False

    def _load_library(self, path, notify_init_status=None):
        """Loads midifiles from a given directory path or
        a midifile if path is actually pointing to a file
        :param path: Path to a folder containing midi-files"""
        if path is None:
            return False

        if not os.path.exists(path):
            return False

        max_files = 1

        # load all midi files in this dir
        if os.path.isdir(path):
            dir_entries = os.listdir(path)
            max_files = len(dir_entries)

            for idx, file in enumerate(dir_entries):
                if notify_init_status is not None:
                    notify_init_status("lib", idx, max_files, file)
                if os.path.isdir(path + "/" + file):
                    self._load_recursive(path + "/" + file, file, notify_init_status)
                if file.endswith(".mid"):
                    self._add_file_to_library(path + "/" + file, file, notify_init_status)
        elif os.path.isfile(path):
            self._add_file_to_library(path, notify_init_status)

        if notify_init_status is not None:
            notify_init_status("lib", max_files, max_files, "")

        return True

    def _load_recursive(self, path, name_prefix, notify_init_status=None):
        # load all midi files in this dir
        for file in os.listdir(path):
            if os.path.isdir(path + "/" + file):
                self._load_recursive(path + "/" + file, name_prefix + "/" + file, notify_init_status)
            if file.endswith(".mid"):
                self._add_file_to_library(path + "/" + file, name_prefix + "/" + file, notify_init_status)

    def get_midifiles(self, idx=None, get_copy=False):
        """Returns a numpy-array of midifiles, selected by idx, or all of them if no indices are provided.
            :param idx: can be a list of indices, if None, get every midi-file in the library.
            :param get_copy: determines, if the midifile returned is a copy of the original, or the originial itself"""
        if idx is None:
            files = list(self._database.values())
        else:
            files = np.array(list(self._database.values()))[np.array(idx)]

        if get_copy:
            return copy.deepcopy(files)
        else:
            return files

    def get_midifile_names(self):
        """Returns a list of all midifile-names stored in the database."""
        return self._database.keys()

    def get_midifile(self, key):
        """Returns the copy of a midifile specified by its name as key.
        :param key: name of a midi-file"""
        try:
            return copy.deepcopy(self._database[key])
        except KeyError:
            return None

    def _add_file_to_library(self, path, filename=None, notify_init_status=None):
        """Adds a file to the library. Qualifies by path, if
        entry with same name is already inside.
        :param path: path to midi-file or a folder containing midifiles.
        :param filename: Optional filename for a given path"""
        if filename is None:
            with open(path, 'rb') as f:
                filename = f.name

        m = self.get_midifile(filename)
        if m is not None:
            filename = path

        try:
            # ignore io-errors, or if the file actually isn't a midi-file
            mf = MidiFile(filename, path)
            self._database[filename] = mf
        except:
            notify_init_status("excpetion", -1, -1, "{} containts too few notes".format(filename))

    def get_length(self):
        """returns the amount of midifiles stored in the database"""
        return len(self._database)

    def create_test_samples(self, sample_size, queries_per_sample, min_query_length, max_query_length, test_dict: dict = None, verbose=False, choose_random_samples=True, **kwargs):
        """ Creates sample_size*queries_per_sample test queries out of the midifiles stored in the database. The created
            samples are of a notelength randomly choosen between min_query_length and max_query_length.
            A testspecification can be given to select, how the samples are manipulated.

            :param sample_size: determines the amount of created samples, if None, use all midifiles stored
            :param queries_per_sample: determines how many queries are generated per sample
            :param min_query_length: determines the minimum length (in notes) of a query
            :param max_query_length: determines the maximum length (in notes) of a query
            :param test_dict: is a dictionary containing the different tests
            :param verbose: prints out more information during creation and manipulation of the library.
            :param kwargs: can contain individual tests, where the key defines the name of the test

            A default test_specification is used if test_specification=None and no kwargs are given"""

        # set a default seed, so all chosen samples from now on
        # equals each other
        np.random.seed(42)

        new_tests = {}

        if test_dict is not None:
            new_tests.update(test_dict)

        new_tests.update(kwargs)

        if len(new_tests) == 0:
            new_tests.update(self._DEFAULT_TEST_SPECIFICATION)

        # Get the query-files
        if sample_size is None:
            sample_indices = None
        else:
            if choose_random_samples:
                sample_indices = np.random.choice(self.get_length(), sample_size)
            else:
                sample_indices = list(range(0, sample_size))

        queries = self.get_midifiles(idx=sample_indices)

        cqueries = []

        # truncate the queries to their length:
        # the query will get a random length between [min_query_length, max_query_length)
        for original_query in queries:
            # Create queries_per_sample queries per samples
            for i in range(queries_per_sample):
                query = self._get_query(original_query, min_query_length, max_query_length)
                cqueries.append(query)

        queries = cqueries

        if verbose:
            print("Queries truncated")

        # every entry in the test specification determines a test.
        for test_name in new_tests:
            cqueries = copy.deepcopy(queries)
            test = new_tests[test_name]

            # collect all possible manipulations for every test
            transposed_settings = test.get(self.TRANSPOSED_QUERIES_SETTINGS, None)
            pitch_error_settings = test.get(self.PITCH_ERROR_SETTING, None)
            tempo_change_settings = test.get(self.TEMPO_CHANGE_SETTING, None)
            changed_note_duration_settings = test.get(self.CHANGED_NOTE_DURATION_SETTING, None)
            add_or_remove_note_settings = test.get(self.ADD_OR_REMOVE_NOTE_SETTING, None)

            part_queries = []

            # for each selected midifile
            for query in cqueries:
                # apply all settings who are specified for the test (e.g. not None)
                if add_or_remove_note_settings is not None:
                    # Remove a note with a given probability or add a note with a specified probability.
                    # The added node will be normally distributed around the previous note and have a length
                    # of prev_length * (1 + uniform(-DURATION_DEVIATION, DURATION_DEVIATION))
                    query.remove_or_add_random_notes(add_or_remove_note_settings[self.ADD_PROBABILITY],
                                                     add_or_remove_note_settings[self.REMOVE_PROBABILITY],
                                                     add_or_remove_note_settings[self.PITCH_DEVIATION],
                                                     add_or_remove_note_settings[self.DURATION_DEVIATION])

                if transposed_settings is not None:
                    # Transpose the query by a randomly selected value between a lower and a higher bound
                    lower_bound = max(transposed_settings[self.LIMIT_MIN], -query.get_lowest_note())
                    higher_bound = min(transposed_settings[self.LIMIT_MAX], 128 - query.get_highest_note())
                    shift = np.random.randint(lower_bound, higher_bound)
                    query.shift_notes(shift)

                if pitch_error_settings is not None:
                    # Change the pitch of a note with a given probability to a note normally distributed with std-dev
                    # given
                    query.randomize_notes(deviation=pitch_error_settings[self.PITCH_DEVIATION],
                                          probability=pitch_error_settings[self.CHANGE_PROBABILITY])

                if tempo_change_settings is not None:
                    # change the tempo of a query. The change is randomly selected within the given limits.
                    # The value is multiplied with the current length of the note to get the new length.
                    tempo_change_factor = np.random.uniform(
                        tempo_change_settings[self.LIMIT_MIN],
                        tempo_change_settings[self.LIMIT_MAX])
                    query.alter_timings(tempo_change_factor)

                if changed_note_duration_settings is not None:
                    # change the notes in the query with a given probability to a new length specified by:
                    # prev_length * (1 + uniform(-DURATION_DEVIATION, DURATION_DEVIATION))
                    query.randomize_timings(deviation=changed_note_duration_settings[self.DURATION_DEVIATION],
                                            probability=changed_note_duration_settings[self.CHANGE_PROBABILITY])

                part_queries.append(query)

            self.evaluation_queries[test_name] = part_queries
            if verbose:
                print("test queries for", test_name, "created")
        self.test_specification.update(new_tests)

        np.random.seed(42)
        self.queries_created = True

    def save_test_samples(self, directory):
        """Saves the created test samples to a specified directory.
        Additionally a representation of the test specification is stored.
        :param directory: Path to where the created test-queries should be stored to."""
        import os
        import pickle

        if not self.queries_created:
            raise Exception('First create_test_samples have to be called')

        # Create directory, if it does not exist
        if not os.path.exists(directory):
            os.mkdir(directory)

        os.chdir(directory)

        # save the test specification
        with open(self.TEST_SPECIFICATION_FILE, 'wb') as f:
            pickle.dump(self.test_specification, f)

        # save every test in a subfolder
        for query_name in self.evaluation_queries:
            if not os.path.exists(query_name):
                os.mkdir(query_name)
            for q in self.evaluation_queries[query_name]:
                if isinstance(q, MidiFile):
                    querynumber = 1
                    path = os.curdir + "/" + query_name

                    fname = self.QUERY_START_PATTERN.format(querynumber, q.name)

                    while os.path.exists(path + "/" + fname):
                        querynumber += 1
                        fname = self.QUERY_START_PATTERN.format(querynumber, q.name)

                    q.save(path, fname)

    def load_test_samples(self, directory):
        """Loads error queries from a given directory
        This directory should contain all files created by the call of save_test_queries.
        :param directory: Path to a folder containing test-queries."""
        import os
        import pickle

        # the directory has to exist
        if not os.path.exists(directory):
            return

        # clear previous samples
        self.evaluation_queries.clear()

        os.chdir(directory)

        # load all midi files in this dir
        for subdir in os.listdir("."):
            if os.path.isdir(subdir):
                self.evaluation_queries[subdir] = self._load_directory(subdir)

        # load test specification
        with open(self.TEST_SPECIFICATION_FILE, 'rb') as f:
            self.test_specification = pickle.load(f)

        self.queries_created = True

    @staticmethod
    def _load_directory(q_dir):
        """Helping method to load all midifiles from a directory.
        :param q_dir: directory"""
        import os
        q_list = []
        os.chdir(q_dir)

        # each subfolder of the given directory represents a test
        for file in os.listdir(os.curdir):
            if file.endswith(".mid"):
                with open(file, 'rb') as f:
                    name = f.name
                    if f.name.startswith(__class__.QUERY_START_KEY):
                        name = name[__class__.QUERY_START_PATTERN_LENGTH:]

                    q_list.append(MidiFile(name, file))
        os.chdir(os.pardir)

        return q_list

    @staticmethod
    def _get_query(query: MidiFile, min_query_length, max_query_length=-1):
        """create a query out of a given midifile, the length of the file will
        be randomly selected between min_query_length and max_query_length.
        :param query: Midifile to create the query of.
        :param min_query_length: Minimum length of the returned query in notes
        :param max_query_length: Maximum lenght of the returned query in notes"""
        if max_query_length == -1 or max_query_length > query.get_nr_of_notes():
            max_query_length = query.get_nr_of_notes()

        if max_query_length <= min_query_length:
            min_query_length = max_query_length - 1

        length = np.random.randint(min_query_length, max_query_length)
        start_idx = np.random.randint(0, query.get_nr_of_notes() - length)
        cq = copy.deepcopy(query)
        cq.truncate(start_idx, start_idx + length)
        return cq

    def get_settings_description(self, test_specification: dict):
        """Returns a list with all settings applied to a single test_specification
        :param test_specification: The test specification."""
        descr = []

        manipulation = test_specification.get(self.TRANSPOSED_QUERIES_SETTINGS, None)
        if manipulation is not None:
            descr.append("Transpose all notes by a value between {} and {}".format(manipulation[self.LIMIT_MIN],
                                                                                   manipulation[self.LIMIT_MAX]))

        manipulation = test_specification.get(self.PITCH_ERROR_SETTING, None)
        if manipulation is not None:
            descr.append(
                "Pitch Error: change_probability={:0.3f}, deviation={:0.3f}".format(manipulation[self.CHANGE_PROBABILITY],
                                                                                    manipulation[self.PITCH_DEVIATION]))

        manipulation = test_specification.get(self.TEMPO_CHANGE_SETTING, None)
        if manipulation is not None:
            descr.append("Change tempo by factor between {:0.3f} and {:0.3f}".format(float(manipulation[self.LIMIT_MIN]),
                                                                                     float(manipulation[self.LIMIT_MAX])))

        manipulation = test_specification.get(self.CHANGED_NOTE_DURATION_SETTING, None)
        if manipulation is not None:
            descr.append(
                "Note durations changed: change_probability={:0.3f}, change_factor between{:0.3f} and {:0.3f}".format(
                    manipulation[self.CHANGE_PROBABILITY],
                    1.0 - manipulation[self.DURATION_DEVIATION],
                    1 + manipulation[self.DURATION_DEVIATION]))

        manipulation = test_specification.get(self.ADD_OR_REMOVE_NOTE_SETTING, None)
        if manipulation is not None:
            add_prob = manipulation[self.ADD_PROBABILITY]
            if add_prob > 0:
                descr.append(
                    "Added notes: add probability={:0.3f}, added_pitch_deviation={:0.3f}, ".format(add_prob,
                                                                                manipulation[self.PITCH_DEVIATION]) +
                    "added_duration_change_factor between {:0.3f} and {:0.3f}".format(1 - manipulation[self.DURATION_DEVIATION],
                                                                                      1 + manipulation[self.DURATION_DEVIATION]))

            rem_prob = manipulation[self.REMOVE_PROBABILITY]
            if rem_prob > 0:
                descr.append("Removed notes with probability={:0.3f}".format(rem_prob))

        # Unmodified setting
        if len(descr) == 0:
            descr.append("Unmodified")

        return descr

    def get_test_description(self, name=None, pretty=True):
        """Returns a list with one item per line, containing the text description a given the test.
        :param name: The name of the test.
        :param pretty: Use pretty formatting with additional lines to make it look more pretty"""
        descr = []

        if name is None:
            descr = []
            for test_name in self.test_specification:
                descr.extend(self.get_test_description(test_name, pretty))
                if pretty:
                    descr.append("")
                    descr.append("")
            return descr
        else:
            spec = self.test_specification[name]

            if pretty:
                descr.append("=====================================================================")

            descr.append(name)

            if pretty:
                descr.append("---------------------------------------------------------------------")
            descr.append(spec.get(self.TEST_DESCRIPTION, ""))

            if pretty:
                for line in self.get_settings_description(spec):
                    descr.append("\t" + line)
            else:
                descr.extend(self.get_settings_description(spec))

        return descr

    def print_test_specification(self, name=None, pretty=True):
        """Prints a test, or all tests if no name is specified
        :param name: The name of the test or None if all tests should be printed.
        :param pretty: Use pretty formatting with additional lines to make it look more pretty"""
        for line in self.get_test_description(name, pretty):
            print(line)

    def clear_test_samples(self):
        self.queries_created = False
        self.test_specification.clear()
        self.evaluation_queries.clear()


def main():
    print(np.ceil(-1.5))

    library = MidiLibrary("lakh_midi")
    # library.create_test_samples(None, 25, 26)
    # library.save_test_samples("test")
    # library.load_test_samples("test")
    #
    # library.print_test_specification()

if __name__ == "__main__":
    main()
