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


class EditDialogView(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("編集画面")
        self.resize(1200, 750)

        ####################################################
        # CSS
        ####################################################
        self.setStyleSheet("""
        QWidget{
            background:#F5F5F5;
            font-size:14px;
        }

        QGroupBox{
            font-weight:bold;
            border:1px solid #888;
            border-radius:8px;
            margin-top:10px;
            background:white;
        }

        QGroupBox::title{
            subcontrol-origin: margin;
            left:14px;
            padding:0px 6px;
            background:#F5F5F5;
        }

        QPushButton{
            min-width:36px;
            min-height:30px;
        }

        QSpinBox{
            min-height:26px;
            min-width:50px;
        }
        """)

        ####################################################
        # メインレイアウト
        ####################################################

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        ####################################################
        # Interactive Spectrum
        ####################################################

        spectrum_group = QGroupBox("Interactive Spectrum")

        spectrum_layout = QVBoxLayout(spectrum_group)
        spectrum_layout.setContentsMargins(16, 20, 16, 16)
        spectrum_layout.setSpacing(12)

        # canvasはダミー。実際はInteractiveSpectrumComponentが入る予定
        self.canvas = QFrame()
        self.canvas.setMinimumSize(650, 480)
        self.canvas.setStyleSheet("""
        QFrame{
            background:white;
            border:1px solid #BBBBBB;
            border-radius:4px;
        }
        """)

        spectrum_layout.addWidget(self.canvas)

        ####################################################
        # Undo / Redo
        ####################################################

        bottom = QHBoxLayout()

        bottom.addStretch()

        self.undo_button = QPushButton("←")
        self.redo_button = QPushButton("→")

        bottom.addWidget(self.undo_button)
        bottom.addWidget(self.redo_button)

        bottom.addStretch()

        spectrum_layout.addLayout(bottom)

        ####################################################
        # ペイントパネル
        ####################################################

        self.paint_group = QGroupBox("ペイント")

        paint_layout = QVBoxLayout(self.paint_group)
        paint_layout.setContentsMargins(16, 20, 16, 16)
        paint_layout.setSpacing(20)

        ####################################################
        # 太さ
        ####################################################

        self.thickness_layout = QHBoxLayout()
        self.thickness_layout.setSpacing(12)

        thickness_label = QLabel("太さ")
        thickness_label.setFixedWidth(40)

        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        # self.thickness_slider.setRange(1, 50)
        # self.thickness_slider.setValue(5)

        self.thickness_spin = QSpinBox()
        # self.thickness_spin.setRange(1, 50)
        # self.thickness_spin.setValue(5)

        self.thickness_slider.valueChanged.connect(self.thickness_spin.setValue)
        self.thickness_spin.valueChanged.connect(self.thickness_slider.setValue)

        self.thickness_layout.addWidget(thickness_label)
        self.thickness_layout.addWidget(self.thickness_slider)
        self.thickness_layout.addWidget(self.thickness_spin)

        ####################################################
        # 数値
        ####################################################

        value_layout = QHBoxLayout()
        value_layout.setSpacing(12)

        value_label = QLabel("数値")
        value_label.setFixedWidth(40)

        self.value_slider = QSlider(Qt.Orientation.Horizontal)
        # self.value_slider.setRange(0, 100)
        # self.value_slider.setValue(50)

        self.value_spin = QSpinBox()
        # self.value_spin.setRange(0, 100)
        # self.value_spin.setValue(50)

        self.value_slider.valueChanged.connect(self.value_spin.setValue)
        self.value_spin.valueChanged.connect(self.value_slider.setValue)

        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_slider)
        value_layout.addWidget(self.value_spin)

        ####################################################
        # レイアウト追加
        ####################################################

        paint_layout.addLayout(self.thickness_layout)
        paint_layout.addLayout(value_layout)
        paint_layout.addStretch()

        self.paint_group.setFixedWidth(300)

        ####################################################
        # Splitter
        ####################################################

        splitter.addWidget(spectrum_group)
        splitter.addWidget(self.paint_group)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        root.addWidget(splitter)

        ####################################################
        # フッター
        ####################################################

        footer = QHBoxLayout()

        self.reset_button = QPushButton("リセット")
        self.close_button = QPushButton("閉じる")

        footer.addWidget(self.reset_button)
        footer.addStretch()
        footer.addWidget(self.close_button)

        root.addLayout(footer)

        ####################################################
        # シグナル
        ####################################################

        # ボタン
        self.undo_button.clicked.connect(self.on_undo_clicked)
        self.redo_button.clicked.connect(self.on_redo_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
        self.close_button.clicked.connect(self.on_close_clicked)

        # スライダー
        self.thickness_slider.valueChanged.connect(self.on_thickness_changed)
        self.value_slider.valueChanged.connect(self.on_value_changed)

    ####################################################
    # スロット
    ####################################################

    def on_undo_clicked(self):
        print("Undo")

    def on_redo_clicked(self):
        print("Redo")

    def on_reset_clicked(self):
        print("Reset")

    def on_close_clicked(self):
        self.close()

    def on_thickness_changed(self, value: int):
        print(f"Thickness: {value}")

    def on_value_changed(self, value: int):
        print(f"Value: {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditDialogView()
    window.show()

    sys.exit(app.exec())