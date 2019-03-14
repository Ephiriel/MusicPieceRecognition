from search_algorithms.fingerprinting import FingerPrinting
from gui.gui import Ui_MainWindow
from gui.loadLibrary import Ui_LoadingLibrary
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QMessageBox, QDialog, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, QTimer, Qt
import sys
from mediaplayer.player import AudioPlayer
import os
import tempfile
import shutil
import pyaudio
import wave
from library.async_database_search import AsyncLibraryClass
from gui.QtWaitingSpinner import QtWaitingSpinner

###
# use this commands to update the user interface files (Qt Designer)
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
        FingerPrinting.ELIMINATE_TOP_PERCENTILE: 99,
        FingerPrinting.SPLIT_QUERIES_LONGER_THAN: None,
        FingerPrinting.SPLIT_QUERIES_SLIDING_WINDOW: 5,
        FingerPrinting.SPLIT_QUERY_LENGTH: 20
    }

    library_msg = pyqtSignal(str, str, int)

    TMP_QUERY_NAME = "new_query_{}.wav"

    DEFAULT_PLAYER_TEXT = "Please select a query"

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    DISPLAY_N_RESULTS = 20

    def __init__(self, **kwargs):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.midi_library = None
        self.search_algorithm = None
        self.midi_library_path = kwargs.get("library", "")

        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_dir_path = self.tmp_dir.name
        self.tmp_query_path = self.tmp_dir_path + "/" + self.TMP_QUERY_NAME

        self.query_path = ""
        self.last_query_path = "."
        self.last_query = ""
        self.lib_path = "."

        self.pauseIcon = QIcon()
        self.pauseIcon.addPixmap(QPixmap("gui/icons/pause.png"), QIcon.Normal, QIcon.Off)
        self.playIcon = self.ui.play_pause_button.icon()

        self.continue_after_slider = False
        self.music_slider_is_pressed = False

        self.select_notes = None

        self.library_load_dialog = None
        self.library_worker = AsyncLibraryClass(self.FINGERPRINTING_PARAMETERS)
        self.library_load_thread = QThread()
        self.library_worker.moveToThread(self.library_load_thread)
        self.library_msg.connect(self.library_worker.get_msg)
        self.library_load_thread.started.connect(self.library_worker.run)
        self.library_load_thread.start()

        self.library_worker.progress_changed.connect(self.update_load_progress)
        self.library_worker.finished.connect(self.library_load_finished)
        self.library_worker.search_complete.connect(self.search_completed)
        self.library_worker.error_occured.connect(self.library_loading_error)

        self.search_spinner = QtWaitingSpinner(self)

        self.is_playing = False
        self.is_recording = False
        self.record_stream = None
        self.pyaudio = pyaudio.PyAudio()
        self.recorded_frames = []
        self.record_length = 0
        self.record_timer = QTimer(self)
        self.record_timer_interval = 1.0
        self.record_timer.timeout.connect(self.update_record_time)

        self.msg_box = None

        # create audioplayer and connect listeners
        self.player = AudioPlayer(self.tmp_dir_path)
        self.player.player_worker.song_position_changed.connect(self.song_position_changed)
        self.player.player_worker.song_finished.connect(self.song_finished)
        self.player.player_worker.error_occured.connect(self.create_error_dialog)
        self.player.player_worker.play_pause_changed.connect(self.player_response)

        # Set menu triggers
        self.ui.actionExit.triggered.connect(self.close_application)
        self.ui.action_open_database.triggered.connect(self.open_new_library)
        self.ui.action_Add_Folder_to_Database.triggered.connect(self.add_to_library)
        self.ui.action_open_query.triggered.connect(self.open_query)
        self.ui.action_save_query.triggered.connect(self.save_query)

        # set player button triggers
        self.ui.play_pause_button.clicked.connect(self.play_clicked)
        self.ui.stop_button.clicked.connect(self.stop_clicked)
        self.ui.music_position_slider.sliderPressed.connect(self.song_position_slider_pressed)
        self.ui.music_position_slider.sliderMoved.connect(self.song_position_slider_moved)
        self.ui.music_position_slider.sliderReleased.connect(self.song_position_slider_released)

        # set zoom triggers
        self.ui.zoom_in_button.clicked.connect(self.zoom_in)
        self.ui.zoom_out_button.clicked.connect(self.zoom_out)
        self.ui.zoom_slider.sliderMoved.connect(self.zoom_slider_changed)

        # set query triggers
        self.ui.search_query_button.clicked.connect(self.search_clicked)
        self.ui.open_query_button.clicked.connect(self.open_query)
        self.ui.save_query_button.clicked.connect(self.save_query)
        self.ui.record_query_button.clicked.connect(self.record_query)
        self.ui.open_temp_folder.clicked.connect(self.open_temp_folder)
        self.ui.load_last_query_button.clicked.connect(self.reload_last_query)

        # database triggers
        self.ui.database_item_list_widget.doubleClicked.connect(self.database_file_selected)
        self.ui.result_table.doubleClicked.connect(self.result_selected)

    def close_application(self):
        self.close()

    #################################
    # LIBRARY CALLBACKS
    def add_to_library(self, clear=False):
        """ Menu Callback, Add folder to library"""
        midi_library_path = str(QFileDialog.getExistingDirectory(None, 'Select directory', self.lib_path))

        # a path was actually selected
        if midi_library_path != '':
            if clear:
                self.ui.result_table.setRowCount(0)
                self.player.stop()
                self.ui.midiViewer.reset_view()
                self.library_worker.midi_library = None
                self.library_worker.search_algorithm = None
                self.midi_library = None
                self.search_algorithm = None
            else:
                self.player.pause()

            self.lib_path = midi_library_path
            self._load_library(midi_library_path)

    def open_new_library(self):
        """ Menu Callback, Load new Library"""
        self.add_to_library(clear=True)

    @pyqtSlot(int, str)
    def update_load_progress(self, progress, progress_text):
        """ Callback for indicating library loading status"""
        self.library_load_dialog.ui.library_loading_progress_bar.setValue(progress)
        self.library_load_dialog.ui.library_loading_task_label.setText(progress_text)

    @pyqtSlot()
    def library_load_finished(self):
        """ Callback when library loading has finished"""
        self.midi_library = self.library_worker.midi_library
        self.search_algorithm = self.library_worker.search_algorithm
        self.ui.database_item_list_widget.clear()
        self.ui.database_item_list_widget.addItems(self.midi_library.get_midifile_names())
        self.library_load_dialog.accept()
        self.library_load_dialog.deleteLater()

    def _load_library(self, path):
        """ Helper function to start library add"""
        self.midi_library_path = path
        self.library_load_dialog = QDialog(parent=self)
        self.library_load_dialog.ui = Ui_LoadingLibrary()
        self.library_load_dialog.ui.setupUi(self.library_load_dialog)
        self.library_load_dialog.ui.load_error_list.clear()

        self.library_msg.emit(AsyncLibraryClass.MSG_LOAD_LIBRARY, path, 0)

        self.library_load_dialog.show()

    def library_loading_error(self, exception, text):
        self.library_load_dialog.ui.load_error_list.addItem(text)

    def database_file_selected(self, item):
        """ Callback after an item in the database list was double clicked.
        Loads the clicked item into the view"""
        db_item = self.ui.database_item_list_widget.item(item.row()).text()
        mf = self.midi_library.get_midifile(db_item)
        self.ui.currently_playing_label.setText(db_item)
        self.select_notes = None
        self.query_path = mf.file_path
        self.player.load(mf.file_path)
        self.search_spinner.start()

    ##################################
    # ZOOM CALLBACKS

    def zoom_in(self):
        """ Callback Zoom + Button"""
        self.ui.zoom_slider.setValue(self.ui.zoom_slider.value() + 10)
        self.zoom_slider_changed()

    def zoom_out(self):
        """ Callback Zoom - Button"""
        self.ui.zoom_slider.setValue(self.ui.zoom_slider.value() - 10)
        self.zoom_slider_changed()

    def zoom_slider_changed(self):
        self.ui.midiViewer.set_width_scale(self.ui.zoom_slider.value())

    ##################################
    # PLAYER CALLBACKS

    @pyqtSlot(int, int)
    def song_position_changed(self, pos, length):
        """ Callback from player to indicate new position during playback"""
        if self.ui.music_position_slider.maximum() != length:
            self.ui.music_position_slider.setMaximum(length)
        self.ui.music_position_slider.setSliderPosition(pos)

        scaled_length = length / 1000.0
        scaled_pos = pos / 1000.0

        self.update_music_duration_label(scaled_pos, scaled_length)
        self.ui.midiViewer.position_bar(scaled_pos, self.ui.lock_view_button.isChecked())

    @pyqtSlot()
    def song_finished(self):
        """ Callbackb y player to indicate that song has finished"""
        self.set_play_button(False)
        self.ui.music_position_slider.setValue(0)
        self.ui.midiViewer.set_play_style(False)

    @pyqtSlot(int)
    def player_response(self, response):
        """ Communication callback from the player to indicate several
        new statuses"""
        if response == self.player.player_worker.MSG_RESPONSE_LOADED:
            # A file was loaded succesfully, load it into view
            queryname = os.path.basename(self.query_path)
            self.ui.currently_playing_label.setText(queryname)
            if queryname.lower().endswith(".mid"):
                self.ui.midiViewer.draw_midi_file(self.query_path, self.select_notes)
            else:
                self.ui.midiViewer.reset_view()
            self.search_spinner.stop()

        elif response == self.player.player_worker.MSG_RESPONSE_STARTED:
            # Player started playing
            self.set_play_button(True)
            self.is_playing = True
            self.ui.midiViewer.set_play_style(True)
        else:
            # MSG_RESPONSE_STOPPED or MSG_RESPONSE_PAUSED
            # Player paused or stopped
            self.set_play_button(False)
            self.is_playing = False
            if response == self.player.player_worker.MSG_RESPONSE_STOPPED:
                self.ui.midiViewer.set_play_style(False)

    @pyqtSlot(str, str)
    def create_error_dialog(self, title, message):
        """ Show an error dialog with given title and message"""
        self.search_spinner.stop()
        QMessageBox.information(self, title, message, QMessageBox.Ok)

    def update_music_duration_label(self, pos, length):
        """ Changes the music position/duration label"""
        # Update time label
        if self.is_recording:
            self.ui.song_time_label.setText("{:2d}:{:02d}".format(int(pos/60), int(pos) % 60))
        else:
            self.ui.song_time_label.setText("{:2d}:{:02d}/{:2d}:{:02d}".format(int(pos/60),
                                                                               int(pos) % 60,
                                                                               int(length/60),
                                                                               int(length) % 60))

    ##################################
    # PLAYER CONTROL BUTTON CALLBACKS

    def song_position_slider_pressed(self):
        """ Callback Scrolling in music piece started"""
        self.music_slider_is_pressed = True
        self.ui.midiViewer.set_play_style(True)
        self.continue_after_slider = self.is_playing
        self.player.pause()

    def song_position_slider_released(self):
        """ Callback Scrolling in music piece stopped"""
        self.music_slider_is_pressed = False
        self.player.set_position(self.ui.music_position_slider.value()/1000.)
        if self.continue_after_slider:
            self.player.play()
        else:
            self.ui.midiViewer.set_play_style(False)

    def song_position_slider_moved(self):
        """ Callback during scrolling in music piece to update the MIDI View"""
        if self.music_slider_is_pressed:
            pos = self.ui.music_position_slider.value()/1000.
            self.ui.midiViewer.position_bar(pos, autoscroll=self.ui.lock_view_button.isChecked())
            self.update_music_duration_label(pos, self.ui.music_position_slider.maximum()/1000.0)

    def play_clicked(self):
        """ Callback play button"""
        self.player.toggle_play_pause()

    def set_play_button(self, is_play):
        """ Change the add button according to play/pause state"""
        if is_play:
            self.ui.play_pause_button.setIcon(self.pauseIcon)
        else:
            self.ui.play_pause_button.setIcon(self.playIcon)

    def stop_clicked(self):
        """ Callback Stop button. Stop recording or music playing"""
        if self.is_recording:
            self.record_timer.stop()
            self.record_stream.stop_stream()
            self.record_stream.close()
            self.set_view_to_recording(False)
            self.create_new_query()
        else:
            self.ui.music_position_slider.setSliderPosition(0)
            self.player.stop()

    ##################################
    # QUERY CONTROL CALLBACKS

    def open_query(self):
        """ Callback open query button to Open Select File Dialog to select and load a query"""
        query_path = str(QFileDialog.getOpenFileName(None, "Select query", self.last_query_path)[0])
        # a file was actually selected

        if query_path != '':
            self.last_query_path = os.path.dirname(query_path)
            self.load_query(query_path)

    def open_temp_folder(self):
        """ Callback to Open Selct File Dialog set to the tmp directory where previously stored queries are stored"""
        query_path = str(QFileDialog.getOpenFileName(None, "Select query", self.tmp_dir.name)[0])

        if query_path != '':
            self.load_query(query_path)

    def load_query(self, path):
        """ Helperfunction to load a selected query"""
        self.query_path = path
        self.ui.currently_playing_label.setText(self.DEFAULT_PLAYER_TEXT)
        # Just load the file to the player, and let the player decide if its playable
        self.player.load(path)
        self.search_spinner.start()

    def reload_last_query(self):
        """ Callback for reload last query button"""
        if self.last_query != "" and self.query_path != self.last_query:
            self.load_query(self.last_query)

    def save_query(self):
        """ Callback to open Save File Dialog to save currently selected query"""
        if self.query_path != '':
            extension = os.path.splitext(self.query_path)[1]
            store_file_loc = str(QFileDialog.getSaveFileName(None, "Save query", self.last_query_path + "/untitled" + extension, "Audio File (*{})".format(extension))[0])
            # a file was actually selected
            if store_file_loc != '':
                self.ui.currently_playing_label.setText(self.DEFAULT_PLAYER_TEXT)

                # save last open directory, for reopen
                self.last_query_path = os.path.dirname(store_file_loc)
                try:
                    # create a copy and set current player file to newly stored file
                    shutil.copyfile(self.query_path, store_file_loc)
                    self.query_path = store_file_loc
                    self.player.load(store_file_loc)
                    self.search_spinner.start()
                except Exception as e:
                    print(e)
                    self.create_error_dialog("Save Query", "Failed to store query")
        else:
            self.create_error_dialog("Save Query", "Create or open a query first")

    def create_new_query(self):
        """ Save a recorded query into the tmp directory after stop was pressed"""
        fnum = 1
        path = self.tmp_query_path.format(fnum)
        while os.path.exists(path):
            fnum += 1
            path = self.tmp_query_path.format(fnum)

        # save
        with wave.open(path, 'w') as wav:
            wav.setnchannels(self.CHANNELS)
            wav.setsampwidth(self.pyaudio.get_sample_size(self.FORMAT))
            wav.setframerate(self.RATE)
            wav.writeframes(b''.join(self.recorded_frames))

            self.load_query(path)

    def record_query(self):
        """ Callback, record button was pressed. Start recording after message box ok"""
        if self.ui.record_query_button.isChecked():
            response = QMessageBox.question(self,
                                            "New recording",
                                            "Do you want to create a new recording?",
                                            QMessageBox.Yes | QMessageBox.Cancel,
                                            QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                # Start callback-stream recording
                self.record_length = 0
                self.set_view_to_recording(True)
                self.update_music_duration_label(0, 0)
                self.recorded_frames.clear()
                # use settings from MAIN
                self.record_stream = self.pyaudio.open(format=self.FORMAT,
                                                       channels=self.CHANNELS,
                                                       rate=self.RATE,
                                                       input=True,
                                                       frames_per_buffer=self.CHUNK,
                                                       stream_callback=self.record_stream_callback)
                self.record_timer.start(self.record_timer_interval*1000)
            else:
                self.ui.record_query_button.setChecked(False)

    def record_stream_callback(self, in_data, frame_count, time_info, status):
        """ Callback to get new recorded data"""
        self.recorded_frames.append(in_data)
        if self.is_recording:
            return None, pyaudio.paContinue
        else:
            return None, pyaudio.paComplete

    def search_clicked(self):
        """ Callback to start a search in the database of the currently selected query"""
        if self.midi_library is None:
            QMessageBox.about(self, "Error", "Please select a database first")
            return
        if self.query_path == "":
            QMessageBox.about(self, "Error", "Please select a query first")
            return

        self.last_query = self.query_path
        self.library_msg.emit(AsyncLibraryClass.MSG_SEARCH, self.query_path, self.DISPLAY_N_RESULTS)
        self.search_spinner.start()

    def search_completed(self, succes, err_msg):
        """ Callback after search was completed."""
        self.search_spinner.stop()
        if succes:
            # When successfully searched, load results into the result table
            self.ui.result_table.setRowCount(0)
            for rank, (name, (score, perc_score), (start, end)) in enumerate(self.library_worker.search_result, 1):
                self.ui.result_table.insertRow(self.ui.result_table.rowCount())
                item = QTableWidgetItem(str(rank))
                item.setTextAlignment(Qt.AlignHCenter)
                self.ui.result_table.setItem(rank - 1, 0, item)
                item = QTableWidgetItem("{:.1f}".format(score))
                item.setTextAlignment(Qt.AlignHCenter)
                self.ui.result_table.setItem(rank - 1, 1, item)
                item = QTableWidgetItem("{:.2f}".format(perc_score))
                item.setTextAlignment(Qt.AlignHCenter)
                self.ui.result_table.setItem(rank - 1, 2, item)
                item = QTableWidgetItem("{:.1f}".format(start))
                item.setTextAlignment(Qt.AlignRight)
                self.ui.result_table.setItem(rank - 1, 3, item)
                item = QTableWidgetItem(name)
                item.setTextAlignment(Qt.AlignLeft)
                self.ui.result_table.setItem(rank - 1, 4, item)

            self.ui.result_table.resizeColumnsToContents()
        else:
            QMessageBox.about(self, "Error", err_msg)

    def result_selected(self, item):
        """ Callback after double click result. Load result of query into view and player"""
        db_item = self.ui.result_table.item(item.row(), 4).text()
        mf = self.midi_library.get_midifile(db_item)
        self.ui.currently_playing_label.setText(db_item)

        self.select_notes = self.library_worker.search_result[item.row()][2]
        self.query_path = mf.file_path
        self.player.load(mf.file_path)
        self.search_spinner.start()
        # set the player to the position of the selection start
        self.player.set_position(self.select_notes[0])

    def close(self):
        """ Close all open streams and threads and finally clear tmp directory"""
        if self.record_stream is not None:
            self.record_stream.stop_stream()
            self.record_stream.close()

        self.pyaudio.terminate()
        self.player.close()
        self.library_msg.emit(AsyncLibraryClass.MSG_EXIT, "", 0)
        self.library_load_thread.quit()
        self.library_load_thread.wait()
        self.tmp_dir.cleanup()

    def set_view_to_recording(self, boolean):
        """ Helpfunction to enable/disable recording view"""
        self.ui.play_pause_button.setDisabled(boolean)
        self.ui.record_query_button.setChecked(boolean)
        self.ui.record_query_button.setDisabled(boolean)
        self.ui.music_position_slider.setDisabled(boolean)
        self.ui.currently_text_label.setVisible(not boolean)
        self.is_recording = boolean

        if boolean:
            self.ui.currently_playing_label.setText("Recording...")
            self.player.stop()
        else:
            self.ui.currently_playing_label.setText(self.DEFAULT_PLAYER_TEXT)

    def update_record_time(self):
        """ Callback of Timerthread to update recording time"""
        self.record_length += self.record_timer_interval
        self.update_music_duration_label(self.record_length, 0)


def main():
    app = QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    exitcode = app.exec_()
    application.close()
    sys.exit(exitcode)


if __name__ == '__main__':
    main()

