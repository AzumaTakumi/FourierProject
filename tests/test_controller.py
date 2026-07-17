from types import SimpleNamespace

import pytest

from src.controller.context_menu_controller import ContextMenuController
from src.controller.file_controller import FileController, FileLoader
from src.controller.file_saver import FileSaver


def test_open_file_chooser_returns_selected_path(monkeypatch):
    """FileControllerがViewを親にしてファイル選択結果を返すことを確認する。"""
    view = object()
    received = {}

    def fake_get_open_file_name(parent, title, directory, file_filter):
        received.update(
            parent=parent,
            title=title,
            directory=directory,
            file_filter=file_filter,
        )
        return "/tmp/signal.txt", "テキストデータ(1次元データ) (*.csv *.txt)"

    monkeypatch.setattr(
        "src.controller.file_controller.QFileDialog.getOpenFileName",
        fake_get_open_file_name,
    )

    selected = FileController(view).openFileChooser()

    assert selected == "/tmp/signal.txt"
    assert received["parent"] is view
    assert received["title"] == "ファイルを開く"
    assert "*.txt" in received["file_filter"]


def test_file_loader_start_returns_false_when_selection_is_cancelled(
    monkeypatch, capsys
):
    """ファイル選択をキャンセルした場合は読込処理を開始しない。"""
    loader = FileLoader(aView=None)
    loaded_paths = []
    monkeypatch.setattr(loader, "openFileChooser", lambda: "")
    monkeypatch.setattr(loader, "loadSignalData", loaded_paths.append)

    assert loader.start() is False
    assert loaded_paths == []
    assert "キャンセル" in capsys.readouterr().out


def test_file_loader_start_loads_selected_path(monkeypatch):
    """ファイルを選択した場合はそのパスを読み込み、成功を返す。"""
    loader = FileLoader(aView=None)
    loaded_paths = []
    monkeypatch.setattr(loader, "openFileChooser", lambda: "/tmp/signal.csv")
    monkeypatch.setattr(loader, "loadSignalData", loaded_paths.append)

    assert loader.start() is True
    assert loaded_paths == ["/tmp/signal.csv"]


def test_input_file_warns_when_file_loader_is_missing(monkeypatch):
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
    ("loaded", "expected_refresh_count"),
    [(True, 1), (False, 0)],
)
def test_input_file_refreshes_view_only_after_successful_load(
    loaded, expected_refresh_count
):
    """読込成功時だけView更新コールバックを呼び出す。"""
    refresh_calls = []
    loader = SimpleNamespace(start=lambda: loaded)
    controller = ContextMenuController(
        fileLoader=loader,
        refreshViewCallback=lambda: refresh_calls.append("refresh"),
    )

    controller.inputFile()

    assert len(refresh_calls) == expected_refresh_count


def test_open_edit_view_calls_callback():
    """編集画面が接続済みならコールバックへ処理を委譲する。"""
    calls = []
    controller = ContextMenuController(
        openEditViewCallback=lambda: calls.append("opened")
    )

    controller.openEditView()

    assert calls == ["opened"]


def test_open_edit_view_informs_when_callback_is_missing(monkeypatch):
    """編集画面が未接続なら情報メッセージを表示する。"""
    messages = []
    parent = object()
    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMessageBox.information",
        lambda *args: messages.append(args),
    )

    ContextMenuController(parent=parent).openEditView()

    assert messages == [(parent, "編集画面", "編集画面はまだ未接続です。")]


def test_output_restored_data_prefers_callback():
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


def test_output_restored_data_warns_when_file_saver_is_missing(monkeypatch):
    """出力処理が未接続の場合は警告を表示する。"""
    warnings = []
    parent = object()
    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMessageBox.warning",
        lambda *args: warnings.append(args),
    )

    ContextMenuController(parent=parent).outputRestoredData()

    assert warnings == [(parent, "エラー", "FileSaverが設定されていません。")]


def test_output_restored_data_delegates_to_file_saver():
    """コールバックがなければFileSaverへ現在のViewを渡す。"""
    exported_views = []
    parent = object()
    saver = SimpleNamespace(exportRestoredImage=exported_views.append)

    ContextMenuController(parent=parent, fileSaver=saver).outputRestoredData()

    assert exported_views == [parent]


@pytest.mark.parametrize(
    ("selected_index", "expected_method"),
    [(0, "inputFile"), (1, "openEditView"), (2, "outputRestoredData")],
)
def test_context_menu_routes_selected_action(
    monkeypatch, selected_index, expected_method
):
    """右クリックメニューで選択した項目に対応する処理だけを呼び出す。"""
    menu_labels = []
    actions = []

    class FakeMenu:
        def __init__(self, parent):
            self.parent = parent

        def addAction(self, label):
            action = object()
            menu_labels.append(label)
            actions.append(action)
            return action

        def exec(self, _global_position):
            return actions[selected_index]

    monkeypatch.setattr(
        "src.controller.context_menu_controller.QMenu",
        FakeMenu,
    )

    calls = []
    controller = ContextMenuController()
    for method_name in ("inputFile", "openEditView", "outputRestoredData"):
        monkeypatch.setattr(
            controller,
            method_name,
            lambda name=method_name: calls.append(name),
        )

    controller.showContextMenu(globalPos=object())

    assert menu_labels == [
        "ファイル入力",
        "編集画面を開く",
        "左下のデータ・画像を出力",
    ]
    assert calls == [expected_method]


def test_export_restored_image_warns_when_image_is_missing(monkeypatch):
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


def test_export_restored_image_does_nothing_when_save_is_cancelled(monkeypatch):
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


def test_export_restored_image_reports_save_error(monkeypatch):
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
