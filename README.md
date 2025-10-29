# Azure OpenAI RAG サンプル

アップロードした PDF を FAISS でベクトル化し、Azure OpenAI を用いた RAG チャットを提供するサンプルアプリケーションです。バックエンドは FastAPI、フロントエンドは Vite + React で構成されています。

## 構成

```
.
├─ backend/                # FastAPI アプリケーション
│  ├─ main.py              # エントリポイント（アップロード & チャット API）
│  ├─ config.py            # 環境変数の読み込み設定
│  ├─ deps.py              # 依存解決ヘルパ
│  ├─ models.py            # Pydantic モデル
│  ├─ requirements.txt     # バックエンド依存パッケージ
│  └─ rag/
│     ├─ loader.py         # PDF 読み込み & チャンク化
│     ├─ embeddings.py     # Azure OpenAI 埋め込みクライアント
│     └─ retriever.py      # FAISS ベクトルストア & 推論パイプライン
├─ frontend/               # Vite + React フロントエンド
│  ├─ package.json
│  ├─ index.html
│  └─ src/
│     ├─ App.tsx           # UI ロジック
│     ├─ api.ts            # REST API クライアント
│     ├─ main.tsx
│     └─ styles.css
├─ scripts/
│  └─ init_faiss.py        # 既存 PDF をまとめてインデックス化するスクリプト
├─ .env.example            # 必要な環境変数サンプル
└─ README.md
```

## 必要な Azure リソース

1. **Azure OpenAI リソース**
   - チャット用モデル (例: `gpt-4o-mini`)
   - 埋め込みモデル (例: `text-embedding-3-large`)
2. （任意）PDF を永続化するストレージ（Azure Blob Storage など）

## 環境変数の設定

`.env.example` を参考に `.env` ファイルを作成し、バックエンド起動ディレクトリ直下に配置します。

```bash
cp .env.example .env
```

必要に応じて以下を編集してください。

| 変数名 | 説明 |
| ------ | ---- |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI リソースのエンドポイント URL |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI の API キー |
| `AZURE_OPENAI_API_VERSION` | 利用する API バージョン（既定: `2024-05-01-preview`） |
| `AZURE_OPENAI_DEPLOYMENT` | チャットモデルのデプロイ名 |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | 埋め込みモデルのデプロイ名 |
| `CHUNK_SIZE` | （任意）ドキュメントチャンクサイズ |
| `CHUNK_OVERLAP` | （任意）チャンク間オーバーラップ |
| `FAISS_INDEX_PATH` | （任意）FAISS インデックス保存先 |

本番環境では Azure App Service やコンテナホスティングの環境変数設定画面で同名の変数を登録してください。

## バックエンドの起動

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 既存 PDF の一括インデックス化（任意）

`scripts/init_faiss.py` は `data/docs` ディレクトリに保存した PDF をまとめてインデックス化します。

```bash
mkdir -p data/docs
cp /path/to/*.pdf data/docs/
python -m scripts.init_faiss
```

## フロントエンドの起動

別ターミナルで以下を実行します。

```bash
cd frontend
npm install
npm run dev
```

ブラウザで <http://localhost:5173> を開くと、
- PDF アップロード
- 質問入力
- 回答と参照コンテキスト表示
が利用できます。開発サーバーは `/api` へのリクエストを FastAPI バックエンド (`http://localhost:8000`) にプロキシします。

## API エンドポイント

| メソッド | パス | 概要 |
| -------- | ---- | ---- |
| `GET` | `/health` | ヘルスチェック |
| `POST` | `/upload` | PDF を受け取り、チャンク化して FAISS に登録 |
| `POST` | `/chat` | 質問を受け取り、FAISS で検索→Azure OpenAI で回答生成 |

## 参考

- [LangChain](https://python.langchain.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vite](https://vitejs.dev/)
