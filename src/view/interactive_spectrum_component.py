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

        self._powerSpectrum = None

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
        self._powerSpectrum = data.copy()

        image = Image.fromarray(self._powerSpectrum.astype(np.uint8))
        pixmap = QPixmap.fromImage(ImageQt(image))

        self.setPixmap(pixmap)

        self.setMinimumSize(0, 0)

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行う
        """
        index = spectrumChange.index
        changedPowerSpectrum = spectrumChange.changedPowerSpectrum

        self._powerSpectrum[
            index:index + len(changedPowerSpectrum)
        ] = changedPowerSpectrum

        image = Image.fromarray(self._powerSpectrum.astype(np.uint8))
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap)

        self.setMinimumSize(0, 0)

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

        self._powerSpectrum = None

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
        self._powerSpectrum = data.copy()

        image = Image.fromarray(self._powerSpectrum.astype(np.uint8))
        pixmap = QPixmap.fromImage(ImageQt(image))

        self.setPixmap(pixmap)

        self.setMinimumSize(0, 0)

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行う
        """
        x = spectrumChange.x
        y = spectrumChange.y
        width = spectrumChange.width
        height = spectrumChange.height

        self._powerSpectrum[
            y:y + height,
            x:x + width
        ] = spectrumChange.changedPowerSpectrum

        image = Image.fromarray(self._powerSpectrum.astype(np.uint8))
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap)

        self.setMinimumSize(0, 0)

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
