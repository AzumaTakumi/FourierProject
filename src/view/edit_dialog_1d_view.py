import sys

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
    def __init__(self, spectrum_component=None):
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

        self.paint_group.setTitle("値の編集")

        self.thickness_slider.hide()
        self.thickness_spin.hide()

        self.value_slider.setRange(0, 100)
        self.value_spin.setRange(0, 100)

        self.value_slider.setValue(50)
        self.value_spin.setValue(50)

    def on_value_changed(self, value: int):
        edit_value = value / 100

    def on_thickness_changed(self, value: int):
        edit_value = value / 100
        # ここで 0.0〜1.0 の値として使える
        pass

    def on_undo_clicked(self):
        pass

    def on_redo_clicked(self):
        pass

    def on_reset_clicked(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditDialogView1d()
    window.show()

    sys.exit(app.exec())

