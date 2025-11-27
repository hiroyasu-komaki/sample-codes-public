# IT Portfolio Dashboard Project

## 概要

- ここに概要を書く

<br>

## 提供している画面機能

1. **IT Portfolio Dashboard** - ITポートフォリオ管理
   - 予算配分とROI分析
   - リソース管理とリスク可視化

2. **Project View** - プロジェクト鳥瞰図
   - 部門別プロジェクト一覧
   - 進捗状況とステータス管理

3. **Application Layer View** - アプリケーション鳥瞰図
   - システムマップとEOL（サポート終了）管理
   - プロジェクトとの関連性を可視化

<br>

## ディレクトリ構造

```
project-root/
├── html/                          # HTMLファイル
│   ├── application_layer_view.html
│   ├── project_view.html
│   └── it_portfolio_dashboard.html
├── js/                            # JavaScriptファイル
│   ├── application_layer_view.js
│   ├── project_view.js
│   └── it_portfolio_dashboard.js
├── config/                        # 設定ファイル
│   ├── config.yaml               # データソース・システム設定
│   ├── config.js                 # スタイル・色設定
│   └── i18n.js                   # 多言語対応テキスト
├── data/                          # データファイル（JSON）
├── assets/                        # 静的アセット
│   └── css/
│       ├── input.css             # Tailwindソース
│       └── output.css            # ビルド済CSS（Gitにコミット）
├── node_modules/                  # npmパッケージ
├── index.html                     # トップページ
├── package.json                   # npmプロジェクト設定
├── tailwind.config.js             # Tailwind CSS設定
└── README.md
```

<br>

## 技術スタック

- **フロントエンド**: Vanilla JavaScript (ES6+)
- **スタイリング**: Tailwind CSS 3.x
- **データ形式**: JSON
- **設定形式**: YAML + JavaScript
- **多言語対応**: カスタム i18n システム

<br>

## セットアップ

### 初回セットアップ

```bash
# 依存関係のインストール
npm install
```

### CSSビルド

Tailwind CSSを使用しているため、スタイル変更時はビルドが必要です。

```bash
# 開発時（ファイル監視モード）
npm run dev

# 本番ビルド（最適化・圧縮）
npm run build:css
```

**CSSビルドが必要なタイミング：**
- ✅ 新しいTailwindクラスを追加したとき
- ✅ `tailwind.config.js`を変更したとき
- ❌ データやテキストのみ変更した場合は不要

<br>

## 貢献ガイドライン

### 歓迎する貢献

- 🐛 バグ報告・修正
- ✨ 新機能の提案・実装
- 📖 ドキュメントの改善
- 🎨 デザインの改善
- 🌍 翻訳の追加

### 貢献の流れ
- 本書末尾に記載します

<br>

## セキュリティ

- このシステムは**社内限定公開**を想定しています
- 機密情報をデータファイルに含める場合は、適切なアクセス制限を設定してください
- 外部公開する場合は、認証・認可の仕組みを追加してください

<br>

## 質問や問題がある場合：
- チャネル: 
- メール: 

---

<br>

## 貢献の流れ

このプロジェクトはGitHubで管理されています。以下の手順で貢献してください。

### 1. **課題を見つける or アイデアを共有**

**Issue を確認・作成**
- Issues ページで既存の課題を確認
- 新しいバグや改善案がある場合は Issue を作成
- 既存の Issue にコメントして担当を表明

**Issue テンプレート例**
```markdown
## 概要
何を改善・修正したいか

## 現状の問題
どんな問題があるか

## 提案する解決策
どう改善したいか

## 優先度
[ ] 高 [ ] 中 [ ] 低
```

### 2. **リポジトリをフォーク & ブランチ作成**

**ローカルにクローン**
```bash
git clone {クローンするリポジトリのURL}
```

**依存関係のインストール**
```bash
npm install
```

**作業用ブランチを作成**
```bash
# ブランチ名の例:
# - feature/add-new-dashboard (新機能)
# - fix/project-view-bug (バグ修正)
# - docs/update-readme (ドキュメント)
# - data/update-applications (データ更新)

git checkout -b feature/your-feature-name
```

### 3. **変更を加える**

**変更タイプ別ガイド**

| 変更内容 | 編集ファイル | CSSビルド必要 | 例 |
|---------|------------|--------------|-----|
| テキスト・ラベル変更 | `config/i18n.js` | ❌ 不要 | 画面タイトル、ボタンラベル |
| 色・スタイル変更 | `config/config.js`, `tailwind.config.js` | ⚠️ カスタムカラー追加時のみ | テーマカラー、レイアウト |
| システム設定 | `config/config.yaml` | ❌ 不要 | データソースパス、デフォルト言語 |
| データ更新 | `data/*.json` | ❌ 不要 | プロジェクト情報、予算データ |
| 機能追加・修正 | `js/*.js` | ⚠️ 新しいクラス使用時のみ | 新機能、バグ修正 |
| 画面レイアウト | `html/*.html` | ✅ 新しいクラス使用時 | HTML構造の変更 |

**スタイル変更時の手順**
```bash
# 開発モード起動（ファイル監視）
npm run dev

# HTMLやJSを編集
# → 保存すると自動で再ビルド

# 完了したら Ctrl+C で停止
```

### 4. **テスト**

**テストチェックリスト**
- [ ] データが正しく表示される
- [ ] 日本語・英語両方で確認
- [ ] エラーがコンソールに出ていない（F12で確認）
- [ ] ブラウザをリロードしても動作する
- [ ] スタイル変更した場合: `npm run build:css` を実行済み

### 5. **プルリクエスト作成**

**変更をコミット**
```bash
# スタイル変更した場合は必ずビルド
npm run build:css

# 変更をステージング
git add .

# コミット
git commit -m "機能: XXXを追加"

# プッシュ
git push origin feature/your-feature-name
```

**重要: CSSファイルのコミット**
スタイルを変更した場合、`assets/css/output.css`も必ずコミットしてください。
（GitHub Pagesでの表示に必要なため）

**GitHub上でプルリクエストを作成**
1. GitHubのリポジトリページにアクセス
2. "Compare & pull request" ボタンをクリック
3. 以下の内容を記入：

```markdown
## 変更内容
何を変更したか簡潔に説明

## 変更理由
なぜこの変更が必要か

## テスト結果
- [x] ローカルで動作確認済み
- [x] 日本語・英語で確認済み
- [x] コンソールエラーなし
- [x] CSSビルド実行済み（該当する場合）

## スクリーンショット
（該当する場合は画面キャプチャを添付）

## 関連Issue
Closes #123
```

**レビュー対応**
- レビュアーからのコメントに対応
- 修正が必要な場合は追加コミット
```bash
git add .
git commit -m "レビュー指摘: XXXを修正"
git push origin feature/your-feature-name
```

---

**最終更新**: 2025年11月16日  
**バージョン**: 1.0.0