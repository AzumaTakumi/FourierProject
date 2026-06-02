from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from typing import Callable
import numpy as np
from .composite_spectrum_edit_command import CompositeSpectrumEditCommand
from .fourier_model import FourierModel
from .spectrum_change import SpectrumChange
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
from .fourier_1_d_model import Fourier1dModel
from .fourier_2_d_model import Fourier2dModel

# データ更新用コマンド
from .set_1_d_source_data_command import Set1dSourceDataCommand
from .set_2_d_source_data_command import Set2dSourceDataCommand
from .change_fourier_model_command import ChangeFourierModelCommand

# １次元編集用コマンド
from .erase_spectrum_at_index_command import EraseSpectrumAtIndexCommand
from .restore_spectrum_at_index_command import RestoreSpectrumAtIndexCommand
from .edit_spectrum_value_at_index_command import EditSpectrumValueAtIndexCommand

# ２次元編集用コマンド
from .erase_spectrum_at_position_command import EraseSpectrumAtPositionCommand
from .paint_rgb_spectrum_at_position_command import PaintRgbSpectrumAtPositionCommand
from .reset_spectrum_command import ResetSpectrumCommand

# View送信用のスペクトル変更クラス
from .spectrum_1_d_change import Spectrum1dChange
from .spectrum_2_d_change import Spectrum2dChange
# SAFE CODE AREA ˄

class FourierModelContext(object):
    # GENERATED CODE AREA: class.header ˅
    """
    現在使用しているFourierModelとUndo/Redo履歴を管理するクラスである。Controllerからの操作を受け取り、必要なCommandを生成・実行し、Modelの変更履歴を管理する。また、スペクトル変更時にはViewから渡された通知用関数を呼び出す。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self, spectrumChangedListener: Callable) -> None:
        """
        FourierModelContextを初期化する。初期Model、Undo/Redo履歴、通知用関数などを設定する。
        """

        # 現在操作対象となっているFourierModelを保持する。
        self.currentModel: Fourier1dModel | Fourier2dModel = Fourier2dModel(sourceData=np.zeros((1, 1)))

        # Undo可能なCommandを保持するスタックである。
        self.undoStack: list = []

        # Redo可能なCommandを保持するスタックである。
        self.redoStack: list = []

        # スペクトル変更時に呼び出す通知用関数を保持する。View側から渡された操作を保持し、SpectrumChangeを引数として呼び出す。
        self.spectrumChangedListener: Callable = spectrumChangedListener

        # ドラッグ操作中に発生した複数の編集Commandを一時的にまとめるCompositeSpectrumEditCommandを保持する。
        self.currentCompositeCommand: CompositeSpectrumEditCommand = None

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # FIXED CODE AREA: method._model ˅
    def _model(self) -> FourierModel:
        """
        現在操作対象となっているFourierModelを返す。
        """

        # SAFE CODE AREA ˅
        return self.currentModel
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._model ˄


    # GENERATED CODE AREA: method.set1dSourceData ˅
    def set1dSourceData(self, sourceData: np.ndarray) -> None:
        """
        1次元元データを設定する。現在のModelが1次元の場合はSet1dSourceDataCommandを実行し、2次元Modelから1次元Modelへ切り替える必要がある場合はChangeFourierModelCommandを実行する。
        """

        # SAFE CODE AREA ˅
        commands = (
            ChangeFourierModelCommand(self, Fourier1dModel(sourceData)),
            Set1dSourceDataCommand(self.currentModel, sourceData),
        )
        self._executeEdit(commands[self.currentModel.sourceData.ndim == 1])
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set1dSourceData ˄


    # GENERATED CODE AREA: method.set2dSourceData ˅
    def set2dSourceData(self, sourceData: np.ndarray) -> None:
        """
        2次元元データを設定する。現在のModelが2次元の場合はSet2dSourceDataCommandを実行し、1次元Modelから2次元Modelへ切り替える必要がある場合はChangeFourierModelCommandを実行する。
        """

        # SAFE CODE AREA ˅
        commands = (
            ChangeFourierModelCommand(self, Fourier2dModel(sourceData)),
            Set2dSourceDataCommand(self.currentModel, sourceData),
        )
        self._executeEdit(commands[self.currentModel.sourceData.ndim == 2])
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set2dSourceData ˄


    # GENERATED CODE AREA: method.setModel ˅
    def setModel(self, model: FourierModel) -> None:
        """
        現在のModelを指定されたFourierModelに差し替える。
        """

        # SAFE CODE AREA ˅
        pass
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setModel ˄


    # GENERATED CODE AREA: method._notifySpectrumChanged ˅
    def _notifySpectrumChanged(self, change: SpectrumChange) -> None:
        """
        スペクトル変更をView側へ通知する。Viewから渡されたspectrumChangedListenerにSpectrumChangeを渡して呼び出す。
        """

        # SAFE CODE AREA ˅
        self.spectrumChangedListener(change)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._notifySpectrumChanged ˄


    # GENERATED CODE AREA: method._executeEdit ˅
    def _executeEdit(self, command: SpectrumEditCommand) -> None:
        """
        指定されたSpectrumEditCommandを実行し、Undo履歴に追加する。新しい編集が行われた場合、Redo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        command.execute()
        change_cls = (Spectrum2dChange, Spectrum1dChange)[self.currentModel.spectrum.ndim == 1]
        self._notifySpectrumChanged(change_cls(self.currentModel.spectrum))
        self.undoStack.append(command)
        self.redoStack.clear()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._executeEdit ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        Undo履歴から直前のCommandを取り出して取り消し、Redo履歴に追加する。
        """

        # SAFE CODE AREA ˅
        try:
            self.undoStack[-1].undo()
            self.redoStack.append(self.undoStack.pop())
        except IndexError:
            return False
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄


    # GENERATED CODE AREA: method.redo ˅
    def redo(self) -> None:
        """
        Redo履歴から直前に取り消したCommandを取り出して再実行し、Undo履歴に戻す。
        """

        # SAFE CODE AREA ˅
        try:
            self.redoStack[-1].execute()
            self.undoStack.append(self.redoStack.pop())
        except IndexError:
            return False
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.redo ˄


    # GENERATED CODE AREA: method._clearStack ˅
    def _clearStack(self) -> None:
        """
        Undo履歴とRedo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        self.undoStack.clear()
        self.redoStack.clear()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._clearStack ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtIndex ˅
    def eraseSpectrumAtIndex(self, index: int) -> None:
        """
        指定indexの周波数成分を編集する。成分を除去する機能。編集結果をinteractive*に反映する。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        self._executeEdit(EraseSpectrumAtIndexCommand(self.currentModel, index))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtIndex ˄


    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˅
    def restoreSpectrumAtIndex(self, index: int) -> None:
        """
        指定indexの周波数成分を編集する。成分をもとに戻す機能。編集結果をinteractive*に反映する。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        self._executeEdit(RestoreSpectrumAtIndexCommand(self.currentModel, index))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˄


    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˅
    def editSpectrumValueAtIndex(self, index: int, realPart: float, imaginaryPart: float) -> None:
        """
        Undo操作で値を戻す際に使用する。restoreSpectrumAtIndex(index)で戻す操作は不適切であり、本来戻す可能性がある値と異なるため、この操作を追加した。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        self._executeEdit(EditSpectrumValueAtIndexCommand(self.currentModel, index, realPart, imaginaryPart))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˅
    def eraseSpectrumAtPosition(self, row: int, col: int, radius: int) -> None:
        """
        指定(row, col)の周波数成分を削除する。radiusは半径の大きさ内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        self._executeEdit(EraseSpectrumAtPositionCommand(self.currentModel, row, col, radius))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˅
    def paintRgbSpectrumAtPosition(self, row: int, col: int, radius: int, rgbColor: list) -> None:
        """
        rgbの場合のスペクトルペイント編集。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        self._executeEdit(PaintRgbSpectrumAtPositionCommand(self.currentModel, row, col, radius, rgbColor))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.beginSpectrumEdit ˅
    def beginSpectrumEdit(self) -> None:
        """
        ドラッグによる連続スペクトル編集を開始する。currentCompositeCommandを生成し、以降の編集Commandを1つの操作としてまとめる準備を行う。
        """

        # SAFE CODE AREA ˅
        self.currentCompositeCommand = CompositeSpectrumEditCommand(self)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.beginSpectrumEdit ˄


    # GENERATED CODE AREA: method._appendSpectrumEdit ˅
    def _appendSpectrumEdit(self, command: SpectrumEditCommand) -> None:
        """
        ドラッグ操作中に実行されたCommandをcurrentCompositeCommandに追加する。Controllerから直接呼び出さず、Context内部で使用する。
        """

        # SAFE CODE AREA ˅
        (self._noop(), self.currentCompositeCommand.add(command))[self.currentCompositeCommand is not None]
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._appendSpectrumEdit ˄


    # GENERATED CODE AREA: method.endSpectrumEdit ˅
    def endSpectrumEdit(self) -> None:
        """
        ドラッグによる連続スペクトル編集を終了する。currentCompositeCommandをUndo履歴に追加し、Redo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        self.undoStack.append(self.currentCompositeCommand)
        self.redoStack.clear()
        self.currentCompositeCommand = None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.endSpectrumEdit ˄


    # GENERATED CODE AREA: method.resetSpectrum ˅
    def resetSpectrum(self) -> None:
        """
        現在のModelの編集用スペクトルを元スペクトル状態に戻すResetSpectrumCommandを実行する。
        """

        # SAFE CODE AREA ˅
        self._executeEdit(ResetSpectrumCommand(self.currentModel))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.resetSpectrum ˄


    # GENERATED CODE AREA: method._noop ˅
    def _noop(self) -> None:
        # SAFE CODE AREA ˅
        return None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._noop ˄

