# veridis 🎧

Projeto de dados que explora meus próprios hábitos de escuta no Spotify, combinando
dados extraídos via **API oficial do Spotify** com uma base histórica maior de
streams globais (Kaggle), construindo um pipeline completo de engenharia de dados:
extração → armazenamento em nuvem (AWS S3) → transformação → modelagem em SQL →
dashboard final em Power BI.

> Nome inspirado em "Veridis Quo", do Daft Punk.

## Status do projeto

🚧 Em construção — começando pela etapa de extração via API.

## Como rodar

### 1. Clone o repositório e entre na pasta
```bash
git clone https://github.com/JGois1/Veridis.git
cd veridis
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure suas credenciais
Copie o arquivo de exemplo e preencha com suas credenciais do
[Spotify Developer Dashboard](https://developer.spotify.com/dashboard):

```bash
cp .env.example .env
```

Depois edite o `.env` com seu `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET`.

### 5. Teste a conexão
```bash
python src/auth_test.py
```

Isso vai abrir o navegador pedindo login e autorização no Spotify, e depois
imprimir suas top 5 faixas mais escutadas recentemente no terminal.

## Arquitetura (planejada)

```
[API Spotify] ─┐
               ├─→ [Extração Python] → [S3: dados brutos] → [Transformação]
[Kaggle CSV] ──┘                                                  │
                                                                    ▼
                                            [SQL: modelagem] → [Power BI]
```

## Tecnologias

- Python (spotipy, pandas)
- AWS S3
- SQL
- Power BI
- Git/GitHub

## Resultados até agora

### Dados brutos organizados no S3

Os arquivos extraídos da API do Spotify são enviados automaticamente pro bucket,
particionados por tipo de dado (top faixas, top artistas, tocadas recentemente,
curtidas):

![Bucket S3 com dados organizados por pasta](screenshots/s3_bucket.png)

## Próximos passos

- [ ] Testar autenticação
- [ ] Extrair top faixas, artistas e audio features
- [ ] Subir dados brutos para o S3
- [ ] Baixar e explorar dataset do Kaggle
- [ ] Transformar e unificar as duas fontes
- [ ] Modelar em SQL
- [ ] Construir dashboard no Power BI
