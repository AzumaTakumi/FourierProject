import sys

import numpy as np

from src.view.edit_dialog_view import EditDialogView
from src.view.interactive_spectrum_component import Interactive1dSpectrumComponent

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGroupBox,
    QFrame,
    QPushButton,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QSizePolicy,
)

class EditDialogView1d(EditDialogView):
    def __init__(self, modelContext=None, spectrum_component=None):
        self.modelContext = modelContext
        self.editValue = 0.5
        self._isDraggingSpectrum = False
        self._activeMouseButton = None
        self._lastIndex = None

        super().__init__()

        self.setWindowTitle("一次元スペクトル編集画面")

        if spectrum_component is None:
            spectrum_component = Interactive1dSpectrumComponent()

        self.spectrum_component = spectrum_component

        parent_layout = self.canvas.parentWidget().layout()
        parent_layout.replaceWidget(self.canvas, self.spectrum_component)
        self.canvas.deleteLater()

        self.spectrum_component.setMinimumSize(650, 480)

        self.spectrum_component.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored
        )
        self.spectrum_component.setScaledContents(True)
        self.spectrum_component.addMousePressEventListener(self._on_spectrum_pressed)
        self.spectrum_component.addMouseMoveEventListener(self._on_spectrum_moved)
        self.spectrum_component.addMouseReleaseEventListener(self._on_spectrum_released)

        self.paint_group.setTitle("値の編集")

        self.thickness_slider.hide()
        self.thickness_spin.hide()

        self.value_slider.setRange(0, 100)
        self.value_spin.setRange(0, 100)

        self.value_slider.setValue(50)
        self.value_spin.setValue(50)

    def _event_position(self, event) -> tuple[float, float]:
        position = event.position() if hasattr(event, "position") else event.pos()
        return float(position.x()), float(position.y())

    def _event_to_index(self, event) -> int | None:
        if self.spectrum_component is None or self.spectrum_component._displayImage is None:
            return None

        if self.spectrum_component._powerSpectrum is None:
            return None

        spectrum_size = int(np.asarray(self.spectrum_component._powerSpectrum).size)
        if spectrum_size == 0:
            return None

        image_width, _ = self.spectrum_component._displayImage.size
        widget_width = max(1, self.spectrum_component.width())
        x, _ = self._event_position(event)
        image_x = (x / widget_width) * (image_width - 1)

        plot_left = 48
        plot_right = max(plot_left + 1, image_width - 12 - 1)
        ratio = (image_x - plot_left) / (plot_right - plot_left)
        index = int(round(np.clip(ratio, 0.0, 1.0) * (spectrum_size - 1)))
        return index

    def _edit_index_range(self, startIndex: int, endIndex: int, button) -> None:
        if button == Qt.MouseButton.RightButton or self.editValue <= 0.0:
            self.modelContext.eraseSpectrumBetweenIndexes(startIndex, endIndex)
            return

        self.modelContext.scaleSpectrumBetweenIndexes(
            startIndex,
            endIndex,
            self.editValue
        )

    def _on_spectrum_pressed(self, event) -> None:
        if self.modelContext is None:
            return

        button = event.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return

        index = self._event_to_index(event)
        if index is None:
            return

        self.modelContext.beginSpectrumEdit()
        self._isDraggingSpectrum = True
        self._activeMouseButton = button
        self._lastIndex = index
        self._edit_index_range(index, index, button)

    def _on_spectrum_moved(self, event) -> None:
        if not self._isDraggingSpectrum or self._lastIndex is None:
            return

        if not (event.buttons() & self._activeMouseButton):
            return

        index = self._event_to_index(event)
        if index is None:
            return

        self._edit_index_range(self._lastIndex, index, self._activeMouseButton)
        self._lastIndex = index

    def _on_spectrum_released(self, event) -> None:
        if not self._isDraggingSpectrum:
            return

        if event.button() == self._activeMouseButton:
            self.modelContext.endSpectrumEdit()
            self._isDraggingSpectrum = False
            self._activeMouseButton = None
            self._lastIndex = None

    def on_value_changed(self, value: int):
        self.editValue = value / 100

    def on_thickness_changed(self, value: int):
        pass

    def on_undo_clicked(self):
        if self.modelContext is not None and self.modelContext.getUndoCount() > 0:
            self.modelContext.undo()

    def on_redo_clicked(self):
        if self.modelContext is not None and self.modelContext.getRedoCount() > 0:
            self.modelContext.redo()

    def on_reset_clicked(self):
        if self.modelContext is not None:
            self.modelContext.resetSpectrum()

    def closeEvent(self, event) -> None:
        if self._isDraggingSpectrum and self.modelContext is not None:
            self.modelContext.endSpectrumEdit()
        self._isDraggingSpectrum = False
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditDialogView1d()
    window.show()

    sys.exit(app.exec())
