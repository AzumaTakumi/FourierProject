from PyQt6.QtWidgets import QWidget

from edit_dialog_view import EditDialogView
from interactive_spectrum_component import Interactive1dSpectrumComponent

import sys

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
)



class EditDialogView1d(EditDialogView):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("一次元スペクトル編集画面")

        self.spectrum_component = Interactive1dSpectrumComponent()

        parent_layout = self.canvas.parentWidget().layout()
        parent_layout.replaceWidget(self.canvas, self.spectrum_component)
        self.canvas.deleteLater()

        self.spectrum_component.setMinimumSize(650, 480)

        self.paint_group.setTitle("値の選択")

        self.thickness_widget.hide()

        self.value_slider.setRange(0, 255)
        self.value_slider.setValue(128)

        self.value_spin.setRange(0, 255)
        self.value_spin.setValue(128)

    def on_value_changed(self, value: int):
        print(f"1D Spectrum Value: {value}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditDialogView()
    window.show()

    sys.exit(app.exec())