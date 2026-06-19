import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class InteractiveSpectrumComponent(QLabel):
    """
    編集可能なパワースペクトルコンポーネントのインタフェース
    """
    def renderAll(self, data: np.ndarray) -> None:
        """
        パワースペクトルを全て描画する
        """
        pass

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行う
        """
        pass

    def addMouseMoveEventListener(self) -> None:
        """
        マウス移動イベント発火時に呼び出される関数を登録する
        """
        pass

    def addMousePressEventListener(self) -> None:
        """
        マウスプレスイベント発火時に呼び出される関数を登録する
        """
        pass

    def addMouseReleaseEventListener(self) -> None:
        """
        マウスリリースイベント発火時に呼び出される関数を登録する
        """
        pass


class Interactive1dSpectrumComponent(InteractiveSpectrumComponent):
    """
    1次元データの編集可能なパワースペクトルコンポーネント
    """
    def __init__(self):
        super().__init__()
        self._mouseMoveListeners = []
        self._mousePressListeners = []
        self._mouseReleaseListeners = []

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("1D Spectrum")

    def _emitMouseMoveEvent(self, event) -> None:
        """
        PyQt6からマウス移動イベント発火時に呼び出され、
        対応するリスナーに引数MouseEventを渡し呼び出す。
        """
        for listener in self._mouseMoveListeners:
            listener(event)
            
    def _emitMousePressEvent(self, event) -> None:
        """
        PyQt6からマウスプレスイベント発火時に呼び出され、
        対応するリスナーに引数MouseEventを渡し呼び出す。
        """
        for listener in self._mousePressListeners:
            listener(event)

    def _emitMouseReleaseEvent(self, event) -> None:
        """
        PyQt6からマウスリリースイベント発火時に呼び出され、
        対応するリスナーに引数MouseEventを渡し呼び出す。
        """
        for listener in self._mouseReleaseListeners:
            listener(event)

    def mouseMoveEvent(self, event) -> None:
        """
        PyQt6からマウス移動イベント発火時に呼び出され、
        登録されたリスナーイベントに通知する。
        """
        self._emitMouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        """
        PyQt6からマウスプレスイベント発火時に呼び出され、
        登録されたリスナーイベントに通知する。
        """
        self._emitMousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """
        PyQt6からマウスリリースイベント発火時に呼び出され、
        登録されたリスナーイベントに通知する。
        """
        self._emitMouseReleaseEvent(event)

    def renderAll(self, data: np.ndarray) -> None:
        """
        パワースペクトルを全て描画する
        """
        image = Image.fromarray(data.astype(np.uint8))
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        ))

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行
        """
        self.renderAll(spectrumChange.changedPowerSpectrum)

    def addMouseMoveEventListener(self, callback) -> None:
        """
        マウス移動イベント発火時に呼び出される関数を登録する
        """
        self._mouseMoveListeners.append(callback)

    def addMousePressEventListener(self, callback) -> None:
        """
        マウスプレスイベント発火時に呼び出される関数を登録する
        """
        self._mousePressListeners.append(callback)

    def addMouseReleaseEventListener(self, callback) -> None:
        """
        マウスリリースイベント発火時に呼び出される関数を登録する
        """
        self._mouseReleaseListeners.append(callback)
        


class Interactive2dSpectrumComponent(InteractiveSpectrumComponent):
    """
    2次元データの編集可能なパワースペクトルコンポーネント
    """
    def __init__(self):
        super().__init__()
        self._mouseMoveListeners = []
        self._mousePressListeners = []
        self._mouseReleaseListeners = []

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("2D Spectrum")

    def _emitMouseMoveEvent(self, event) -> None:
        """
        PyQt6からマウス移動イベント発火時に呼び出され、
        対応するリスナーに引数MouseEventを渡し呼び出す。
        """
        for listener in self._mouseMoveListeners:
            listener(event)
            
    def _emitMousePressEvent(self, event) -> None:
        """
        PyQt6からマウスプレスイベント発火時に呼び出され、
        対応するリスナーに引数MouseEventを渡し呼び出す。
        """
        for listener in self._mousePressListeners:
            listener(event)


    def _emitMouseReleaseEvent(self, event) -> None:
        """
        PyQt6からマウスリリースイベント発火時に呼び出され、
        対応するリスナーに引数MouseEventを渡し呼び出す。
        """
        for listener in self._mouseReleaseListeners:
            listener(event)

    def mouseMoveEvent(self, event) -> None:
        """
        PyQt6からマウス移動イベント発火時に呼び出され、
        登録されたリスナーイベントに通知する。
        """
        self._emitMouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        """
        PyQt6からマウスプレスイベント発火時に呼び出され、
        登録されたリスナーイベントに通知する。
        """
        self._emitMousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """
        PyQt6からマウスリリースイベント発火時に呼び出され、
        登録されたリスナーイベントに通知する。
        """
        self._emitMouseReleaseEvent(event)

    def renderAll(self, data: np.ndarray) -> None:
        """
        パワースペクトルを全て描画する
        """
        image = Image.fromarray(data.astype(np.uint8))
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        ))

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行う
        """
        self.renderAll(spectrumChange.changedPowerSpectrum)

    def addMouseMoveEventListener(self, callback) -> None:
        """
        マウス移動イベント発火時に呼び出される関数を登録する
        """
        self._mouseMoveListeners.append(callback)

    def addMousePressEventListener(self, callback) -> None:
        """
        マウスプレスイベント発火時に呼び出される関数を登録する
        """
        self._mousePressListeners.append(callback)

    def addMouseReleaseEventListener(self, callback) -> None:
        """
        マウスリリースイベント発火時に呼び出される関数を登録する
        """
        self._mouseReleaseListeners.append(callback)


class MainWindowView(QMainWindow):
    """
    メインウィンドウの描画を管理するView
    """
    def __init__(self, spectrumComponent: InteractiveSpectrumComponent):
        super().__init__()

        self._originalData = None
        self._originalSpectrum = None
        self._restoredDataImage = None
        self._spectrumComponent = spectrumComponent

        self._originalDataLabel = QLabel()
        self._originalSpectrumLabel = QLabel()
        self._restoredDataImageLabel = QLabel()

        self._originalDataLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._originalSpectrumLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._restoredDataImageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setWindowTitle("Result")

        widget = QWidget()
        layout = QGridLayout()

        layout.addWidget(self._originalDataLabel, 0, 0)
        layout.addWidget(self._originalSpectrumLabel, 0, 1)
        layout.addWidget(self._restoredDataImageLabel, 1, 0)
        layout.addWidget(self._spectrumComponent, 1, 1)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def display(
        self,
        originalData: Image.Image,
        originalSpectrum: Image.Image,
        restoredDataImage: Image.Image
    ) -> None:
        """
        元データ、元データのパワースペクトル、復元したデータ、
        編集可能なパワースペクトルを2x2で表示する
        """
        self._originalData = originalData
        self._originalSpectrum = originalSpectrum
        self._restoredDataImage = restoredDataImage

        self._originalDataLabel.setPixmap(QPixmap.fromImage(ImageQt(originalData)))
        self._originalSpectrumLabel.setPixmap(QPixmap.fromImage(ImageQt(originalSpectrum)))
        self._restoredDataImageLabel.setPixmap(QPixmap.fromImage(ImageQt(restoredDataImage)))

        self._spectrumComponent.renderAll(np.array(originalSpectrum))

        self.show()

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