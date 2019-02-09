import time
import tempfile
from midifile import MidiFile
import wave
from PyQt5.QtCore import pyqtSignal, QObject, QThread, pyqtSlot
import queue


class AudioPlayer(QObject):
    msg = pyqtSignal(str, str, float)

    WAV = ".wav"
    MIDI = ".mid"
    OTHER = "other"
    TMP = "tmp.tmp"

    def __init__(self):
        super().__init__()

        self.player_worker = self.MediaPlayerWorker()
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
        self.msg.emit(self.MediaPlayerWorker.MSG_CLOSE, "", 0.0)
        self.thread.quit()
        self.thread.wait()

    def set_position(self, new_position, relative=False):
        self.msg.emit(self.MediaPlayerWorker.MSG_SET_POS, "", new_position)

    class MediaPlayerWorker(QObject):
        song_position_changed = pyqtSignal(int, int)
        song_finished = pyqtSignal()
        error_occured = pyqtSignal(str, str)
        play_pause_changed = pyqtSignal(int)

        WAV = ".wav"
        MIDI = ".mid"
        OTHER = "other"
        TMP = "tmp.tmp"

        ERROR_TITLE = "Media Player Error"

        MSG_CLOSE = "close"
        MSG_PLAY = "play"
        MSG_PAUSE = "pause"
        MSG_TOGGLE = "toggle"
        MSG_STOP = "stop"
        MSG_SET_POS = "set_pos"
        MSG_LOAD = "load"

        MSG_TOGGLE_STOPPED = 0
        MSG_TOGGLE_PAUSED = 1
        MSG_TOGGLE_STARTED = 2

        def __init__(self):
            super().__init__()
            self.exiting = False
            self.last_pos = 0
            self.messages = queue.Queue()
            self.original_file_path = ""
            self.file_type = self.OTHER
            self.start_pos = 0
            self.is_playing = False
            self.file_loaded = False
            self.tmp_dir = tempfile.TemporaryDirectory()
            self.pause_mark = 0
            self.file_len = 1
            self.is_closed = False
            self.mixer = None
            self.pygame = None

        def __del__(self):
            self.close()

        @pyqtSlot()
        def run(self):
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
                if msg == self.MSG_PLAY:
                    self.play()
                    self.play_pause_changed.emit(self.MSG_TOGGLE_STARTED)
                elif msg == self.MSG_PAUSE:
                    self.pause()
                    self.play_pause_changed.emit(self.MSG_TOGGLE_PAUSED)
                elif msg == self.MSG_STOP:
                    self.stop()
                    self.play_pause_changed.emit(self.MSG_TOGGLE_STOPPED)
                    self.song_position_changed.emit(0., self.file_len*1000)
                elif msg == self.MSG_TOGGLE:
                    play_or_pause = self.toggle_play_pause()
                    if play_or_pause:
                        self.play_pause_changed.emit(self.MSG_TOGGLE_STARTED)
                    else:
                        self.play_pause_changed.emit(self.MSG_TOGGLE_PAUSED)
                elif msg == self.MSG_LOAD:
                    self.load(path)
                    self.song_position_changed.emit(0., self.file_len*1000)
                elif msg == self.MSG_SET_POS:
                    self.set_position(pos)
                elif msg == self.MSG_CLOSE:
                    self.exiting = True

                if self.is_playing:
                    new_pos, length = self.get_position()
                    new_pos = int(new_pos*1000)
                    if self.last_pos != new_pos:
                        if self.mixer.music.get_pos() < 0:
                            self.is_playing = False
                            self.set_position(0.)
                            self.song_position_changed.emit(0., self.file_len*1000)
                            self.song_finished.emit()
                        else:
                            self.song_position_changed.emit(new_pos, self.file_len*1000)
                    self.last_pos = new_pos

            self.close()

        def get_msg(self, msg, path, pos):
            self.messages.put((msg, path, pos))

        def load(self, path):
            self.original_file_path = path
            self.start_pos = 0
            if str(path).lower().endswith(self.MIDI):
                self.file_type = self.MIDI
            elif str(path).lower().endswith(self.WAV):
                self.file_type = self.WAV
            else:
                self.file_type = self.OTHER

            try:
                self.file_len = self._get_len(path)
                self.mixer.music.load(path)
                if self.file_type != self.MIDI:
                    self.mixer.music.play()
                    self.mixer.music.pause()
            except Exception as e:
                # TODO: Error Popup: Filetype not supported
                self.error_occured.emit(self.ERROR_TITLE, str(e))
                # self.notify_error(self.ERROR_TITLE, str(e))
                pass
            self.is_playing = False
            self.file_loaded = True

        def toggle_play_pause(self):
            if not self.file_loaded:
                return False

            if self.is_playing:
                self.pause()
            else:
                self.play()

            return self.is_playing

        def play(self):
            if self.file_loaded:
                if self.file_type == self.MIDI:
                    self.set_position(self.pause_mark)
                    self.mixer.music.play()
                else:
                    self.mixer.music.unpause()
                self.is_playing = True

        def pause(self):
            if self.file_loaded:
                if self.file_type == self.MIDI:
                    self.pause_mark, _ = self.get_position()
                    self.mixer.music.stop()
                else:
                    self.mixer.music.pause()

                self.mixer.music.pause()
                self.is_playing = False

        def stop(self):
            if self.file_type == self.OTHER:
                self.pause()
                self.mixer.music.rewind()
            else:
                self.load(self.original_file_path)
                self.pause_mark = 0

        def _get_len(self, path: str):
            if path.lower().endswith(".aiff"):
                from mutagen.aiff import AIFF
                filetype = AIFF(path)
                return filetype.info.length
            elif path.lower().endswith(".mid"):
                mf = MidiFile(self.TMP, path)
                return mf.get_length()
            elif path.lower().endswith(".mp3"):
                from mutagen.mp3 import MP3
                filetype = MP3(path)
                return filetype.info.length
            elif path.lower().endswith(".wav"):
                with wave.open(self.original_file_path, 'r') as wav:
                    return wav.getnframes() / wav.getframerate()

        def set_position(self, new_position):
            """
            :param new_position: Position in seconds
            """
            if not self.file_loaded:
                return

            if self.file_type == self.OTHER:
                try:
                    self.mixer.music.pause()
                    self.mixer.music.set_pos(new_position)
                except Exception as e:
                    # TODO: Error Popup: Filetype does not support set_pos
                    self.error_occured.emit(self.ERROR_TITLE, str(e))
            else:
                try:
                    if self.file_type == self.MIDI:
                        mf = MidiFile(self.TMP, self.original_file_path)
                        mf.truncate_ticks(new_position, -1)
                        mf.save(self.tmp_dir.name, mf.name)
                    elif self.file_type == self.WAV:
                        with wave.open(self.original_file_path, 'r') as wav, \
                                wave.open(self.tmp_dir.name + "/" + self.TMP, "w") as out:

                            start_pos = int(wav.getframerate() * new_position)
                            length = wav.getnframes() - start_pos
                            out.setparams((wav.getnchannels(),
                                           wav.getsampwidth(),
                                           wav.getframerate(),
                                           length,
                                           wav.getcomptype(),
                                           wav.getcompname()))
                            wav.rewind()
                            start_pos = wav.tell() + start_pos
                            wav.setpos(start_pos)
                            out.writeframes(wav.readframes(length))

                    self.mixer.music.load(self.tmp_dir.name + "/" + self.TMP)
                except Exception as e:
                    # TODO: Error Popup: set_pos not possible
                    self.error_occured.emit(self.ERROR_TITLE, str(e))
                    pass

                if self.file_type != self.MIDI:
                    self.mixer.music.play()
                    self.mixer.music.pause()

            if self.file_type == self.OTHER:
                self.start_pos = new_position - self.mixer.music.get_pos() / 1000.0
            else:
                self.start_pos = new_position

            self.pause_mark = new_position

            if self.is_playing:
                self.play()

        def get_position(self):
            return self.mixer.music.get_pos()/1000.0 + self.start_pos, self.file_len

        def close(self):
            if not self.is_closed:
                self.mixer.quit()
                self.tmp_dir.cleanup()
                self.is_closed = True


def main():

    player = AudioPlayer()

    # player.load("audiofiles/10245 - How long has this been going on.mp3")
    # player.load("audiofiles/sample.aac") # NOT WORKING
    # player.load("audiofiles/sample.ac3") # NOT WORKING
    # player.load("audiofiles/sample.amr") # NOT WORKING
    # player.load("audiofiles/sample.au") # NOT WORKING
    # player.load("audiofiles/sample.flac") # NOT WORKING
    # player.load("audiofiles/sample.m4a") # NOT WORKING
    # player.load("audiofiles/sample.mka") # NOT WORKING
    # player.load("audiofiles/sample.ogg") # NOT WORKING
    # player.load("audiofiles/sample.ra") # NOT WORKING
    # player.load("audiofiles/sample.voc") # NOT WORKING
    # player.load("audiofiles/sample.wma") # NOT WORKING
    player.load("audiofiles/sample.mid")  # OK
    # player.load("audiofiles/sample.mp3")  # OK
    # player.load("audiofiles/sample.wav")  # OK
    # player.load("audiofiles/sample.aiff")  # NO SET_POS

    # player.set_position(2)
    player.play()
    while True:
        time.sleep(1)
        player.pause()


if __name__ == '__main__':
    main()

