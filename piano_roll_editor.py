"""
A piano roll viewer/editor

"""
from PyQt5 import QtGui, QtCore, QtWidgets
from midifile import MidiFile
import numpy as np
import os


class NoteItem(QtWidgets.QGraphicsRectItem):
    '''a note on the pianoroll sequencer'''

    def __init__(self, height, length, note_info):
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, length, height)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 100)))
        self.orig_brush = QtGui.QColor(100, 0, 0)
        self.hover_brush = QtGui.QColor(200, 200, 100)
        self.select_brush = QtGui.QColor(210, 190, 77)
        self.highlight_brush = QtGui.QColor(210, 190, 77)
        self.setBrush(self.orig_brush)

        self.length = length
        self.piano = self.scene

        (note_num, note_start, note_length, note_velocity) = note_info
        self.note_num = note_num
        self.note_start = note_start
        self.note_length = note_length
        self.note_velocity = note_velocity

        self.selected = False
        self.highlighted = False
        self.moving_diff = (0, 0)
        self.expand_diff = 0

    def set_selected(self, boolean):
        self.selected = boolean
        if boolean:
            self.setBrush(self.select_brush)
        else:
            self.setBrush(self.orig_brush)

    def set_highlighted(self, boolean):
        self.highlighted = boolean
        if boolean:
            self.setBrush(self.highlight_brush)
        else:
            self.set_selected(self.selected)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def moveEvent(self, event):
        pass


class PianoKeyItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, width, height, parent):
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, width, height, parent)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 80)))
        self.width = width
        self.height = height
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.hover_brush = QtGui.QColor(200, 0, 0)
        self.click_brush = QtGui.QColor(255, 100, 100)
        self.orig_brush = self.brush()
        self.pressed = False

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass


class PianoRoll(QtWidgets.QGraphicsScene):
    '''the piano roll'''

    def __init__(self, time_sig=(4, 4)):
        QtWidgets.QGraphicsScene.__init__(self)
        self.setBackgroundBrush(QtGui.QColor(50, 50, 50))
        self.mousePos = QtCore.QPointF()

        self.notes = []
        # self.selected_notes = []
        self.piano_keys = []

        ## dimensions
        self.padding = 2

        ## piano dimensions
        self.note_height = 10
        self.notes_in_octave = 12
        self.start_octave = 0
        self.end_octave = 0
        self.lowest_note = 0
        self.highest_note = 0
        self.total_notes = 0
        self.piano_height = 0
        self.octave_height = 0
        self.total_height = 0

        self.header_height = 20
        self.piano_width = 50

        self.set_note_limit(0, 127)

        ## width
        self.one_second_width = 50
        self.bps = [(0, 2)]
        self.snap_value = None
        # self.quantize_val = quantize_val

        ### dummy vars that will be changed
        self.time_sig = [(0, time_sig)]
        self.measures = []
        # self.num_measures = 0
        # self.max_note_length = 0
        self.grid_width = 0
        self.value_width = 0
        # self.grid_div = 0
        self.piano = None
        self.header = None
        self.play_head = None

        self.position_pen = QtGui.QPen(QtGui.QColor(255, 0, 0, 120))
        self.position_indicator = None
        self.create_position_indicator()

        self.reset_view()

    def create_position_indicator(self):
        self.position_indicator = QtWidgets.QGraphicsRectItem(0, 0, 1, self.piano_height +
                                                              self.header_height -
                                                              self.position_pen.width())
        self.position_indicator.setPen(self.position_pen)
        self.position_indicator.setPos(self.piano_width, 0.5 * self.position_pen.width())
        self.position_indicator.setVisible(False)
        self.addItem(self.position_indicator)

    def get_grid_width(self):
        sum = 0
        for width, _ in self.measures:
            sum += width

        return sum

    def set_note_limit(self, lowest, highest):
        self.note_height = 10
        self.lowest_note = lowest
        self.highest_note = highest
        self.start_octave = np.floor(lowest / self.notes_in_octave).astype(int) - 1
        self.end_octave = np.ceil(highest / self.notes_in_octave).astype(int) - 1
        self.total_notes = highest - lowest
        self.piano_height = self.note_height * (self.total_notes + 1)
        self.octave_height = self.notes_in_octave * self.note_height

        self.total_height = self.piano_height + self.header_height

    def get_measure(self, measure_pos):
        _, act_bps = self.bps[0]
        _, act_time_sig = self.time_sig[0]

        for pos, bps in self.bps:
            if measure_pos < pos:
                break
            act_bps = bps

        for pos, time_sig in self.time_sig:
            if measure_pos < pos:
                break
            act_time_sig = time_sig

        return self.one_second_width / act_bps * act_time_sig[0], act_time_sig[0]

    def setMeasures(self, measures):
        n_measures = self.get_num_measures()
        if measures == n_measures:
            return

        if measures < n_measures:
            self.measures = self.measures[0: measures]
        else:
            act_measure_pos = self.get_grid_width()
            for new_measure_num in range(int(n_measures), int(measures), 1):
                new_measure = self.get_measure(act_measure_pos / self.one_second_width)
                self.measures.append(new_measure)
                act_measure_pos += new_measure[0]

    def reset_view(self):
        self.notes.clear()
        self.set_note_limit(0, 127)
        self.setMeasures(0)
        self.setMeasures(10)
        self.refresh_scene()

    def get_num_measures(self):
        return len(self.measures)

    # -------------------------------------------------------------------------
    # Event Callbacks

    def keyPressEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    # -------------------------------------------------------------------------
    # Internal Functions

    def draw_header(self):
        self.header = QtWidgets.QGraphicsRectItem(0, 0, self.get_grid_width(), self.header_height)
        self.header.setPos(self.piano_width, 0)
        self.addItem(self.header)

    def draw_piano(self):
        piano_keys_width = self.piano_width - self.padding
        black_notes = (1, 3, 5, 8, 10)
        piano_label = QtGui.QFont()
        piano_label.setPointSize(6)
        self.piano = QtWidgets.QGraphicsRectItem(0, 0, piano_keys_width, self.piano_height)
        self.piano.setPos(0, self.header_height)
        self.addItem(self.piano)

        for i in range(int(self.highest_note), int(self.lowest_note - 1), -1):
            octave_note = i % self.notes_in_octave
            if octave_note in black_notes:
                key = PianoKeyItem(piano_keys_width * 0.5, self.note_height, self.piano)
                key.setBrush(QtGui.QColor(0, 0, 0))
                key.setZValue(1.0)
                key.setPos(0, self.note_height * (i - self.lowest_note))
            elif (octave_note - 1) in black_notes and (octave_note + 1) in black_notes:
                key = PianoKeyItem(piano_keys_width, self.note_height * 2, self.piano)
                key.setBrush(QtGui.QColor(255, 255, 255))
                key.setPos(0, self.note_height * (i - self.lowest_note) - self.note_height / 2.)
            elif (octave_note - 1) in black_notes:
                key = PianoKeyItem(piano_keys_width, self.note_height * 3. / 2, self.piano)
                key.setBrush(QtGui.QColor(255, 255, 255))
                key.setPos(0, self.note_height * (i - self.lowest_note) - self.note_height / 2.)
            elif (octave_note + 1) in black_notes:
                key = PianoKeyItem(piano_keys_width, self.note_height * 3. / 2, self.piano)
                key.setBrush(QtGui.QColor(255, 255, 255))
                key.setPos(0, self.note_height * (i - self.lowest_note))
            if octave_note == 11:
                label = QtWidgets.QGraphicsSimpleTextItem('C{}'.format(
                    int(self.highest_note / self.notes_in_octave) - int(i / self.notes_in_octave) + int(
                        self.lowest_note / self.notes_in_octave) - 1), key)
                label.setPos(self.piano_width - 20, 5)
                label.setFont(piano_label)

    def draw_grid(self):
        clearpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))

        for i in range(self.highest_note, self.lowest_note - 1, -1):
            scale_bar = QtWidgets.QGraphicsRectItem(0, 0, self.get_grid_width(), self.note_height, self.piano)
            scale_bar.setPos(self.piano_width, self.note_height * (i - self.lowest_note))
            scale_bar.setPen(clearpen)
            if i % 2 == 0:
                scale_bar.setBrush(QtGui.QColor(120, 120, 120))
            else:
                scale_bar.setBrush(QtGui.QColor(100, 100, 100))

        measure_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 120), 3)
        line_pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 40))

        sum_pos = 0
        for i in range(0, int(self.get_num_measures()) + 1):
            measure = QtWidgets.QGraphicsLineItem(0, 0, 0, self.piano_height + self.header_height - measure_pen.width(),
                                                  self.header)
            measure.setPos(sum_pos, 0.5 * measure_pen.width())
            measure.setPen(measure_pen)

            if i < self.get_num_measures():
                n_string = '%d' % (i + 1)
                number = QtWidgets.QGraphicsSimpleTextItem(n_string, self.header)
                n_width = QtGui.QFontMetrics(self.font()).width(n_string)
                number.setPos(sum_pos + self.measures[i][0] / 2 - n_width / 2, 2)
                number.setBrush(QtCore.Qt.white)
                for j in range(int(self.measures[i][1])):
                    line = QtWidgets.QGraphicsLineItem(0, 0, 0, self.piano_height, self.header)
                    line.setZValue(1.0)
                    line.setPos(sum_pos + self.measures[i][0] / self.measures[i][1] * j, self.header_height)
                    line.setPen(line_pen)

                sum_pos += self.measures[i][0]

    def draw_play_head(self):
        self.play_head = QtWidgets.QGraphicsLineItem(self.piano_width, self.header_height, self.piano_width,
                                                     self.total_height)
        self.play_head.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 50), 2))
        self.play_head.setZValue(1.)
        self.addItem(self.play_head)

    def refresh_scene(self):
        self.piano_keys = []
        self.clear()
        self.draw_piano()
        self.draw_header()
        self.draw_grid()
        self.draw_play_head()

        self.create_position_indicator()
        if self.views():
            self.views()[0].setSceneRect(self.itemsBoundingRect())

    def clear_drawn_items(self):
        self.clear()
        self.draw_piano()
        self.draw_header()
        self.draw_grid()

    def draw_note(self, note_num, note_start=None, note_length=None, note_velocity=None, add=True,
                  pos_scale=1.0, length_scale=1.0):
        """
        note_num: midi number, 0 - 127
        note_start: 0 - (num_measures * time_sig[0])
        note_length: 0 - (num_measures  * time_sig[0]/time_sig[1])
        note_velocity: 0 - 127
        """

        note_start *= pos_scale
        note_length *= length_scale

        info = (note_num, note_start, note_length, note_velocity)

        if note_start * self.one_second_width >= self.get_grid_width():
            while note_start * self.one_second_width >= self.get_grid_width():
                self.setMeasures(self.get_num_measures() + 1)
            self.refresh_scene()

        x_start = self.get_note_x_start(note_start)
        x_length = self.get_note_x_length(note_length)
        y_pos = self.get_note_y_pos(note_num)

        note = NoteItem(self.note_height, x_length, info)
        note.setPos(x_start, y_pos)

        self.notes.append(note)
        if add:
            self.addItem(note)
        return note

    def get_note_x_start(self, note_start):
        return self.piano_width + self.one_second_width * note_start

    def get_note_x_length(self, note_length):
        return float(note_length * self.one_second_width)

    def get_note_y_pos(self, note_num):
        return self.header_height + self.note_height * (self.highest_note - note_num - 1)


class PianoRollView(QtWidgets.QGraphicsView):
    def __init__(self, time_sig=(4, 4)):
        QtWidgets.QGraphicsView.__init__(self)
        self.piano = PianoRoll(time_sig)
        self.setScene(self.piano)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        x = 0 * self.sceneRect().width() + self.sceneRect().left()
        y = 0.4 * self.sceneRect().height() + self.sceneRect().top()
        self.centerOn(x, y)

        self.setAlignment(QtCore.Qt.AlignLeft)
        self.o_transform = self.transform()


class PianoWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        super(PianoWidget, self).__init__(*args)

        self.view = PianoRollView(
            time_sig=(4, 4))

        self.piano = self.view.piano

        self.midifile = None
        self.select = -1
        self.play_mode = False
        self.padding = 5

        self.viewBox = QtWidgets.QHBoxLayout()
        self.viewBox.addWidget(self.view)
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addLayout(self.viewBox)

        self.setLayout(self.layout)
        self.resize(500, 500)
        self.view.setFocus()

    def draw_midi_file(self, mf, select=None, set_y_to_default=True):
        if isinstance(mf, str):
            queryname = os.path.basename(mf)
            self.midifile = MidiFile(queryname, mf)
        elif isinstance(mf, MidiFile):
            self.midifile = mf
        else:
            self.reset_view()
            return

        self.select = select

        self.piano.notes.clear()

        if isinstance(select, int):
            select_from = select
            select_to = select
        elif isinstance(select, tuple):
            select_from = select[0]
            if len(select) == 1:
                select_to = select[0]
            else:
                select_to = select[1]
        else:
            select_from = -1
            select_to = -1

        notes, durations, positions = self.midifile.get_notelist()
        highest_note = self.midifile.get_highest_note()
        lowest_note = self.midifile.get_lowest_note()
        bps, time_sig = self.midifile.get_bps_and_time_sig()

        padding = self.padding
        max_notes_in_window = int(
            (self.view.viewport().height() - self.piano.header_height) / self.piano.note_height) - 1
        if highest_note - lowest_note + padding * 2 < max_notes_in_window:
            padding = int((max_notes_in_window - (highest_note - lowest_note)) / 2)

        self.piano.set_note_limit(max(0, lowest_note - padding), min(127, highest_note + padding))

        self.piano.setMeasures(0)

        self.piano.time_sig = time_sig
        self.piano.bps = bps

        selected_ysum = 0
        selected_cnt = 0
        ysum = 0
        cnt = 0
        for idx in reversed(range(len(notes))):
            note = self.piano.draw_note(notes[idx], positions[idx], durations[idx])
            ysum += note.y()
            cnt += 1
            if select_from <= positions[idx] <= select_to:
                note.set_selected(True)
                selected_ysum += note.y()
                selected_cnt += 1

        if set_y_to_default:
            if select is None:
                self.view.centerOn(0, ysum/cnt)
            else:
                self.view.centerOn(0, selected_ysum/selected_cnt)

        self.piano.position_indicator.setVisible(True)

    def reset_view(self):
        self.midifile = None
        self.piano.reset_view()

    def set_width_scale(self, new_scale):
        self.piano.one_second_width = new_scale

        if self.midifile is not None:
            self.draw_midi_file(self.midifile, self.select)
        else:
            self.piano.setMeasures(0)
            self.piano.setMeasures(10)
            self.piano.refresh_scene()

    def set_play_style(self, enadisable: bool):
        if not enadisable:
            self.position_bar(False)
            self.piano.position_indicator.setVisible(False)

        self.play_mode = enadisable

    def position_bar(self, pos, autoscroll=True):
        if self.midifile is not None:
            pixel_pos = pos * self.piano.one_second_width
            visible_rect = self.view.mapToScene(self.view.viewport().geometry()).boundingRect()
            xpos = pixel_pos + self.view.viewport().width() * 0.2
            ymid = visible_rect.y() + (visible_rect.height() / 2) - 1
            new_y_center = ymid

            for note in self.piano.notes:
                if isinstance(note, NoteItem):
                    if note.note_start <= pos < note.note_start + note.note_length:
                        if autoscroll:
                            if note.y() - self.piano.note_height < visible_rect.y():
                                new_y_center = ymid - (visible_rect.y() - note.y() + self.piano.note_height)
                            elif visible_rect.y() + visible_rect.height() < note.y() + self.piano.note_height*2:
                                new_y_center = ymid + (note.y() - visible_rect.y() - visible_rect.height() + self.piano.note_height*2)

            if autoscroll:
                self.view.centerOn(xpos, new_y_center)

            self.piano.position_indicator.setVisible(True)
            self.piano.position_indicator.setPos(pixel_pos + self.piano.piano_width, 0.5 * self.piano.position_pen.width())


if __name__ == '__main__':
    import sys

    midifile = MidiFile("ashover1.mid", "./small_db/ashover1.mid")
    print(midifile)
    app = QtWidgets.QApplication(sys.argv)

    main = PianoWidget()
    main.show()
    # main.piano.drawNote(71, 0, 0.50, 20)
    # main.piano.drawNote(73, 1, 0.50, 20)
    # note = main.piano.drawNote(76, 2, 0.50, 20)
    # note.setSelected(True)
    # main.piano.drawNote(77, 3, 0.50, 20)
    # note = main.piano.drawNote(10, 4, 0.50, 20)
    # note = main.piano.drawNote(50, 5, 0.50, 20)
    # note = main.piano.drawNote(50, 6, 0.50, 20)
    # note = main.piano.drawNote(50, 7, 0.50, 20)
    # note = main.piano.drawNote(50, 8, 0.50, 20)
    # note = main.piano.drawNote(50, 9, 0.50, 20)
    # note = main.piano.drawNote(50, 10, 0.50, 20)
    # note = main.piano.drawNote(50, 11, 0.50, 20)
    # note = main.piano.drawNote(77, 20, 0.50, 20)
    main.draw_midi_file(midifile, (5, 9))
    # note.setSelected(True)
    # note.setFocus()
    # main.view.centerOn(note.x(), note.y())

    # import time
    # time.sleep(5)
    main.set_width_scale(20)
    sys.exit(app.exec_())
