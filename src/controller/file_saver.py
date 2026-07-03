from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PIL import Image
from src.controller.file_controller import FileController
# ˄

class FileSaver(FileController):
    # ˅
    # 必要に応じて初期化処理などを拡張可能
    # ˄
    def __init__(self, aView):
        super().__init__(aView)

    def saveSignalData(self, aPath: str, aData: Image.Image) -> None:
        """
        渡された復元画像データ（PIL Image）を指定されたパスに画像ファイルとして保存する。
        """
        # ˅
        try:
            # 1. PIL Image の機能を使って、拡張子(png/jpgなど)を自動判別して保存
            aData.save(aPath)
        except Exception as e:
            print(f"[エラー] ファイルの保存に失敗しました: {e}")
            raise e
        # ˄

    # ˅
    def exportRestoredImage(self, view) -> None:
        """
        ユーザーにファイル保存ダイアログを表示し、MainWindowViewから左下の復元画像を取得して保存する。
        """
        # 1. 保存対象の画像（左下の復元画像）をViewから取得
        restored_image = view._restoredDataImage
        if restored_image is None:
            QMessageBox.warning(view, "警告", "保存する復元画像がありません。")
            return

        # 2. ファイル保存用のダイアログを開く（PNGとJPGに対応）
        file_path, _ = QFileDialog.getSaveFileName(
            view,
            "復元画像を保存",
            "",
            "JPEG Files (*.jpeg);;PNG Files (*.png)"
        )

        # 3. ユーザーがキャンセルしなかった場合、保存処理を実行
        if file_path:
            try:
                self.saveSignalData(file_path, restored_image)
                QMessageBox.information(view, "完了", "画像を正常に保存しました")
            except Exception as e:
                QMessageBox.critical(view, "エラー", f"画像の保存に失敗しました:\n{e}")
    # ˄
