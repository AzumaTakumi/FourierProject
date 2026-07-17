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
    def __init__(self, modelContext=None, spectrumComponent=None):
        self.modelContext = modelContext
        self.editValue = 0.5
        self._isDraggingSpectrum = False
        self._activeMouseButton = None
        self._lastIndex = None

        super().__init__()

        self.setWindowTitle("一次元スペクトル編集画面")

        if spectrumComponent is None:
            spectrumComponent = Interactive1dSpectrumComponent()

        self.spectrumComponent = spectrumComponent

        parentLayout = self.canvas.parentWidget().layout()
        parentLayout.replaceWidget(self.canvas, self.spectrumComponent)
        self.canvas.deleteLater()

        self.spectrumComponent.setMinimumSize(650, 480)

        self.spectrumComponent.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Ignored
        )
        self.spectrumComponent.setScaledContents(True)
        self.spectrumComponent.addMousePressEventListener(self._onSpectrumPressed)
        self.spectrumComponent.addMouseMoveEventListener(self._onSpectrumMoved)
        self.spectrumComponent.addMouseReleaseEventListener(self._onSpectrumReleased)

        self.paintGroup.setTitle("値の編集")

        self.thicknessSlider.hide()
        self.thicknessSpin.hide()

        self.valueSlider.setRange(0, 100)
        self.valueSpin.setRange(0, 100)

        self.valueSlider.setValue(50)
        self.valueSpin.setValue(50)

    def _eventPosition(self, event) -> tuple[float, float]:
        position = event.position() if hasattr(event, "position") else event.pos()
        return float(position.x()), float(position.y())

    def _eventToIndex(self, event) -> int | None:
        if self.spectrumComponent is None or self.spectrumComponent._displayImage is None:
            return None

        if self.spectrumComponent._powerSpectrum is None:
            return None

        spectrumSize = int(np.asarray(self.spectrumComponent._powerSpectrum).size)
        if spectrumSize == 0:
            return None

        imageWidth, _ = self.spectrumComponent._displayImage.size
        widgetWidth = max(1, self.spectrumComponent.width())
        x, _ = self._eventPosition(event)
        imageX = (x / widgetWidth) * (imageWidth - 1)

        plotLeft = 48
        plotRight = max(plotLeft + 1, imageWidth - 12 - 1)
        ratio = (imageX - plotLeft) / (plotRight - plotLeft)
        index = int(round(np.clip(ratio, 0.0, 1.0) * (spectrumSize - 1)))
        return index

    def _editIndexRange(self, startIndex: int, endIndex: int, button) -> None:
        if button == Qt.MouseButton.RightButton or self.editValue <= 0.0:
            self.modelContext.eraseSpectrumBetweenIndexes(startIndex, endIndex)
            return

        self.modelContext.scaleSpectrumBetweenIndexes(
            startIndex,
            endIndex,
            self.editValue
        )

    def _onSpectrumPressed(self, event) -> None:
        if self.modelContext is None:
            return

        button = event.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return

        index = self._eventToIndex(event)
        if index is None:
            return

        self.modelContext.beginSpectrumEdit()
        self._isDraggingSpectrum = True
        self._activeMouseButton = button
        self._lastIndex = index
        self._editIndexRange(index, index, button)

    def _onSpectrumMoved(self, event) -> None:
        if not self._isDraggingSpectrum or self._lastIndex is None:
            return

        if not (event.buttons() & self._activeMouseButton):
            return

        index = self._eventToIndex(event)
        if index is None:
            return

        self._editIndexRange(self._lastIndex, index, self._activeMouseButton)
        self._lastIndex = index

    def _onSpectrumReleased(self, event) -> None:
        if not self._isDraggingSpectrum:
            return

        if event.button() == self._activeMouseButton:
            self.modelContext.endSpectrumEdit()
            self._isDraggingSpectrum = False
            self._activeMouseButton = None
            self._lastIndex = None

    def onValueChanged(self, value: int):
        self.editValue = value / 100

    def onThicknessChanged(self, value: int):
        pass

    def onUndoClicked(self):
        if self.modelContext is not None and self.modelContext.getUndoCount() > 0:
            self.modelContext.undo()

    def onRedoClicked(self):
        if self.modelContext is not None and self.modelContext.getRedoCount() > 0:
            self.modelContext.redo()

    def onResetClicked(self):
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
