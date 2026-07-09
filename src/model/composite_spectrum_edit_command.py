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
        if self._undo2dCommandsAsSingleRestore():
            return

        # Undo時は最後に行った編集から逆順に戻し、ドラッグ前の状態へ戻す。
        for command in reversed(self.commands):
            command.undo()
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.undo ˄

    def _undo2dCommandsAsSingleRestore(self) -> bool:
        """
        2D編集Command群を1つの矩形復元としてUndoする。
        """

        if not self._canUndo2dCommandsAsSingleRestore():
            return False

        commands = self.commands
        model = commands[0].model
        row_start = min(command.rect[0] for command in commands)
        row_stop = max(command.rect[1] for command in commands)
        col_start = min(command.rect[2] for command in commands)
        col_stop = max(command.rect[3] for command in commands)

        old_real, old_imaginary = model.getInteractiveSpectrumAtRect(
            row_start,
            row_stop,
            col_start,
            col_stop,
        )
        filled = np.zeros(old_real.shape[:2], dtype=bool)

        for command in commands:
            r0, r1, c0, c1 = command.rect
            relative_rows = slice(r0 - row_start, r1 - row_start)
            relative_cols = slice(c0 - col_start, c1 - col_start)
            filled_region = filled[relative_rows, relative_cols]
            missing = ~filled_region

            real_region = old_real[relative_rows, relative_cols]
            imaginary_region = old_imaginary[relative_rows, relative_cols]
            real_region[missing] = np.asarray(command.oldRealPart)[missing]
            imaginary_region[missing] = np.asarray(command.oldImaginaryPart)[missing]
            filled_region[missing] = True

        model.restoreInteractiveSpectrumAtRect(
            row_start,
            row_stop,
            col_start,
            col_stop,
            old_real,
            old_imaginary,
        )
        return True

    def _canUndo2dCommandsAsSingleRestore(self) -> bool:
        """
        現在の子Command群が2D矩形復元に統合できるかを判定する。
        """

        if len(self.commands) == 0:
            return False

        model = getattr(self.commands[0], "model", None)
        if model is None or not hasattr(model, "restoreInteractiveSpectrumAtRect"):
            return False

        required_attributes = (
            "model",
            "rect",
            "oldRealPart",
            "oldImaginaryPart",
        )
        for command in self.commands:
            if getattr(command, "model", None) is not model:
                return False
            if not all(hasattr(command, attribute) for attribute in required_attributes):
                return False
            rect = getattr(command, "rect", None)
            if rect is None or len(rect) != 4:
                return False
            if np.asarray(command.oldRealPart).size == 0:
                return False
            if np.asarray(command.oldImaginaryPart).size == 0:
                return False

        return True


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
