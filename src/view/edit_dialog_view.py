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
            background-color:#FFFFFF;
            color:#222222;
            font-size:14px;
        }

        QGroupBox{
            font-weight:bold;
            border:1px solid #888;
            border-radius:8px;
            margin-top:10px;
            background-color:#FFFFFF;
            color:#222222;
        }

        QGroupBox::title{
            subcontrol-origin: margin;
            left:14px;
            padding:0px 6px;
            background-color:#FFFFFF;
            color:#222222;
        }

        QLabel{
            background-color:transparent;
            color:#222222;
        }

        QPushButton{
            min-width:36px;
            min-height:30px;
            background-color:#FFFFFF;
            color:#222222;
            border:1px solid #999999;
            border-radius:4px;
        }

        QPushButton:hover{
            background-color:#F0F0F0;
        }

        QSpinBox,
        QDoubleSpinBox{
            min-height:26px;
            min-width:50px;
            background-color:#FFFFFF;
            color:#222222;
            border:1px solid #999999;
        }

        QSpinBox::up-button,
        QSpinBox::down-button,
        QDoubleSpinBox::up-button,
        QDoubleSpinBox::down-button{
            background-color:#F0F0F0;
        }

        QSpinBox QLineEdit,
        QDoubleSpinBox QLineEdit{
            background-color:#FFFFFF;
            color:#222222;
        }

        QSlider{
            background-color:#FFFFFF;
        }

        QFrame{
            background-color:#FFFFFF;
        }
        """)

        self.setAutoFillBackground(True)

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

        spectrumGroup = QGroupBox("Interactive Spectrum")

        spectrumLayout = QVBoxLayout(spectrumGroup)
        spectrumLayout.setContentsMargins(16, 20, 16, 16)
        spectrumLayout.setSpacing(12)

        # canvasはダミー。実際はInteractiveSpectrumComponentが入る予定

        self.canvas = QFrame()
        self.canvas.setMinimumSize(650, 480)
        self.canvas.setStyleSheet("""
        QFrame{
            background-color:#FFFFFF;
            border:1px solid #BBBBBB;
            border-radius:4px;
        }
        """)

        spectrumLayout.addWidget(self.canvas)

        ####################################################
        # Undo / Redo
        ####################################################

        bottom = QHBoxLayout()

        bottom.addStretch()

        self.undoButton = QPushButton("←")
        self.redoButton = QPushButton("→")

        bottom.addWidget(self.undoButton)
        bottom.addWidget(self.redoButton)

        bottom.addStretch()

        spectrumLayout.addLayout(bottom)

        ####################################################
        # ペイントパネル
        ####################################################

        self.paintGroup = QGroupBox("ペイント")

        paintLayout = QVBoxLayout(self.paintGroup)
        paintLayout.setContentsMargins(16, 20, 16, 16)
        paintLayout.setSpacing(20)

        ####################################################
        # 太さ
        ####################################################

        self.thicknessWidget = QWidget()
        self.thicknessLayout = QHBoxLayout(self.thicknessWidget)
        self.thicknessLayout.setContentsMargins(0, 0, 0, 0)
        self.thicknessLayout.setSpacing(12)


        thicknessLabel = QLabel("太さ")
        thicknessLabel.setFixedWidth(40)

        self.thicknessSlider = QSlider(Qt.Orientation.Horizontal)
        # self.thicknessSlider.setRange(1, 50)
        # self.thicknessSlider.setValue(5)

        self.thicknessSpin = QSpinBox()
        # self.thicknessSpin.setRange(1, 50)
        # self.thicknessSpin.setValue(5)

        self.thicknessSlider.valueChanged.connect(self.thicknessSpin.setValue)
        self.thicknessSpin.valueChanged.connect(self.thicknessSlider.setValue)

        self.thicknessLayout.addWidget(thicknessLabel)
        self.thicknessLayout.addWidget(self.thicknessSlider)
        self.thicknessLayout.addWidget(self.thicknessSpin)

        ####################################################
        # 数値
        ####################################################

        valueLayout = QHBoxLayout()
        valueLayout.setSpacing(12)

        valueLabel = QLabel("数値")
        valueLabel.setFixedWidth(40)

        self.valueSlider = QSlider(Qt.Orientation.Horizontal)
        # self.valueSlider.setRange(0, 100)
        # self.valueSlider.setValue(50)

        self.valueSpin = QSpinBox()
        # self.valueSpin.setRange(0, 100)
        # self.valueSpin.setValue(50)

        self.valueSlider.valueChanged.connect(self.valueSpin.setValue)
        self.valueSpin.valueChanged.connect(self.valueSlider.setValue)

        valueLayout.addWidget(valueLabel)
        valueLayout.addWidget(self.valueSlider)
        valueLayout.addWidget(self.valueSpin)

        paintLayout.addWidget(self.thicknessWidget)
        paintLayout.addLayout(valueLayout)
        paintLayout.addStretch()

        self.paintGroup.setFixedWidth(300)

        ####################################################
        # Splitter
        ####################################################

        splitter.addWidget(spectrumGroup)

        splitter.addWidget(self.paintGroup)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        root.addWidget(splitter)

        ####################################################
        # フッター
        ####################################################

        footer = QHBoxLayout()

        self.resetButton = QPushButton("リセット")
        self.closeButton = QPushButton("閉じる")

        footer.addWidget(self.resetButton)
        footer.addStretch()
        footer.addWidget(self.closeButton)

        root.addLayout(footer)

        ####################################################
        # シグナル
        ####################################################

        # ボタン
        self.undoButton.clicked.connect(self.onUndoClicked)
        self.redoButton.clicked.connect(self.onRedoClicked)
        self.resetButton.clicked.connect(self.onResetClicked)
        self.closeButton.clicked.connect(self.onCloseClicked)

        # スライダー
        self.thicknessSlider.valueChanged.connect(self.onThicknessChanged)
        self.valueSlider.valueChanged.connect(self.onValueChanged)

    ####################################################
    # スロット
    ####################################################

    def onUndoClicked(self):
        print("Undo")

    def onRedoClicked(self):
        print("Redo")

    def onResetClicked(self):
        print("Reset")

    def onCloseClicked(self):
        self.close()

    def onThicknessChanged(self, value: int):
        print(f"Thickness: {value}")

    def onValueChanged(self, value: int):
        print(f"Value: {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditDialogView()
    window.show()

    sys.exit(app.exec())
