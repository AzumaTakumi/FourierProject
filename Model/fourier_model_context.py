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
from .erase_spectrum_at_positions_command import EraseSpectrumAtPositionsCommand
from .paint_rgb_spectrum_at_positions_command import PaintRgbSpectrumAtPositionsCommand
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
        # View/ControllerからModelインスタンスを直接扱わせないため、この公開アクセサは使用不可にする。
        raise RuntimeError("model() は使用しないでください。getData() / getImage() などのContextメソッドを使用してください。")
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
        # Model状態が変わったので、Viewへ変更範囲だけを通知する。
        self._notifySpectrumChanged(self._createSpectrumChangeForCommand(command))
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

    # SAFE CODE AREA ˅
    def eraseSpectrumBetweenIndexes(self, startIndex: int, endIndex: int) -> None:
        # 1Dドラッグで点が飛んだ場合に、前回indexから今回indexまでを線として削除する。
        self._require1dModel()
        indices = self._indexLine(startIndex, endIndex)
        commands = [EraseSpectrumAtIndexCommand(self.currentModel, index) for index in indices]
        self._executeEditBatch(
            commands,
            lambda: self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1),
        )

    def restoreSpectrumBetweenIndexes(self, startIndex: int, endIndex: int) -> None:
        # 1Dドラッグで点が飛んだ場合に、前回indexから今回indexまでを線として復元する。
        self._require1dModel()
        indices = self._indexLine(startIndex, endIndex)
        commands = [RestoreSpectrumAtIndexCommand(self.currentModel, index) for index in indices]
        self._executeEditBatch(
            commands,
            lambda: self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1),
        )
    # SAFE CODE AREA ˄


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

    # SAFE CODE AREA ˅
    def eraseSpectrumLineAtPosition(self, startRow: int, startCol: int, endRow: int, endCol: int, radius: int) -> None:
        # 2Dドラッグでイベント間隔が空いた場合に、前回座標と今回座標を線で結んで削除する。
        self._require2dModel()
        points = self._linePoints(startRow, startCol, endRow, endCol)
        # 線分上の全点を1つのCommandで処理し、逆FFTとView通知を1回にまとめる。
        self._executeEdit(EraseSpectrumAtPositionsCommand(self.currentModel, points, radius))

    def paintRgbSpectrumLineAtPosition(
        self,
        startRow: int,
        startCol: int,
        endRow: int,
        endCol: int,
        radius: int,
        rgbColor: list,
    ) -> None:
        # 2Dドラッグでイベント間隔が空いた場合に、前回座標と今回座標を線で結んでRGBペイントする。
        self._require2dModel()
        points = self._linePoints(startRow, startCol, endRow, endCol)
        # 線分上の全点を1つのCommandで処理し、逆FFTとView通知を1回にまとめる。
        self._executeEdit(PaintRgbSpectrumAtPositionsCommand(self.currentModel, points, radius, rgbColor))
    # SAFE CODE AREA ˄


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
    def getData(self) -> dict:
        # Viewが表示用の数値配列を取得できるよう、現在ModelのgetDataをContext経由で呼び出す。
        return self.currentModel.getData()

    def getImage(self) -> dict:
        # Viewが表示用のPIL.Imageを取得できるよう、現在ModelのgetImageをContext経由で呼び出す。
        return self.currentModel.getImage()

    def getModelName(self) -> str:
        # Viewのステータス表示用に、現在Modelのクラス名だけを返す。
        return self.currentModel.__class__.__name__

    def getUndoCount(self) -> int:
        # Viewのステータス表示用に、Undo可能なCommand数を返す。
        return len(self.undoStack)

    def getRedoCount(self) -> int:
        # Viewのステータス表示用に、Redo可能なCommand数を返す。
        return len(self.redoStack)

    def is1dModel(self) -> bool:
        # Controllerが1D専用操作を呼び分けるための判定結果を返す。
        return isinstance(self.currentModel, Fourier1dModel)

    def is2dModel(self) -> bool:
        # Controllerが2D専用操作を呼び分けるための判定結果を返す。
        return isinstance(self.currentModel, Fourier2dModel)

    def getInteractiveSpectrumAtIndex(self, index: int) -> tuple:
        # 1D入力欄の表示用に、指定indexの編集用スペクトル実部・虚部をContext経由で返す。
        self._require1dModel()
        return self.currentModel.getInteractiveSpectrumAtIndex(index)

    def _executeEditBatch(self, commands: list, changeFactory: Callable) -> None:
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

    def _createSpectrumChange(self) -> SpectrumChange:
        # 明示的な変更範囲が分からない場合は、現在スペクトル全体を1つの変更範囲として扱う。
        return self._createFullSpectrumChange()

    def _createSpectrumChangeForCommand(self, command: SpectrumEditCommand) -> SpectrumChange:
        # Commandの種類から、Viewが部分更新できる最小範囲の変更情報を作る。
        if isinstance(command, (EraseSpectrumAtIndexCommand, RestoreSpectrumAtIndexCommand, EditSpectrumValueAtIndexCommand)):
            return self._create1dSpectrumChangeAtIndex(command.index)
        if isinstance(command, (EraseSpectrumAtPositionCommand, PaintRgbSpectrumAtPositionCommand)):
            return self._create2dSpectrumChangeAtPosition(command.row, command.col, command.radius)
        if isinstance(command, (EraseSpectrumAtPositionsCommand, PaintRgbSpectrumAtPositionsCommand)):
            return self._create2dSpectrumChangeForLine(command.positions, command.radius)
        if isinstance(command, CompositeSpectrumEditCommand):
            return self._createCompositeSpectrumChange(command)
        return self._createFullSpectrumChange()

    def _createFullSpectrumChange(self) -> SpectrumChange:
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

    def _create1dSpectrumChangeAtIndex(self, index: int) -> Spectrum1dChange:
        # 1Dの単一点編集では、変更されたindexとその1要素だけをViewへ渡す。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None:
            return Spectrum1dChange(index=0, changedPowerSpectrum=None)
        size = int(spectrum.shape[0]) if spectrum.ndim >= 1 else 0
        if size <= 0:
            return Spectrum1dChange(index=0, changedPowerSpectrum=np.array([]))
        normalized_index = int(index)
        if normalized_index < 0:
            normalized_index += size
        normalized_index = int(np.clip(normalized_index, 0, size - 1))
        return Spectrum1dChange(
            index=normalized_index,
            changedPowerSpectrum=np.copy(spectrum[normalized_index:normalized_index + 1]),
        )

    def _create1dSpectrumChangeForRange(self, start: int, stop: int) -> Spectrum1dChange:
        # 複数indexをまとめて通知する場合は、startからstopまでの連続範囲を切り出す。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None:
            return Spectrum1dChange(index=0, changedPowerSpectrum=None)
        size = int(spectrum.shape[0]) if spectrum.ndim >= 1 else 0
        if size <= 0:
            return Spectrum1dChange(index=0, changedPowerSpectrum=np.array([]))
        start = int(np.clip(start, 0, size - 1))
        stop = int(np.clip(stop, start + 1, size))
        return Spectrum1dChange(index=start, changedPowerSpectrum=np.copy(spectrum[start:stop]))

    def _create2dSpectrumChangeAtPosition(self, row: int, col: int, radius: int) -> Spectrum2dChange:
        # 2Dのブラシ編集では、円形ブラシを含む矩形範囲を切り出してViewへ渡す。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None or getattr(spectrum, "ndim", 0) < 2:
            return Spectrum2dChange(x=0, y=0, width=0, height=0, changedPowerSpectrum=None)
        rect = self._spectrumRect(row, col, radius, spectrum.shape[:2])
        return self._create2dSpectrumChangeForRect(rect)

    def _create2dSpectrumChangeForRect(self, rect: tuple[int, int, int, int]) -> Spectrum2dChange:
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

    def _createCompositeSpectrumChange(self, command: CompositeSpectrumEditCommand) -> SpectrumChange:
        # CompositeCommandのUndo/Redoでは、含まれる編集範囲を1つの連続範囲または矩形にまとめて通知する。
        commands = self._flattenCommands(command)
        if not commands:
            return self._createFullSpectrumChange()
        if isinstance(self.currentModel, Fourier1dModel):
            indices: list[int] = []
            spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
            size = int(spectrum.shape[0]) if spectrum is not None and spectrum.ndim >= 1 else 0
            for child in commands:
                if not isinstance(child, (EraseSpectrumAtIndexCommand, RestoreSpectrumAtIndexCommand, EditSpectrumValueAtIndexCommand)):
                    return self._createFullSpectrumChange()
                index = int(child.index)
                if size > 0 and index < 0:
                    index += size
                indices.append(index)
            if not indices:
                return self._createFullSpectrumChange()
            return self._create1dSpectrumChangeForRange(min(indices), max(indices) + 1)

        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None or getattr(spectrum, "ndim", 0) < 2:
            return self._createFullSpectrumChange()
        rects: list[tuple[int, int, int, int]] = []
        for child in commands:
            if isinstance(child, (EraseSpectrumAtPositionCommand, PaintRgbSpectrumAtPositionCommand)):
                rects.append(self._spectrumRect(child.row, child.col, child.radius, spectrum.shape[:2]))
                continue
            if isinstance(child, (EraseSpectrumAtPositionsCommand, PaintRgbSpectrumAtPositionsCommand)):
                rects.append(self._spectrumRectForPoints(child.positions, child.radius, spectrum.shape[:2]))
                continue
            else:
                return self._createFullSpectrumChange()
        if not rects:
            return self._createFullSpectrumChange()
        row_start = min(rect[0] for rect in rects)
        row_stop = max(rect[1] for rect in rects)
        col_start = min(rect[2] for rect in rects)
        col_stop = max(rect[3] for rect in rects)
        return self._create2dSpectrumChangeForRect((row_start, row_stop, col_start, col_stop))

    def _create2dSpectrumChangeForLine(self, points: list[tuple[int, int]], radius: int) -> Spectrum2dChange:
        # 線分上の複数ブラシ編集を、すべて含む1つの矩形changeへまとめる。
        spectrum = getattr(self.currentModel, "interactivePowerSpectrum", None)
        if spectrum is None or getattr(spectrum, "ndim", 0) < 2 or not points:
            return Spectrum2dChange(x=0, y=0, width=0, height=0, changedPowerSpectrum=None)
        return self._create2dSpectrumChangeForRect(self._spectrumRectForPoints(points, radius, spectrum.shape[:2]))

    def _spectrumRect(self, row: int, col: int, radius: int, shape: tuple[int, int]) -> tuple[int, int, int, int]:
        # 2Dスペクトル配列上で、指定中心と半径を含む矩形範囲を安全に計算する。
        height, width = shape
        row = int(np.clip(row, 0, max(height - 1, 0)))
        col = int(np.clip(col, 0, max(width - 1, 0)))
        radius = max(0, int(radius))
        row_start = max(0, row - radius)
        row_stop = min(height, row + radius + 1)
        col_start = max(0, col - radius)
        col_stop = min(width, col + radius + 1)
        return row_start, row_stop, col_start, col_stop

    def _spectrumRectForPoints(self, points: list[tuple[int, int]], radius: int, shape: tuple[int, int]) -> tuple[int, int, int, int]:
        # 複数ブラシを含む1つの矩形範囲を計算する。
        rects = [self._spectrumRect(row, col, radius, shape) for row, col in points]
        row_start = min(rect[0] for rect in rects)
        row_stop = max(rect[1] for rect in rects)
        col_start = min(rect[2] for rect in rects)
        col_stop = max(rect[3] for rect in rects)
        return row_start, row_stop, col_start, col_stop

    def _linePoints(self, startRow: int, startCol: int, endRow: int, endCol: int) -> list[tuple[int, int]]:
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
        points: list[tuple[int, int]] = []
        for row, col in zip(rows, cols):
            point = (int(row), int(col))
            if not points or points[-1] != point:
                points.append(point)
        return points

    def _indexLine(self, startIndex: int, endIndex: int) -> list[int]:
        # 1Dでも前回indexから今回indexまでの間を連続範囲として編集できるようにする。
        start = int(startIndex)
        end = int(endIndex)
        step = 1 if end >= start else -1
        return list(range(start, end + step, step))

    def _flattenCommands(self, command: SpectrumEditCommand) -> list:
        # 入れ子になったCompositeCommandを、変更範囲計算しやすいよう通常Commandのリストに展開する。
        if isinstance(command, CompositeSpectrumEditCommand):
            flattened: list = []
            for child in command.commands:
                flattened.extend(self._flattenCommands(child))
            return flattened
        return [command]

    def _require1dModel(self) -> None:
        # 誤って2Dモデルへ1D編集を実行しないよう、Context入口で型を保証する。
        if not isinstance(self.currentModel, Fourier1dModel):
            raise TypeError("Current model is not Fourier1dModel.")

    def _require2dModel(self) -> None:
        # 誤って1Dモデルへ2D編集を実行しないよう、Context入口で型を保証する。
        if not isinstance(self.currentModel, Fourier2dModel):
            raise TypeError("Current model is not Fourier2dModel.")
    # SAFE CODE AREA ˄
