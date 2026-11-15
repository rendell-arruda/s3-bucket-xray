"""Gera um dataset sintético de buckets S3.

Os campos imitam o formato devolvido pelas APIs reais da AWS (boto3 + CloudWatch),
para que no futuro a fonte sintética possa ser trocada por uma conta real sem
mudar o código de análise.

Uso:
    python src/generate_data.py --buckets 50 --seed 42
"""

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

GB = 1024**3
TB = 1024**4

REGIONS = ["us-east-1", "us-east-2", "sa-east-1", "eu-west-1"]
OWNERS = ["data-team", "platform", "finance", "marketing", None]  # None = sem dono
PREFIXES = ["logs", "backup", "datalake", "app-assets", "reports", "tmp", "ml-models"]

# Dimensão StorageType usada pela métrica BucketSizeBytes do CloudWatch
STORAGE_CLASSES = [
    "StandardStorage",
    "StandardIAStorage",
    "GlacierInstantRetrievalStorage",
    "DeepArchiveStorage",
]


def random_lifecycle(versioning_enabled: bool) -> list[dict]:
    """Retorna regras no formato de get_bucket_lifecycle_configuration()['Rules']."""
    if random.random() < 0.5:
        return []  # bucket sem lifecycle (cenário problemático comum)

    rules = [
        {
            "ID": "transition-to-ia",
            "Status": "Enabled",
            "Filter": {"Prefix": ""},
            "Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"}],
        }
    ]
    # Só às vezes há regra para versões antigas, mesmo com versionamento ligado
    if versioning_enabled and random.random() < 0.4:
        rules.append(
            {
                "ID": "expire-noncurrent",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "NoncurrentVersionExpiration": {"NoncurrentDays": 30},
            }
        )
    return rules


def random_storage(total_bytes: int, has_lifecycle: bool) -> dict[str, int]:
    """Distribui o tamanho total entre storage classes.

    Sem lifecycle, quase tudo fica em Standard (o que gera o desperdício).
    """
    if not has_lifecycle:
        weights = [0.95, 0.05, 0.0, 0.0]
    else:
        weights = [random.uniform(0.1, 0.5), random.uniform(0.2, 0.5),
                   random.uniform(0.0, 0.3), random.uniform(0.0, 0.2)]
    total_w = sum(weights)
    return {sc: int(total_bytes * w / total_w) for sc, w in zip(STORAGE_CLASSES, weights)}


def generate_bucket(index: int, now: datetime) -> dict:
    prefix = random.choice(PREFIXES)
    region = random.choice(REGIONS)
    owner = random.choice(OWNERS)

    versioning_enabled = random.random() < 0.6
    lifecycle_rules = random_lifecycle(versioning_enabled)

    # Distribuição de cauda longa: poucos buckets enormes, muitos pequenos
    total_bytes = int(random.lognormvariate(mu=4.0, sigma=2.0) * GB)
    object_count = max(1, int(total_bytes / random.uniform(0.5, 50) / 1024**2))

    noncurrent_bytes = 0
    if versioning_enabled:
        has_noncurrent_rule = any("NoncurrentVersionExpiration" in r for r in lifecycle_rules)
        ratio = random.uniform(0.01, 0.1) if has_noncurrent_rule else random.uniform(0.2, 1.5)
        noncurrent_bytes = int(total_bytes * ratio)

    creation_date = now - timedelta(days=random.randint(30, 2000))
    age_days = (now - creation_date).days
    days_since_last_access = random.randint(0, age_days)

    return {
        "Name": f"acme-{prefix}-{region}-{index:03d}",
        "Region": region,
        "CreationDate": creation_date.isoformat(),
        "Tags": [{"Key": "owner", "Value": owner}] if owner else [],
        "Versioning": {"Status": "Enabled"} if versioning_enabled else {},
        "LifecycleRules": lifecycle_rules,
        "Metrics": {
            "BucketSizeBytes": random_storage(total_bytes, bool(lifecycle_rules)),
            "NumberOfObjects": object_count,
            "NoncurrentVersionBytes": noncurrent_bytes,
        },
        # Simulado: no mundo real viria de Server Access Logs ou CloudTrail data events
        "DaysSinceLastAccess": days_since_last_access,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dataset sintético de buckets S3")
    parser.add_argument("--buckets", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/buckets.json"))
    args = parser.parse_args()

    random.seed(args.seed)
    now = datetime.now(timezone.utc)
    buckets = [generate_bucket(i, now) for i in range(1, args.buckets + 1)]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(buckets, indent=2, ensure_ascii=False))
    print(f"{len(buckets)} buckets gerados em {args.output}")


if __name__ == "__main__":
    main()
