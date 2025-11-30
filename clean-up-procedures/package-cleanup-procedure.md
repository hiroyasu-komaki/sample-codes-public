
# Pythonグローバル環境クリーンアップ手順

## 1. 事前準備

### requirements.txtの作成
```bash
# 現在の環境
pip freeze > requirements_to_remove.txt

# 現在の環境を保存（念のため）
pip list > ./backup/pip_backup_$(date +%Y%m%d).txt
```

### 残すパッケージリストの作成
```bash
cat > ./packages_to_keep.txt << 'EOF'
black
flake8
pycodestyle
pyflakes
mccabe
mypy_extensions
ipython
ipykernel
jupyter_core
jupyter_client
jupyter_server
jupyterlab
notebook
build
setuptools
pytest
EOF
```

## 2. 全パッケージのアンインストール
```bash
# requirements_to_remove.txtを使用して全削除
pip uninstall -r ./requirements_to_remove.txt -y
```

## 3. 必要なパッケージの再インストール
```bash
# packages_to_keep.txtから一括インストール
pip install -r ./packages_to_keep.txt
```

## 4. インストール確認
```bash
pip list
```

以下のようなクリーンな状態になっているはずです：
```
Package          Version
---------------- -------
black            25.9.0
flake8           7.3.0
ipykernel        (最新)
ipython          (最新)
jupyter_client   (最新)
jupyter_core     (最新)
jupyter_server   (最新)
jupyterlab       (最新)
notebook         (最新)
build            (最新)
pytest           (最新)
pip              (最新)
setuptools       (最新)
+ 上記の依存パッケージ
```

<br>

## 今後の運用ルール

1. **新規プロジェクト作成時**
```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

2. **グローバル環境には何もインストールしない**
   - 誤ってグローバルにインストールした場合は即座に `pip uninstall` する

3. **定期的なチェック**
```bash
   # グローバル環境の確認
   pip list
   
   # 不要なパッケージがあれば削除
   pip uninstall <package_name>
```