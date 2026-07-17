import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


def _fourierRenderer():
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
        self._setDisplayImage(_fourierRenderer().imageFromSpectrum(self._powerSpectrum))

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
        self._setDisplayImage(_fourierRenderer().imageFromSpectrum(self._powerSpectrum))

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
        return tuple(_fourierRenderer().spectrumDisplayArray(data).shape)

    def _setDisplayImage(self, image: Image.Image) -> None:
        self._displayImage = image
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.setPixmap(pixmap)
        self.setMinimumSize(0, 0)

    def _renderSpectrumImage(self) -> Image.Image:
        return _fourierRenderer().imageFromSpectrum(
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
        displayShape = self._displayShapeFromSpectrum(self._powerSpectrum)
        if self._displayValueRange is None or displayShape != self._displayRangeShape:
            self._displayValueRange = _fourierRenderer().displayRangeFromSpectrum(
                self._powerSpectrum
            )
            self._displayRangeShape = displayShape

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

        # 変更された矩形領域を内部のパワースペクトル配列へ反映する。
        self._powerSpectrum[y:y + height, x:x + width] = spectrumChange.changedPowerSpectrum
        spectrumHeight, spectrumWidth = self._powerSpectrum.shape[:2]
        rowShift = spectrumHeight // 2
        colShift = spectrumWidth // 2
        rowPivot = spectrumHeight - rowShift
        colPivot = spectrumWidth - colShift

        # 表示画像はfftshift後の座標になるため、折り返し位置をまたぐ更新領域は分割する。
        rowPoints = [y]
        colPoints = [x]
        if y < rowPivot < y + height:
            rowPoints.append(rowPivot)
        if x < colPivot < x + width:
            colPoints.append(colPivot)
        rowPoints.append(y + height)
        colPoints.append(x + width)

        for sourceRowStart, sourceRowStop in zip(rowPoints, rowPoints[1:]):
            for sourceColStart, sourceColStop in zip(colPoints, colPoints[1:]):
                localY = sourceRowStart - y
                localX = sourceColStart - x
                regionSpectrum = spectrumChange.changedPowerSpectrum[
                    localY:localY + sourceRowStop - sourceRowStart,
                    localX:localX + sourceColStop - sourceColStart
                ]

                # 分割した領域だけを表示用の濃淡画像へ変換する。
                regionArray = np.asarray(regionSpectrum)
                regionArray = {True: np.abs, False: np.real}[np.iscomplexobj(regionArray)](regionArray)
                regionArray = np.nan_to_num(regionArray.astype(float, copy=False))
                regionArray = np.log1p(np.abs(regionArray))
                displayArray = {3: lambda value: np.mean(value, axis=2)}.get(
                    regionArray.ndim,
                    lambda value: value,
                )(regionArray)
                regionImage = Image.fromarray(
                    _fourierRenderer().normalize(displayArray, self._displayValueRange),
                    "L"
                )

                # 元スペクトル上の座標を、fftshift後の表示画像上の貼り付け位置へ変換する。
                displayX = (sourceColStart + colShift) % spectrumWidth
                displayY = (sourceRowStart + rowShift) % spectrumHeight
                self._displayImage.paste(regionImage, (displayX, displayY))

                # 既存pixmapが使える場合は変更部分だけ描画し、使えない場合は全体を作り直す。
                pixmap = self.pixmap()
                if (
                    pixmap is None
                    or pixmap.isNull()
                    or pixmap.width() != self._displayImage.width
                    or pixmap.height() != self._displayImage.height
                ):
                    pixmap = QPixmap.fromImage(ImageQt(self._displayImage))
                else:
                    from PyQt6.QtGui import QPainter
                    pixmap = QPixmap(pixmap)
                    painter = QPainter(pixmap)
                    painter.drawImage(displayX, displayY, ImageQt(regionImage))
                    painter.end()
                self.setPixmap(pixmap)
                self.update(displayX, displayY, regionImage.width, regionImage.height)

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
