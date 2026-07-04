import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def _fourier_renderer():
    from src.model.fourier_renderer import FourierRenderer
    return FourierRenderer

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
        self._displayImage = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("1D Spectrum")

    def _setDisplayImage(self, image: Image.Image) -> None:
        self._displayImage = image
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap)
        self.setMinimumSize(0, 0)

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
        self._powerSpectrum = np.asarray(data).copy()
        self._setDisplayImage(_fourier_renderer().imageFrom1dData(self._powerSpectrum))

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行う
        """
        index = spectrumChange.index
        changedPowerSpectrum = spectrumChange.changedPowerSpectrum

        if self._powerSpectrum is None:
            self.renderAll(changedPowerSpectrum)
            return

        self._powerSpectrum[index:index + len(changedPowerSpectrum)] = changedPowerSpectrum
        self._setDisplayImage(_fourier_renderer().imageFrom1dData(self._powerSpectrum))

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
        self._displayImage = None
        self._displayValueRange = None
        self._displayRangeShape = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("2D Spectrum")

    def _displayShapeFromSpectrum(self, data: np.ndarray) -> tuple[int, ...]:
        return tuple(_fourier_renderer().spectrumDisplayArray(data).shape)

    def _setDisplayImage(self, image: Image.Image) -> None:
        self._displayImage = image
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap)
        self.setMinimumSize(0, 0)

    def _renderSpectrumImage(self) -> Image.Image:
        return _fourier_renderer().imageFromSpectrum(
            self._powerSpectrum,
            self._displayValueRange
        )

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
        self._powerSpectrum = np.asarray(data).copy()
        display_shape = self._displayShapeFromSpectrum(self._powerSpectrum)
        if self._displayValueRange is None or display_shape != self._displayRangeShape:
            self._displayValueRange = _fourier_renderer().displayRangeFromSpectrum(
                self._powerSpectrum
            )
            self._displayRangeShape = display_shape

        self._setDisplayImage(self._renderSpectrumImage())

    def renderDirtyRegion(self, spectrumChange) -> None:
        """
        spectrumChangeを元に矩形領域で再描画を行う
        """
        x = spectrumChange.x
        y = spectrumChange.y
        width = spectrumChange.width
        height = spectrumChange.height

        if self._powerSpectrum is None:
            self.renderAll(spectrumChange.changedPowerSpectrum)
            return

        self._powerSpectrum[y:y + height, x:x + width] = spectrumChange.changedPowerSpectrum
        self._setDisplayImage(self._renderSpectrumImage())

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
