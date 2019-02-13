from library.midifile import MidiFile
from PyQt5.QtCore import pyqtSignal, QObject, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication
import queue
import ffmpeg
import re
import os


class AudioPlayer(QObject):
    """ Class that can handle player features like loading scrolling or playing an audiofile.
    The Player itself runs in a separate thread, all functions here are just message-forwarders"""
    msg = pyqtSignal(str, str, float)

    def __init__(self, tmp_dir):
        super().__init__()

        self.player_worker = self.MediaPlayerWorker(tmp_dir)
        self.msg.connect(self.player_worker.get_msg)
        self.thread = QThread()
        self.player_worker.moveToThread(self.thread)

        self.thread.started.connect(self.player_worker.run)
        self.thread.start()

    def __del__(self):
        self.close()

    def load(self, path):
        self.msg.emit(self.MediaPlayerWorker.MSG_LOAD, path, 0.0)

    def toggle_play_pause(self):
        self.msg.emit(self.MediaPlayerWorker.MSG_TOGGLE, "", 0.0)

    def play(self):
        self.msg.emit(self.MediaPlayerWorker.MSG_PLAY, "", 0.0)

    def pause(self):
        self.msg.emit(self.MediaPlayerWorker.MSG_PAUSE, "", 0.0)

    def stop(self):
        self.msg.emit(self.MediaPlayerWorker.MSG_STOP, "", 0.0)

    def close(self):
        """ Shutdown the player e.g. stop thread"""
        self.msg.emit(self.MediaPlayerWorker.MSG_CLOSE, "", 0.0)
        self.thread.quit()
        self.thread.wait()

    def set_position(self, new_position):
        self.msg.emit(self.MediaPlayerWorker.MSG_SET_POS, "", new_position)

    class MediaPlayerWorker(QObject):
        """ Player Thread to handle playback of audio files async"""
        song_position_changed = pyqtSignal(int, int)
        song_finished = pyqtSignal()
        error_occured = pyqtSignal(str, str)
        play_pause_changed = pyqtSignal(int)

        MIDI = ".mid"
        OTHER = "other"
        TMP = "tmp.mp3"
        TMP_MID = "tmp.mid"

        ERROR_TITLE = "Media Player Error"

        MSG_CLOSE = "close"
        MSG_PLAY = "play"
        MSG_PAUSE = "pause"
        MSG_TOGGLE = "toggle"
        MSG_STOP = "stop"
        MSG_SET_POS = "set_pos"
        MSG_LOAD = "load"

        MSG_RESPONSE_STOPPED = 0
        MSG_RESPONSE_PAUSED = 1
        MSG_RESPONSE_STARTED = 2
        MSG_RESPONSE_LOADED = 3

        def __init__(self, tmp_dir):
            super().__init__()
            self.exiting = False
            self.last_pos = 0
            self.messages = queue.Queue()
            self.original_file_path = ""
            self.file_type = self.OTHER
            self.start_pos = 0
            self.is_playing = False
            self.file_loaded = False
            self.tmp_dir = tmp_dir
            self.tmp_file_mp3 = self.tmp_dir + "/" + self.TMP
            self.tmp_file_mid = self.tmp_dir + "/" + self.TMP_MID
            self.pause_mark = 0
            self.file_len = 1
            self.is_closed = False
            self.mixer = None
            self.pygame = None
            self.slider_delay_update_start = 5
            self.slider_delay_update = self.slider_delay_update_start

        def __del__(self):
            self.close()

        @pyqtSlot()
        def run(self):
            """ Main thread function to handle massages passed to it"""
            global reset, path, pos

            # since run() is executed in another thread
            # import pygame directly in the thread
            # otherwise we get a segmentation fault
            from pygame import mixer
            self.mixer = mixer

            self.mixer.pre_init(44100, -16, 1, 1024)
            self.mixer.init()

            while not self.exiting:
                try:
                    msg, path, pos = self.messages.get(block=True, timeout=0.01)
                except queue.Empty:
                    msg = ""
                QApplication.instance().processEvents()
                if msg == self.MSG_PLAY:
                    self.play()
                    self.play_pause_changed.emit(self.MSG_RESPONSE_STARTED)
                elif msg == self.MSG_PAUSE:
                    self.pause()
                    self.play_pause_changed.emit(self.MSG_RESPONSE_PAUSED)
                elif msg == self.MSG_STOP:
                    self.stop()
                    self.play_pause_changed.emit(self.MSG_RESPONSE_STOPPED)
                    self.song_position_changed.emit(0., self.file_len*1000)
                elif msg == self.MSG_TOGGLE:
                    play_or_pause = self.toggle_play_pause()
                    if play_or_pause:
                        self.play_pause_changed.emit(self.MSG_RESPONSE_STARTED)
                    else:
                        self.play_pause_changed.emit(self.MSG_RESPONSE_PAUSED)
                elif msg == self.MSG_LOAD:
                    self.load(path)
                    self.song_position_changed.emit(0., self.file_len*1000)
                    self.play_pause_changed.emit(self.MSG_RESPONSE_STOPPED)
                    if self.file_loaded:
                        self.play_pause_changed.emit(self.MSG_RESPONSE_LOADED)
                elif msg == self.MSG_SET_POS:
                    self.set_position(pos)
                elif msg == self.MSG_CLOSE:
                    self.exiting = True

                # send updates on playback position of the player if it is playing
                if self.is_playing:
                    if self.slider_delay_update > 0:
                        self.slider_delay_update -= 1
                    else:
                        new_pos, length = self.get_position()
                        new_pos = int(new_pos*1000)
                        if self.last_pos != new_pos:
                            # a negative value means playback has stopped (end reached)
                            if self.mixer.music.get_pos() < 0:
                                self.is_playing = False
                                if self.file_type == self.MIDI:
                                    self.set_position(0.)
                                else:
                                    self.mixer.music.play()
                                    self.mixer.music.pause()
                                self.song_position_changed.emit(0., self.file_len*1000)
                                self.song_finished.emit()
                            else:
                                self.song_position_changed.emit(new_pos, self.file_len*1000)
                        self.last_pos = new_pos
                else:
                    self.slider_delay_update = self.slider_delay_update_start

            self.close()

        def get_msg(self, msg, path, pos):
            """ Callback to receive new messaged"""
            self.messages.put((msg, path, pos))

        def load(self, path):
            """ Loads afile"""
            self.original_file_path = path
            self.start_pos = 0
            self.pause_mark = 0
            self.mixer.music.stop()

            # Midifile has to be handled separately
            try:
                if str(path).lower().endswith(self.MIDI):
                    self.file_type = self.MIDI
                    self.file_len = MidiFile(os.path.basename(path), path).get_length()
                else:
                    try:
                        # load default file, otherwise the tmp file cannot be overridden
                        self.mixer.music.load(path)
                    except:
                        pass

                    # For all other filetypes convert the input to MP3, since the player
                    # is only capable of scrolling in MP3 Files
                    self.file_type = self.OTHER
                    self.file_len = self.convert_input_to_mp3(path, self.tmp_file_mp3)
                    path = self.tmp_file_mp3  # force path to converted mp3 file

                self.mixer.music.load(path)
                if self.file_type != self.MIDI:
                    # The player cannot pause midi playback,
                    # on the otherhand, scrolling needs pause mode in MP3
                    self.mixer.music.play()
                    self.mixer.music.pause()

                self.file_loaded = True
            except Exception as e:
                print(e)
                # indicate error during loading
                self.error_occured.emit(self.ERROR_TITLE, str(e))
                self.file_len = 0.
                self.file_loaded = False

            self.is_playing = False

        def toggle_play_pause(self):
            if not self.file_loaded:
                return False

            if self.is_playing:
                self.pause()
            else:
                self.play()

            return self.is_playing

        def play(self):
            """ start playing again"""
            if self.file_loaded:
                if self.file_type == self.MIDI:
                    # MIDI needs to reload a pausemark, since
                    # only stop can stop playing (no pause)
                    self.set_position(self.pause_mark)
                    self.mixer.music.play()
                else:
                    self.mixer.music.unpause()
                self.is_playing = True

        def pause(self):
            """ Pause playback"""
            if self.file_loaded:
                if self.file_type == self.MIDI:
                    # Midi file needs to be stopped, store last position
                    self.pause_mark, _ = self.get_position()
                    self.mixer.music.stop()
                else:
                    self.mixer.music.pause()

                self.mixer.music.pause()
                self.is_playing = False

        def stop(self):
            """ Stop playback"""
            if self.file_type == self.OTHER:
                self.pause()
                self.mixer.music.rewind()
            else:
                self.load(self.original_file_path)
                self.pause_mark = 0

        def set_position(self, new_position):
            """
            :param new_position: Position in seconds
            """
            if not self.file_loaded:
                return

            try:
                if self.file_type == self.MIDI:
                    # The player cannot set the position for MIDI-Files
                    # So create a new midi-file and truncate all notes before
                    # new_pos
                    mf = MidiFile(self.TMP_MID, self.original_file_path)
                    if new_position > 0:
                        new_position += mf.truncate_ticks(new_position, -1)
                    mf.save(self.tmp_dir, mf.name)
                    self.mixer.music.load(self.tmp_file_mid)
                else:
                    self.mixer.music.pause()
                    self.mixer.music.set_pos(new_position)
            except Exception as e:
                print(e)
                self.error_occured.emit(self.ERROR_TITLE, str(e))
                return

            # if self.file_type != self.MIDI:
            #     self.mixer.music.play()
            #     self.mixer.music.pause()

            # The player is only showing OVERALL play time, not position dependent,
            # so store real position by offsets
            if self.file_type == self.OTHER:
                self.start_pos = new_position - self.mixer.music.get_pos() / 1000.0
            else:
                self.start_pos = new_position

            self.pause_mark = new_position

            if self.is_playing:
                self.play()
            else:
                self.song_position_changed.emit(new_position * 1000, self.file_len * 1000)

        def get_position(self):
            return self.mixer.music.get_pos()/1000.0 + self.start_pos, self.file_len

        def close(self):
            if not self.is_closed:
                self.mixer.quit()
                self.is_closed = True

        def convert_input_to_mp3(self, input, output=None):
            """ Converts an input file to MP§ using FFmpeg"""
            try:
                if output is None:
                    output = input + "_converted.mp3"

                process = (ffmpeg
                           .input(input)
                           .output(output)
                           .overwrite_output()
                           .run_async(quiet=True))

                out, err = process.communicate()
                # the duration of the file is in text form in err
                result = re.search('Duration: (.*),', str(err))
                time = sum(x * float(t) for x, t in zip([3600, 60, 1], result.group(1).split(',')[0].split(":")))
                return time
            except Exception as e:
                print(e)
                self.error_occured.emit(self.ERROR_TITLE, "Unsupported file format: {}".format(os.path.splitext(input)[1]))
                return 0.0
