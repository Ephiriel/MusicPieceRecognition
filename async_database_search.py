from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
import os
import queue
from transcribe_offline import Transcriptor
from midifile import MidiFile


class AsyncLibraryClass(QObject):
    progress_changed = pyqtSignal(int, str)
    finished = pyqtSignal()
    search_complete = pyqtSignal(bool, str)

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
        global msg, str_param, int_param
        while not self.exiting:
            try:
                msg, str_param, int_param = self.messages.get(block=True, timeout=0.1)
            except queue.Empty:
                msg = ""
            QApplication.instance().processEvents()
            if msg == self.MSG_LOAD_LIBRARY:
                self.create_library(str_param)
            elif msg == self.MSG_SEARCH:
                self.search(str_param, int_param)
            elif msg == self.MSG_EXIT:
                self.exiting = True

    def create_library(self, path):
        self.midi_library = MidiLibrary(path, self.library_update_progress)
        self.search_algorithm = FingerPrinting(self.midi_library, self.library_update_progress,
                                               **self.params)
        self.finished.emit()

    def search(self, path: str, n_of_results):
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
        if called_from == "lib":
            progress = int(act / max * 100 * 0.15)
            progress_text = "Loading file {}/{}...".format(act, max)
        else:
            progress = int(15 + act / max * 100 * 0.85)
            progress_text = "Creating fingerprints {}/{}...".format(act, max)

        self.progress_changed.emit(progress, progress_text)

    @pyqtSlot(str, str, int)
    def get_msg(self, msg, str_param, int_param):
        self.messages.put((msg, str_param, int_param))
