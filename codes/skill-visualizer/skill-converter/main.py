from pathlib import Path
from modules.convert_skill import convert_skill


def main():
    base_dir = Path(__file__).parent

    csv_dir = base_dir / "csv"
    yaml_path = base_dir / "config" / "skillstd_conv.yaml"
    out_path = base_dir / "out" / "converted_skill_data.csv"

    convert_skill(
        csv_dir=csv_dir,
        yaml_path=yaml_path,
        out_path=out_path
    )

    print(f"変換完了: {out_path}")


if __name__ == "__main__":
    main()
