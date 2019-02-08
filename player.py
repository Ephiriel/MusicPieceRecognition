import time
import tempfile
from midifile import MidiFile
import wave
import pygame
from pygame import mixer


class AudioPlayer:

    WAV = ".wav"
    MIDI = ".mid"
    OTHER = "other"
    TMP = "tmp.tmp"

    def __init__(self):
        pygame.init()
        self.original_file_path = ""
        self.file_type = self.OTHER
        self.start_pos = 0
        self.is_playing = False
        self.file_loaded = False
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pause_mark = 0

    def __del__(self):
        self.close()

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
            mixer.music.load(path)
            if self.file_type != self.MIDI:
                mixer.music.play()
                mixer.music.pause()
        except Exception as e:
            print(e)
            # TODO: Error Popup: Filetype not supported
            pass
        self.is_playing = False
        self.file_loaded = True

    def toggle_play_pause(self, reset=False):
        if not self.file_loaded:
            return False

        if reset or self.is_playing:
            self.pause()
        else:
            self.play()

        return self.is_playing

    def play(self):
        if self.file_loaded:
            if self.file_type == self.MIDI:
                self.set_position(self.pause_mark)
                mixer.music.play()
            else:
                mixer.music.unpause()
            self.is_playing = True

    def pause(self):
        if self.file_loaded:
            if self.file_type == self.MIDI:
                self.pause_mark = self.get_position()
                mixer.music.stop()
            else:
                mixer.music.pause()

            mixer.music.pause()
            self.is_playing = False

    def stop(self):
        if self.file_type == self.OTHER:
            self.pause()
            mixer.music.rewind()
        else:
            self.load(self.original_file_path)
            self.pause_mark = 0


    def set_position(self, new_position):
        """
        :param new_position: Position in seconds
        """
        if self.file_type == self.OTHER:
            try:
                mixer.music.pause()
                mixer.music.set_pos(new_position)
            except Exception as e:
                print(e)
                # TODO: Error Popup: Filetype does not support set_pos
                pass
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

                mixer.music.load(self.tmp_dir.name + "/" + self.TMP)
            except Exception as e:
                print(e)
                # TODO: Error Popup: set_pos not possible
                pass

            if self.file_type != self.MIDI:
                mixer.music.play()
                mixer.music.pause()

        self.start_pos = new_position

        if self.is_playing:
            print("unpause for no reason")
            self.play()

    def get_position(self):
        return mixer.music.get_pos()/1000 + self.start_pos

    def close(self):
        pygame.quit()
        self.tmp_dir.cleanup()


def main():

    player = AudioPlayer()

    # player.load("audiofiles/10245 - How long has this been going on.mp3")
    # player.load("audiofiles/sample.aac") # NOT WORKING
    # player.load("audiofiles/sample.ac3") # NOT WORKING
    # player.load("audiofiles/sample.aiff") # NO SET_POS
    # player.load("audiofiles/sample.amr") # NOT WORKING
    # player.load("audiofiles/sample.au") # NOT WORKING
    # player.load("audiofiles/sample.flac") # NOT WORKING
    # player.load("audiofiles/sample.m4a") # NOT WORKING
    # player.load("audiofiles/sample.mid") # OK
    # player.load("audiofiles/sample.mka") # NOT WORKING
    # player.load("audiofiles/sample.mp3") # OK
    # player.load("audiofiles/sample.ogg") # NOT WORKING
    # player.load("audiofiles/sample.ra") # NOT WORKING
    # player.load("audiofiles/sample.voc") # NOT WORKING
    player.load("audiofiles/sample.wav") # OK
    # player.load("audiofiles/sample.wma") # NOT WORKING
    # player.load("small_db/ashover1.mid")
    player.set_position(2)
    player.play()
    while mixer.music.get_busy():
        time.sleep(1)
        print(player.get_position())


if __name__ == '__main__':
    main()

