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
# ContextはControllerの代わりに各Commandを生成するため、具体ModelとCommandをここで読み込む。
from .fourier_1_d_model import Fourier1dModel
from .fourier_2_d_model import Fourier2dModel
from .set_1_d_source_data_command import Set1dSourceDataCommand
from .set_2_d_source_data_command import Set2dSourceDataCommand
from .change_fourier_model_command import ChangeFourierModelCommand
from .erase_spectrum_at_index_command import EraseSpectrumAtIndexCommand
from .restore_spectrum_at_index_command import RestoreSpectrumAtIndexCommand
from .edit_spectrum_value_at_index_command import EditSpectrumValueAtIndexCommand
from .erase_spectrum_at_position_command import EraseSpectrumAtPositionCommand
from .paint_rgb_spectrum_at_position_command import PaintRgbSpectrumAtPositionCommand
from .reset_spectrum_command import ResetSpectrumCommand
from .spectrum_1_d_change import Spectrum1dChange
from .spectrum_2_d_change import Spectrum2dChange
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
    def __init__(self, spectrumChangedListener: Callable | None = None) -> None:
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
        self.spectrumChangedListener: Callable | None = spectrumChangedListener

        # ドラッグ操作中に発生した複数の編集Commandを一時的にまとめるCompositeSpectrumEditCommandを保持する。
        self.currentCompositeCommand: CompositeSpectrumEditCommand | None = None

        # SAFE CODE AREA ˅
        # 固定領域で初期化したフィールドをそのまま使用するため、SAFE内の追加初期化は行わない。
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # FIXED CODE AREA: method._model ˅
    def _model(self) -> FourierModel:
        """
        現在操作対象となっているFourierModelを返す。
        """

        # SAFE CODE AREA ˅
        # 互換用の内部アクセサ。現在の操作対象Modelをそのまま返す。
        return self.currentModel
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method._model ˄


    # GENERATED CODE AREA: method.model ˅
    def model(self) -> FourierModel:
        """
        現在操作対象となっているFourierModelを返す。
        """

        # SAFE CODE AREA ˅
        # Controller/Viewから参照される公開アクセサとして現在のModelを返す。
        return self.currentModel
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.model ˄


    # GENERATED CODE AREA: method.set1dSourceData ˅
    def set1dSourceData(self, sourceData: np.ndarray) -> None:
        """
        1次元元データを設定する。現在のModelが1次元の場合はSet1dSourceDataCommandを実行し、2次元Modelから1次元Modelへ切り替える必要がある場合はChangeFourierModelCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # 入力データを1Dモデル用のfloat配列へそろえる。
        data = np.asarray(sourceData, dtype=float)
        # すでに1Dモデルならデータ差し替えCommand、2DモデルならModel切り替えCommandを使う。
        command = (
            Set1dSourceDataCommand(self.currentModel, data)
            if isinstance(self.currentModel, Fourier1dModel)
            else ChangeFourierModelCommand(self, Fourier1dModel(data))
        )
        self._executeEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set1dSourceData ˄


    # GENERATED CODE AREA: method.set2dSourceData ˅
    def set2dSourceData(self, sourceData: np.ndarray) -> None:
        """
        2次元元データを設定する。現在のModelが2次元の場合はSet2dSourceDataCommandを実行し、1次元Modelから2次元Modelへ切り替える必要がある場合はChangeFourierModelCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # 入力データを2Dモデル用のfloat配列へそろえる。
        data = np.asarray(sourceData, dtype=float)
        # すでに2Dモデルならデータ差し替えCommand、1DモデルならModel切り替えCommandを使う。
        command = (
            Set2dSourceDataCommand(self.currentModel, data)
            if isinstance(self.currentModel, Fourier2dModel)
            else ChangeFourierModelCommand(self, Fourier2dModel(data))
        )
        self._executeEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.set2dSourceData ˄


    # GENERATED CODE AREA: method.setModel ˅
    def setModel(self, model: FourierModel) -> None:
        """
        現在のModelを指定されたFourierModelに差し替える。
        """

        # SAFE CODE AREA ˅
        # Model差し替えもUndo可能な編集操作として扱う。
        self._executeEdit(ChangeFourierModelCommand(self, model))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setModel ˄


    # GENERATED CODE AREA: method.notifySpectrumChanged ˅
    def notifySpectrumChanged(self, change: SpectrumChange | None = None) -> None:
        """
        スペクトル変更をView側へ通知する。
        """

        # SAFE CODE AREA ˅
        # 呼び出し側が変更情報を渡さない場合は、現在Modelの全体変更情報を作る。
        self._notifySpectrumChanged(change or self._createSpectrumChange())
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.notifySpectrumChanged ˄


    # GENERATED CODE AREA: method._notifySpectrumChanged ˅
    def _notifySpectrumChanged(self, change: SpectrumChange) -> None:
        """
        スペクトル変更をView側へ通知する。Viewから渡されたspectrumChangedListenerにSpectrumChangeを渡して呼び出す。
        """

        # SAFE CODE AREA ˅
        # View側から登録された関数がある場合だけ通知する。
        if callable(self.spectrumChangedListener):
            self.spectrumChangedListener(change)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._notifySpectrumChanged ˄


    # GENERATED CODE AREA: method.executeEdit ˅
    def executeEdit(self, command: SpectrumEditCommand) -> None:
        """
        指定されたSpectrumEditCommandを実行する。
        """

        # SAFE CODE AREA ˅
        # 外部から渡されたCommandも、Context管理のUndo/Redo処理へ統一して流す。
        self._executeEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.executeEdit ˄


    # GENERATED CODE AREA: method._executeEdit ˅
    def _executeEdit(self, command: SpectrumEditCommand) -> None:
        """
        指定されたSpectrumEditCommandを実行し、Undo履歴に追加する。新しい編集が行われた場合、Redo履歴を消去する。
        """

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
        # Model状態が変わったので、Viewへ最新スペクトルを通知する。
        self._notifySpectrumChanged(self._createSpectrumChange())
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._executeEdit ˄


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
        # Undo後のModel状態をViewへ通知する。
        self._notifySpectrumChanged(self._createSpectrumChange())
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
        # Redo後のModel状態をViewへ通知する。
        self._notifySpectrumChanged(self._createSpectrumChange())
        return True
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.redo ˄


    # GENERATED CODE AREA: method.clearStack ˅
    def clearStack(self) -> None:
        """
        Undo履歴とRedo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        # 公開メソッドから内部の履歴消去処理へ委譲する。
        self._clearStack()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.clearStack ˄


    # GENERATED CODE AREA: method._clearStack ˅
    def _clearStack(self) -> None:
        """
        Undo履歴とRedo履歴を消去する。
        """

        # SAFE CODE AREA ˅
        # 新しいファイル読み込みや初期化時に、Undo/Redo履歴を完全に消す。
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
        # 1D専用操作なので、現在Modelの型を先に検査する。
        self._require1dModel()
        # 実際の編集とUndo用保存はCommandへ任せる。
        self._executeEdit(EraseSpectrumAtIndexCommand(self.currentModel, index))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtIndex ˄


    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˅
    def restoreSpectrumAtIndex(self, index: int) -> None:
        """
        指定indexの周波数成分を編集する。成分をもとに戻す機能。編集結果をinteractive*に反映する。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        # 1D専用操作なので、現在Modelの型を先に検査する。
        self._require1dModel()
        # 指定成分を元スペクトルへ戻すCommandを実行する。
        self._executeEdit(RestoreSpectrumAtIndexCommand(self.currentModel, index))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.restoreSpectrumAtIndex ˄


    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˅
    def editSpectrumValueAtIndex(self, index: int, realPart: float, imaginaryPart: float) -> None:
        """
        Undo操作で値を戻す際に使用する。restoreSpectrumAtIndex(index)で戻す操作は不適切であり、本来戻す可能性がある値と異なるため、この操作を追加した。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        # 1D専用操作なので、現在Modelの型を先に検査する。
        self._require1dModel()
        # 指定成分の実部・虚部を直接書き換えるCommandを実行する。
        self._executeEdit(EditSpectrumValueAtIndexCommand(self.currentModel, index, realPart, imaginaryPart))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.editSpectrumValueAtIndex ˄


    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˅
    def eraseSpectrumAtPosition(self, row: int, col: int, radius: int) -> None:
        """
        指定(row, col)の周波数成分を削除する。radiusは半径の大きさ内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        # 2D専用操作なので、現在Modelの型を先に検査する。
        self._require2dModel()
        # 指定位置周辺のスペクトルを消去するCommandを実行する。
        self._executeEdit(EraseSpectrumAtPositionCommand(self.currentModel, row, col, radius))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.eraseSpectrumAtPosition ˄


    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˅
    def paintRgbSpectrumAtPosition(self, row: int, col: int, radius: int, rgbColor: list) -> None:
        """
        rgbの場合のスペクトルペイント編集。内部にSpectrumEditCommandを作成する機構あり
        """

        # SAFE CODE AREA ˅
        # 2D専用操作なので、現在Modelの型を先に検査する。
        self._require2dModel()
        # 指定位置周辺のスペクトルをRGB値で編集するCommandを実行する。
        self._executeEdit(PaintRgbSpectrumAtPositionCommand(self.currentModel, row, col, radius, rgbColor))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.paintRgbSpectrumAtPosition ˄


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


    # GENERATED CODE AREA: method.appendSpectrumEdit ˅
    def appendSpectrumEdit(self, command: SpectrumEditCommand) -> None:
        """
        ドラッグ操作中に実行されたCommandをcurrentCompositeCommandに追加する。
        """

        # SAFE CODE AREA ˅
        # 追加されたCommandも通常実行と同じ経路で実行し、Compositeへ格納させる。
        self._executeEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.appendSpectrumEdit ˄


    # GENERATED CODE AREA: method._appendSpectrumEdit ˅
    def _appendSpectrumEdit(self, command: SpectrumEditCommand) -> None:
        """
        ドラッグ操作中に実行されたCommandをcurrentCompositeCommandに追加する。Controllerから直接呼び出さず、Context内部で使用する。
        """

        # SAFE CODE AREA ˅
        # 古い内部名から公開メソッドへ委譲する。
        self.appendSpectrumEdit(command)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._appendSpectrumEdit ˄


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


    # GENERATED CODE AREA: method._noop ˅
    def _noop(self) -> None:
        # SAFE CODE AREA ˅
        # 自動生成された空操作用メソッド。呼ばれても状態を変更しない。
        return None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method._noop ˄


    # SAFE CODE AREA ˅
    def _createSpectrumChange(self) -> SpectrumChange:
        # Viewへ渡すスペクトルは、通知後の編集で変わらないようcopyしておく。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        spectrum_copy = np.copy(spectrum) if spectrum is not None else None
        if isinstance(self.currentModel, Fourier1dModel):
            # 1Dでは全体更新を表すため、個別indexではなく-1を指定する。
            return Spectrum1dChange(index=-1, changedPowerSpectrum=spectrum_copy)

        # 2Dでは現在スペクトルの縦横サイズを通知情報へ入れる。
        height = int(spectrum.shape[0]) if spectrum is not None and spectrum.ndim >= 2 else 0
        width = int(spectrum.shape[1]) if spectrum is not None and spectrum.ndim >= 2 else 0
        return Spectrum2dChange(x=0, y=0, width=width, height=height, changedPowerSpectrum=spectrum_copy)

    def _require1dModel(self) -> None:
        # 誤って2Dモデルへ1D編集を実行しないよう、Context入口で型を保証する。
        if not isinstance(self.currentModel, Fourier1dModel):
            raise TypeError("Current model is not Fourier1dModel.")

    def _require2dModel(self) -> None:
        # 誤って1Dモデルへ2D編集を実行しないよう、Context入口で型を保証する。
        if not isinstance(self.currentModel, Fourier2dModel):
            raise TypeError("Current model is not Fourier2dModel.")
    # SAFE CODE AREA ˄
