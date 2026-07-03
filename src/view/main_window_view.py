import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

from src.view.interactive_spectrum_component import (
    InteractiveSpectrumComponent
)
from src.model.pane_type import PaneType
from src.controller.context_menu_controller import ContextMenuController

class MainWindowView(QMainWindow):
    """
    メインウィンドウの描画を管理するView
    """
    def __init__(self):
        super().__init__()

        self._originalData = None
        self._originalSpectrum = None
        self._restoredDataImage = None
        self._spectrumComponent = None
        self._contextMenuController = ContextMenuController(self)

        self._originalDataLabel = QLabel()
        self._originalSpectrumLabel = QLabel()
        self._restoredDataImageLabel = QLabel()

        self._originalDataLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._originalSpectrumLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._restoredDataImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setWindowTitle("Result")

        widget = QWidget()
        self._layout = QGridLayout()

        self._layout.addWidget(self._originalDataLabel, 0, 0)
        self._layout.addWidget(self._originalSpectrumLabel, 0, 1)
        self._layout.addWidget(self._restoredDataImageLabel, 1, 0)

        # 0行目と1行目の引き伸ばし比率を 1:1 に設定
        self._layout.setRowStretch(0, 1)
        self._layout.setRowStretch(1, 1)
        
        # 0列目と1列目の引き伸ばし比率を 1:1 に設定
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)

        widget.setLayout(self._layout)
        self.setCentralWidget(widget)

    def display(self, model) -> None:
        """
        元データ、元データのパワースペクトル、復元したデータ、
        編集可能なパワースペクトルを2x2で表示する
        """
        images = model.getImage()

        self._originalData = images[PaneType.SOURCE_DATA]
        self._originalSpectrum = images[PaneType.POWER_SPECTRUM]
        self._restoredDataImage = images[PaneType.INVERSE_DATA]

        self._spectrumComponent = model.getSpectrumComponent()
        self._layout.addWidget(self._spectrumComponent, 1, 1)

        self._spectrumComponent.renderAll(np.array(images[PaneType.INTERACTIVE_POWER_SPECTRUM]))

        self.setMinimumSize(900, 650)
        self.resize(1000, 750)
        self.show()

        QTimer.singleShot(0, self._refreshImages)

    def _refreshImages(self) -> None:
        """
        4つのラベル・コンポーネントそれぞれの現在の表示領域に合わせて、
        縦横比を維持したまま最大サイズで画像をぴったり表示する
        """
        if self._originalData is None:
            return

        # 1. 左上：元画像
        w1, h1 = self._originalDataLabel.width(), self._originalDataLabel.height()
        self._originalDataLabel.setPixmap(
            QPixmap.fromImage(ImageQt(self._originalData)).scaled(w1, h1, Qt.AspectRatioMode.KeepAspectRatio)
        )

        # 2. 右上：元スペクトラム
        w2, h2 = self._originalSpectrumLabel.width(), self._originalSpectrumLabel.height()
        self._originalSpectrumLabel.setPixmap(
            QPixmap.fromImage(ImageQt(self._originalSpectrum)).scaled(w2, h2, Qt.AspectRatioMode.KeepAspectRatio)
        )

        # 3. 左下：復元画像
        w3, h3 = self._restoredDataImageLabel.width(), self._restoredDataImageLabel.height()
        self._restoredDataImageLabel.setPixmap(
            QPixmap.fromImage(ImageQt(self._restoredDataImage)).scaled(w3, h3, Qt.AspectRatioMode.KeepAspectRatio)
        )
        
        # 4. 右下：編集用スペクトラム（ここが今回の主役！）
        if self._spectrumComponent and hasattr(self._spectrumComponent, "_powerSpectrum") and self._spectrumComponent._powerSpectrum is not None:
            # 右下のセルの幅と高さをそのまま取得する
            w4, h4 = self._spectrumComponent.width(), self._spectrumComponent.height()
            
            # 部分編集用の配列から画像を生成
            img = Image.fromarray(self._spectrumComponent._powerSpectrum.astype(np.uint8))
            
            # 【ここがポイント！】右下自身に .scaled() をさせて突っ張らせるのではなく、
            # View側がセルのサイズに合わせて「比率を維持（KeepAspectRatio）」して綺麗にはめ込みます！
            pix = QPixmap.fromImage(ImageQt(img)).scaled(w4, h4, Qt.AspectRatioMode.KeepAspectRatio)
            self._spectrumComponent.setPixmap(pix)
        

    def resizeEvent(self, event) -> None:
        """ ウィンドウ全体のサイズが変更されたら、自動的に画像をリサイズする """
        super().resizeEvent(event)
        # マウスでウィンドウを伸ばした瞬間に、この関数がリアルタイムに実行されるよ
        self._refreshImages()


    def setContextMenuController(self, controller) -> None:
        """
        MainWindowViewで使用する右クリックメニューControllerを設定する
        """
        self._contextMenuController = controller

    def contextMenuEvent(self, event) -> None:
        """
        メインウィンドウで右クリックされたときにControllerへ処理を渡す
        """
        if self._contextMenuController is not None:
            self._contextMenuController.showContextMenu(event.globalPos())


    def getSpectrumComponent(self) -> InteractiveSpectrumComponent:
        """
        MainWindowViewで使用している、編集可能なパワースペクトルのコンポーネントを取得する
        """
        return self._spectrumComponent

    def updateRestoredDataImage(self, restoredDataImage: Image.Image) -> None:
        """
        復元したデータの画像を更新する
        """
        self._restoredDataImage = restoredDataImage
        self._restoredDataImageLabel.setPixmap(QPixmap.fromImage(ImageQt(restoredDataImage)))