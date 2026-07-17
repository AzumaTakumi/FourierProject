import numpy as np
import pytest
from PIL import Image

from src.controller.file_controller import FileLoader
from src.model.fourier_1_d_model import Fourier1dModel
from src.model.fourier_2_d_model import Fourier2dModel

def testLoadValid1dTextFile(tmp_path):
    path = tmp_path / "signal.txt"
    data = np.array([0.1, 0.2, 0.3, 0.4], dtype=float)
    np.savetxt(path, data)

    loader = FileLoader(aView=None)
    loader.loadSignalData(str(path))

    assert isinstance(loader.model.currentModel, Fourier1dModel)
    assert loader.model.currentModel.sourceData.shape == (4,)
    assert np.allclose(loader.model.currentModel.sourceData, data)

def testLoadValid2dImageFile(tmp_path):
    path = tmp_path / "image.png"
    image = Image.new("RGB", (2, 3), color=(128, 64, 32))
    image.save(path)

    loader = FileLoader(aView=None)
    loader.loadSignalData(str(path))

    assert isinstance(loader.model.currentModel, Fourier2dModel)
    assert loader.model.currentModel.sourceData.shape == (3, 2, 3)
    assert np.all(loader.model.currentModel.sourceData == np.array(image, dtype=float))

def testInvalidTextFileRaisesValueError(tmp_path):
    path = tmp_path / "invalid.txt"
    path.write_text("not,numeric,values\n")

    loader = FileLoader(aView=None)
    with pytest.raises(ValueError):
        loader.loadSignalData(str(path))

def testEmptyTextFileRaisesValueError(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("")

    loader = FileLoader(aView=None)
    with pytest.raises(ValueError, match="Empty input file"):
        loader.loadSignalData(str(path))

def testUnsupportedExtensionUsesNullReader(tmp_path, capsys):
    path = tmp_path / "data.xyz"
    path.write_text("1,2,3\n")

    loader = FileLoader(aView=None)
    loader.loadSignalData(str(path))

    captured = capsys.readouterr()
    assert "未対応のファイル形式" in captured.out
    assert isinstance(loader.model.currentModel, Fourier2dModel)
    # Fourier2dModel は内部でグレースケールをRGB(3チャンネル)に拡張するため
    # shape は (高さ, 幅, チャンネル) となる
    assert loader.model.currentModel.sourceData.shape == (1, 1, 3)
