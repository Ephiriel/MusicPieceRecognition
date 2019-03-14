from library.midilibrary import MidiLibrary
from search_algorithms.fingerprinting import FingerPrinting
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
import os
import queue
from search_algorithms.transcribe_offline import Transcriptor
from library.midifile import MidiFile


class AsyncLibraryClass(QObject):
    """ This class runs in an async thread load and perform
    queries on a database."""

    # ListenerList for progress of loading the library
    progress_changed = pyqtSignal(int, str)

    # ListenerList for finished of loading the library
    finished = pyqtSignal()

    # ListenerList for search complete indicating
    search_complete = pyqtSignal(bool, str)

    error_occured = pyqtSignal(str, str)

    MSG_LOAD_LIBRARY = "load_lib"
    MSG_SEARCH = "search"
    MSG_EXIT = "exit"

    def __init__(self, params):
        QObject.__init__(self)
        self.exiting = False
        self.messages = queue.Queue()

        self.midi_library = None
        self.search_algorithm = None
        self.params = params
        self.search_result = None
        self.transcriber = Transcriptor()

    @pyqtSlot()
    def run(self):
        """ Main threadloop, handle messages to perform tasks"""
        global msg, str_param, int_param
        while not self.exiting:
            try:
                msg, str_param, int_param = self.messages.get(block=True, timeout=0.1)
            except queue.Empty:
                msg = ""

            # Let other tasks do something as well
            QApplication.instance().processEvents()
            if msg == self.MSG_LOAD_LIBRARY:
                self.create_library(str_param)
            elif msg == self.MSG_SEARCH:
                self.search(str_param, int_param)
            elif msg == self.MSG_EXIT:
                self.exiting = True

    def create_library(self, path):
        """ Create a new library"""
        if self.midi_library is None:
            self.midi_library = MidiLibrary(path, self.library_update_progress)
            self.search_algorithm = FingerPrinting(self.midi_library, self.library_update_progress,
                                                   **self.params)
        else:
            self.midi_library._load_library(path, self.library_update_progress)
            self.search_algorithm.create_fp_from_library(self.library_update_progress)

        self.finished.emit()

    def search(self, path: str, n_of_results):
        """ Perform search query"""
        try:
            filename = os.path.basename(path)
            if path.lower().endswith(".mid"):
                query = MidiFile(filename, path)
            else:
                query = self.transcriber.process_file(path)
            self.search_result = self.search_algorithm.search(query, query_name=filename,
                                                              evaluate=False, get_top_x=n_of_results)

            # Signal Finished
            self.search_complete.emit(True, "")
        except Exception as e:
            print(e)
            self.search_complete.emit(False, str(e))

    def library_update_progress(self, called_from, act, max, name):
        """ Inform listeners about loading library progress"""
        if max == 0:
            max = 1

        if called_from == "lib":
            progress = int(act / max * 100 * 0.15)
            progress_text = "Loading file {}/{}...".format(act, max)
        elif called_from == "fp":
            progress = int(15 + act / max * 100 * 0.85)
            progress_text = "Creating fingerprints {}/{}...".format(act, max)
        else:
            self.error_occured.emit(called_from, name)
            return

        self.progress_changed.emit(progress, progress_text)

    @pyqtSlot(str, str, int)
    def get_msg(self, msg, str_param, int_param):
        self.messages.put((msg, str_param, int_param))
