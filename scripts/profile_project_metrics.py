import ast
import csv
import json
from collections import Counter
from pathlib import Path


def count_api_endpoints(api_file: Path) -> int:
    if not api_file.exists():
        return 0

    tree = ast.parse(api_file.read_text(encoding="utf-8"))
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in {"get", "post", "put", "patch", "delete"}
            ):
                path_arg = decorator.args[0] if decorator.args else None
                if isinstance(path_arg, ast.Constant) and path_arg.value != "/health":
                    count += 1
    return count


def raw_data_metrics(base_dir: Path) -> dict:
    rows = []
    for path in sorted(base_dir.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "partition": path.parent.name,
                "channel": path.stem,
                "messages": len(data),
                "messages_with_media": sum(1 for item in data if item.get("has_media")),
                "messages_with_image_path": sum(1 for item in data if item.get("image_path")),
            }
        )

    return {
        "raw_json_files": len(rows),
        "raw_partitions": sorted({row["partition"] for row in rows}),
        "channels": sorted({row["channel"] for row in rows}),
        "total_messages": sum(row["messages"] for row in rows),
        "messages_with_media": sum(row["messages_with_media"] for row in rows),
        "messages_with_image_path": sum(row["messages_with_image_path"] for row in rows),
        "messages_by_channel": {row["channel"]: row["messages"] for row in rows},
    }


def image_metrics(images_dir: Path) -> dict:
    images = [
        path
        for path in images_dir.glob("*/*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ]
    return {
        "image_files": len(images),
        "images_by_channel": dict(sorted(Counter(path.parent.name for path in images).items())),
    }


def detection_metrics(detections_csv: Path) -> dict:
    if not detections_csv.exists():
        return {"labeled_detections": 0, "object_categories": 0}

    with detections_csv.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    return {
        "labeled_detections": len(rows),
        "object_categories": len({row["object_label"] for row in rows if row.get("object_label")}),
    }


def dbt_metrics(manifest_path: Path, tests_dir: Path) -> dict:
    if not manifest_path.exists():
        return {
            "dbt_models": 0,
            "dbt_tests": 0,
            "custom_dbt_tests": len(list(tests_dir.glob("*.sql"))),
        }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    nodes = manifest.get("nodes", {}).values()
    models = sorted(node["name"] for node in nodes if node.get("resource_type") == "model")
    tests = sorted(node["name"] for node in nodes if node.get("resource_type") == "test")
    return {
        "dbt_models": len(models),
        "dbt_model_names": models,
        "dbt_tests": len(tests),
        "custom_dbt_tests": len(list(tests_dir.glob("*.sql"))),
    }


def main():
    metrics = {
        **raw_data_metrics(Path("data/raw/telegram_messages")),
        **image_metrics(Path("data/raw/images")),
        **detection_metrics(Path("data/processed/detections/detections.csv")),
        **dbt_metrics(Path("medical_warehouse/target/manifest.json"), Path("medical_warehouse/tests")),
        "analytical_api_endpoints": count_api_endpoints(Path("api/main.py")),
    }
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
