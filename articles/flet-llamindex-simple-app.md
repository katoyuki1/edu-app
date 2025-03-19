---
title: "FletとLlamaIndexで簡単なAIアシスタントを作ってみる" # 記事のタイトル
emoji: "😸" # アイキャッチとして使われる絵文字（1文字だけ）
type: "tech" # tech: 技術記事 / idea: アイデア記事
topics: ["Flet", "LlamaIndex"] # タグ。["markdown", "rust", "aws"]のように指定する
published: false # 公開設定（falseにすると下書き）
---
## 目的
- **ベクトル検索**や**RAG（Retrieval-Augmented Generation）の基本概念を理解する**    
- **サンプルアプリ制作を通して、FletとLlamaIndexを体験する**

## 対象読者
- *ベクトル検索*や**RAG**をざっくり理解したい。
- **アプリを作りながら学びたい**
- **Flet、LlamaIndexを学びたい**

## 開発環境
- OS：**macOS(Apple M1)**

---

## この記事でどんなものを作るのか？
この記事では、**FletとLlamaIndexを活用した簡単なAIアシスタント**を作成します。

このアプリは、**SQLiteに保存された情報を検索し、OllamaのLLMを使って回答を生成するRAG（Retrieval-Augmented Generation）システム** です。

具体的には、ユーザーが質問を入力すると、**データベース内の関連情報を検索**し、  
Ollamaを使って適切な回答を生成します。

**完成イメージ:**
- ユーザー：「tanakaの職業は？」
- AI：「tanakaの職業はシステムエンジニアです。」

---


## Fletとは？
[Flet](https://flet.dev/) は、Pythonで**簡単にGUIアプリを作成できるフレームワーク** です。

- **HTMLやJavaScript不要！** PythonだけでGUIを作れる
- **Flutterベース**なので、クロスプラットフォームで動作（Windows, macOS, Linux）
- **シンプルなAPI設計**で、直感的にアプリ開発ができる

今回のアプリでは、Fletを使って**ユーザーが質問を入力し、AIの回答を表示するインターフェース**を作成します。

---

## LlamaIndexとは？
[LlamaIndex](https://gpt-index.readthedocs.io/en/latest/) は、**データを検索し、生成AIと統合するためのライブラリ** です。

- **RAGの実装に最適**（検索+生成AIの統合）
- **ベクトル検索を簡単に実装可能**（SQLite, Qdrant, Weaviateなどと連携）
- **OpenAI, Ollama, Hugging Face など様々なLLMを利用できる**

今回のアプリでは、LlamaIndexを使用して**SQLiteのデータを検索し、OllamaのLLMを用いて回答を生成**します。



## ベクトル検索、RAGとは？

### 1. ベクトル検索とは

ベクトルとは「大きさ」と「向き」を持つデータのことです。

数学的には数値の配列（リスト）として表します。


	例:
	•	文章「今日は晴れです」 → [0.2, 0.8, -0.1, 0.5]
	•	画像（犬の写真） → [0.7, -0.3, 0.9, -0.2]



ベクトル検索では、データをベクトルに変換し、「どれだけ似ているか（類似度）」を計算して検索します。

例えば、「犬、芝犬、チワワ」「猫、スコテッシュフィールド、マンチカン」をベクトル変換して、以下のような数値の配列になったとします(あくまで例で、実際はもっと複雑な数値になると思います)。
- 犬[1.0]、芝犬[1.1]、チワワ[1.2]
- 猫[2.0]、スコティッシュフィールド[2.1]、マンチカン[2.2]

そして「犬の写真」でベクトル検索をすると、
犬[1.0]の数値に近い芝犬[1.1]やチワワ[1.2]の写真が、
検索結果として表示されます。

これがベクトル検索の大まかな流れになります。

	例：
	1.	「犬の写真」のベクトルを計算
	2.	他のデータ（猫の写真、人の写真）のベクトルと比較
	3.	一番似ているデータ（犬の写真）を検索結果として表示れになります。


ベクトル検索は、今までのグーグルなどのキーワード検索よりも
曖昧な指示で柔軟な検索をすることができます。


⸻

### 2. RAG（Retrieval-Augmented Generation）とは

RAG（リトリーバル・オーグメンテッド・ジェネレーション）は、すでに大量のデータで学習済みのAI（LLM）に、追加の情報を与えることで、ベクトル検索の精度を向上させる仕組みです。


(個人や企業などの、公になってないデータなど)

例：

質問：「パンダは何を食べますか？」
	1.	「パンダ」「食べ物」をベクトルに変換
	2.	ベクトル検索で「パンダは竹を食べる」という知識を取得
	3.	「パンダは主に竹を食べます」とAIが回答

⸻

3. まとめ
	•	ベクトル検索 → データをベクトルに変換して「似ているデータ」を検索
	•	RAG → ベクトル検索で知識を取得し、AIが文章生成

ベクトル検索とRAGを組み合わせることで、より正確で詳しい回答が可能になります。

### **なぜRAGを使うのか？**
- LLMは**学習データにない情報には回答できない** → **RAGなら最新データを活用可能！**
- 長文プロンプトを入れるとコストがかかる → **RAGなら検索して必要な情報だけ渡せる！**

今回のアプリでは、**SQLiteを使って情報を検索し、Ollamaを使って回答を生成するRAGを実装**します。

---
## Ollamaとは？

Ollama は、ローカル環境で LLM（大規模言語モデル）を実行できるツールです。

### Ollamaの特徴

- ローカル実行可能

    OpenAI APIのようにインターネット接続が必要ないため、オフラインでも動作可能。

    モデルやデータがローカル環境に保存されるため、セキュリティが高い。

- 高速な応答速度

    モデルをローカルで稼働させるため、API通信の待機時間がなく、高速に応答可能。

    GPU が利用できる場合はさらにパフォーマンスが向上。

- コスト削減
OpenAI API などのクラウドベースのLLMサービスは利用量に応じて課金が発生しますが、Ollama は無料で利用可能。

    一度モデルをダウンロードすれば、ローカルで無制限に利用可能。

- さまざまなモデルに対応

    llama3, mistralなどの様々なモデルに対応。


### なぜOllamaを使用したのか？

- コスト削減 → OpenAI の API 利用には料金が発生するが、Ollama なら無料


モデルの選択肢が豊富 → Mistral や Llama など、タスクに応じてモデルを選択可能

今回のアプリでは、Ollama の mistral モデルを使用しています。


## RAGとは？

RAG（Retrieval-Augmented Generation） とは、
データベースなどの外部情報を検索し、その情報をもとにLLM（大規模言語モデル）が回答を生成する仕組み です。

### RAGの仕組み

検索（Retrieval）: データベースやベクトルストアから関連情報を取得

生成（Generation）: 検索結果をもとに、生成AI（LLM）が回答を作成

### なぜRAGを使うのか？

LLMは学習データにない情報には回答できなません。
例えば「営業部の田中さんの月の給料は？」みたいな企業の内部情報など。

RAGを使えば、企業のデータベースの情報をもとに、LLMで「田中さんは月収30万円です」
のように回答を生成できませう。




今回のアプリでは、SQLiteを使って情報を検索し、Ollamaを使って回答を生成するRAGを実装します。

## サンプルアプリ 簡易AI-Assistant の作成手順

1. プロジェクトフォルダを作成

mkdir ai_assistant
cd ai_assistant

2. 仮想環境を作成し、有効化

python -m venv venv
source venv/bin/activate  # macOS/Linux の場合
venv\Scripts\activate  # Windows の場合

3. 必要なライブラリをインストール

pip install flet llama-index ollama python-dotenv

4. データベースの作成 (initialize_db.py)

(省略)

5. AIアシスタントの検索 (rag.py)

(省略)

6. Flet で UI を作成 (app.py)

(省略)

7. アプリを実行

python app.py

まとめ

FletとLlamaIndexを活用して、簡単なRAGシステムを実装しました。

SQLiteのデータを検索し、生成AIで回答を生成

Fletを使ってシンプルなUIを実装

RAGの基本を学びながら、FletとLlamaIndexの活用方法も体験できるサンプルとなっています。

参考文献

Flet公式ドキュメント

LlamaIndex公式ドキュメント

Ollama公式サイト




## サンプルアプリ **簡易AI-Assistant** の作成手順

### **1. プロジェクトフォルダを作成**
```bash
mkdir ollama_assistant
cd ollama_assistant
```

### **2. 仮想環境を作成し、有効化**
```bash
python -m venv venv
source venv/bin/activate
```
![スクリーンショット 2025-03-08 21.52.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/7dc954e4-4a9a-44b9-a7d3-c24ad59aae69.png)  


### **3. 必要なライブラリをインストール**
```bash
pip install flet llama-index ollama python-dotenv llama-index-llms-ollama llama-index-embeddings-ollama
```
![スクリーンショット 2025-03-08 21.54.15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/7b7a6316-6bd6-492f-b87e-fa9d4be907df.png)          
![スクリーンショット 2025-03-08 21.55.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/498be186-b9cf-43f0-ba95-c1aacaf05efb.png)      



### **4. データベースの作成 (`ollama_assistant/data/initialize_db.py`)**
ホームディレクトリにて、
dataフォルダを作成します。
さらにその配下にinitialize_db.pyというファイルを作成します。
```
mkdir data
touch data/initialize_db.py
```
initialize_db.pyに以下のコードを記載します。
```python
import sqlite3

# SQLiteデータベースを作成
conn = sqlite3.connect("data/data.db")
cursor = conn.cursor()

# データテーブルを作成
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
)
""")

# サンプルデータを追加
documents = [
    "suzukiの年齢は50歳です",
    "tanakaの職業はシステムエンジニアです"
]

for doc in documents:
    cursor.execute("INSERT INTO documents (text) VALUES (?)", (doc,))

conn.commit()
conn.close()

print("データベースの初期化が完了しました！")
```

作成したらターミナルで上記のコードを実行します。
```
python data/initialize_db.py
```
![スクリーンショット 2025-03-08 22.04.44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/b34a92bc-6bd7-4bbc-8b63-63a984343dd9.png)


### **5. AIアシスタントの検索 (`rag.py`)**
ホームディレクトリにて、
modelsフォルダを作成します。
さらにその配下に、rag.pyファイルを作成。
```
mkdir models
touch models/rag.py  
```

rag.py  に以下のコードを記載します。
``` python:
import os
import sqlite3
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding  # ← Embedding も Ollama に変更
from llama_index.core.schema import Document
import ollama

# Ollamaの設定（ローカルモデルを使用）
llm = Ollama(model="mistral")  # LLM を Ollama に設定
embed_model = OllamaEmbedding(model_name="mistral")

# LlamaIndex のデフォルト設定を Ollama に切り替え
Settings.llm = llm
Settings.embed_model = embed_model  # OpenAI の Embedding を使わない

# SQLiteデータを取得
def fetch_data():
    conn = sqlite3.connect("data/data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM documents")
    docs = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print("📌 データ取得確認:", docs)  # デバッグ用のログ
    return docs

# データをLlamaIndexに登録（Documentオブジェクトに変換）
documents = [Document(text=doc) for doc in fetch_data()]
print("📌 LlamaIndex に取り込むデータ:", [doc.text for doc in documents])  # デバッグ用

index = VectorStoreIndex.from_documents(documents)

# 検索関数（RAG処理）
def search_query(query):
    query_engine = index.as_query_engine(similarity_top_k=3)  # 類似度検索の上位3件を取得
    retrieved_docs = query_engine.query(query)  # 関連情報を取得

    print("📌 検索結果:", retrieved_docs)  # デバッグ用ログ

    # Ollama を使って最終的な回答を生成
    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "あなたは役立つアシスタントです。"},
            {"role": "user", "content": f"以下の情報を参考にして質問に答えてください:\n\n{retrieved_docs}\n\n質問: {query}"}
        ]
    )
    return response["message"]["content"]
```


### **6. Flet で UI を作成 (`app.py`)**
ホームディレクトリにapp.pyを作成し、以下のコードを記載します。
```
import flet as ft
from models.rag import search_query

def main(page: ft.Page):
    page.title = "AIアシスタント"
    page.scroll = "adaptive"

    chat = ft.Column()

    def send_message(e):
        user_input = input_box.value
        if not user_input:
            return
        
        # ユーザーメッセージを表示
        chat.controls.append(ft.Text(f"👤: {user_input}", size=16))
        page.update()

        # RAGで検索 + 生成AIで回答
        response = search_query(user_input)
        
        # AIの回答を表示
        chat.controls.append(ft.Text(f"🤖: {response}", size=16, color="blue"))  
        page.update()

        # 入力ボックスをクリア
        input_box.value = ""
        page.update()

    # UIレイアウト
    input_box = ft.TextField(label="質問を入力", width=500)
    send_button = ft.ElevatedButton("送信", on_click=send_message)

    page.add(chat, ft.Row([input_box, send_button]))

ft.app(target=main)

```


### **7. ollamaを起動　&　アプリを実行**
以下のコマンドでollamaを起動します
```
ollama serve
```
![スクリーンショット 2025-03-08 22.29.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/d71af94f-f093-4f74-85de-fb1d1b3f8c5c.png)


別のコンソール画面を開き、
ホームディレクトリでapp.pytを実行すると
以下のログが出力され、アプリが起動します。
```bash
python app.py
```
![スクリーンショット 2025-03-08 22.14.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/25ffe434-7a26-4e50-aa9b-67ac693d4ec1.png)            

![スクリーンショット 2025-03-08 22.14.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/ca416dac-80c7-423d-a99f-941dc0b53381.png)  
initialize_db.pyで登録した
suzukiとtanakaについて入力し「送信」を押下、しばらく待つと、DBに登録した情報を検索することができます。

![スクリーンショット 2025-03-08 22.17.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/c5f0c241-665f-4b90-b30c-6ba77e4a7249.png)
ただollamaはあまり賢くないのか、検索の精度は低いです。
「tanakaの職業は？」で回答へ得られないのに、
「tanaka」だけの質問で職業システムエンジニアと取得されます。
加えて余計な文章も含まれるという。。

ollamaは無料かつローカルのみで使えますが



---

## **まとめ**
- RAGとは、
- **SQLiteのデータを検索し、生成AIで回答を生成**
- **Fletを使ってシンプルなUIを実装**
- 
今回はRAGってどんな仕組み？をサンプルアプリを通して解説してみました。
ollamaが商用利用には適しませんが、
OpenAIのようにアカウント作ることなく無料で使えるので、ローカルで生成AIアプリを動かして遊分には良いと思います。

興味があったらぜひ上記コード動かしてみてください。

次は商用でも使えるAzule Open AIとかで遊んでみたいと思います。


---

## **参考文献**
- [Flet公式ドキュメント](https://flet.dev/)
- [LlamaIndex公式ドキュメント](https://gpt-index.readthedocs.io/)


## 用語整理
- AIモデル
    - AIの種類。人間でも医者Aや医者B、エンジニアCとエンジニアDなど、職業や人によって能力はことまります。AIモデルもllama3, gpt4oなど、モデルによって性能や得意なことがが異なる
- 