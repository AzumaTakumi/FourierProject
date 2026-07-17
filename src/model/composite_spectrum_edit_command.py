from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from .spectrum_edit_command import SpectrumEditCommand

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
import numpy as np
# SAFE CODE AREA ˄

class CompositeSpectrumEditCommand(SpectrumEditCommand):
    # GENERATED CODE AREA: class.header ˅
    """
    複数のSpectrumEditCommandを1つの編集操作としてまとめるCommandである。ドラッグ操作中に発生した複数のペイント編集や消しゴム編集を、Undo上は1回分の操作として扱うために使用する。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # FIXED CODE AREA: method.__init__ ˅
    def __init__(self) -> None:
        # まとめて管理するSpectrumEditCommandのリストを保持する。
        self.commands: list[SpectrumEditCommand] = []

        # SAFE CODE AREA ˅
        # 子Command追加時に、View通知用の変更種別を引き継ぐ。
        self.spectrumChangeKind: str = "full"
        # SAFE CODE AREA ˄
    # FIXED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.add ˅
    def add(self, command: SpectrumEditCommand) -> None:
        """
        指定されたSpectrumEditCommandをcommandsに追加する。
        """

        # SAFE CODE AREA ˅
        # ドラッグ中に発生した個別編集Commandを順序付きで保持する。
        self.commands.append(command)
        self.spectrumChangeKind = command.spectrumChangeKind
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.add ˄


    # GENERATED CODE AREA: method.execute ˅
    def execute(self) -> None:
        """
        commandsに保持されたCommandを順に実行する。
        """

        # SAFE CODE AREA ˅
        # Redo時は、ドラッグ中に行われた編集と同じ順番で再実行する。
        for command in self.commands:
            command.execute()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.execute ˄


    # GENERATED CODE AREA: method.undo ˅
    def undo(self) -> None:
        """
        commandsに保持されたCommandを実行時と逆順に取り消す。
        """

        # SAFE CODE AREA ˅
        {
            True: lambda: None,
            False: self._undoCommandsOneByOne,
        }[self._undo2dCommandsAsSingleRestore()]()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄

    def _undoCommandsOneByOne(self) -> None:
        """
        子Commandを実行時と逆順に取り消す。
        """

        for command in reversed(self.commands):
            command.undo()

    def _undo2dCommandsAsSingleRestore(self) -> bool:
        """
        2D編集Command群を1つの矩形復元としてUndoする。
        """

        return {
            True: self._restore2dCommandsAsSingleRect,
            False: lambda: False,
        }[self._canUndo2dCommandsAsSingleRestore()]()

    def _restore2dCommandsAsSingleRect(self) -> bool:
        """
        2D編集Command群のUndoデータを1つの矩形へ統合して復元する。
        """

        commands = self.commands
        model = commands[0].model
        rowStart = min(command.rect[0] for command in commands)
        rowStop = max(command.rect[1] for command in commands)
        colStart = min(command.rect[2] for command in commands)
        colStop = max(command.rect[3] for command in commands)

        oldReal, oldImaginary = model.getInteractiveSpectrumAtRect(
            rowStart,
            rowStop,
            colStart,
            colStop,
        )
        filled = np.zeros(oldReal.shape[:2], dtype=bool)

        for command in commands:
            r0, r1, c0, c1 = command.rect
            relativeRows = slice(r0 - rowStart, r1 - rowStart)
            relativeCols = slice(c0 - colStart, c1 - colStart)
            filledRegion = filled[relativeRows, relativeCols]
            missing = ~filledRegion

            realRegion = oldReal[relativeRows, relativeCols]
            imaginaryRegion = oldImaginary[relativeRows, relativeCols]
            realRegion[missing] = np.asarray(command.oldRealPart)[missing]
            imaginaryRegion[missing] = np.asarray(command.oldImaginaryPart)[missing]
            filledRegion[missing] = True

        model.restoreInteractiveSpectrumAtRect(
            rowStart,
            rowStop,
            colStart,
            colStop,
            oldReal,
            oldImaginary,
        )
        return True

    def _canUndo2dCommandsAsSingleRestore(self) -> bool:
        """
        現在の子Command群が2D矩形復元に統合できるかを判定する。
        """

        return bool(self.commands) and self._commandsShare2dRestoreModel()

    def _commandsShare2dRestoreModel(self) -> bool:
        """
        子Command群が同じ2D Modelの矩形復元Commandであるかを判定する。
        """

        model = getattr(self.commands[0], "model", None)
        return (
            model is not None
            and hasattr(model, "restoreInteractiveSpectrumAtRect")
            and all(
                self._is2dRectRestoreCommand(command, model)
                for command in self.commands
            )
        )

    def _is2dRectRestoreCommand(self, command: SpectrumEditCommand, model) -> bool:
        """
        子Commandが矩形復元へ統合できる2D編集Commandであるかを判定する。
        """

        rect = getattr(command, "rect", None)
        return (
            getattr(command, "model", None) is model
            and rect is not None
            and len(rect) == 4
            and np.asarray(getattr(command, "oldRealPart", [])).size > 0
            and np.asarray(getattr(command, "oldImaginaryPart", [])).size > 0
        )


    # GENERATED CODE AREA: method.description ˅
    def description(self) -> str:
        """
        このCompositeCommandの内容を説明する文字列を返す。
        """

        # SAFE CODE AREA ˅
        # デバッグや履歴表示用に、まとめられたCommand数を返す。
        return f"Composite Command: {len(self.commands)} sub-commands"
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.description ˄
