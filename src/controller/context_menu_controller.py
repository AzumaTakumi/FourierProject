from PyQt6.QtWidgets import QMenu, QMessageBox
from src.controller.file_saver import FileSaver

class ContextMenuController:
    """
    右クリックメニューに関するユーザー操作を受け取り、
    必要なControllerやView表示処理へ振り分けるController。
    """

    def __init__(
        self,
        parent=None,
        fileLoader=None,
        fileSaver=None,
        openEditViewCallback=None,
        refreshViewCallback=None,
        outputRestoredDataCallback=None,
    ):
        self.parent = parent
        self.fileLoader = fileLoader
        self.fileSaver = fileSaver
        self.openEditViewCallback = openEditViewCallback
        self.refreshViewCallback = refreshViewCallback
        self.outputRestoredDataCallback = outputRestoredDataCallback

    def showContextMenu(self, globalPos) -> None:
        menu = QMenu(self.parent)

        inputAction = menu.addAction("ファイル入力")
        openEditViewAction = menu.addAction("編集画面を開く")
        outputAction = menu.addAction("左下のデータ・画像を出力")

        selectedAction = menu.exec(globalPos)

        if selectedAction == inputAction:
            self.inputFile()
        elif selectedAction == openEditViewAction:
            self.openEditView()
        elif selectedAction == outputAction:
            self.outputRestoredData()

    def inputFile(self) -> None:
        """
        Finderを表示してファイル入力を行う。
        """
        if self.fileLoader is None:
            QMessageBox.warning(self.parent, "エラー", "FileLoaderが設定されていません。")
            return

        loaded = self.fileLoader.start()

        if loaded and callable(self.refreshViewCallback):
            self.refreshViewCallback()

    def openEditView(self) -> None:
        """
        編集画面を開く。
        実際の編集画面Viewができたらcallbackに接続する。
        """
        if callable(self.openEditViewCallback):
            self.openEditViewCallback()
        else:
            QMessageBox.information(self.parent, "編集画面", "編集画面はまだ未接続です。")

    def outputRestoredData(self) -> None:
        """
        左下に表示されている復元データ・画像を出力する。
        実際の保存処理ができたらcallbackまたはFileSaverに接続する。
        """
        if callable(self.outputRestoredDataCallback):
            self.outputRestoredDataCallback()
            return

        print(f"file saver is {self.fileSaver}")
        if self.fileSaver is None:
            QMessageBox.warning(self.parent, "エラー", "FileSaverが設定されていません。")
            return

        self.fileSaver.exportRestoredImage(self.parent)
        