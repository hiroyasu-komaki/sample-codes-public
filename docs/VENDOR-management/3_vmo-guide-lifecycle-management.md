# ベンダーマネジメント実践ガイド

## 第3章：ベンダーライフサイクル管理

ベンダーマネジメントは「選定して終わり」ではありません。VMOは契約締結から終了まで、継続的にベンダーを管理する責任があります。

### 3.1 ベンダー台帳の作成と管理（VMOの最重要業務）

**VMOが管理すべきベンダー台帳の項目**：

```mermaid
erDiagram
    VENDOR ||--o{ CONTRACT : has
    VENDOR ||--o{ REVIEW : undergoes
    VENDOR ||--o{ RISK_SCORE : has
    
    VENDOR {
        string vendor_id PK
        string vendor_name
        string classification
        string contact_person
        date next_review_date
    }
    
    CONTRACT {
        string contract_id PK
        string vendor_id FK
        string contract_type
        decimal annual_amount
        date start_date
        date end_date
    }
    
    REVIEW {
        string review_id PK
        string vendor_id FK
        date review_date
        decimal sla_achievement
        string issues
    }
    
    RISK_SCORE {
        string score_id PK
        string vendor_id FK
        string risk_level
        date score_date
    }
```

**ベンダー分類（VMOが決定）**：

| 分類 | 定義 | レビュー頻度 | 管理レベル |
|------|------|---------------------|-----------|
| 戦略ベンダー | IT支出10%以上 or 事業継続必須 | 四半期毎 | 最高 |
| 重要ベンダー | 単一依存 or 機密データ取扱 | 半期毎 | 高 |
| 一般ベンダー | 代替可能・低額 | 年次 | 標準 |

**VMOが実施する分類基準**：
```mermaid
flowchart TD
    A[新規ベンダー] --> B{IT支出比率<br/>10%以上?}
    B -->|Yes| C[戦略ベンダー]
    B -->|No| D{事業継続<br/>必須?}
    D -->|Yes| C
    D -->|No| E{単一依存 or<br/>機密データ取扱?}
    E -->|Yes| F[重要ベンダー]
    E -->|No| G[一般ベンダー]
```

<br>

### 3.2 オンボーディング（VMOが主導）

契約締結後、VMOがベンダーを組織に迎え入れるプロセスです。

**VMOのオンボーディングチェックリスト**：

```mermaid
gantt
    title ベンダーオンボーディング（30日計画）
    dateFormat  YYYY-MM-DD
    section 初期設定
    ベンダー台帳登録           :done, a1, 2024-01-01, 1d
    役割・窓口の明確化         :done, a2, after a1, 2d
    エスカレーション経路設定   :active, a3, after a2, 2d
    section アクセス管理
    アカウント発行申請         :a4, after a3, 3d
    VPN・ネットワーク設定      :a5, after a4, 3d
    最低権限付与確認           :a6, after a5, 1d
    section キックオフ
    キックオフミーティング     :milestone, a7, after a6, 1d
    SLA/KPI確認               :a8, after a7, 2d
    section 初期監視
    初回レビュー設定           :a9, after a8, 14d
```

**VMOが実施すべき項目**：
1. ベンダー台帳への登録（ベンダーID、分類、連絡先）
2. ビジネスオーナー、技術オーナーの任命
3. エスカレーション経路の整備
4. アクセス権・VPN・アカウント発行のワークフロー化
5. キックオフミーティングの開催

<br>

### 3.3 パフォーマンス/リスクモニタリング（VMOの日常業務）

**月次レビュー（VMOが主催）**：

```mermaid
sequenceDiagram
    participant VMO
    participant ITサービスMGR
    participant サービスオーナー
    participant ベンダー
    
    ITサービスMGR->>VMO: SLA/KPI実績データ提供
    VMO->>VMO: データ分析・課題抽出
    VMO->>ベンダー: 月次レビュー招集
    ベンダー->>VMO: 実績報告
    VMO->>ベンダー: 改善要求・次月計画確認
    VMO->>サービスオーナー: レビュー結果報告
```

**VMOがモニタリングすべきKPI**：

| カテゴリ | KPI | 目標値 | データ取得元 | VMOの対応 |
|----------|-----|--------|-------------|-------------|
| サービス品質 | 可用性 | 99.9% | ITサービスMGR | 未達時に料金減額交渉 |
| サービス品質 | MTTR（平均復旧時間） | 4時間 | ITサービスMGR | 未達時に改善計画要求 |
| 関係性 | CSATスコア | 4.0/5 | サービスオーナー | 低評価時にエスカレーション |
| コスト | TCO削減率 | 年5% | 財務部門 | 未達時に再交渉 |
| リスク | セキュリティインシデント | 0件 | セキュリティ担当 | 発生時に契約解除検討 |

**四半期戦略レビュー（戦略・重要ベンダー向け、VMOが主導）**：

**VMOが準備すべき資料**：
- TCO実績 vs 契約時見込み
- ライセンス使用率分析
- ベンダーロードマップと自社IT戦略の整合性
- リスク変化（財務、体制、セキュリティ）

**VMOが協議すべき内容**：
- 契約更新に向けた改善提案
- 価格交渉・ボリュームディスカウント
- 共創企画・イノベーション機会
- 次年度のサービスレベル見直し

<br>

### 3.4 関係性・コスト最適化（VMOの価値創出）

**VMOが実施するコスト最適化手法**：

```mermaid
flowchart LR
    A[利用実績データ収集] --> B[分析]
    B --> C{最適化機会?}
    C -->|未使用ライセンス| D[ライセンス削減]
    C -->|利用集中| E[ボリュームディスカウント交渉]
    C -->|重複サービス| F[サービス統合]
    C -->|過剰スペック| G[プラン変更]
    D --> H[年間削減目標: 5-10%]
    E --> H
    F --> H
    G --> H
```

**VMOが戦略的ベンダーと実施すべき活動**：
- ロードマップ共有会議（四半期毎）
- 共創企画ワークショップ（年2回）
- エグゼクティブレビュー（CIO参加、年1回）
- イノベーションラボ参加（継続）

<br>

### 3.5 リスク管理とエスカレーション（VMOの危機管理）

**VMOが監視すべきリスクトリガー**：
- SLA連続未達（2ヶ月連続）
- 重大インシデント発生（事業影響大）
- ベンダー財務悪化（決算短信確認）
- セキュリティ事案・法令違反
- 主要担当者の離職・体制変更

**VMOが実行するエスカレーション**：

```mermaid
graph TD
    A[リスク検知] --> B{リスクレベル判定}
    B -->|レベル1: 軽微| C[月次レビューで対応]
    B -->|レベル2: 中程度| D[四半期レビュー前倒し<br/>改善計画要求]
    B -->|レベル3: 重大| E[緊急エスカレーション<br/>経営層報告]
    C --> F[VMOが記録・追跡]
    D --> G[VMO+サービスオーナー対応]
    E --> H[CIO/投資委員会判断<br/>契約凍結/解除検討]
```

<br>

### 3.6 オフボーディング（VMOが完遂する最終プロセス）

契約終了時、VMOが混乱なくベンダーを退出させる責任を負います。

**VMOのオフボーディング計画（90日前開始）**：

```mermaid
gantt
    title ベンダーオフボーディング（90日計画）
    dateFormat  YYYY-MM-DD
    section 準備期間
    終了通知発行               :done, o1, 2024-01-01, 1d
    後任ベンダー選定           :done, o2, after o1, 30d
    データ移管計画策定         :active, o3, after o1, 15d
    section 移行期間
    知識移管実施               :o4, after o3, 30d
    データ抽出・移行           :o5, after o3, 45d
    並行運用                   :o6, after o5, 15d
    section 終了処理
    アクセス遮断               :milestone, o7, 2024-04-01, 1d
    データ削除証明取得         :o8, after o7, 14d
    最終請求精算               :o9, after o7, 14d
    最終評価実施               :o10, after o9, 7d
```

**VMOのオフボーディングチェックリスト**：

- [ ] **90日前**：ベンダーに終了通知を正式発行
- [ ] **60日前**：データ移管計画完成（フォーマット、移管先確認）
- [ ] **30日前**：知識移管完了（運用マニュアル、設定情報、トラブルシューティングDB）
- [ ] **契約終了日**：全アカウント無効化、VPN切断
- [ ] **14日以内**：データ削除証明書取得
- [ ] **14日以内**：最終請求精算（未払・前払調整、ペナルティ）
- [ ] **30日以内**：最終評価レビュー実施、ベンダー台帳更新
- [ ] **30日以内**：事後検証（新ベンダー稼働確認、移行完了報告）

