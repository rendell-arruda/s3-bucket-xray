# s3-bucket-xray

Raio-X de buckets S3: tamanho, padrão de acesso, versionamento e lifecycle consolidados em um relatório de otimização de custo.

## Por quê

Buckets crescem sem que ninguém olhe para eles. Versionamento ligado sem regra para versões antigas, dados frios em Standard e buckets sem dono são fontes comuns de desperdício. Este projeto gera um resumo por bucket apontando esses problemas, por exemplo:

```
acme-backup-sa-east-1-007
  Tamanho: 4.2 TB (92% em Standard)
  Último acesso: há 310 dias
  Versionamento: habilitado, sem regra para versões antigas (+1.8 TB noncurrent)
  Lifecycle: nenhum
  Owner: não definido
  → Sugestão: lifecycle para Glacier IR após 90 dias + expirar versões antigas após 30 dias
```

## Roadmap

Um commit por semana. Cada versão entrega algo utilizável.

| Versão | Entrega | Status |
|---|---|---|
| v0.1 | Gerador de dataset sintético no formato das APIs da AWS | ✅ |
| v0.2 | Relatório por bucket no terminal com as primeiras regras de diagnóstico | 🔜 |
| v0.3 | Estimativa de custo atual e economia potencial em USD | |
| v0.4 | Exportação do relatório em CSV e HTML | |
| v0.5 | Coletor real via `boto3` + CloudWatch (troca a fonte sintética por uma conta AWS) | |
| v0.6 | Resumo e recomendações em linguagem natural com IA | |

### Regras de diagnóstico planejadas

- Bucket sem lifecycle configurado
- Versionamento habilitado sem `NoncurrentVersionExpiration`
- Dados frios (sem acesso há N dias) ainda em Standard
- Bucket sem tag `owner`
- Multipart uploads incompletos (futuro)

## Como rodar

```bash
python src/generate_data.py --buckets 50 --seed 42
```

Gera `data/buckets.json`. Requer apenas Python 3.10+ (sem dependências externas).

## Dados

O dataset é sintético e imita o formato devolvido por `boto3` e pelo CloudWatch (`BucketSizeBytes`, `NumberOfObjects`), para que a fonte possa ser trocada por uma conta AWS real sem alterar a análise.

O "último acesso" é simulado. Em uma conta real, ele viria de S3 Server Access Logs ou de data events do CloudTrail.

## Uso de IA

O projeto é desenvolvido em pareamento com IA (Claude), usada como parceira de estudo e revisão de código. As decisões de design e o aprendizado ficam documentados nos commits.

## Como contribuir

Contribuições são bem-vindas, principalmente:

- Novas regras de diagnóstico (abra uma issue descrevendo o cenário de desperdício)
- Experiências reais com custos de S3 que o dataset sintético ainda não cobre
- Revisão de código e sugestões

Abra uma issue ou um PR.

## Licença

MIT
