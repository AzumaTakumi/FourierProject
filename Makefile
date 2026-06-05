PYTHON	= python
PYDOC	= pydoc
TARGET	= src/main.py
MODULE	= src.main
ARCHIVE	= $(shell basename `pwd`)
PYLINT	= pylint
LINTRCF	= pylintrc.txt
LINTRST	= lintresult.txt

all:
	@echo "ターゲットを指定してください: make run / make test / make lint / make clean"

# 1. アプリケーションの起動（起動コマンド要件）
run:
	PYTHONPATH=. $(PYTHON) $(TARGET)

# 2. 自動テストの実行（xUnitによる回帰テスト要件）
test:
	$(PYTHON) -m unittest discover -s test

# 3. 静的解析の実行（コーディング規約遵守の検証環境）
lint: clean
	@if [ ! -e $(LINTRCF) ] ; then $(PYLINT) --generate-rcfile > $(LINTRCF) 2> /dev/null ; fi
	$(PYLINT) --rcfile=$(LINTRCF) `find src test -name "*.py"` > $(LINTRST) ; less $(LINTRST)

# 4. ドキュメント自動生成（HTML文書化要件への補助）
doc:
	$(PYDOC) $(MODULE)

# 5. 不要ファイルの掃除（納品リポジトリを綺麗に保つため）
clean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "__pycache__" -type d 2>/dev/null | xargs rm -rf
	@if [ -e $(LINTRST) ] ; then rm -f $(LINTRST) ; fi

wipe: clean
	@find . -name ".DS_Store" -exec rm -f {} \;