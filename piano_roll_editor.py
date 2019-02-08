"""
A piano roll viewer/editor

"""
from PyQt5 import QtGui, QtCore, QtWidgets
from midifile import MidiFile
import numpy as np

# class NoteExpander(QtWidgets.QGraphicsRectItem):
#     def __init__(self, length, height, parent):
#         QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, length, height, parent)
#         self.parent = parent
#         self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
#         self.setAcceptHoverEvents(True)
#
#         clearpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
#         self.setPen(clearpen)
#
#         self.orig_brush = QtGui.QColor(0, 0, 0, 0)
#         self.hover_brush = QtGui.QColor(200, 200, 200)
#         self.stretch = False
#
#     def mousePressEvent(self, event):
#         QtWidgets.QGraphicsRectItem.mousePressEvent(self, event)
#         self.stretch = True
#
#     def hoverEnterEvent(self, event):
#         QtWidgets.QGraphicsRectItem.hoverEnterEvent(self, event)
#         if self.parent.isSelected():
#             self.parent.setBrush(self.parent.select_brush)
#         else:
#             self.parent.setBrush(self.parent.orig_brush)
#         self.setBrush(self.hover_brush)
#
#     def hoverLeaveEvent(self, event):
#         QtWidgets.QGraphicsRectItem.hoverLeaveEvent(self, event)
#         if self.parent.isSelected():
#             self.parent.setBrush(self.parent.select_brush)
#         elif self.parent.hovering:
#             self.parent.setBrush(self.parent.hover_brush)
#         else:
#             self.parent.setBrush(self.parent.orig_brush)
#         self.setBrush(self.orig_brush)


class NoteItem(QtWidgets.QGraphicsRectItem):
    '''a note on the pianoroll sequencer'''

    def __init__(self, height, length, note_info):
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, length, height)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        self.orig_brush = QtGui.QColor(100, 0, 0)
        self.hover_brush = QtGui.QColor(200, 200, 100)
        self.select_brush = QtGui.QColor(150, 50, 50)
        self.setBrush(self.orig_brush)

        self.note = note_info
        self.length = length
        self.piano = self.scene

        self.pressed = False
        self.hovering = False
        self.moving_diff = (0, 0)
        self.expand_diff = 0

        # l = 5
        # self.front = NoteExpander(l, height, self)
        # self.back = NoteExpander(l, height, self)
        # self.back.setPos(length - l, 0)

    def setSelected(self, boolean):
        # QtWidgets.QGraphicsRectItem.setSelected(self, boolean)
        if boolean:
            self.setBrush(self.select_brush)
        else:
            self.setBrush(self.orig_brush)

    # def hoverEnterEvent(self, event):
    #     self.hovering = True
    #     QtWidgets.QGraphicsRectItem.hoverEnterEvent(self, event)
    #     if not self.isSelected():
    #         self.setBrush(self.hover_brush)

    # def hoverLeaveEvent(self, event):
    #     self.hovering = False
    #     QtWidgets.QGraphicsRectItem.hoverLeaveEvent(self, event)
    #     if not self.isSelected():
    #         self.setBrush(self.orig_brush)
    #     elif self.isSelected():
    #         self.setBrush(self.select_brush)

    def mousePressEvent(self, event):
        pass
    #     QtWidgets.QGraphicsRectItem.mousePressEvent(self, event)
    #     self.setSelected(True)
    #     self.pressed = True

    def mouseMoveEvent(self, event):
        pass

    def moveEvent(self, event):
        pass
    #     offset = event.scenePos() - event.lastScenePos()
    #
    #     if self.back.stretch:
    #         self.expand(self.back, offset)
    #     else:
    #         move_pos = self.scenePos() + offset + QtCore.QPointF(self.moving_diff[0], self.moving_diff[1])
    #         pos = self.piano().enforce_bounds(move_pos)
    #         pos_x, pos_y = pos.x(), pos.y()
    #         pos_sx, pos_sy = self.piano().snap(pos_x, pos_y)
    #         self.moving_diff = (pos_x - pos_sx, pos_y - pos_sy)
    #         if self.front.stretch:
    #             right = self.rect().right() - offset.x() + self.expand_diff
    #             if (self.scenePos().x() == self.piano().piano_width and offset.x() < 0) \
    #                     or right < 10:
    #                 self.expand_diff = 0
    #                 return
    #             self.expand(self.front, offset)
    #             self.setPos(pos_sx, self.scenePos().y())
    #         else:
    #             self.setPos(pos_sx, pos_sy)

    # def expand(self, rectItem, offset):
    #     rect = self.rect()
    #     right = rect.right() + self.expand_diff
    #     if rectItem == self.back:
    #         right += offset.x()
    #         if right > self.piano().grid_width:
    #             right = self.piano().grid_width
    #         elif right < 10:
    #             right = 10
    #         new_x = self.piano().snap(right, piano_width=0)
    #     else:
    #         right -= offset.x()
    #         new_x = self.piano().snap(right, piano_width=0)
    #     # if self.piano().snap_value:
    #     #     new_x -= 2.75  # where does this number come from?!
    #     self.expand_diff = right - new_x
    #     self.back.setPos(new_x - 5, 0)
    #     rect.setRight(new_x)
    #     self.setRect(rect)

    # def updateNoteInfo(self, pos_x, pos_y):
    #     self.note[0] = self.piano().get_note_num_from_y(pos_y)
    #     self.note[1] = self.piano().get_note_start_from_x(pos_x)
    #     self.note[2] = self.piano().get_note_length_from_x(
    #         self.rect().right() - self.rect().left())
    #     print("note: {}".format(self.note))

    # def mouseReleaseEvent(self, event):
    #     QtWidgets.QGraphicsRectItem.mouseReleaseEvent(self, event)
    #     self.pressed = False
    #     if event.button() == QtCore.Qt.LeftButton:
    #         self.moving_diff = (0, 0)
    #         self.expand_diff = 0
    #         self.back.stretch = False
    #         self.front.stretch = False
    #         (pos_x, pos_y,) = self.piano().snap(self.pos().x(), self.pos().y())
    #         self.setPos(pos_x, pos_y)
    #         self.updateNoteInfo(pos_x, pos_y)

    # def updateVelocity(self, event):
    #     offset = event.scenePos().x() - event.lastScenePos().x()
    #     self.note[3] += int(offset / 5)
    #     if self.note[3] > 127:
    #         self.note[3] = 127
    #     elif self.note[3] < 0:
    #         self.note[3] = 0
    #     print("new vel: {}".format(self.note[3]))
    #     self.orig_brush = QtGui.QColor(self.note[3], 0, 0)
    #     self.select_brush = QtGui.QColor(self.note[3] + 100, 100, 100)
    #     self.setBrush(self.orig_brush)


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

    # def hoverEnterEvent(self, event):
    #     QtWidgets.QGraphicsRectItem.hoverEnterEvent(self, event)
    #     self.orig_brush = self.brush()
    #     self.setBrush(self.hover_brush)

    # def hoverLeaveEvent(self, event):
    #     if self.pressed:
    #         self.pressed = False
    #         self.setBrush(self.hover_brush)
    #         QtWidgets.QGraphicsRectItem.hoverLeaveEvent(self, event)
    #     self.setBrush(self.orig_brush)

    def mousePressEvent(self, event):
        pass
    #    self.pressed = True
    #    self.setBrush(self.click_brush)

    def mouseMoveEvent(self, event):
        pass
    #     """this may eventually do something"""
    #     pass

    def mouseReleaseEvent(self, event):
        pass
    #     self.pressed = False
    #     QtWidgets.QGraphicsRectItem.mouseReleaseEvent(self, event)
    #     self.setBrush(self.hover_brush)


class PianoRoll(QtWidgets.QGraphicsScene):
    '''the piano roll'''

    # measureupdate = QtCore.pyqtSignal(int)
    # modeupdate = QtCore.pyqtSignal(str)

    def __init__(self, time_sig=(4, 4)):
        QtWidgets.QGraphicsScene.__init__(self)
        self.setBackgroundBrush(QtGui.QColor(50, 50, 50))
        self.mousePos = QtCore.QPointF()

        # self.notes = []
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

        # self.setTimeSig([(0, time_sig)])
        # self.refreshScene()
        # self.setMeasures(num_measures)
        # self.setQuantize(quantize_val)
        # self.setGridDiv()
        # self.default_length = 1. / self.grid_div

        self.setMeasures(10)
        self.refreshScene()

        self.midifile = None
        self.select = -1

    # -------------------------------------------------------------------------
    # Callbacks

    # def genTransport(self, pos):
    #     print(pos)
    #     bar, pos = pos / (1920 * int(self.act_time_sig[0])), pos % (1920 * int(self.act_time_sig[0]))
    #     beat, tick = pos / 1920, pos % 1920
    #     print("{} | {} | {}".format(bar, beat, tick))
    #     transport_info = {
    #         "bar": bar,
    #         "beat": beat,
    #         "tick": tick,
    #     }
    #     self.movePlayHead(transport_info)
    #
    # def movePlayHead(self, t):
    #     total_duration = 1920 * self.act_time_sig[0] * self.num_measures
    #     pos = t['bar'] * 1920 * self.act_time_sig[0] + t['beat'] * 1920 + t['tick']
    #     frac = (pos % total_duration) / total_duration
    #     self.play_head.setPos(QtCore.QPointF(frac * self.grid_width, 0))

    # def setTimeSig(self, time_sig):
    #     try:
    #         new_time_sig = time_sig[0][1]
    #         if len(new_time_sig) == 2:
    #             self.act_time_sig = new_time_sig
    #
    #             self.measure_width = self.one_second_width / self.bps[0][1] * self.act_time_sig[0]
    #             # self.max_note_length = self.num_measures * self.act_time_sig[0] / self.act_time_sig[1]
    #             self.grid_width = self.measure_width * self.num_measures
    #             self.value_width = self.measure_width / self.act_time_sig[0]
    #             self.refreshScene()
    #     except ValueError:
    #         pass

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
            # self.max_note_length = self.num_measures * self.act_time_sig[0] / self.act_time_sig[1]
            # self.refreshScene()
        else:
            act_measure_pos = self.get_grid_width()
            for new_measure_num in range(int(n_measures), int(measures), 1):
                new_measure = self.get_measure(act_measure_pos / self.one_second_width)
                self.measures.append(new_measure)
                act_measure_pos += new_measure[0]
        # self.num_measures = measures

    def get_num_measures(self):
        return len(self.measures)

    # def setDefaultLength(self, length):
    #     try:
    #         v = list(map(float, length.split('/')))
    #         if len(v) < 3:
    #             self.default_length = \
    #                 v[0] if len(v) == 1 else \
    #                     v[0] / v[1]
    #             pos = self.enforce_bounds(self.mousePos)
    #             # if self.insert_mode: self.makeGhostNote(pos.x(), pos.y())
    #     except ValueError:
    #         pass

    # def setGridDiv(self, div=None):
    #     self.grid_div = 4
    #     self.value_width = self.full_note_width / float(self.grid_div)
    #     self.refreshScene()

        # if not div:
        #     div = self.quantize_val
        # try:
        #     val = list(map(int, div.split('/')))
        #     if len(val) < 3:
        #         self.quantize_val = div
        #         if len(val) == 1:
        #             self.grid_div = val[0]
        #         else:
        #             self.grid_div = val[1]
        #         self.value_width = self.full_note_width / float(self.grid_div) if self.grid_div else None
        #         self.setQuantize(div)
        #
        #         self.refreshScene()
        # except ValueError:
        #     pass

    # def setQuantize(self, value):
    #     try:
    #         val = list(map(float, value.split('/')))
    #         if len(val) == 1:
    #             self.quantize(val[0])
    #             # self.quantize_val = value
    #         elif len(val) == 2:
    #             self.quantize(val[0] / val[1])
    #             # self.quantize_val = value
    #     except ValueError:
    #         pass

    # -------------------------------------------------------------------------
    # Event Callbacks

    def keyPressEvent(self, event):
        pass
        # QtWidgets.QGraphicsScene.keyPressEvent(self, event)
        # if event.key() == QtCore.Qt.Key_B:
        #     if not self.insert_mode:
        #         self.velocity_mode = False
        #         self.insert_mode = True
        #         self.makeGhostNote(self.mousePos.x(), self.mousePos.y())
        #     elif self.insert_mode:
        #         self.insert_mode = False
        #         if self.place_ghost: self.place_ghost = False
        #         self.removeItem(self.ghost_note)
        #         self.ghost_note = None
        # elif event.key() == QtCore.Qt.Key_D:
        #     if self.velocity_mode:
        #         self.velocity_mode = False
        #     else:
        #         if self.insert_mode:
        #             self.removeItem(self.ghost_note)
        #         self.ghost_note = None
        #         self.insert_mode = False
        #         self.place_ghost = False
        #         self.velocity_mode = True
        # elif event.key() == QtCore.Qt.Key_A:
        #     if all((note.isSelected() for note in self.notes)):
        #         for note in self.notes:
        #             note.setSelected(False)
        #         self.selected_notes = []
        #     else:
        #         for note in self.notes:
        #             note.setSelected(True)
        #         self.selected_notes = self.notes[:]
        # elif event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
        #     self.notes = [note for note in self.notes if note not in self.selected_notes]
        #     for note in self.selected_notes:
        #         self.removeItem(note)
        #         del note
        #     self.selected_notes = []

    def mousePressEvent(self, event):
        pass
        # QtWidgets.QGraphicsScene.mousePressEvent(self, event)
        # if not (any(key.pressed for key in self.piano_keys)
        #         or any(note.pressed for note in self.notes)):
        #     for note in self.selected_notes:
        #         note.setSelected(False)
        #     self.selected_notes = []
        #
        #     if event.button() == QtCore.Qt.LeftButton:
        #         if self.insert_mode:
        #             self.place_ghost = True
        #         else:
        #             self.marquee_select = True
        #             self.marquee_rect = QtCore.QRectF(event.scenePos().x(), event.scenePos().y(), 1, 1)
        #             self.marquee = QtWidgets.QGraphicsRectItem(self.marquee_rect)
        #             self.marquee.setBrush(QtGui.QColor(255, 255, 255, 100))
        #             self.addItem(self.marquee)
        # else:
        #     for s_note in self.notes:
        #         if s_note.pressed and s_note in self.selected_notes:
        #             break
        #         elif s_note.pressed and s_note not in self.selected_notes:
        #             for note in self.selected_notes:
        #                 note.setSelected(False)
        #             self.selected_notes = [s_note]
        #             break
        #     for note in self.selected_notes:
        #         if not self.velocity_mode:
        #             note.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pass
        # QtWidgets.QGraphicsScene.mouseMoveEvent(self, event)
        # self.mousePos = event.scenePos()
        # if not (any((key.pressed for key in self.piano_keys))):
        #     m_pos = event.scenePos()
        #     if self.insert_mode and self.place_ghost:  # placing a note
        #         m_width = self.ghost_rect.x() + self.ghost_rect_orig_width
        #         if m_pos.x() > m_width:
        #             m_new_x = self.snap(m_pos.x())
        #             self.ghost_rect.setRight(m_new_x)
        #             self.ghost_note.setRect(self.ghost_rect)
        #         # self.adjust_note_vel(event)
        #     else:
        #         m_pos = self.enforce_bounds(m_pos)
        #
        #         if self.insert_mode:  # ghostnote follows mouse around
        #             (m_new_x, m_new_y) = self.snap(m_pos.x(), m_pos.y())
        #             self.ghost_rect.moveTo(m_new_x, m_new_y)
        #             try:
        #                 self.ghost_note.setRect(self.ghost_rect)
        #             except RuntimeError:
        #                 self.ghost_note = None
        #                 self.makeGhostNote(m_new_x, m_new_y)
        #
        #         elif self.marquee_select:
        #             marquee_orig_pos = event.buttonDownScenePos(QtCore.Qt.LeftButton)
        #             if marquee_orig_pos.x() < m_pos.x() and marquee_orig_pos.y() < m_pos.y():
        #                 self.marquee_rect.setBottomRight(m_pos)
        #             elif marquee_orig_pos.x() < m_pos.x() and marquee_orig_pos.y() > m_pos.y():
        #                 self.marquee_rect.setTopRight(m_pos)
        #             elif marquee_orig_pos.x() > m_pos.x() and marquee_orig_pos.y() < m_pos.y():
        #                 self.marquee_rect.setBottomLeft(m_pos)
        #             elif marquee_orig_pos.x() > m_pos.x() and marquee_orig_pos.y() > m_pos.y():
        #                 self.marquee_rect.setTopLeft(m_pos)
        #             self.marquee.setRect(self.marquee_rect)
        #             self.selected_notes = []
        #             for item in self.collidingItems(self.marquee):
        #                 if item in self.notes:
        #                     self.selected_notes.append(item)
        #
        #             for note in self.notes:
        #                 if note in self.selected_notes:
        #                     note.setSelected(True)
        #                 else:
        #                     note.setSelected(False)
        #
        #         elif self.velocity_mode:
        #             if QtCore.Qt.LeftButton == event.buttons():
        #                 for note in self.selected_notes:
        #                     note.updateVelocity(event)
        #
        #         elif not self.marquee_select:  # move selected
        #             if QtCore.Qt.LeftButton == event.buttons():
        #                 x = y = False
        #                 if any(note.back.stretch for note in self.selected_notes):
        #                     x = True
        #                 elif any(note.front.stretch for note in self.selected_notes):
        #                     y = True
        #                 for note in self.selected_notes:
        #                     note.back.stretch = x
        #                     note.front.stretch = y
        #                     note.moveEvent(event)

    def mouseReleaseEvent(self, event):
        pass
        # if not (any((key.pressed for key in self.piano_keys)) or any((note.pressed for note in self.notes))):
        #     if event.button() == QtCore.Qt.LeftButton:
        #         if self.place_ghost and self.insert_mode:
        #             self.place_ghost = False
        #             note_start = self.get_note_start_from_x(self.ghost_rect.x())
        #             note_num = self.get_note_num_from_y(self.ghost_rect.y())
        #             note_length = self.get_note_length_from_x(self.ghost_rect.width())
        #             self.drawNote(note_num, note_start, note_length, self.ghost_vel)
        #             self.makeGhostNote(self.mousePos.x(), self.mousePos.y())
        #         elif self.marquee_select:
        #             self.marquee_select = False
        #             self.removeItem(self.marquee)
        # elif not self.marquee_select:
        #     for note in self.selected_notes:
        #         note.mouseReleaseEvent(event)
        #         if self.velocity_mode:
        #             note.setSelected(True)

    # -------------------------------------------------------------------------
    # Internal Functions

    def drawHeader(self):
        self.header = QtWidgets.QGraphicsRectItem(0, 0, self.get_grid_width(), self.header_height)
        # self.header.setZValue(1.0)
        self.header.setPos(self.piano_width, 0)
        self.addItem(self.header)

    def drawPiano(self):
        piano_keys_width = self.piano_width - self.padding
        black_notes = (1, 3, 5, 8, 10)
        # black_notes = (2, 4, 6, 9, 11)
        piano_label = QtGui.QFont()
        piano_label.setPointSize(6)
        self.piano = QtWidgets.QGraphicsRectItem(0, 0, piano_keys_width, self.piano_height)
        self.piano.setPos(0, self.header_height)
        self.addItem(self.piano)

        # key = PianoKeyItem(piano_keys_width, self.note_height, self.piano)
        # label = QtWidgets.QGraphicsSimpleTextItem('C8', key)
        # label.setPos(18, 1)
        # label.setFont(piano_label)
        # key.setBrush(QtGui.QColor(255, 255, 255))

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
                label = QtWidgets.QGraphicsSimpleTextItem('C{}'.format(int(self.highest_note / self.notes_in_octave) - int(i / self.notes_in_octave) + int(self.lowest_note / self.notes_in_octave) - 1), key)
                label.setPos(self.piano_width - 20, 5)
                label.setFont(piano_label)
            # self.piano_keys.append(key)

        # for i in range(self.end_octave - self.start_octave, self.start_octave - self.start_octave, -1):
        #     for j in range(self.notes_in_octave, 0, -1):
        #         if j in black_notes:
        #             key = PianoKeyItem(piano_keys_width / 1.4, self.note_height, self.piano)
        #             key.setBrush(QtGui.QColor(0, 0, 0))
        #             key.setZValue(1.0)
        #             key.setPos(0, self.note_height * j + self.octave_height * (i - 1))
        #         elif (j - 1) and (j + 1) in black_notes:
        #             key = PianoKeyItem(piano_keys_width, self.note_height * 2, self.piano)
        #             key.setBrush(QtGui.QColor(255, 255, 255))
        #             key.setPos(0, self.note_height * j + self.octave_height * (i - 1) - self.note_height / 2.)
        #         elif (j - 1) in black_notes:
        #             key = PianoKeyItem(piano_keys_width, self.note_height * 3. / 2, self.piano)
        #             key.setBrush(QtGui.QColor(255, 255, 255))
        #             key.setPos(0, self.note_height * j + self.octave_height * (i - 1) - self.note_height / 2.)
        #         elif (j + 1) in black_notes:
        #             key = PianoKeyItem(piano_keys_width, self.note_height * 3. / 2, self.piano)
        #             key.setBrush(QtGui.QColor(255, 255, 255))
        #             key.setPos(0, self.note_height * j + self.octave_height * (i - 1))
        #         if j == 12:
        #             label = QtWidgets.QGraphicsSimpleTextItem('{}{}'.format('C', self.end_octave - i), key)
        #             label.setPos(18, 6)
        #             label.setFont(piano_label)
        #         self.piano_keys.append(key)

    def drawGrid(self):
        # scale_bar = QtWidgets.QGraphicsRectItem(0, 0, self.get_grid_width(), self.note_height, self.piano)
        # scale_bar.setPos(self.piano_width, 0)
        # scale_bar.setBrush(QtGui.QColor(120, 120, 120))
        clearpen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))

        for i in range(self.highest_note, self.lowest_note-1, -1):
            scale_bar = QtWidgets.QGraphicsRectItem(0, 0, self.get_grid_width(), self.note_height, self.piano)
            scale_bar.setPos(self.piano_width, self.note_height * (i - self.lowest_note))
            scale_bar.setPen(clearpen)
            if i % 2 == 0:
                scale_bar.setBrush(QtGui.QColor(120, 120, 120))
            else:
                scale_bar.setBrush(QtGui.QColor(100, 100, 100))


        # for i in range(self.end_octave - self.start_octave, self.start_octave - self.start_octave, -1):
        #     for j in range(self.notes_in_octave, 0, -1):
        #         scale_bar = QtWidgets.QGraphicsRectItem(0, 0, self.get_grid_width(), self.note_height, self.piano)
        #         scale_bar.setPos(self.piano_width, self.note_height * j + self.octave_height * (i - 1))
        #         scale_bar.setPen(clearpen)
        #         if j % 2 == 0:
        #             scale_bar.setBrush(QtGui.QColor(120, 120, 120))
        #         else:
        #             scale_bar.setBrush(QtGui.QColor(100, 100, 100))

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
                number.setPos(sum_pos + self.measures[i][0]/2 - n_width/2, 2)
                number.setBrush(QtCore.Qt.white)
                for j in range(int(self.measures[i][1])):
                    line = QtWidgets.QGraphicsLineItem(0, 0, 0, self.piano_height, self.header)
                    line.setZValue(1.0)
                    line.setPos(sum_pos + self.measures[i][0] / self.measures[i][1] * j, self.header_height)
                    line.setPen(line_pen)

                sum_pos += self.measures[i][0]

        # for i in range(0, int(self.num_measures) + 1):
        #     measure = QtWidgets.QGraphicsLineItem(0, 0, 0, self.piano_height + self.header_height - measure_pen.width(),
        #                                           self.header)
        #     measure.setPos(self.measure_width * i, 0.5 * measure_pen.width())
        #     measure.setPen(measure_pen)
        #     if i < self.num_measures:
        #         number = QtWidgets.QGraphicsSimpleTextItem('%d' % (i + 1), self.header)
        #         number.setPos(self.measure_width * i + 5, 2)
        #         number.setBrush(QtCore.Qt.white)
        #         for j in range(int(self.act_time_sig[0])):
        #             line = QtWidgets.QGraphicsLineItem(0, 0, 0, self.piano_height, self.header)
        #             line.setZValue(1.0)
        #             line.setPos(self.measure_width * i + self.value_width * j, self.header_height)
        #             line.setPen(line_pen)

    def drawPlayHead(self):
        self.play_head = QtWidgets.QGraphicsLineItem(self.piano_width, self.header_height, self.piano_width,
                                                     self.total_height)
        self.play_head.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 50), 2))
        self.play_head.setZValue(1.)
        self.addItem(self.play_head)

    def refreshScene(self):
        # map(self.removeItem, self.notes)
        # self.selected_notes = []
        self.piano_keys = []
        self.clear()
        self.drawPiano()
        self.drawHeader()
        self.drawGrid()
        self.drawPlayHead()
        # for note in self.notes[:]:
        #     if note.note[1] >= (self.num_measures * self.time_sig[0]):
        #         self.notes.remove(note)
            # elif note.note[2] > self.max_note_length:
            #     new_note = note.note
            #     self.notes.remove(note)
            #     self.drawNote(new_note[0], new_note[1], self.max_note_length, new_note[3], False)
        # map(self.addItem, self.notes)
        if self.views():
            self.views()[0].setSceneRect(self.itemsBoundingRect())

    def clearDrawnItems(self):
        self.clear()
        # self.notes = []
        # self.selected_notes = []
        self.drawPiano()
        self.drawHeader()
        self.drawGrid()

    # def makeGhostNote(self, pos_x, pos_y):
    #     """creates the ghostnote that is placed on the scene before the real one is."""
    #     if self.ghost_note:
    #         self.removeItem(self.ghost_note)
    #     length = self.full_note_width * self.default_length
    #     (start, note) = self.snap(pos_x, pos_y)
    #     self.ghost_vel = self.default_ghost_vel
    #     self.ghost_rect = QtCore.QRectF(start, note, length, self.note_height)
    #     self.ghost_rect_orig_width = self.ghost_rect.width()
    #     self.ghost_note = QtWidgets.QGraphicsRectItem(self.ghost_rect)
    #     self.ghost_note.setBrush(QtGui.QColor(230, 221, 45, 100))
    #     self.addItem(self.ghost_note)

    def drawNote(self, note_num, note_start=None, note_length=None, note_velocity=None, add=True,
                 pos_scale=1.0, length_scale=1.0):
        """
        note_num: midi number, 0 - 127
        note_start: 0 - (num_measures * time_sig[0])
        note_length: 0 - (num_measures  * time_sig[0]/time_sig[1])
        note_velocity: 0 - 127
        """

        note_start *= pos_scale
        note_length *= length_scale

        info = [note_num, note_start, note_length, note_velocity]

        # if self.num_measures == 0:
        #     self.setMeasures(self.num_measures + 1)

        if note_start*self.one_second_width >= self.get_grid_width():
            while note_start*self.one_second_width >= self.get_grid_width():
                self.setMeasures(self.get_num_measures() + 1)
            # self.measureupdate.emit(self.num_measures)
            self.refreshScene()

        x_start = self.get_note_x_start(note_start)
        # if note_length > self.max_note_length:
        #     note_length = self.max_note_length + 0.25
        x_length = self.get_note_x_length(note_length)
        y_pos = self.get_note_y_pos(note_num)

        note = NoteItem(self.note_height, x_length, info)
        note.setPos(x_start, y_pos)

        # self.notes.append(note)
        if add:
            self.addItem(note)
        return note

    def drawMidiFile(self, mf: MidiFile, select=-1):
        self.midifile = mf
        self.select = select

        select_from = select
        select_to = select

        if isinstance(select, tuple):
            select_from = select[0]
            if len(select) == 1:
                select_to = select[0]
            else:
                select_to = select[1]

        notes, durations, positions = self.midifile.get_notelist()
        highest_note = mf.get_highest_note()
        lowest_note = mf.get_lowest_note()
        bps, time_sig = mf.get_bps_and_time_sig()

        padding = 5
        if highest_note - lowest_note + padding*2 < 24:
            padding = int((24 - (highest_note - lowest_note)) / 2)

        self.set_note_limit(max(0, lowest_note - padding), min(127, highest_note + padding))

        self.setMeasures(0)

        self.time_sig = time_sig
        self.bps = bps

        # self.setTimeSig(time_sig)

        for idx in reversed(range(len(notes))):
            note = self.drawNote(notes[idx], positions[idx], durations[idx])
            if select_from - 0.5 < positions[idx] < select_to + 0.5:
                note.setSelected(True)

    def set_width_scale(self, new_scale):
        self.one_second_width = new_scale

        if self.midifile is not None:
            self.drawMidiFile(self.midifile, self.select)
        else:
            self.setMeasures(0)
            self.setMeasures(10)
            self.refreshScene()

    # def truncateSelection(self):
    #     if len(self.selected_notes) > 0:
    #         # note[1] is the start position
    #         # note[2] is the length
    #         highest = max(self.selected_notes, key=lambda x: x.note[1]).note[1]
    #         lowest = min(self.selected_notes, key=lambda x: x.note[1]).note[1]
    #
    #         # rescale to midifile input
    #         if self.midifile is not None:
    #             highest *= self.midifile.get_resolution()
    #             lowest *= self.midifile.get_resolution()
    #
    #             self.midifile.truncate_ticks(lowest, highest)
    #
    #             self.drawMidiFile()

    # -------------------------------------------------------------------------
    # Helper Functions

    # def frange(self, x, y, t):
    #     while x < y:
    #         yield x
    #         x += t

    # def quantize(self, value):
    #     self.snap_value = float(self.full_note_width) * value if value else None
    #
    # def snap(self, pos_x, pos_y=None, piano_width=None):
    #     if piano_width is None:
    #         piano_width = self.piano_width
    #     if self.snap_value:
    #         pos_x = int(round((pos_x - piano_width) / self.snap_value, 0)) \
    #                 * self.snap_value + piano_width
    #     if pos_y:
    #         pos_y = int((pos_y - self.header_height) / self.note_height) \
    #                 * self.note_height + self.header_height
    #     return (pos_x, pos_y) if pos_y else pos_x

    # def adjust_note_vel(self, event):
    #     m_pos = event.scenePos()
    #     # bind velocity to vertical mouse movement
    #     self.ghost_vel += (event.lastScenePos().y() - m_pos.y()) / 10
    #     if self.ghost_vel < 0:
    #         self.ghost_vel = 0
    #     elif self.ghost_vel > 127:
    #         self.ghost_vel = 127
    #
    #     m_width = self.ghost_rect.x() + self.ghost_rect_orig_width
    #     if m_pos.x() < m_width:
    #         m_pos.setX(m_width)
    #     m_new_x = self.snap(m_pos.x())
    #     self.ghost_rect.setRight(m_new_x)
    #     self.ghost_note.setRect(self.ghost_rect)

    # def enforce_bounds(self, pos):
    #     if pos.x() < self.piano_width:
    #         pos.setX(self.piano_width)
    #     elif pos.x() > self.grid_width + self.piano_width:
    #         pos.setX(self.grid_width + self.piano_width)
    #     if pos.y() < self.header_height + self.padding:
    #         pos.setY(self.header_height + self.padding)
    #     return pos

    def get_note_x_start(self, note_start):
        return self.piano_width + self.one_second_width*note_start
        # return self.piano_width + \
        #        (self.grid_width / self.num_measures / self.time_sig[0]) * note_start

    def get_note_x_length(self, note_length):
        return float(note_length * self.one_second_width)
        # return float(self.time_sig[1]) / self.time_sig[0] * note_length * self.grid_width / self.num_measures

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
        self.zoom_x = 1
        self.zoom_y = 1


# class ModeIndicator(QtWidgets.QWidget):
#     def __init__(self):
#         QtWidgets.QWidget.__init__(self)
#         # self.setGeometry(0, 0, 30, 20)
#         self.setFixedSize(30, 20)
#         self.mode = None
#
#     def paintEvent(self, event):
#         painter = QtGui.QPainter()
#         painter.begin(self)
#         painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
#         if self.mode == 'velocity_mode':
#             painter.setBrush(QtGui.QColor(127, 0, 0))
#         elif self.mode == 'insert_mode':
#             painter.setBrush(QtGui.QColor(0, 100, 127))
#         else:
#             painter.setBrush(QtGui.QColor(0, 0, 0, 0))
#         painter.drawRect(0, 0, 30, 20)
#         painter.end()
#
#     def changeMode(self, new_mode):
#         self.mode = new_mode
#         self.update()


class PianoWidget(QtWidgets.QWidget):
    def __init__(self, *args):
        super(PianoWidget, self).__init__(*args)

        self.view = PianoRollView(
            time_sig=(4, 4))

        self.piano = self.view.piano

        self.timeSigLabel = QtWidgets.QLabel('time signature')
        self.timeSigLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        self.timeSigLabel.setMaximumWidth(100)
        self.timeSigBox = QtWidgets.QComboBox()
        self.timeSigBox.setEditable(False)
        self.timeSigBox.setMaximumWidth(100)
        self.timeSigBox.addItems(
            ('1/4', '2/4', '3/4', '4/4', '5/4', '6/4', '12/8'))
        self.timeSigBox.setCurrentIndex(3)

        self.defaultLengthLabel = QtWidgets.QLabel('default length')
        self.defaultLengthLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        self.defaultLengthLabel.setMaximumWidth(100)
        self.defaultLengthBox = QtWidgets.QComboBox()
        self.defaultLengthBox.setEditable(False)
        self.defaultLengthBox.setMaximumWidth(100)
        self.defaultLengthBox.addItems(('1/16', '1/15', '1/12', '1/9', '1/8', '1/6', '1/4', '1/3', '1/2', '1'))
        self.defaultLengthBox.setCurrentIndex(4)

        self.quantizeLabel = QtWidgets.QLabel('Grid')
        self.quantizeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        self.quantizeLabel.setMaximumWidth(100)
        self.quantizeBox = QtWidgets.QComboBox()
        self.quantizeBox.setEditable(False)
        self.quantizeBox.setMaximumWidth(100)
        self.quantizeBox.addItems(('0', '1/32', '1/16', '1/8', '1/4', '1/2', '1'))
        self.quantizeBox.setCurrentIndex(3)

        # Truncates midifile to the selected ones
        # self.truncateButton = QtWidgets.QPushButton('Truncate')

        # Shows the shuffle popup
        # self.shuffleButton = QtWidgets.QPushButton('Shuffle')

        # For shifting all notes at once
        # self.shiftButton = QtWidgets.QPushButton("Shift")

        # self.modeIndicator = ModeIndicator()

        # self.timeSigBox.currentIndexChanged[str].connect(self.piano.setTimeSig)
        # self.defaultLengthBox.currentIndexChanged[str].connect(self.piano.setDefaultLength)
        # self.quantizeBox.currentIndexChanged[str].connect(self.piano.setQuantize)
        # self.truncateButton.clicked.connect(self.piano.truncateSelection)
        # self.shuffleButton.clicked.connect(self.showShuffleDialog)
        # self.shiftButton.clicked.connect(self.showShiftDialog)

        # self.shuffleDialog = ShuffleDialog(self)

        # self.hBox = QtWidgets.QHBoxLayout()

        # self.hBox.addWidget(self.modeIndicator)
        # self.hBox.addWidget(self.timeSigLabel)
        # self.hBox.addWidget(self.timeSigBox)
        # self.hBox.addWidget(self.defaultLengthLabel)
        # self.hBox.addWidget(self.defaultLengthBox)
        # self.hBox.addWidget(self.quantizeLabel)
        # self.hBox.addWidget(self.quantizeBox)
        # self.hBox.addWidget(self.truncateButton)
        # self.hBox.addWidget(self.shuffleButton)
        # self.hBox.addWidget(self.shiftButton)

        self.viewBox = QtWidgets.QHBoxLayout()
        self.viewBox.addWidget(self.view)
        self.layout = QtWidgets.QVBoxLayout()

        # self.layout.addLayout(self.hBox)
        self.layout.addLayout(self.viewBox)

        self.setLayout(self.layout)
        self.resize(500, 500)
        self.view.setFocus()

        # self.piano.modeupdate.connect(self.modeIndicator.changeMode)

    # def showShuffleDialog(self):
    #     if self.piano.midifile is not None:
    #         if self.shuffleDialog.show():
    #             n_shift, n_prob, d_shift, d_prob = self.shuffleDialog.get_values()
    #             self.piano.midifile.randomize_notes(n_shift, n_prob)
    #             self.piano.midifile.randomize_timings(d_shift, d_prob)
    #             self.piano.drawMidiFile()

    # def showShiftDialog(self):
    #     shift_amount, ok = QtWidgets.QInputDialog.getInt(self, "Shift notes", "Enter shift amount:")
    #
    #     if ok:
    #         self.piano.midifile.shift_notes(shift_amount)
    #         self.piano.drawMidiFile()


# class ShuffleDialog(QtWidgets.QDialog):
#     def __init__(self, parent=None):
#         super(ShuffleDialog, self).__init__(parent)
#         grid = QtWidgets.QGridLayout()
#
#         self.note_shift_editor = QtWidgets.QSpinBox()
#         self.note_shift_editor.setRange(-100, 100)
#         self.note_shift_editor.setValue(1)
#
#         self.note_prob_editor = QtWidgets.QDoubleSpinBox()
#         self.note_prob_editor.setDecimals(2)
#         self.note_prob_editor.setRange(0, 1)
#         self.note_prob_editor.setSingleStep(0.01)
#         self.note_prob_editor.setValue(0.1)
#
#         grid.addWidget(QtWidgets.QLabel("Change note height:"), 0, 0)
#         grid.addWidget(QtWidgets.QLabel("note height:"), 1, 0)
#         grid.addWidget(self.note_shift_editor, 1, 1)
#         grid.addWidget(QtWidgets.QLabel("probability:"), 2, 0)
#         grid.addWidget(self.note_prob_editor, 2, 1)
#
#         self.duration_shift_editor = QtWidgets.QDoubleSpinBox()
#         self.duration_shift_editor.setDecimals(2)
#         self.duration_shift_editor.setRange(0, 1)
#         self.duration_shift_editor.setSingleStep(0.01)
#         self.duration_shift_editor.setValue(0.1)
#
#         self.duration_prob_editor = QtWidgets.QDoubleSpinBox()
#         self.duration_prob_editor.setDecimals(2)
#         self.duration_prob_editor.setRange(0, 1)
#         self.duration_prob_editor.setSingleStep(0.01)
#         self.duration_prob_editor.setValue(0.1)
#
#         grid.addWidget(QtWidgets.QLabel("Change note length:"), 0, 2)
#         grid.addWidget(QtWidgets.QLabel("deviation:"), 1, 2)
#         grid.addWidget(self.duration_shift_editor, 1, 3)
#         grid.addWidget(QtWidgets.QLabel("probability:"), 2, 2)
#         grid.addWidget(self.duration_prob_editor, 2, 3)
#
#         cancel_button = QtWidgets.QPushButton("Cancel")
#         apply_button = QtWidgets.QPushButton("Apply")
#         grid.addWidget(cancel_button, 3, 3)
#         grid.addWidget(apply_button, 3, 2)
#
#         cancel_button.clicked.connect(self.close)
#         apply_button.clicked.connect(self.accept)
#
#         self.setLayout(grid)
#
#     def show(self):
#         return self.exec_()
#
#     def get_values(self):
#         return self.note_shift_editor.value(), self.note_prob_editor.value(), \
#                self.duration_shift_editor.value(), self.duration_prob_editor.value()


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
    main.piano.drawMidiFile(midifile, (5, 9))
    # note.setSelected(True)
    # note.setFocus()
    # main.view.centerOn(note.x(), note.y())

    # import time
    # time.sleep(5)
    main.piano.set_width_scale(20)
    sys.exit(app.exec_())
