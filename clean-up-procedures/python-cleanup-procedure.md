# Python環境クリーンアップ手順

## Python環境の重複有無の確認手順

### 1. 利用可能なPythonコマンドを全て確認
```bash
which -a python python3 python3.9 python3.10 python3.11 python3.12 python3.13

# 実行結果
python not found
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
/usr/local/bin/python3
/usr/bin/python3
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12
/usr/local/bin/python3.12
```

### 2. 各コマンドのバージョン確認
```bash
# 見つかったコマンド（not foundi以外）それぞれで実行
python3 --version
python3.12 --version # など

# それぞれのバージョンが表示される
Python 3.12.4
Python 3.12.4
```

### 3. シンボリックリンクと実体を確認
```bash
# すべてのpython関連のシンボリックリンクを確認
ls -la /usr/local/bin/python* 2>/dev/null
ls -la /opt/homebrew/bin/python* 2>/dev/null
ls -la /Library/Frameworks/Python.framework/Versions/*/bin/python* 2>/dev/null
```

### 4. 実体の場所を特定
```bash
# Step 1で見つかった各コマンドの実体を確認
readlink -f $(which python3)
readlink -f $(which python3.12)

# または
file $(which python3)
file $(which python3.12)
```

### 5. Homebrewでインストールされたものを確認
```bash
brew list --formula | grep -i python
```

### 6. すべてのPythonインストール場所を検索
```bash
# Homebrew (Intel Mac)
ls -la /usr/local/Cellar/python* 2>/dev/null

# Homebrew (Apple Silicon)
ls -la /opt/homebrew/Cellar/python* 2>/dev/null

# 公式インストーラー
ls -la /Library/Frameworks/Python.framework/Versions/

# pyenv
ls -la ~/.pyenv/versions/ 2>/dev/null

# ユーザーディレクトリ
ls -la ~/Library/Python/*/bin/ 2>/dev/null
```

## 判定基準

### ✅ 重複なし（正常）のパターン
```
例1: シンボリックリンクで同じ実体を指している
/usr/local/bin/python3 -> /Library/Frameworks/.../python3
/usr/local/bin/python3.12 -> /Library/Frameworks/.../python3.12
└─ 実体は1つ ✅

例2: システム標準と独立したインストール
/usr/bin/python3 (macOS標準 3.9.6)
/Library/Frameworks/.../python3 (自分でインストール 3.12.4)
└─ 用途が異なるため正常 ✅
```

### ❌ 重複あり（要整理）のパターン
```
例1: 同じバージョンの実体が複数
/Library/Frameworks/.../python3.12 (3.12.4)
/opt/homebrew/Cellar/python@3.12/.../python3.12 (3.12.4)
└─ 重複！どちらか削除 ❌

例2: 異なるバージョンが多数
/opt/homebrew/bin/python3.9
/opt/homebrew/bin/python3.10
/opt/homebrew/bin/python3.11
/opt/homebrew/bin/python3.12
└─ 使わないバージョンは削除推奨 ⚠️
```

## ワンライナーチェックスクリプト
```bash
echo "=== Python重複チェック ===" && \
echo "" && \
echo "1. 利用可能なコマンド:" && \
which -a python python3 python3.{9..13} 2>/dev/null | sort -u && \
echo "" && \
echo "2. 各コマンドの実体:" && \
for cmd in python3 python3.12; do \
  if command -v $cmd &>/dev/null; then \
    echo "$cmd -> $(ls -la $(which $cmd) 2>/dev/null | awk '{print $NF}')"; \
  fi; \
done && \
echo "" && \
echo "3. インストール場所:" && \
ls -d /Library/Frameworks/Python.framework/Versions/*/ 2>/dev/null && \
ls -d /opt/homebrew/Cellar/python*/ 2>/dev/null && \
ls -d /usr/local/Cellar/python*/ 2>/dev/null && \
ls -d ~/.pyenv/versions/*/ 2>/dev/null && \
echo "" && \
echo "4. Homebrewインストール:" && \
brew list --formula 2>/dev/null | grep -i python || echo "なし"
```

## あなたの環境の結果
```
✅ Python 3.12.4 の実体: 1つのみ
   /Library/Frameworks/Python.framework/Versions/3.12/

✅ シンボリックリンク: /usr/local/bin/python3* → すべて上記を参照

✅ macOS標準: /usr/bin/python3 (3.9.6) → 別用途のため正常

結論: 重複なし、クリーンな状態 ✅
```
