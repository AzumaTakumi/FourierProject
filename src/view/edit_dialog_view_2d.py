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
        self.thickness_slider.setRange(1, 50)
        self.thickness_spin.setRange(1, 50)
        self.thickness_slider.setValue(self.brushSize)
        self.thickness_spin.setValue(self.brushSize)

        # value_slider は整数しか扱えないので、0〜10 として扱う。
        # 実際の編集値は value / 10 にして、表示上の明るさ 0.0〜1.0 に対応させる。
        self.value_slider.setRange(0, 10)
        self.value_slider.setValue(int(self.editValue * 10))

        # 親クラスで作られた QSpinBox を、2D用の QDoubleSpinBox に差し替える
        old_value_spin = self.value_spin
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0.0, 1.0)
        self.value_spin.setDecimals(1)
        self.value_spin.setSingleStep(0.1)
        self.value_spin.setValue(self.editValue)

        value_layout = old_value_spin.parentWidget().layout()
        value_layout.replaceWidget(old_value_spin, self.value_spin)
        old_value_spin.deleteLater()

        # slider と double spin を同期する
        self.value_slider.valueChanged.connect(
            lambda value: self.value_spin.setValue(value / 10)
        )
        self.value_spin.valueChanged.connect(
            lambda value: self.value_slider.setValue(int(round(value * 10)))
        )

        if self.spectrumComponent is not None:
            parent_layout = self.canvas.parentWidget().layout()
            parent_layout.replaceWidget(self.canvas, self.spectrumComponent)
            self.canvas.deleteLater()

            self.spectrumComponent.setMinimumSize(650, 480)
            self.spectrumComponent.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Ignored
            )
            self.spectrumComponent.setScaledContents(True)
            self.spectrumComponent.addMousePressEventListener(self._on_spectrum_pressed)
            self.spectrumComponent.addMouseMoveEventListener(self._on_spectrum_moved)
            self.spectrumComponent.addMouseReleaseEventListener(self._on_spectrum_released)

    def _event_position(self, event) -> tuple[float, float]:
        position = event.position() if hasattr(event, "position") else event.pos()
        return float(position.x()), float(position.y())

    def _event_to_display_point(self, event) -> tuple[int, int] | None:
        if self.spectrumComponent is None or self.spectrumComponent._displayImage is None:
            return None

        image_width, image_height = self.spectrumComponent._displayImage.size
        widget_width = max(1, self.spectrumComponent.width())
        widget_height = max(1, self.spectrumComponent.height())
        x, y = self._event_position(event)
        display_col = int(np.clip(round((x / widget_width) * (image_width - 1)), 0, image_width - 1))
        display_row = int(np.clip(round((y / widget_height) * (image_height - 1)), 0, image_height - 1))
        return display_row, display_col

    def _display_line_points(
        self,
        startPoint: tuple[int, int],
        endPoint: tuple[int, int],
    ) -> list[tuple[int, int]]:
        start_row, start_col = startPoint
        end_row, end_col = endPoint
        steps = max(abs(end_row - start_row), abs(end_col - start_col))
        rows = np.rint(np.linspace(start_row, end_row, steps + 1)).astype(int)
        cols = np.rint(np.linspace(start_col, end_col, steps + 1)).astype(int)
        points = []
        for row, col in zip(rows, cols):
            point = (int(row), int(col))
            if not points or points[-1] != point:
                points.append(point)
        return points

    def _display_point_to_spectrum_point(self, point: tuple[int, int]) -> tuple[int, int]:
        height, width = self.spectrumComponent._powerSpectrum.shape[:2]
        row, col = point
        return (
            int((row + ((height + 1) // 2)) % height),
            int((col + ((width + 1) // 2)) % width),
        )

    def _paint_color_from_edit_value(self) -> list[float]:
        """
        UIの0.0〜1.0を、現在のスペクトル表示レンジ上の明るさとしてFFT実部値へ変換する。
        """
        display_value = float(np.clip(self.editValue, 0.0, 1.0))
        value_range = getattr(self.spectrumComponent, "_displayValueRange", None)

        if value_range is None and getattr(self.spectrumComponent, "_powerSpectrum", None) is not None:
            display_array = np.log1p(np.abs(np.asarray(self.spectrumComponent._powerSpectrum, dtype=float)))
            if display_array.ndim == 3:
                display_array = np.mean(display_array, axis=2)
            value_range = (float(np.min(display_array)), float(np.max(display_array)))

        min_value, max_value = value_range if value_range is not None else (0.0, 1.0)
        target_display_value = min_value + display_value * (max_value - min_value)
        channel_power = max(0.0, float(np.expm1(target_display_value)))
        channel_real_value = float(np.sqrt(channel_power))
        return [channel_real_value] * 3

    def _edit_display_line(
        self,
        startPoint: tuple[int, int],
        endPoint: tuple[int, int],
        button,
    ) -> None:
        display_points = self._display_line_points(startPoint, endPoint)
        spectrum_points = [
            self._display_point_to_spectrum_point(point)
            for point in display_points
        ]
        radius = max(0, int(self.brushSize))
        if button == Qt.MouseButton.RightButton:
            self.modelContext.eraseSpectrumAtPositions(spectrum_points, radius)
            return

        self.modelContext.paintRgbSpectrumAtPositions(
            spectrum_points,
            radius,
            self._paint_color_from_edit_value()
        )

    def _on_spectrum_pressed(self, event) -> None:
        if self.modelContext is None or self.spectrumComponent is None:
            return

        button = event.button()
        if button not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return

        display_point = self._event_to_display_point(event)
        if display_point is None:
            return

        self.modelContext.beginSpectrumEdit()
        self._isDraggingSpectrum = True
        self._activeMouseButton = button
        self._lastDisplayPoint = display_point
        self._edit_display_line(display_point, display_point, button)

    def _on_spectrum_moved(self, event) -> None:
        if not self._isDraggingSpectrum or self._lastDisplayPoint is None:
            return

        if not (event.buttons() & self._activeMouseButton):
            return

        display_point = self._event_to_display_point(event)
        if display_point is None:
            return

        self._edit_display_line(self._lastDisplayPoint, display_point, self._activeMouseButton)
        self._lastDisplayPoint = display_point

    def _on_spectrum_released(self, event) -> None:
        if not self._isDraggingSpectrum:
            return

        if event.button() == self._activeMouseButton:
            self.modelContext.endSpectrumEdit()
            self._isDraggingSpectrum = False
            self._activeMouseButton = None
            self._lastDisplayPoint = None

    def on_undo_clicked(self):
        if self.modelContext is None:
            print("2D Undo: modelContext is not set")
            return

        if self.modelContext.getUndoCount() == 0:
            print("2D Undo: undo stack is empty")
            return

        self.modelContext.undo()

    def on_redo_clicked(self):
        if self.modelContext is None:
            print("2D Redo: modelContext is not set")
            return

        if self.modelContext.getRedoCount() == 0:
            print("2D Redo: redo stack is empty")
            return

        self.modelContext.redo()

    def on_reset_clicked(self):
        if self.modelContext is None:
            print("2D Reset: modelContext is not set")
            return

        try:
            self.modelContext.resetSpectrum()
        except Exception as e:
            print(f"2D Reset error: {e}")


    def on_thickness_changed(self, value: int):
        self.brushSize = value
        print(f"2D Thickness: {self.brushSize}")

    def on_value_changed(self, value: int):
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
