from src.view.edit_dialog_view import EditDialogView
import numpy as np

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy, QDoubleSpinBox


class EditDialogView2d(EditDialogView):
    """
    2次元スペクトル編集用の編集画面。
    EditDialogViewを継承し、2D専用の処理を追加する。
    """

    def __init__(self, modelContext=None, spectrumComponent=None):
        self.modelContext = modelContext
        self.spectrumComponent = spectrumComponent

        self.brushSize = 1
        self.editValue = 0
        self._isDraggingSpectrum = False
        self._activeMouseButton = None
        self._lastDisplayPoint = None

        super().__init__()

        self.setWindowTitle("2次元編集画面")

        self._setup2dView()

    def _setup2dView(self) -> None:
        """
        2D編集画面専用の初期設定を行う。
        """
        self.thicknessSlider.setRange(1, 50)
        self.thicknessSpin.setRange(1, 50)
        self.thicknessSlider.setValue(self.brushSize)
        self.thicknessSpin.setValue(self.brushSize)

        # valueSlider は整数しか扱えないので、0〜10 として扱う。
        # 実際の編集値は value / 10 にして、表示上の明るさ 0.0〜1.0 に対応させる。
        self.valueSlider.setRange(0, 10)
        self.valueSlider.setValue(int(self.editValue * 10))

        # 親クラスで作られた QSpinBox を、2D用の QDoubleSpinBox に差し替える
        oldValueSpin = self.valueSpin
        self.valueSpin = QDoubleSpinBox()
        self.valueSpin.setRange(0.0, 1.0)
        self.valueSpin.setDecimals(1)
        self.valueSpin.setSingleStep(0.1)
        self.valueSpin.setValue(self.editValue)

        valueLayout = oldValueSpin.parentWidget().layout()
        valueLayout.replaceWidget(oldValueSpin, self.valueSpin)
        oldValueSpin.deleteLater()

        # slider と double spin を同期する
        self.valueSlider.valueChanged.connect(
            lambda value: self.valueSpin.setValue(value / 10)
        )
        self.valueSpin.valueChanged.connect(
            lambda value: self.valueSlider.setValue(int(round(value * 10)))
        )

        if self.spectrumComponent is not None:
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

    def _eventPosition(self, event) -> tuple[float, float]:
        position = event.position() if hasattr(event, "position") else event.pos()
        return float(position.x()), float(position.y())

    def _eventToDisplayPoint(self, event) -> tuple[int, int] | None:
        if self.spectrumComponent is None or self.spectrumComponent._displayImage is None:
            return None

        imageWidth, imageHeight = self.spectrumComponent._displayImage.size
        widgetWidth = max(1, self.spectrumComponent.width())
        widgetHeight = max(1, self.spectrumComponent.height())
        x, y = self._eventPosition(event)
        displayCol = int(np.clip(round((x / widgetWidth) * (imageWidth - 1)), 0, imageWidth - 1))
        displayRow = int(np.clip(round((y / widgetHeight) * (imageHeight - 1)), 0, imageHeight - 1))
        return displayRow, displayCol

    def _displayLinePoints(
        self,
        startPoint: tuple[int, int],
        endPoint: tuple[int, int],
    ) -> list[tuple[int, int]]:
        startRow, startCol = startPoint
        endRow, endCol = endPoint
        steps = max(abs(endRow - startRow), abs(endCol - startCol))
        rows = np.rint(np.linspace(startRow, endRow, steps + 1)).astype(int)
        cols = np.rint(np.linspace(startCol, endCol, steps + 1)).astype(int)
        points = []
        for row, col in zip(rows, cols):
            point = (int(row), int(col))
            if not points or points[-1] != point:
                points.append(point)
        return points

    def _displayPointToSpectrumPoint(self, point: tuple[int, int]) -> tuple[int, int]:
        height, width = self.spectrumComponent._powerSpectrum.shape[:2]
        row, col = point
        return (
            int((row + ((height + 1) // 2)) % height),
            int((col + ((width + 1) // 2)) % width),
        )

    def _paintColorFromEditValue(self) -> list[float]:
        """
        UIの0.0〜1.0を、現在のスペクトル表示レンジ上の明るさとしてFFT実部値へ変換する。
        """
        displayValue = float(np.clip(self.editValue, 0.0, 1.0))
        valueRange = getattr(self.spectrumComponent, "_displayValueRange", None)

        if valueRange is None and getattr(self.spectrumComponent, "_powerSpectrum", None) is not None:
            displayArray = np.log1p(np.abs(np.asarray(self.spectrumComponent._powerSpectrum, dtype=float)))
            if displayArray.ndim == 3:
                displayArray = np.mean(displayArray, axis=2)
            valueRange = (float(np.min(displayArray)), float(np.max(displayArray)))

        minValue, maxValue = valueRange if valueRange is not None else (0.0, 1.0)
        targetDisplayValue = minValue + displayValue * (maxValue - minValue)
        channelPower = max(0.0, float(np.expm1(targetDisplayValue)))
        channelRealValue = float(np.sqrt(channelPower))
        return [channelRealValue] * 3

    def _editDisplayLine(
        self,
        startPoint: tuple[int, int],
        endPoint: tuple[int, int],
        button,
    ) -> None:
        displayPoints = self._displayLinePoints(startPoint, endPoint)
        spectrumPoints = [
            self._displayPointToSpectrumPoint(point)
            for point in displayPoints
        ]
        radius = max(0, int(self.brushSize))
        if button == Qt.MouseButton.RightButton:
            self.modelContext.eraseSpectrumAtPositions(spectrumPoints, radius)
            return

        self.modelContext.paintRgbSpectrumAtPositions(
            spectrumPoints,
            radius,
            self._paintColorFromEditValue()
        )

    def _onSpectrumPressed(self, event) -> None:
        if self.modelContext is None or self.spectrumComponent is None:
            return

        button = event.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return

        displayPoint = self._eventToDisplayPoint(event)
        if displayPoint is None:
            return

        self.modelContext.beginSpectrumEdit()
        self._isDraggingSpectrum = True
        self._activeMouseButton = button
        self._lastDisplayPoint = displayPoint
        self._editDisplayLine(displayPoint, displayPoint, button)

    def _onSpectrumMoved(self, event) -> None:
        if not self._isDraggingSpectrum or self._lastDisplayPoint is None:
            return

        if not (event.buttons() & self._activeMouseButton):
            return

        displayPoint = self._eventToDisplayPoint(event)
        if displayPoint is None:
            return

        self._editDisplayLine(self._lastDisplayPoint, displayPoint, self._activeMouseButton)
        self._lastDisplayPoint = displayPoint

    def _onSpectrumReleased(self, event) -> None:
        if not self._isDraggingSpectrum:
            return

        if event.button() == self._activeMouseButton:
            self.modelContext.endSpectrumEdit()
            self._isDraggingSpectrum = False
            self._activeMouseButton = None
            self._lastDisplayPoint = None

    def onUndoClicked(self):
        if self.modelContext is None:
            print("2D Undo: modelContext is not set")
            return

        if self.modelContext.getUndoCount() == 0:
            print("2D Undo: undo stack is empty")
            return

        self.modelContext.undo()

    def onRedoClicked(self):
        if self.modelContext is None:
            print("2D Redo: modelContext is not set")
            return

        if self.modelContext.getRedoCount() == 0:
            print("2D Redo: redo stack is empty")
            return

        self.modelContext.redo()

    def onResetClicked(self):
        if self.modelContext is None:
            print("2D Reset: modelContext is not set")
            return

        try:
            self.modelContext.resetSpectrum()
        except Exception as e:
            print(f"2D Reset error: {e}")


    def onThicknessChanged(self, value: int):
        self.brushSize = value
        print(f"2D Thickness: {self.brushSize}")

    def onValueChanged(self, value: int):
        self.editValue = value / 10
        print(f"2D Value: {self.editValue}")

    def closeEvent(self, event) -> None:
        if self._isDraggingSpectrum and self.modelContext is not None:
            self.modelContext.endSpectrumEdit()
        self._isDraggingSpectrum = False
        super().closeEvent(event)



if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = EditDialogView2d()
    window.show()

    sys.exit(app.exec())
