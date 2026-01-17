import yaml
import pandas as pd
from pathlib import Path


def load_skill_mapping(yaml_path: Path) -> dict:
    """
    YAMLから「スキル項目（skill_name）」→ capability の対応辞書を作成
    """
    print(f"[INFO] YAML読み込み: {yaml_path}")

    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    mapping = {
        skill["skill_name"]: skill["capability"]
        for skill in data.get("skills", [])
        if "skill_name" in skill and "capability" in skill
    }

    print(f"[INFO] YAML定義スキル数: {len(mapping)}")
    return mapping


def read_csv_files(csv_dir: Path) -> pd.DataFrame:
    """
    csvフォルダ配下のCSVをすべて読み込み、1つのDataFrameに結合
    """
    csv_files = sorted(csv_dir.glob("*.csv"))

    if not csv_files:
        raise RuntimeError("csvフォルダにCSVファイルが存在しません")

    print(f"[INFO] CSVフォルダ: {csv_dir}")
    print(f"[INFO] 読み込むCSVファイル数: {len(csv_files)}")

    df_list = []
    for f in csv_files:
        df = pd.read_csv(f, encoding="utf-8-sig")
        print(f"  - {f.name}: {len(df)} 行")
        df_list.append(df)

    df_all = pd.concat(df_list, ignore_index=True)

    print(f"[INFO] CSV結合後: {df_all.shape[0]} 行 × {df_all.shape[1]} 列")
    print(f"[INFO] 列一覧: {list(df_all.columns)}")

    return df_all


def convert_skill(
    csv_dir: Path,
    yaml_path: Path,
    out_path: Path
):
    print("[INFO] スキル変換処理 開始")

    # YAML → dict
    skill_mapping = load_skill_mapping(yaml_path)

    # CSV → DataFrame
    df = read_csv_files(csv_dir)

    if "スキル項目" not in df.columns:
        raise KeyError("CSVに「スキル項目」列が存在しません")

    # capability 列を追加
    df["capability"] = df["スキル項目"].map(skill_mapping)

    total_rows = len(df)
    defined_count = df["capability"].notna().sum()
    undefined_count = total_rows - defined_count

    df["capability"] = df["capability"].fillna("")

    print("[INFO] 変換結果サマリ")
    print(f"  - 総レコード数        : {total_rows}")
    print(f"  - capability 付与成功 : {defined_count}")
    print(f"  - 未定義スキル        : {undefined_count}")

    # capability別件数（空は除外）
    cap_stats = (
        df[df["capability"] != ""]
        ["capability"]
        .value_counts()
    )

    print("[INFO] capability 別件数")
    for cap, cnt in cap_stats.items():
        print(f"  - {cap}: {cnt}")

    # 出力
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"[INFO] 出力完了: {out_path}")
    print("[INFO] スキル変換処理 終了")
