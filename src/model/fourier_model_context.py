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
from .set_source_data_command import SetSourceDataCommand
from .edit_spectrum_value_at_index_command import EditSpectrumValueAtIndexCommand
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
    def __init__(self, spectrumChangedListener: Callable[[SpectrumChange], None] | None = None) -> None:
        """
        FourierModelContextを初期化する。初期Model、Undo/Redo履歴、通知用関数などを設定する。
        """

        # 現在操作対象となっているFourierModelを保持する。
        self.currentModel: Fourier1dModel | Fourier2dModel = Fourier2dModel(sourceData=np.zeros((1, 1)))

        # Undo可能なCommandを保持するスタックである。
        self.undoStack: list[SpectrumEditCommand] = []

        # Redo可能なCommandを保持するスタックである。
        self.redoStack: list[SpectrumEditCommand] = []

        # スペクトル変更時に呼び出す通知用関数を保持する。View側から渡された操作を保持し、SpectrumChangeを引数として呼び出す。
        self.spectrumChangedListener: Callable[[SpectrumChange], None] | None = spectrumChangedListener

        # ドラッグ操作中に発生した複数の編集Commandを一時的にまとめるCompositeSpectrumEditCommandを保持する。
        self.currentCompositeCommand: CompositeSpectrumEditCommand | None = None

        # SAFE CODE AREA ˅
        # 固定領域で初期化したフィールドをそのまま使用するため、SAFE内の追加初期化は行わない。
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.set1dSourceData ˅
    def set1dSourceData(self, sourceData: np.ndarray) -> None:
        """
        1次元元データを設定する。現在のModelが1次元の場合はSetSourceDataCommandを実行し、2次元Modelから1次元Modelへ切り替える必要がある場合はChangeFourierModelCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # 入力データを1Dモデル用のfloat配列へそろえる。
        data = np.asarray(sourceData, dtype=float)
        # すでに1Dモデルならデータ差し替えCommand、2DモデルならModel切り替えCommandを使う。
        command = (
            SetSourceDataCommand(self.currentModel, data)
            if isinstance(self.currentModel, Fourier1dModel)
            else ChangeFourierModelCommand(self, Fourier1dModel(data))
        )
        self._executeEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set1dSourceData ˄


    # GENERATED CODE AREA: method.set2dSourceData ˅
    def set2dSourceData(self, sourceData: np.ndarray) -> None:
        """
        2次元元データを設定する。現在のModelが2次元の場合はSetSourceDataCommandを実行し、1次元Modelから2次元Modelへ切り替える必要がある場合はChangeFourierModelCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # 入力データを2Dモデル用のfloat配列へそろえる。
        data = np.asarray(sourceData, dtype=float)
        # すでに2Dモデルならデータ差し替えCommand、1DモデルならModel切り替えCommandを使う。
        command = (
            SetSourceDataCommand(self.currentModel, data)
            if isinstance(self.currentModel, Fourier2dModel)
            else ChangeFourierModelCommand(self, Fourier2dModel(data))
        )
        self._executeEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set2dSourceData ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        現在のModelの編集用スペクトルを元スペクトル状態に戻すResetSpectrumCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # リセットもUndo可能な編集として扱う。
        self._executeEdit(ResetSpectrumCommand(self.currentModel))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method.beginSpectrumEdit ˅
    def beginSpectrumEdit(self) -> None:
        """
        ドラッグによる連続スペクトル編集を開始する。currentCompositeCommandを生成し、以降の編集Commandを1つの操作としてまとめる準備を行う。
        """

        # SAFE CODE AREA ˅
        # 以降の連続編集を1回のUndo対象にまとめるため、CompositeCommandを作る。
        self.currentCompositeCommand = CompositeSpectrumEditCommand()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.beginSpectrumEdit ˄


    # GENERATED CODE AREA: method.endSpectrumEdit ˅
    def endSpectrumEdit(self) -> None:
        """
        ドラッグによる連続スペクトル編集を終了する。currentCompositeCommandをUndo履歴に追加し、Redo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        # beginされていない場合は、終了対象がないため何もしない。
        if self.currentCompositeCommand is None:
            return
        # ドラッグ中に実行されたCommandがある場合だけ、CompositeをUndoスタックへ積む。
        if self.currentCompositeCommand.commands:
            self.undoStack.append(self.currentCompositeCommand)
            self.redoStack.clear()
        # ドラッグ編集のまとめ処理を終了する。
        self.currentCompositeCommand = None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.endSpectrumEdit ˄


    # GENERATED CODE AREA: method.eraseSpectrumBetweenIndexes ˅
    def eraseSpectrumBetweenIndexes(self, startIndex: int, endIndex: int) -> None:
        # SAFE CODE AREA ˅
        # 1Dドラッグで点が飛んだ場合に、前回indexから今回indexまでを線として削除する。
        self._require1dModel()
        indices = self._indexLine(startIndex, endIndex)
        commands = [EditSpectrumValueAtIndexCommand(self.currentModel, index, 0.0, 0.0) for index in indices]
        self._executeEditBatch(
            commands,
            lambda: self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1),
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumBetweenIndexes ˄


    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˅
    def editSpectrumValueAtIndex(self, index: int, realPart: float, imaginaryPart: float) -> None:
        # SAFE CODE AREA ˅
        # 1D専用操作なので、現在Modelの型を先に検査する。
        self._require1dModel()
        # 指定成分の実部・虚部を直接書き換えるCommandを実行する。
        self._executeEdit(EditSpectrumValueAtIndexCommand(self.currentModel, index, realPart, imaginaryPart))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˄


    # GENERATED CODE AREA: method.restoreSpectrumBetweenIndexes ˅
    def restoreSpectrumBetweenIndexes(self, startIndex: int, endIndex: int) -> None:
        # SAFE CODE AREA ˅
        # 1Dドラッグで点が飛んだ場合に、前回indexから今回indexまでを線として復元する。
        self._require1dModel()
        indices = self._indexLine(startIndex, endIndex)
        commands = [
            EditSpectrumValueAtIndexCommand(
                self.currentModel,
                index,
                self.currentModel.realPart[index],
                self.currentModel.imaginaryPart[index],
            )
            for index in indices
        ]
        self._executeEditBatch(
            commands,
            lambda: self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1),
        )
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSpectrumBetweenIndexes ˄


    # GENERATED CODE AREA: method.eraseSpectrumLineAtPosition ˅
    def eraseSpectrumLineAtPosition(self, startRow: int, startCol: int, endRow: int, endCol: int, radius: int) -> None:
        # SAFE CODE AREA ˅
        # 2Dドラッグでイベント間隔が空いた場合に、前回座標と今回座標を線で結んで削除する。
        self._require2dModel()
        points = self._linePoints(startRow, startCol, endRow, endCol)
        # 線分上の全点を1つのCommandで処理し、逆FFTとView通知を1回にまとめる。
        self._executeEdit(EraseSpectrumAtPositionsCommand(self.currentModel, points, radius))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumLineAtPosition ˄


    # FIXED CODE AREA: method.paintRgbSpectrumLineAtPosition ˅
    def paintRgbSpectrumLineAtPosition(self, startRow: int, startCol: int, endRow: int, endCol: int, radius: int, rgbColor: list[float]) -> None:
        # SAFE CODE AREA ˅
        # 2Dドラッグでイベント間隔が空いた場合に、前回座標と今回座標を線で結んでRGBペイントする。
        self._require2dModel()
        points = self._linePoints(startRow, startCol, endRow, endCol)
        # 線分上の全点を1つのCommandで処理し、逆FFTとView通知を1回にまとめる。
        self._executeEdit(PaintRgbSpectrumAtPositionsCommand(self.currentModel, points, radius, rgbColor))
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.paintRgbSpectrumLineAtPosition ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> bool:
        """
        Undo履歴から直前のCommandを取り出して取り消し、Redo履歴に追加する。
        """

        # SAFE CODE AREA ˅
        # Undo対象が無ければ何もせず、呼び出し側へ失敗を返す。
        if not self.undoStack:
            return False
        # 最後に実行したCommandを取り消し、RedoできるようRedoスタックへ移す。
        command = self.undoStack.pop()
        command.undo()
        self.redoStack.append(command)
        # Undo後の変更範囲だけをViewへ通知する。
        self._notifySpectrumChanged(self._createSpectrumChangeForCommand(command))
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.redo ˅
    def redo(self) -> bool:
        """
        Redo履歴から直前に取り消したCommandを取り出して再実行し、Undo履歴に戻す。
        """

        # SAFE CODE AREA ˅
        # Redo対象が無ければ何もせず、呼び出し側へ失敗を返す。
        if not self.redoStack:
            return False
        # 直前にUndoしたCommandを再実行し、Undoスタックへ戻す。
        command = self.redoStack.pop()
        command.execute()
        self.undoStack.append(command)
        # Redo後の変更範囲だけをViewへ通知する。
        self._notifySpectrumChanged(self._createSpectrumChangeForCommand(command))
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.redo ˄


    # FIXED CODE AREA: method.getData ˅
    def getData(self) -> dict[PaneType, np.ndarray | None]:
        # SAFE CODE AREA ˅
        # Viewが表示用の数値配列を取得できるよう、現在ModelのgetDataをContext経由で呼び出す。
        return self.currentModel.getData()
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.getData ˄


    # FIXED CODE AREA: method.getImage ˅
    def getImage(self) -> dict[PaneType, Image.Image | None]:
        # SAFE CODE AREA ˅
        # Viewが表示用のPIL.Imageを取得できるよう、現在ModelのgetImageをContext経由で呼び出す。
        return self.currentModel.getImage()
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.getImage ˄


    # GENERATED CODE AREA: method.getModelName ˅
    def getModelName(self) -> str:
        # SAFE CODE AREA ˅
        # Viewのステータス表示用に、現在Modelのクラス名だけを返す。
        return self.currentModel.__class__.__name__
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getModelName ˄


    # GENERATED CODE AREA: method.getUndoCount ˅
    def getUndoCount(self) -> int:
        # SAFE CODE AREA ˅
        # Viewのステータス表示用に、Undo可能なCommand数を返す。
        return len(self.undoStack)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getUndoCount ˄


    # GENERATED CODE AREA: method.getRedoCount ˅
    def getRedoCount(self) -> int:
        # SAFE CODE AREA ˅
        # Viewのステータス表示用に、Redo可能なCommand数を返す。
        return len(self.redoStack)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.getRedoCount ˄


    # GENERATED CODE AREA: method.is1dModel ˅
    def is1dModel(self) -> bool:
        # SAFE CODE AREA ˅
        # Controllerが1D専用操作を呼び分けるための判定結果を返す。
        return isinstance(self.currentModel, Fourier1dModel)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.is1dModel ˄


    # GENERATED CODE AREA: method.is2dModel ˅
    def is2dModel(self) -> bool:
        # SAFE CODE AREA ˅
        # Controllerが2D専用操作を呼び分けるための判定結果を返す。
        return isinstance(self.currentModel, Fourier2dModel)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.is2dModel ˄


    # FIXED CODE AREA: method.getInteractiveSpectrumAtIndex ˅
    def getInteractiveSpectrumAtIndex(self, index: int) -> tuple[float, float]:
        # SAFE CODE AREA ˅
        # 1D入力欄の表示用に、指定indexの編集用スペクトル実部・虚部をContext経由で返す。
        self._require1dModel()
        return self.currentModel.getInteractiveSpectrumAtIndex(index)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.getInteractiveSpectrumAtIndex ˄


    # GENERATED CODE AREA: method._require1dModel ˅
    def _require1dModel(self) -> None:
        # SAFE CODE AREA ˅
        # 誤って2Dモデルへ1D編集を実行しないよう、Context入口で型を保証する。
        if not isinstance(self.currentModel, Fourier1dModel):
            raise TypeError("Current model is not Fourier1dModel.")
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._require1dModel ˄


    # GENERATED CODE AREA: method._require2dModel ˅
    def _require2dModel(self) -> None:
        # SAFE CODE AREA ˅
        # 誤って1Dモデルへ2D編集を実行しないよう、Context入口で型を保証する。
        if not isinstance(self.currentModel, Fourier2dModel):
            raise TypeError("Current model is not Fourier2dModel.")
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._require2dModel ˄


    # GENERATED CODE AREA: method._executeEdit ˅
    def _executeEdit(self, command: SpectrumEditCommand) -> None:
        # SAFE CODE AREA ˅
        # まずCommandを実行してModel本体の状態を変更する。
        command.execute()
        if self.currentCompositeCommand is None:
            # 通常操作はUndoスタックへ積み、新規編集なのでRedo履歴は破棄する。
            self.undoStack.append(command)
            self.redoStack.clear()
        else:
            # ドラッグ中は個別CommandをUndoスタックへ積まず、Compositeの中へまとめる。
            self.currentCompositeCommand.add(command)
        # Model状態が変わったので、Viewへ変更範囲だけを通知する。
        self._notifySpectrumChanged(self._createSpectrumChangeForCommand(command))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._executeEdit ˄


    # FIXED CODE AREA: method._executeEditBatch ˅
    def _executeEditBatch(self, commands: list[SpectrumEditCommand], changeFactory: Callable[[], SpectrumChange]) -> None:
        # SAFE CODE AREA ˅
        # 複数の点編集を1つの編集操作として実行し、View通知も1回にまとめる。
        commands = [command for command in commands if command is not None]
        if not commands:
            return

        composite = CompositeSpectrumEditCommand()
        for command in commands:
            command.execute()
            composite.add(command)

        stored_command = composite if len(commands) > 1 else commands[0]
        if self.currentCompositeCommand is None:
            self.undoStack.append(stored_command)
            self.redoStack.clear()
        else:
            self.currentCompositeCommand.add(stored_command)

        self._notifySpectrumChanged(changeFactory())
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._executeEditBatch ˄


    # GENERATED CODE AREA: method._createSpectrumChangeForCommand ˅
    def _createSpectrumChangeForCommand(self, command: SpectrumEditCommand) -> SpectrumChange:
        # SAFE CODE AREA ˅
        # Commandの種類から、Viewが部分更新できる最小範囲の変更情報を作る。
        if isinstance(command, EditSpectrumValueAtIndexCommand):
            return self._create1dSpectrumChangeForRange(command.index, command.index + 1)
        if isinstance(command, (EraseSpectrumAtPositionsCommand, PaintRgbSpectrumAtPositionsCommand)):
            return self._create2dSpectrumChangeForLine(command.positions, command.radius)
        if isinstance(command, CompositeSpectrumEditCommand):
            return self._createCompositeSpectrumChange(command)
        return self._createFullSpectrumChange()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createSpectrumChangeForCommand ˄


    # GENERATED CODE AREA: method._createFullSpectrumChange ˅
    def _createFullSpectrumChange(self) -> SpectrumChange:
        # SAFE CODE AREA ˅
        # ファイル読み込み、Model切り替え、Resetなどは全スペクトルが変更されたものとして通知する。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        spectrum_copy = np.copy(spectrum) if spectrum is not None else None
        if isinstance(self.currentModel, Fourier1dModel):
            # 1Dではindexを変更開始位置として扱う。全体更新では0から全配列を渡す。
            return Spectrum1dChange(index=0, changedPowerSpectrum=spectrum_copy)

        # 2Dでは現在スペクトルの縦横サイズを通知情報へ入れる。
        height = int(spectrum.shape[0]) if spectrum is not None and spectrum.ndim >= 2 else 0
        width = int(spectrum.shape[1]) if spectrum is not None and spectrum.ndim >= 2 else 0
        return Spectrum2dChange(x=0, y=0, width=width, height=height, changedPowerSpectrum=spectrum_copy)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createFullSpectrumChange ˄


    # GENERATED CODE AREA: method._create1dSpectrumChangeForRange ˅
    def _create1dSpectrumChangeForRange(self, start: int, stop: int) -> Spectrum1dChange:
        # SAFE CODE AREA ˅
        # 複数indexをまとめて通知する場合は、startからstopまでの連続範囲を切り出す。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None:
            return Spectrum1dChange(index=0, changedPowerSpectrum=None)
        size = int(spectrum.shape[0]) if spectrum.ndim >= 1 else 0
        if size <= 0:
            return Spectrum1dChange(index=0, changedPowerSpectrum=np.array([]))
        raw_start = int(start)
        raw_stop = int(stop)
        normalized_start = raw_start + size if raw_start < 0 else raw_start
        normalized_stop = raw_stop + size if raw_stop < 0 or (raw_start < 0 and raw_stop == 0) else raw_stop
        start = int(np.clip(normalized_start, 0, size - 1))
        stop = int(np.clip(normalized_stop, start + 1, size))
        return Spectrum1dChange(index=start, changedPowerSpectrum=np.copy(spectrum[start:stop]))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._create1dSpectrumChangeForRange ˄


    # FIXED CODE AREA: method._create2dSpectrumChangeForRect ˅
    def _create2dSpectrumChangeForRect(self, rect: tuple[int, int, int, int]) -> Spectrum2dChange:
        # SAFE CODE AREA ˅
        # rectは(row_start, row_stop, col_start, col_stop)。通知ではx=col, y=rowとして渡す。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None or getattr(spectrum, "ndim", 0) < 2:
            return Spectrum2dChange(x=0, y=0, width=0, height=0, changedPowerSpectrum=None)
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
    # FIXED CODE AREA: method._create2dSpectrumChangeForRect ˄


    # FIXED CODE AREA: method._create2dSpectrumChangeForLine ˅
    def _create2dSpectrumChangeForLine(self, points: list[tuple[int, int]], radius: int) -> Spectrum2dChange:
        # SAFE CODE AREA ˅
        # 線分上の複数ブラシ編集を、すべて含む1つの矩形changeへまとめる。
        if not isinstance(self.currentModel, Fourier2dModel):
            return Spectrum2dChange(x=0, y=0, width=0, height=0, changedPowerSpectrum=None)
        rect = self.currentModel.getSpectrumRectForPositions(points, radius)
        if rect is None:
            return Spectrum2dChange(x=0, y=0, width=0, height=0, changedPowerSpectrum=None)
        return self._create2dSpectrumChangeForRect(rect)
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._create2dSpectrumChangeForLine ˄


    # GENERATED CODE AREA: method._createCompositeSpectrumChange ˅
    def _createCompositeSpectrumChange(self, command: CompositeSpectrumEditCommand) -> SpectrumChange:
        # SAFE CODE AREA ˅
        # CompositeCommandのUndo/Redoでは、含まれる編集範囲を1つの連続範囲または矩形にまとめて通知する。
        commands = self._flattenCommands(command)
        if not commands:
            return self._createFullSpectrumChange()
        if isinstance(self.currentModel, Fourier1dModel):
            indices = []
            spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
            size = int(spectrum.shape[0]) if spectrum is not None and spectrum.ndim >= 1 else 0
            for child in commands:
                if not isinstance(child, EditSpectrumValueAtIndexCommand):
                    return self._createFullSpectrumChange()
                index = int(child.index)
                if size > 0 and index < 0:
                    index += size
                indices.append(index)
            if not indices:
                return self._createFullSpectrumChange()
            return self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1)

        if not isinstance(self.currentModel, Fourier2dModel):
            return self._createFullSpectrumChange()

        rects = []
        for child in commands:
            if isinstance(child, (EraseSpectrumAtPositionsCommand, PaintRgbSpectrumAtPositionsCommand)):
                rect = self.currentModel.getSpectrumRectForPositions(child.positions, child.radius)
                if rect is not None:
                    rects.append(rect)
                continue
            return self._createFullSpectrumChange()

        if not rects:
            return self._createFullSpectrumChange()
        row_start = min(rect[0] for rect in rects)
        row_stop = max(rect[1] for rect in rects)
        col_start = min(rect[2] for rect in rects)
        col_stop = max(rect[3] for rect in rects)
        return self._create2dSpectrumChangeForRect((row_start, row_stop, col_start, col_stop))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._createCompositeSpectrumChange ˄


    # FIXED CODE AREA: method._linePoints ˅
    def _linePoints(self, startRow: int, startCol: int, endRow: int, endCol: int) -> list[tuple[int, int]]:
        # SAFE CODE AREA ˅
        # 前回座標と今回座標の間を線形補間し、イベントが飛んでも点ではなく線として編集する。
        start_row = int(startRow)
        start_col = int(startCol)
        end_row = int(endRow)
        end_col = int(endCol)
        steps = max(abs(end_row - start_row), abs(end_col - start_col))
        if steps == 0:
            return [(start_row, start_col)]

        rows = np.rint(np.linspace(start_row, end_row, steps + 1)).astype(int)
        cols = np.rint(np.linspace(start_col, end_col, steps + 1)).astype(int)
        points = []
        for row, col in zip(rows, cols):
            point = (int(row), int(col))
            if not points or points[-1] != point:
                points.append(point)
        return points
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._linePoints ˄


    # FIXED CODE AREA: method._indexLine ˅
    def _indexLine(self, startIndex: int, endIndex: int) -> list[int]:
        # SAFE CODE AREA ˅
        # 1Dでも前回indexから今回indexまでの間を連続範囲として編集できるようにする。
        start = int(startIndex)
        end = int(endIndex)
        step = 1 if end >= start else -1
        return list(range(start, end + step, step))
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._indexLine ˄


    # FIXED CODE AREA: method._flattenCommands ˅
    def _flattenCommands(self, command: SpectrumEditCommand) -> list[SpectrumEditCommand]:
        # SAFE CODE AREA ˅
        # 入れ子になったCompositeCommandを、変更範囲計算しやすいよう通常Commandのリストに展開する。
        if isinstance(command, CompositeSpectrumEditCommand):
            flattened: list[SpectrumEditCommand] = []
            for child in command.commands:
                flattened.extend(self._flattenCommands(child))
            return flattened
        return [command]
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._flattenCommands ˄


    # GENERATED CODE AREA: method._notifySpectrumChanged ˅
    def _notifySpectrumChanged(self, change: SpectrumChange) -> None:
        # SAFE CODE AREA ˅
        # View側から登録された関数がある場合だけ通知する。
        if callable(self.spectrumChangedListener):
            self.spectrumChangedListener(change)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._notifySpectrumChanged ˄
