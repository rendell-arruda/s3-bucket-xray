# s3-bucket-xray

Raio-X de buckets S3: tamanho, padrão de acesso, versionamento e lifecycle consolidados em um relatório de otimização de custo.

## Por quê

Buckets crescem sem que ninguém olhe para eles. Versionamento ligado sem regra para versões antigas, dados frios em Standard e buckets sem dono são fontes comuns de desperdício. Este projeto gera um resumo por bucket apontando esses problemas.

## Status

| Versão | Entrega |
|---|---|
| v0.1 | Gerador de dataset sintético no formato das APIs da AWS |
| v0.2 | Relatório por bucket com as primeiras regras de diagnóstico |

## Como rodar

```bash
python src/generate_data.py --buckets 50 --seed 42
```

Gera `data/buckets.json`. Requer apenas Python 3.10+ (sem dependências externas).

## Dados

O dataset é sintético e imita o formato devolvido por `boto3` e pelo CloudWatch (`BucketSizeBytes`, `NumberOfObjects`), para que a fonte possa ser trocada por uma conta AWS real sem alterar a análise.
