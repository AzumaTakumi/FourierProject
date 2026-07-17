from types import SimpleNamespace

import pytest

from src.controller.context_menu_controller import ContextMenuController
from src.controller.file_controller import FileController, FileLoader
from src.controller.file_saver import FileSaver


def testOpenFileChooserReturnsSelectedPath(monkeypatch):
    """FileControllerがViewを親にしてファイル選択結果を返すことを確認する。"""
    view = object()
    received = {}

    def fakeGetOpenFileName(parent, title, directory, fileFilter):
        received.update(
            parent=parent,
            title=title,
            directory=directory,
            fileFilter=fileFilter,
        )
        return "/tmp/signal.txt", "テキストデータ(1次元データ) (*.csv *.txt)"

    monkeypatch.setattr(
        "src.controller.file_controller.QFileDialog.getOpenFileName",
        fakeGetOpenFileName,
    )

    selected = FileController(view).openFileChooser()

    assert selected == "/tmp/signal.txt"
    assert received["parent"] is view
    assert received["title"] == "ファイルを開く"
    assert "*.txt" in received["fileFilter"]


def testFileLoaderStartReturnsFalseWhenSelectionIsCancelled(
    monkeypatch, capsys
):
    """ファイル選択をキャンセルした場合は読込処理を開始しない。"""
    loader = FileLoader(aView=None)
    loadedPaths = []
    monkeypatch.setattr(loader, "openFileChooser", lambda: "")
    monkeypatch.setattr(loader, "loadSignalData", loadedPaths.append)

    assert loader.start() is False
    assert loadedPaths == []
    assert "キャンセル" in capsys.readouterr().out


def testFileLoaderStartLoadsSelectedPath(monkeypatch):
    """ファイルを選択した場合はそのパスを読み込み、成功を返す。"""
    loader = FileLoader(aView=None)
    loadedPaths = []
    monkeypatch.setattr(loader, "openFileChooser", lambda: "/tmp/signal.csv")
    monkeypatch.setattr(loader, "loadSignalData", loadedPaths.append)

    assert loader.start() is True
    assert loadedPaths == ["/tmp/signal.csv"]


def testInputFileWarnsWhenFileLoaderIsMissing(monkeypatch):
    """FileLoader未設定時は警告し、処理を終了する。"""
    warnings = []
    parent = object()
    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMessageBox.warning",
        lambda *args: warnings.append(args),
    )

    ContextMenuController(parent=parent).inputFile()

    assert warnings == [(parent, "エラー", "FileLoaderが設定されていません。")]


@pytest.mark.parametrize(
    ("loaded", "expectedRefreshCount"),
    [(True, 1), (False, 0)],
)
def testInputFileRefreshesViewOnlyAfterSuccessfulLoad(
    loaded, expectedRefreshCount
):
    """読込成功時だけView更新コールバックを呼び出す。"""
    refreshCalls = []
    loader = SimpleNamespace(start=lambda: loaded)
    controller = ContextMenuController(
        fileLoader=loader,
        refreshViewCallback=lambda: refreshCalls.append("refresh"),
    )

    controller.inputFile()

    assert len(refreshCalls) == expectedRefreshCount


def testOpenEditViewCallsCallback():
    """編集画面が接続済みならコールバックへ処理を委譲する。"""
    calls = []
    controller = ContextMenuController(
        openEditViewCallback=lambda: calls.append("opened")
    )

    controller.openEditView()

    assert calls == ["opened"]


def testOpenEditViewInformsWhenCallbackIsMissing(monkeypatch):
    """編集画面が未接続なら情報メッセージを表示する。"""
    messages = []
    parent = object()
    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMessageBox.information",
        lambda *args: messages.append(args),
    )

    ContextMenuController(parent=parent).openEditView()

    assert messages == [(parent, "編集画面", "編集画面はまだ未接続です。")]


def testOutputRestoredDataPrefersCallback():
    """出力コールバックがある場合はFileSaverより優先して使用する。"""
    calls = []
    saver = SimpleNamespace(
        exportRestoredImage=lambda _view: calls.append("file_saver")
    )
    controller = ContextMenuController(
        fileSaver=saver,
        outputRestoredDataCallback=lambda: calls.append("callback"),
    )

    controller.outputRestoredData()

    assert calls == ["callback"]


def testOutputRestoredDataWarnsWhenFileSaverIsMissing(monkeypatch):
    """出力処理が未接続の場合は警告を表示する。"""
    warnings = []
    parent = object()
    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMessageBox.warning",
        lambda *args: warnings.append(args),
    )

    ContextMenuController(parent=parent).outputRestoredData()

    assert warnings == [(parent, "エラー", "FileSaverが設定されていません。")]


def testOutputRestoredDataDelegatesToFileSaver():
    """コールバックがなければFileSaverへ現在のViewを渡す。"""
    exportedViews = []
    parent = object()
    saver = SimpleNamespace(exportRestoredImage=exportedViews.append)

    ContextMenuController(parent=parent, fileSaver=saver).outputRestoredData()

    assert exportedViews == [parent]


@pytest.mark.parametrize(
    ("selectedIndex", "expectedMethod"),
    [(0, "inputFile"), (1, "openEditView"), (2, "outputRestoredData")],
)
def testContextMenuRoutesSelectedAction(
    monkeypatch, selectedIndex, expectedMethod
):
    """右クリックメニューで選択した項目に対応する処理だけを呼び出す。"""
    menuLabels = []
    actions = []

    class FakeMenu:
        def __init__(self, parent):
            self.parent = parent

        def addAction(self, label):
            action = object()
            menuLabels.append(label)
            actions.append(action)
            return action

        def exec(self, _globalPosition):
            return actions[selectedIndex]

    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMenu",
        FakeMenu,
    )

    calls = []
    controller = ContextMenuController()
    for methodName in ("inputFile", "openEditView", "outputRestoredData"):
        monkeypatch.setattr(
            controller,
            methodName,
            lambda name=methodName: calls.append(name),
        )

    controller.showContextMenu(globalPos=object())

    assert menuLabels == [
        "ファイル入力",
        "編集画面を開く",
        "左下のデータ・画像を出力",
    ]
    assert calls == [expectedMethod]


def testExportRestoredImageWarnsWhenImageIsMissing(monkeypatch):
    """保存対象画像がない場合は警告し、保存ダイアログを開かない。"""
    warnings = []
    view = SimpleNamespace(_restoredDataImage=None)
    monkeypatch.setattr(
        "src.controller.file_saver.QMessageBox.warning",
        lambda *args: warnings.append(args),
    )
    monkeypatch.setattr(
        "src.controller.file_saver.QFileDialog.getSaveFileName",
        lambda *args: pytest.fail("保存ダイアログを開いてはいけない"),
    )

    FileSaver(aView=view).exportRestoredImage(view)

    assert warnings == [(view, "警告", "保存する復元画像がありません。")]


def testExportRestoredImageDoesNothingWhenSaveIsCancelled(monkeypatch):
    """保存先選択をキャンセルした場合は保存処理を呼び出さない。"""
    image = object()
    view = SimpleNamespace(_restoredDataImage=image)
    saver = FileSaver(aView=view)
    monkeypatch.setattr(
        "src.controller.file_saver.QFileDialog.getSaveFileName",
        lambda *args: ("", ""),
    )
    monkeypatch.setattr(
        saver,
        "saveSignalData",
        lambda *args: pytest.fail("保存処理を呼び出してはいけない"),
    )

    saver.exportRestoredImage(view)


def testExportRestoredImageReportsSaveError(monkeypatch):
    """保存中の例外を捕捉し、エラーメッセージとして通知する。"""
    image = object()
    view = SimpleNamespace(_restoredDataImage=image)
    saver = FileSaver(aView=view)
    errors = []
    monkeypatch.setattr(
        "src.controller.file_saver.QFileDialog.getSaveFileName",
        lambda *args: ("/tmp/restored.png", "PNG Files (*.png)"),
    )
    monkeypatch.setattr(
        saver,
        "saveSignalData",
        lambda *_args: (_ for _ in ()).throw(OSError("disk full")),
    )
    monkeypatch.setattr(
        "src.controller.file_saver.QMessageBox.critical",
        lambda *args: errors.append(args),
    )

    saver.exportRestoredImage(view)

    assert errors == [(view, "エラー", "画像の保存に失敗しました:\ndisk full")]
