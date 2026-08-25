import json
from pathlib import Path
import pandas as pd

class SnapshotStore:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def save(self, snapshot_id: str, records: list[dict]) -> dict[str, str]:
        raw_dir = self.project_root / "data" / "raw" / "catalog_snapshots" / snapshot_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        json_path = raw_dir / "products.json"
        csv_path = raw_dir / "products.csv"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        flat = []
        for r in records:
            x = dict(r)
            x["sizes"] = "|".join(x.get("sizes") or [])
            x["image_urls"] = "|".join(x.get("image_urls") or [])
            flat.append(x)
        df = pd.DataFrame(flat)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        latest_csv = self.project_root / "data" / "processed" / "inti_catalog_latest.csv"
        latest_json = self.project_root / "data" / "processed" / "inti_catalog_latest.json"
        latest_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(latest_csv, index=False, encoding="utf-8-sig")
        with latest_json.open("w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return {"snapshot_csv": str(csv_path), "snapshot_json": str(json_path), "latest_csv": str(latest_csv)}
