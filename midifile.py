import midi
import numpy as np
from enum import Enum


class NoteRepresentation(Enum):
    ABSOLUTE = 1
    RELATIVE = 2
    UPDOWN = 3


class DurationRepresentation(Enum):
    ABSOLUTE = 1
    RELATIVE = 2


class MidiFile:
    """ Midi file loading / saving / manipulating the samples"""

    def __init__(self, name, filename):
        """Opens a new midi file with given string filename"""
        self._pattern = midi.read_midifile(filename)
        self.name = name
        self.file_path = filename

        if self._pattern.tick_relative is False:
            self._pattern.make_ticks_rel()

        self.bps = 120/60  # Get a default value, in case the midi Event is missing

        self.notes = self.get_notes()
        self.rel_notelist = None
        self.rel_poslist = None
        self.rel_durlist = None

        self.abs_notelist = None
        self.abs_poslist = None
        self.abs_durlist = None

    def save(self, path, filename=None):
        """Saves the midifile to filename"""
        if filename is not None:
            store_path = "{}/{}".format(path, filename)
        else:
            store_path = path

        midi.write_midifile(store_path, self._pattern)

    def randomize_timings(self, deviation=0.2, probability=1.0):
        """Randomly change all notes length, a note is changed with the given
        probability. The new length is gaussian distributed around the current length
        with given deviation"""
        for track in self._pattern:
            for msg in track:
                if isinstance(msg, (midi.NoteEvent, midi.NoteOnEvent, midi.NoteOffEvent)):
                    # Draw a sample from a binomial distribution, that is 0 or 1,
                    # if 1, change the note
                    if np.random.binomial(1, probability) == 1:
                        rnd = 1 + np.random.uniform(-deviation, deviation)
                        msg.tick = int(msg.tick * rnd)
        self.notes = self.get_notes()

    def alter_timings(self, change_factor, probability=1.0):
        """Change the timing of the track by change_factor. All durations get multiplied by this change_factor with
        a probability of <probability>"""
        for track in self._pattern:
            for idx, msg in enumerate(track):
                if isinstance(msg, (midi.NoteEvent, midi.NoteOnEvent, midi.NoteOffEvent)):
                    # Draw a sample from a binomial distribution, that is 0 or 1,
                    # if 1, change the note
                    if np.random.binomial(1, probability) == 1:
                        # Set both, the on and off event
                        msg.tick = int(msg.tick * change_factor)
        self.notes = self.get_notes()

    def randomize_notes(self, deviation=1, probability=1.0):
        """Shuffles all notes with probability, shift is made with a gaussion distribution with deviation around
        center=pitch"""
        for track in self._pattern:
            for idx, msg in enumerate(track):
                if isinstance(msg, midi.NoteOnEvent):
                    # Draw a sample from a binomial distribution, that is 0 or 1,
                    # if 1, change the note
                    if np.random.binomial(1, probability) == 1:
                        # Set both, the on and off event
                        off = self._get_note_off_event(msg.get_pitch(), track, idx)
                        rnd = np.random.normal(loc=0, scale=deviation)

                        if rnd < 0:
                            rnd = np.floor(rnd)
                        else:
                            rnd = np.ceil(rnd)

                        rnd = int(msg.get_pitch() + rnd)

                        rnd = max(0, min(127, rnd))

                        msg.set_pitch(rnd)
                        off.set_pitch(rnd)
        self.notes = self.get_notes()

    def shift_notes(self, shift_amount, probability=1.0):
        """Shifts all notes by shift_amount, but does so with a probability.
        on average every probability note gets changed"""
        for track in self._pattern:
            for idx, msg in enumerate(track):
                if isinstance(msg, midi.NoteOnEvent):
                    # Draw a sample from a binomial distribution, that is 0 or 1,
                    # if 1, change the note
                    if np.random.binomial(1, probability) == 1:
                        # Set both, the on and off event
                        off = self._get_note_off_event(msg.get_pitch(), track, idx)
                        msg.set_pitch(msg.get_pitch() + int(shift_amount))
                        off.set_pitch(off.get_pitch() + int(shift_amount))
        self.notes = self.get_notes()

    def remove_or_add_random_notes(self, add_probability, remove_probability, add_pitch_deviation=0.7,
                                   add_length_deviation=0.2):
        """For each note in the track, there is a probability (add_probability) of adding a note after it with
        a random value sampled from a gauss-distribution, coming from the note before.
        Additionally a note is removed with given probability (remove_probability)"""
        for track in self._pattern:
            idx = 0
            while True:
                if idx >= len(track):
                    break
                msg = track[idx]
                if isinstance(msg, midi.NoteOnEvent):
                    # Draw a sample from a binomial distribution, that is 0 or 1,
                    # if 1, add a new note
                    off_idx, off = self._get_note_off_event(msg.get_pitch(), track, idx, return_idx=True)
                    if np.random.binomial(1, add_probability) == 1:
                        # Add a noteon and noteoff event
                        rnd = 1 + np.random.uniform(-add_length_deviation, add_length_deviation)
                        length = int(abs(off.tick - msg.tick) * rnd)
                        pitch = int(round(np.random.normal(loc=msg.get_pitch(), scale=add_pitch_deviation)))
                        pitch = max(0, min(127, pitch))
                        on_event = midi.NoteOnEvent()
                        on_event.set_pitch(pitch)
                        on_event.set_velocity(msg.get_velocity())
                        off_event = midi.NoteOffEvent()
                        off_event.set_pitch(pitch)
                        off_event.set_velocity(off.get_velocity())
                        off_event.tick = length
                        idx = off_idx + 1
                        track.insert(idx, on_event)
                        idx += 1
                        track.insert(idx, off_event)
                        idx += 1
                    else:
                        idx += 1
                    if np.random.binomial(1, remove_probability) == 1:
                        track.remove(msg)
                        track.remove(off)
                    else:
                        idx += 1
                else:
                    idx += 1

        self.notes = self.get_notes()

    @staticmethod
    def _get_note_off_event(note, track, offset=0, return_idx=False):
        """Returns the next note_off event, matching note"""
        for idx in range(offset, len(track)):
            msg = track[idx]
            if isinstance(msg, midi.NoteOffEvent):
                if msg.get_pitch() == note:
                    if return_idx:
                        return idx, msg
                    else:
                        return msg

    def get_resolution(self):
        return self._pattern.resolution

    def get_time_signature(self):
        for track in self._pattern:
            for msg in track:
                if isinstance(msg, midi.TimeSignatureEvent):
                    return msg.get_numerator(), msg.get_denominator()
        return None

    def get_highest_note(self, track_number=0):
        notes, _, _ = self.get_notelist(track_number=track_number)
        return max(notes)

    def get_lowest_note(self, track_number=0):
        notes, _, _ = self.get_notelist(track_number=track_number)
        return min(notes)

    def truncate_ticks(self, start, end=-1):
        startpos = 0
        endpos = -1
        _, _, positions = self.get_notelist(0)
        lastpos = 0

        if end == -1:
            end = len(positions) + 1

        for idx, pos in enumerate(positions):
            if pos >= start > lastpos:
                startpos = idx

            if pos > end >= lastpos:
                endpos = idx
                break

            lastpos = pos

        self.truncate(startpos, endpos)

    def truncate(self, start, end=-1):
        """Truncates the midifile where start and end denotes number
        of notes from beginning. The new midisize is then end - start + 1 e.g.
        including end, start has to be < end"""
        note_count = 0
        track = self._pattern[0]
        idx = 0

        if end == -1:
            end = len(track) + 1

        while idx < len(track):
            msg = track[idx]
            if note_count > end and not isinstance(msg, midi.EndOfTrackEvent):
                if isinstance(msg, midi.NoteOnEvent):
                    off = self._get_note_off_event(msg.get_pitch(), track, idx)
                    track.remove(msg)
                    track.remove(off)
                elif not isinstance(msg, midi.NoteOffEvent):
                    track.remove(msg)
                else:
                    idx += 1
            elif isinstance(msg, midi.NoteOnEvent):
                if note_count < start:
                    off = self._get_note_off_event(msg.get_pitch(), track, idx)
                    track.remove(msg)
                    track.remove(off)
                else:
                    idx += 1
                note_count += 1
            else:
                idx += 1

        self.notes = self.get_notes()

    def get_notes(self):
        """Returns for each track a list of (note, duration)-pairs, where the pairs can
        be a list itself, if more then one notes plays simultaneously"""
        tracks = []

        self.rel_notelist = None
        self.rel_poslist = None
        self.rel_durlist = None

        self.abs_notelist = None
        self.abs_poslist = None
        self.abs_durlist = None

        for track in self._pattern:
            tr = []
            tracks.append(tr)
            pos = 0
            note_idx = 0

            for idx, msg in enumerate(track):

                if isinstance(msg, midi.SetTempoEvent):
                    self.bps = msg.bpm/60

                if isinstance(msg, midi.NoteOnEvent):
                    off = self._get_note_off_event(msg.get_pitch(), track, idx)

                    pos += msg.tick/(self._pattern.resolution*self.bps)
                    duration = off.tick/(self._pattern.resolution*self.bps)

                    tr.append((off.get_pitch(), duration, pos, note_idx))

                    note_idx += 1
                    pos += duration

        return tracks

    def get_notelist(self, track_number=0, note_representation=NoteRepresentation.ABSOLUTE,
                     duration_representation=DurationRepresentation.ABSOLUTE):
        """returns a list of notes and a list of durations, if more then one track is present,
        track_number selects the track. If several notes occur at the same time,
        the first one will be chosen.
        if relative=True, get_notelist returns not the absolute values of the notes,
        but their difference from the last note. Note that the first value is then simply representing
        the actual starting value.
        if updown=True, get_notelist returns only 1 for note going up, 0 if the note stays the same and
        -1 if the note is lower"""

        # ts = MeasureTime(True)

        # ts.timestamp("NL Start")
        if note_representation == NoteRepresentation.ABSOLUTE and self.abs_notelist is not None:
            return self.abs_notelist, self.abs_durlist, self.abs_poslist
        elif note_representation == NoteRepresentation.RELATIVE and self.rel_notelist is not None:
            return self.rel_notelist, self.rel_durlist, self.rel_poslist

        track = self.notes[track_number]
        notes = []
        durations = []
        positions = []
        lastpitch = 0

        for pitch, duration, pos, idx in track:
            if note_representation == NoteRepresentation.RELATIVE:
                p_diff = pitch - lastpitch
            elif note_representation == NoteRepresentation.UPDOWN:
                p_diff = max(-1, min(1, pitch - lastpitch))
            else:
                p_diff = pitch

            notes.append(p_diff)
            lastpitch = pitch
            durations.append(duration)
            positions.append(pos)

        if note_representation == NoteRepresentation.RELATIVE or note_representation == NoteRepresentation.UPDOWN:
            notes = notes[1:]
            positions = positions[1:]

        if note_representation == NoteRepresentation.ABSOLUTE:
            self.abs_notelist = notes
            self.abs_poslist = positions
            self.abs_durlist = durations
        elif note_representation == NoteRepresentation.RELATIVE:
            self.rel_notelist = notes
            self.rel_poslist = positions
            self.rel_durlist = durations

        return notes, durations, positions

    def get_bps_and_time_sig(self):
        track = self._pattern[0]
        bps = []
        time_sig = []
        pos = 0

        for idx, msg in enumerate(track):
            pos += msg.tick / (self._pattern.resolution * self.bps)

            if isinstance(msg, midi.SetTempoEvent):
                self.bps = msg.bpm/60
                bps.append((pos, self.bps))

            if isinstance(msg, midi.TimeSignatureEvent):
                time_sig.append((pos, (msg.get_numerator(), msg.get_denominator())))

        if len(bps) == 0:
            bps.append((0, self.bps))

        if len(time_sig) == 0:
            time_sig.append((0, (4, 4)))

        return bps, time_sig

    def get_nr_of_notes(self, track=0):
        return len(self.notes[track])

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name + "\n"

def main():
    pass


if __name__ == "__main__":
    main()

