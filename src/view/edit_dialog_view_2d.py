from src.view.edit_dialog_view import EditDialogView
from PyQt6.QtWidgets import QSizePolicy


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

        self.value_slider.setRange(0, 255)
        self.value_spin.setRange(0, 255)
        self.value_slider.setValue(self.editValue)
        self.value_spin.setValue(self.editValue)

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
        self.editValue = value
        print(f"2D Value: {self.editValue}")



if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = EditDialogView2d()
    window.show()

    sys.exit(app.exec())
