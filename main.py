from midilibrary import MidiLibrary
from FingerPrinting import FingerPrinting
from gui import Ui_MainWindow
from loadLibrary import Ui_LoadingLibrary
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QMessageBox, QDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import pyqtSignal, QObject, QThread, pyqtSlot
import sys
from player import AudioPlayer
import os

###
# python -m PyQt5.uic.pyuic -x GUI.ui -o gui.py
# python -m PyQt5.uic.pyuic -x LoadingLibrary.ui -o loadLibrary.py
###

class ApplicationWindow(QMainWindow):

    FINGERPRINTING_PARAMETERS = {
        FingerPrinting.N_OF_NOTES: 4,
        FingerPrinting.FINGERPRINT_PER_NOTES: (3, 2, 2),
        FingerPrinting.NOTE_DISTANCE: 0.05,
        FingerPrinting.PITCH_DIFF: 24,
        FingerPrinting.VERIFICATION_TIME_WINDOW: 0.5,
        FingerPrinting.TDR_HASH_TYPE: 3,
        FingerPrinting.TDR_RESOLUTION: 16,
        FingerPrinting.TDR_WINDOW: 0.25,
        FingerPrinting.TDR_MASK: 0x1F,
        FingerPrinting.TDR_RANGE: 8.0,
        FingerPrinting.USE_VERIFICATION: False,
        FingerPrinting.ELIMINATE_TOP_PERCENTILE: 99
    }

    def __init__(self, **kwargs):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.midi_library = None
        self.search_algorithm = None
        self.midi_library_path = kwargs.get("library", "")

        self.query_path = ""

        self.pauseIcon = QIcon()
        self.pauseIcon.addPixmap(QPixmap("icons/pause.png"), QIcon.Normal, QIcon.Off)
        self.playIcon = self.ui.play_pause_button.icon()

        self.currently_playing = False
        self.continue_after_slider = False
        self.music_slider_is_pressed = False

        self.library_load_dialog = None
        self.library_loader = None
        self.library_load_thread = None

        # create audioplayer and connect listeners
        self.player = AudioPlayer()
        self.player.player_worker.song_position_changed.connect(self.song_position_changed)
        self.player.player_worker.song_finished.connect(self.song_finished)
        self.player.player_worker.error_occured.connect(self.create_error_dialog)
        self.player.player_worker.play_pause_changed.connect(self.toggle_response)

        # Set menu triggers
        self.ui.actionExit.triggered.connect(self.close_application)
        self.ui.action_open_database.triggered.connect(self.open_library)
        self.ui.action_open_query.triggered.connect(self.open_query)

        # set button triggers
        self.ui.open_query_button.clicked.connect(self.open_query)
        self.ui.play_pause_button.clicked.connect(self.play_clicked)
        self.ui.stop_button.clicked.connect(self.stop_clicked)
        self.ui.search_query_button.clicked.connect(self.search_clicked)
        self.ui.zoom_in_button.clicked.connect(self.zoom_in)
        self.ui.zoom_out_button.clicked.connect(self.zoom_out)

        # slider triggers
        self.ui.zoom_slider.sliderMoved.connect(self.zoom_slider_changed)
        self.ui.music_position_slider.sliderPressed.connect(self.song_position_slider_pressed)
        self.ui.music_position_slider.sliderMoved.connect(self.song_position_slider_moved)
        self.ui.music_position_slider.sliderReleased.connect(self.song_position_slider_released)

        # list triggers
        self.ui.database_item_list_widget.doubleClicked.connect(self.database_file_selected)

    def close_application(self):
        self.close()

    def zoom_in(self):
        self.ui.zoom_slider.setValue(self.ui.zoom_slider.value() + 10)
        self.zoom_slider_changed()

    def zoom_out(self):
        self.ui.zoom_slider.setValue(self.ui.zoom_slider.value() - 10)
        self.zoom_slider_changed()

    def zoom_slider_changed(self):
        self.ui.midiViewer.set_width_scale(self.ui.zoom_slider.value())

    def open_library(self):
        midi_library_path = str(QFileDialog.getExistingDirectory(None, 'Select directory'))

        # a path was actually selected
        if midi_library_path != '':
            self._load_library(midi_library_path)

    def _load_library(self, path):
        self.midi_library_path = path
        self.library_load_dialog = QDialog(parent=self)
        self.library_load_dialog.ui = Ui_LoadingLibrary()
        self.library_load_dialog.ui.setupUi(self.library_load_dialog)

        self.library_load_thread = QThread()
        self.library_loader = self.CreateLibraryClass(self.midi_library_path, self.FINGERPRINTING_PARAMETERS)
        self.library_loader.moveToThread(self.library_load_thread)
        self.library_loader.progress_changed.connect(self.update_load_progress)
        self.library_loader.finished.connect(self.library_load_finished)

        self.library_load_thread.started.connect(self.library_loader.create_library)
        self.library_load_thread.start()
        self.library_load_thread.quit()


        self.library_load_dialog.show()

    @pyqtSlot(int, str)
    def update_load_progress(self, progress, progress_text):
        self.library_load_dialog.ui.library_loading_progress_bar.setValue(progress)
        self.library_load_dialog.ui.library_loading_task_label.setText(progress_text)

    @pyqtSlot()
    def library_load_finished(self):
        self.midi_library = self.library_loader.midi_library
        self.search_algorithm = self.library_loader.search_algorithm
        self.ui.database_item_list_widget.addItems(self.midi_library.get_midifile_names())
        self.library_load_dialog.accept()

    @pyqtSlot(int, int)
    def song_position_changed(self, pos, length):
        if self.ui.music_position_slider.maximum() != length:
            self.ui.music_position_slider.setMaximum(length)
        self.ui.music_position_slider.setSliderPosition(pos)

        scaled_length = length / 1000.0
        scaled_pos = pos / 1000.0

        self.update_music_duration_label(scaled_pos, scaled_length)
        self.ui.midiViewer.highlight_note(scaled_pos, self.ui.lock_view_button.isChecked())

    def update_music_duration_label(self, pos, length):
        # Update time label
        self.ui.song_time_label.setText("{:2d}:{:02d}/{:2d}:{:02d}".format(int(pos/60),
                                                                           int(pos) % 60,
                                                                           int(length/60),
                                                                           int(length) % 60))

    @pyqtSlot()
    def song_finished(self):
        self.set_play_button(False)
        self.ui.music_position_slider.setValue(0)
        self.ui.midiViewer.set_play_style(False)

    @pyqtSlot(int)
    def toggle_response(self, response):
        if response == self.player.player_worker.MSG_TOGGLE_STARTED:
            self.set_play_button(True)
            self.currently_playing = True
            self.ui.midiViewer.set_play_style(True)
        else:
            self.set_play_button(False)
            self.currently_playing = False
            if response == self.player.player_worker.MSG_TOGGLE_STOPPED:
                self.ui.midiViewer.set_play_style(False)

    def song_position_slider_pressed(self):
        self.music_slider_is_pressed = True
        self.ui.midiViewer.set_play_style(True)
        self.continue_after_slider = self.currently_playing
        self.player.pause()

    def song_position_slider_released(self):
        self.music_slider_is_pressed = False
        self.player.set_position(self.ui.music_position_slider.value()/1000.)
        if self.continue_after_slider:
            self.player.play()
        else:
            self.ui.midiViewer.set_play_style(False)

    def song_position_slider_moved(self):
        if self.music_slider_is_pressed:
            pos = self.ui.music_position_slider.value()/1000.
            self.ui.midiViewer.highlight_note(pos, autoscroll=self.ui.lock_view_button.isChecked())
            self.update_music_duration_label(pos, self.ui.music_position_slider.maximum()/1000.0)

    @staticmethod
    def create_error_dialog(title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.show()

    class CreateLibraryClass(QObject):
        progress_changed = pyqtSignal(int, str)
        finished = pyqtSignal()

        def __init__(self, path, params):
            QObject.__init__(self)

            self.midi_library = None
            self.search_algorithm = None
            self.midi_library_path = path
            self.params = params

        @pyqtSlot()
        def create_library(self):
            self.midi_library = MidiLibrary(self.midi_library_path, self.library_update_progress)
            self.search_algorithm = FingerPrinting(self.midi_library, self.library_update_progress,
                                                   **self.params)
            self.finished.emit()

        def library_update_progress(self, called_from, act, max, name):
            if called_from == "lib":
                progress = int(act/max*100*0.15)
                progress_text = "Loading file {}/{}...".format(act, max)
            else:
                progress = int(15 + act/max*100*0.85)
                progress_text = "Creating fingerprints {}/{}...".format(act, max)

            self.progress_changed.emit(progress, progress_text)

    def open_query(self):
        self.query_path = str(QFileDialog.getOpenFileName(None, "Select query")[0])

        # a file was actually selected
        if self.query_path != '':
            print("file selected")
        else:
            print("nothing selected")

    def play_clicked(self):
        self.player.toggle_play_pause()

    def set_play_button(self, is_play):
        if is_play:
            self.ui.play_pause_button.setIcon(self.pauseIcon)
        else:
            self.ui.play_pause_button.setIcon(self.playIcon)

    def stop_clicked(self):
        self.ui.music_position_slider.setSliderPosition(0)
        self.player.stop()

    def search_clicked(self):
        if self.midi_library is None:
            QMessageBox.about(self, "Error", "Please select a database first")

    def database_file_selected(self, item):
        db_item = self.ui.database_item_list_widget.item(item.row()).text()
        mf = self.midi_library.get_midifile(db_item)
        self.ui.currently_playing_label.setText(db_item)
        self.ui.midiViewer.draw_midi_file(mf)
        self.player.load(mf.file_path)


def main():
    app = QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    # TODO: Entfernen - fürs debuggen damits schneller geht
    application._load_library("small_db")
    exitcode = app.exec_()
    application.player.close()
    sys.exit(exitcode)


if __name__ == '__main__':
    main()

