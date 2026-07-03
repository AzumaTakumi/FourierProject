from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from typing import Callable
import numpy as np
from .composite_spectrum_edit_command import CompositeSpectrumEditCommand
from .fourier_model import FourierModel
from .spectrum_1_d_change import Spectrum1dChange
from .spectrum_2_d_change import Spectrum2dChange
from .spectrum_change import SpectrumChange
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# ContextはControllerの代わりに各Commandを生成するため、具体ModelとCommandをここで読み込む。
from PIL import Image
from .fourier_1_d_model import Fourier1dModel
from .fourier_2_d_model import Fourier2dModel
from .change_fourier_model_command import ChangeFourierModelCommand
from .edit_spectrum_values_at_indexes_command import EditSpectrumValuesAtIndexesCommand
from .erase_spectrum_at_positions_command import EraseSpectrumAtPositionsCommand
from .paint_rgb_spectrum_at_positions_command import PaintRgbSpectrumAtPositionsCommand
from .reset_spectrum_command import ResetSpectrumCommand
from .spectrum_1_d_change import Spectrum1dChange
from .spectrum_2_d_change import Spectrum2dChange
from .pane_type import PaneType
# SAFE CODE AREA ˄

class FourierModelContext(object):
    # GENERATED CODE AREA: class.header ˅
    """
    現在使用しているFourierModelとUndo/Redo履歴を管理するクラスである。Controllerからの操作を受け取り、必要なCommandを生成・実行し、Modelの変更履歴を管理する。また、スペクトル変更時にはViewから渡された通知用関数を呼び出す。
    """

    # SAFE CODE AREA ˅
    # 追加のクラス共通処理は不要。状態管理は__init__と各操作メソッドで行う。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, spectrumChangedListener: Callable[[SpectrumChange], None]) -> None:
        """
        FourierModelContextを初期化する。初期Model、Undo/Redo履歴、通知用関数などを設定する。
        """

        if spectrumChangedListener is None:
            raise ValueError("spectrumChangedListener must not be None")

        # 現在操作対象となっているFourierModelを保持する。
        self.currentModel: Fourier1dModel | Fourier2dModel = Fourier2dModel(sourceData=np.zeros((1, 1)))

        # Undo可能なCommandを保持するスタックである。
        self.undoStack: list[CompositeSpectrumEditCommand] = []

        # Redo可能なCommandを保持するスタックである。
        self.redoStack: list[CompositeSpectrumEditCommand] = []

        # スペクトル変更時に呼び出す通知用関数を保持する。View側から渡された操作を保持し、SpectrumChangeを引数として呼び出す。
        self.spectrumChangedListener: Callable[[SpectrumChange], None] = spectrumChangedListener

        # ドラッグ操作中に発生した複数の編集Commandを一時的にまとめるCompositeSpectrumEditCommandを保持する。
        self.currentCompositeCommand: CompositeSpectrumEditCommand | None = None

        # SAFE CODE AREA ˅
        # Commandの変更種別から通知範囲生成処理を選ぶ。
        self.spectrumChangeFactories = {
            "1d": self._create1dSpectrumChangeForCommand,
            "2d": self._create2dSpectrumChangeForCommand,
            "full": self._createFullSpectrumChangeForCommand,
        }
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.set1dSourceData ˅
    def set1dSourceData(self, sourceData: np.ndarray) -> None:
        """
        1次元元データを設定する。
        ファイル入力によるデータ切り替えはUndo対象にせず、履歴をクリアする。
        """

        # SAFE CODE AREA ˅
        data = np.asarray(sourceData, dtype=float)
        self._replaceCurrentModel(Fourier1dModel(data))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set1dSourceData ˄


    # GENERATED CODE AREA: method.set2dSourceData ˅
    def set2dSourceData(self, sourceData: np.ndarray) -> None:
        """
        2次元元データを設定する。
        ファイル入力によるデータ切り替えはUndo対象にせず、履歴をクリアする。
        """

        # SAFE CODE AREA ˅
        data = np.asarray(sourceData, dtype=float)
        self._replaceCurrentModel(Fourier2dModel(data))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set2dSourceData ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        現在のModelの編集用スペクトルを元スペクトル状態に戻すResetSpectrumCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # リセットもUndo可能な編集として扱う。
        self._executeUndoableCommand(ResetSpectrumCommand(self.currentModel))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄

    def _replaceCurrentModel(self, newModel: FourierModel) -> None:
        """
        ファイル入力などで現在のModelを差し替える。
        データ切り替えはUndo対象にせず、過去のUndo/Redo履歴を破棄する。
        """

        # SAFE CODE AREA ˅
        self.currentModel = newModel
        self.undoStack.clear()
        self.redoStack.clear()
        self.currentCompositeCommand = None
        self._notifySpectrumChanged(self._createFullSpectrumChangeForCommand(None))
        # SAFE CODE AREA ˄


    # GENERATED CODE AREA: method.beginSpectrumEdit ˅
    def beginSpectrumEdit(self) -> None:
        """
        ドラッグによる連続スペクトル編集を開始する。currentCompositeCommandを生成し、以降の編集Commandを1つの操作としてまとめる準備を行う。
        """

        # SAFE CODE AREA ˅
        # 以降の連続編集を1回のUndo対象にまとめるため、CompositeCommandを作る。
        if self.currentCompositeCommand is not None:
            raise RuntimeError("spectrum edit is already open")
        self.currentCompositeCommand = CompositeSpectrumEditCommand()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.beginSpectrumEdit ˄


    # GENERATED CODE AREA: method.endSpectrumEdit ˅
    def endSpectrumEdit(self) -> None:
        """
        ドラッグによる連続スペクトル編集を終了する。currentCompositeCommandをUndo履歴に追加し、Redo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        # ドラッグ中に実行されたCommandをCompositeとしてUndoスタックへ積む。
        command = self.currentCompositeCommand
        self.currentCompositeCommand = None
        if command is None or len(command.commands) == 0:
            return
        self.undoStack.append(command)
        self.redoStack.clear()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.endSpectrumEdit ˄


    # GENERATED CODE AREA: method.eraseSpectrumBetweenIndexes ˅
    def eraseSpectrumBetweenIndexes(self, startIndex: int, endIndex: int) -> None:
        """
        1次元スペクトルの開始インデックスから終了インデックスまでを連続範囲として消去する。
        """

        # SAFE CODE AREA ˅
        # 1Dドラッグで点が飛んだ場合に、前回indexから今回indexまでを線として削除する。
        indices = self._indexLine(startIndex, endIndex)
        # 1回のドラッグイベントで通過した複数indexを、1つのCommandとして実行する。
        self._executeCommandInOpenEdit(EditSpectrumValuesAtIndexesCommand(
            self.currentModel,
            indices,
            np.zeros(len(indices), dtype=float),
            np.zeros(len(indices), dtype=float),
        ))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumBetweenIndexes ˄


    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˅
    def editSpectrumValueAtIndex(self, index: int, realPart: float, imaginaryPart: float) -> None:
        """
        1次元スペクトルの指定インデックスに対して、実部と虚部を指定値へ直接変更する編集Commandを実行する。
        """

        # SAFE CODE AREA ˅
        # 指定成分の実部・虚部を、複数index用Commandの1要素編集として実行する。
        self._executeUndoableCommand(EditSpectrumValuesAtIndexesCommand(
            self.currentModel,
            [index],
            np.array([realPart], dtype=float),
            np.array([imaginaryPart], dtype=float),
        ))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˄


    # GENERATED CODE AREA: method.restoreSpectrumBetweenIndexes ˅
    def restoreSpectrumBetweenIndexes(self, startIndex: int, endIndex: int) -> None:
        """
        1次元スペクトルの開始インデックスから終了インデックスまでを、フーリエ変換直後の元スペクトル値へ復元する。
        """

        # SAFE CODE AREA ˅
        # 1Dドラッグで点が飛んだ場合に、前回indexから今回indexまでを線として復元する。
        indices = self._indexLine(startIndex, endIndex)
        # 1回のドラッグイベントで通過した複数indexを、1つのCommandとして実行する。
        self._executeCommandInOpenEdit(EditSpectrumValuesAtIndexesCommand(
            self.currentModel,
            indices,
            self.currentModel.realPart[indices],
            self.currentModel.imaginaryPart[indices],
        ))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSpectrumBetweenIndexes ˄


    # GENERATED CODE AREA: method.eraseSpectrumLineAtPosition ˅
    def eraseSpectrumLineAtPosition(self, startRow: int, startCol: int, endRow: int, endCol: int, radius: int) -> None:
        """
        2次元スペクトル上の開始座標から終了座標までを線分として補間し、指定半径で消去する。
        """

        # SAFE CODE AREA ˅
        points = self._linePoints(startRow, startCol, endRow, endCol)
        # 線分上の全点を1つのCommandで処理し、逆FFTとView通知を1回にまとめる。
        self._executeCommandInOpenEdit(
            EraseSpectrumAtPositionsCommand(self.currentModel, points, radius)
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumLineAtPosition ˄


    # GENERATED CODE AREA: method.paintRgbSpectrumLineAtPosition ˅
    def paintRgbSpectrumLineAtPosition(self, startRow: int, startCol: int, endRow: int, endCol: int, radius: int, rgbColor: list) -> None:
        """
        2次元スペクトル上の開始座標から終了座標までを線分として補間し、指定半径とRGB色でペイント編集する。
        """

        # SAFE CODE AREA ˅
        points = self._linePoints(startRow, startCol, endRow, endCol)
        # 線分上の全点を1つのCommandで処理し、逆FFTとView通知を1回にまとめる。
        self._executeCommandInOpenEdit(
            PaintRgbSpectrumAtPositionsCommand(self.currentModel, points, radius, rgbColor)
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.paintRgbSpectrumLineAtPosition ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> bool:
        """
        Undo履歴から直前のCommandを取り出して取り消し、Redo履歴に追加する。
        """

        # SAFE CODE AREA ˅
        # 最後に実行したCommandを取り消し、RedoできるようRedoスタックへ移す。
        command = self.undoStack.pop()
        command.undo()
        self.redoStack.append(command)
        # Undo後の変更範囲だけをViewへ通知する。
        self._notifySpectrumChanged(self._createSpectrumChange(command))
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.redo ˅
    def redo(self) -> bool:
        """
        Redo履歴から直前に取り消したCommandを取り出して再実行し、Undo履歴に戻す。
        """

        # SAFE CODE AREA ˅
        # 直前にUndoしたCommandを再実行し、Undoスタックへ戻す。
        command = self.redoStack.pop()
        command.execute()
        self.undoStack.append(command)
        # Redo後の変更範囲だけをViewへ通知する。
        self._notifySpectrumChanged(self._createSpectrumChange(command))
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.redo ˄


    # GENERATED CODE AREA: method.getData ˅
    def getData(self) -> dict:
        """
        現在のModelが保持する表示用データを取得する。ViewやControllerはModelを直接参照せず、このメソッドを通して取得する。
        """

        # SAFE CODE AREA ˅
        # Viewが表示用の数値配列を取得できるよう、現在ModelのgetDataをContext経由で呼び出す。
        return self.currentModel.getData()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getData ˄


    # GENERATED CODE AREA: method.getImage ˅
    def getImage(self) -> dict:
        """
        現在のModelが生成する表示用画像を取得する。ViewやControllerはModelを直接参照せず、このメソッドを通して取得する。
        """

        # SAFE CODE AREA ˅
        # Viewが表示用のPIL.Imageを取得できるよう、現在ModelのgetImageをContext経由で呼び出す。
        return self.currentModel.getImage()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getImage ˄

    # GENERATED CODE AREA: method.getSpectrumComponent ˅
    def getSpectrumComponent(self):
        """
        現在使用しているModelに対応する編集用スペクトルコンポーネントを取得する。
        """

        # SAFE CODE AREA ˅
        # Contextは現在のModelへ処理を委譲するため、
        # Componentの生成もcurrentModelへ任せる。
        return self.currentModel.getSpectrumComponent()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getSpectrumComponent ˄


    # GENERATED CODE AREA: method.getModelName ˅
    def getModelName(self) -> str:
        """
        現在Contextが保持しているModelのクラス名を文字列として返す。
        """

        # SAFE CODE AREA ˅
        # Viewのステータス表示用に、現在Modelのクラス名だけを返す。
        return self.currentModel.__class__.__name__
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getModelName ˄


    # GENERATED CODE AREA: method.getUndoCount ˅
    def getUndoCount(self) -> int:
        """
        Undo可能なCommand数を返す。
        """

        # SAFE CODE AREA ˅
        # Viewのステータス表示用に、Undo可能なCommand数を返す。
        return len(self.undoStack)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getUndoCount ˄


    # GENERATED CODE AREA: method.getRedoCount ˅
    def getRedoCount(self) -> int:
        """
        Redo可能なCommand数を返す。
        """

        # SAFE CODE AREA ˅
        # Viewのステータス表示用に、Redo可能なCommand数を返す。
        return len(self.redoStack)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getRedoCount ˄


    # GENERATED CODE AREA: method.is1dModel ˅
    def is1dModel(self) -> bool:
        """
        現在のModelがFourier1dModelであるかを判定する。
        """

        # SAFE CODE AREA ˅
        # Controllerが1D専用操作を呼び分けるための判定結果を返す。
        return isinstance(self.currentModel, Fourier1dModel)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.is1dModel ˄


    # GENERATED CODE AREA: method.is2dModel ˅
    def is2dModel(self) -> bool:
        """
        現在のModelがFourier2dModelであるかを判定する。
        """

        # SAFE CODE AREA ˅
        # Controllerが2D専用操作を呼び分けるための判定結果を返す。
        return isinstance(self.currentModel, Fourier2dModel)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.is2dModel ˄


    # GENERATED CODE AREA: method.getInteractiveSpectrumAtIndex ˅
    def getInteractiveSpectrumAtIndex(self, index: int) -> tuple:
        """
        現在の1次元Modelから、指定インデックスの編集用スペクトルの実部と虚部を取得する。
        """

        # SAFE CODE AREA ˅
        # 1D入力欄の表示用に、指定indexの編集用スペクトル実部・虚部をContext経由で返す。
        return self.currentModel.getInteractiveSpectrumAtIndex(index)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getInteractiveSpectrumAtIndex ˄


    # GENERATED CODE AREA: method._executeCommandInOpenEdit ˅
    def _executeCommandInOpenEdit(self, command: SpectrumEditCommand) -> None:
        """
        beginSpectrumEdit()で開いた編集単位の中でだけCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # beginSpectrumEdit()で開いた編集単位の中でだけCommandを実行する。
        open_command = self.currentCompositeCommand
        if open_command is None:
            raise RuntimeError("beginSpectrumEdit() must be called before drag spectrum edits")

        # まずCommandを実行してModel本体の状態を変更する。
        command.execute()
        open_command.add(command)
        # Model状態が変わったので、Viewへ変更範囲だけを通知する。
        self._notifySpectrumChanged(self._createSpectrumChange(command))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._executeCommandInOpenEdit ˄


    # GENERATED CODE AREA: method._executeUndoableCommand ˅
    def _executeUndoableCommand(self, command: SpectrumEditCommand) -> None:
        """
        単発操作だけを1つのCompositeCommandとして実行・保存する。
        """

        # SAFE CODE AREA ˅
        # 単発操作だけを1つのCompositeCommandとして実行・保存する。
        if self.currentCompositeCommand is not None:
            raise RuntimeError("single spectrum edit cannot run during an open spectrum edit")
        self.beginSpectrumEdit()
        try:
            self._executeCommandInOpenEdit(command)
        finally:
            self.endSpectrumEdit()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._executeUndoableCommand ˄


    # GENERATED CODE AREA: method._createFull1dSpectrumChange ˅
    def _createFull1dSpectrumChange(self) -> SpectrumChange:
        """
        1Dではindexを変更開始位置として扱う。全体更新では0から全配列を渡す。
        """

        # SAFE CODE AREA ˅
        # 1Dではindexを変更開始位置として扱う。全体更新では0から全配列を渡す。
        spectrum = self.currentModel.interactivePowerSpectrum
        return Spectrum1dChange(index=0, changedPowerSpectrum=np.copy(spectrum))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createFull1dSpectrumChange ˄


    # GENERATED CODE AREA: method._createFull2dSpectrumChange ˅
    def _createFull2dSpectrumChange(self) -> SpectrumChange:
        """
        2Dでは現在スペクトルの縦横サイズを通知情報へ入れる。
        """

        # SAFE CODE AREA ˅
        # 2Dでは現在スペクトルの縦横サイズを通知情報へ入れる。
        spectrum = self.currentModel.interactivePowerSpectrum
        height = int(spectrum.shape[0])
        width = int(spectrum.shape[1])
        return Spectrum2dChange(x=0, y=0, width=width, height=height, changedPowerSpectrum=np.copy(spectrum))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createFull2dSpectrumChange ˄


    # GENERATED CODE AREA: method._create1dSpectrumChangeForRange ˅
    def _create1dSpectrumChangeForRange(self, start: int, stop: int) -> Spectrum1dChange:
        """
        複数indexをまとめて通知する場合は、startからstopまでの連続範囲を切り出す。
        """

        # SAFE CODE AREA ˅
        # 複数indexをまとめて通知する場合は、startからstopまでの連続範囲を切り出す。
        spectrum = self.currentModel.interactivePowerSpectrum
        size = int(spectrum.shape[0])
        raw_start = int(start)
        raw_stop = int(stop)
        normalized_start = raw_start + size if raw_start < 0 else raw_start
        normalized_stop = raw_stop + size if raw_stop < 0 or (raw_start < 0 and raw_stop == 0) else raw_stop
        start = int(np.clip(normalized_start, 0, size - 1))
        stop = int(np.clip(normalized_stop, start + 1, size))
        return Spectrum1dChange(index=start, changedPowerSpectrum=np.copy(spectrum[start:stop]))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._create1dSpectrumChangeForRange ˄


    # GENERATED CODE AREA: method._create2dSpectrumChangeForRect ˅
    def _create2dSpectrumChangeForRect(self, rect: tuple) -> Spectrum2dChange:
        """
        rectは(row_start, row_stop, col_start, col_stop)。通知ではx=col, y=rowとして渡す。
        """

        # SAFE CODE AREA ˅
        # rectは(row_start, row_stop, col_start, col_stop)。通知ではx=col, y=rowとして渡す。
        spectrum = self.currentModel.interactivePowerSpectrum
        row_start, row_stop, col_start, col_stop = rect
        changed = np.copy(spectrum[row_start:row_stop, col_start:col_stop])
        return Spectrum2dChange(
            x=col_start,
            y=row_start,
            width=col_stop - col_start,
            height=row_stop - row_start,
            changedPowerSpectrum=changed,
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._create2dSpectrumChangeForRect ˄


    # GENERATED CODE AREA: method._createSpectrumChange ˅
    def _createSpectrumChange(self, command: SpectrumEditCommand) -> SpectrumChange:
        """
        Commandが保持する変更種別に応じて、部分更新または全体更新の通知を作る。
        """

        # SAFE CODE AREA ˅
        # Commandが保持する変更種別に応じて、部分更新または全体更新の通知を作る。
        return self.spectrumChangeFactories[command.spectrumChangeKind](command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createSpectrumChange ˄


    # GENERATED CODE AREA: method._editCommandsIn ˅
    def _editCommandsIn(self, command: SpectrumEditCommand) -> list:
        """
        Undo/Redo通知ではComposite、通常通知では単一Commandを同じ形で扱う。
        """

        # SAFE CODE AREA ˅
        # Undo/Redo通知ではComposite、通常通知では単一Commandを同じ形で扱う。
        if isinstance(command, CompositeSpectrumEditCommand):
            return command.commands
        return [command]
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._editCommandsIn ˄


    # GENERATED CODE AREA: method._create1dSpectrumChangeForCommand ˅
    def _create1dSpectrumChangeForCommand(self, command: SpectrumEditCommand) -> Spectrum1dChange:
        """
        1D編集Command群のindexをまとめ、連続範囲として通知する。
        """

        # SAFE CODE AREA ˅
        # 1D編集Command群のindexをまとめ、連続範囲として通知する。
        indices = []
        for child in self._editCommandsIn(command):
            indices.extend(child.indexes)
        return self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._create1dSpectrumChangeForCommand ˄


    # GENERATED CODE AREA: method._create2dSpectrumChangeForCommand ˅
    def _create2dSpectrumChangeForCommand(self, command: SpectrumEditCommand) -> Spectrum2dChange:
        """
        2D編集Command群の矩形範囲をまとめ、すべてを含む1つの矩形として通知する。
        """

        # SAFE CODE AREA ˅
        # 2D編集Command群の矩形範囲をまとめ、すべてを含む1つの矩形として通知する。
        rects = []
        for child in self._editCommandsIn(command):
            rect = self.currentModel.getSpectrumRectForPositions(child.positions, child.radius)
            rects.append(rect)

        row_start = min(rect[0] for rect in rects)
        row_stop = max(rect[1] for rect in rects)
        col_start = min(rect[2] for rect in rects)
        col_stop = max(rect[3] for rect in rects)
        return self._create2dSpectrumChangeForRect((row_start, row_stop, col_start, col_stop))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._create2dSpectrumChangeForCommand ˄


    # GENERATED CODE AREA: method._createFullSpectrumChangeForCommand ˅
    def _createFullSpectrumChangeForCommand(self, command: SpectrumEditCommand) -> SpectrumChange:
        """
        Model差し替えやResetは、現在Modelの次元に応じた全体更新として通知する。
        """

        # SAFE CODE AREA ˅
        # Model差し替えやResetは、現在Modelの次元に応じた全体更新として通知する。
        return {
            Fourier1dModel: self._createFull1dSpectrumChange,
            Fourier2dModel: self._createFull2dSpectrumChange,
        }[type(self.currentModel)]()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createFullSpectrumChangeForCommand ˄


    # GENERATED CODE AREA: method._linePoints ˅
    def _linePoints(self, startRow: int, startCol: int, endRow: int, endCol: int) -> list:
        """
        2次元編集で開始座標から終了座標までを補間し、線分上の座標列を生成する。
        """

        # SAFE CODE AREA ˅
        # 前回座標と今回座標の間を線形補間し、イベントが飛んでも点ではなく線として編集する。
        start_row = int(startRow)
        start_col = int(startCol)
        end_row = int(endRow)
        end_col = int(endCol)
        steps = max(abs(end_row - start_row), abs(end_col - start_col))
        rows = np.rint(np.linspace(start_row, end_row, steps + 1)).astype(int)
        cols = np.rint(np.linspace(start_col, end_col, steps + 1)).astype(int)
        points = []
        for row, col in zip(rows, cols):
            point = (int(row), int(col))
            points.append(point)
        return points
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._linePoints ˄


    # GENERATED CODE AREA: method._indexLine ˅
    def _indexLine(self, startIndex: int, endIndex: int) -> list:
        """
        1次元編集で開始インデックスから終了インデックスまでを補間し、連続したインデックス列を生成する。
        """

        # SAFE CODE AREA ˅
        # 1Dでも前回indexから今回indexまでの間を連続範囲として編集できるようにする。
        start = int(startIndex)
        end = int(endIndex)
        step = 1 if end >= start else -1
        return list(range(start, end + step, step))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._indexLine ˄


    # GENERATED CODE AREA: method._notifySpectrumChanged ˅
    def _notifySpectrumChanged(self, change: SpectrumChange) -> None:
        """
        登録済みの通知用listenerへ、指定されたSpectrumChangeを渡して変更通知を行う。
        """

        # SAFE CODE AREA ˅
        # View側から登録された関数へ変更内容を通知する。
        self.spectrumChangedListener(change)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._notifySpectrumChanged ˄

