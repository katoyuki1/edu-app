---
title: "FletとLlamaIndexで簡単なAIアシスタントを作ってみる" # 記事のタイトル
emoji: "😸" # アイキャッチとして使われる絵文字（1文字だけ）
type: "tech" # tech: 技術記事 / idea: アイデア記事
topics: ["Flet", "LlamaIndex"] # タグ。["markdown", "rust", "aws"]のように指定する
published: true # 公開設定（falseにすると下書き）
---
## 目的
- **ベクトル検索**や**RAG（Retrieval-Augmented Generation）の基本概念を理解する**    
- **以下のようなサンプルアプリ制作を通して、FletとLlamaIndexを体験する**
![](https://storage.googleapis.com/zenn-user-upload/e9f7c592c433-20250320.png)

## 対象読者
- *ベクトル検索*や**RAG**をざっくり理解したい。
- **アプリを作りながら学びたい**
- **Flet、LlamaIndexを学びたい**

## 開発環境
- OS：**macOS(Apple M1)**


## この記事でどんなものを作るのか？
この記事では、**FletとLlamaIndexを活用した簡単なAIアシスタント**を作成します。

このアプリは、**SQLiteに保存された情報を検索し、OllamaのLLMを使って回答を生成するRAG（Retrieval-Augmented Generation）システム** です。

具体的には、ユーザーが質問を入力すると、**データベース内の関連情報を検索**し、  
Ollamaを使って適切な回答を生成します。

**完成イメージ:**
- ユーザー：「tanakaの職業は？」
- AI：「tanakaの職業はシステムエンジニアです。」



## Fletとは？
[Flet](https://flet.dev/) は、Pythonで**簡単にGUIアプリを作成できるフレームワーク** です。

- PythonだけでGUIを作れ、**HTMLやJavaScriptが不要** 
- **Flutterベース**なので、クロスプラットフォームで動作（Windows, macOS, Linux）

今回のアプリでは、Fletを使って**ユーザーが質問を入力し、AIの回答を表示するインターフェース**を作成します。


## LlamaIndexとは？
[LlamaIndex](https://gpt-index.readthedocs.io/en/latest/) は、**データを検索し、生成AIと統合するためのライブラリ** です。

- **RAGの実装に最適**（検索+生成AIの統合）
- **ベクトル検索を簡単に実装可能**（SQLite, Qdrant, Weaviateなどと連携）
- **OpenAI, Ollama, Hugging Face など様々なLLMを利用できる**

今回のアプリでは、LlamaIndexを使用して**SQLiteのデータを検索し、ローカルで動作するOllamaのLLMを用いて回答を生成**します。


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



### 2. RAG（Retrieval-Augmented Generation）とは

RAG（リトリーバル・オーグメンテッド・ジェネレーション）は、すでに大量のデータで学習済みのAI（LLM）に、追加の情報を与えることで、ベクトル検索の精度を向上させる仕組みです。

#### なぜRAGを使うのか？

LLMは学習データにない情報には正確な回答ができません。
例えば「営業部の田中さんの月の給料は？」みたいな企業の内部情報などは回答できないか、間違った内容をあたかも正しい情報のように解答してしまいます。


RAGを使えば、企業のデータベースの情報をもとに、LLMで「田中さんは月収30万円です」
のように回答を生成することができます。



今回のアプリでは、SQLiteを使って情報を検索し、Ollamaを使って回答を生成するRAGを実装します。


## Ollamaとは？

Ollama は、ローカル環境で LLM（大規模言語モデル）を実行できるツールです。

### Ollamaの特徴

- ローカル実行可能

    OpenAI APIのようにインターネット接続が必要ないため、オフラインでも動作可能です


- コスト削減

    OpenAI API などのクラウドベースのLLMサービスは、利用量に応じて課金が発生しますが、Ollama は無料で利用可能です

    一度モデルをダウンロードすれば、ローカルで無制限に利用できます。


- さまざまなモデルに対応

    llama3, mistralなどの様々なモデルに対応。

今回のアプリでは、Ollama の mistral モデルを使用しています。


## サンプルアプリ **簡易AI-Assistant** の作成手順
最終的なディレクトリ構成は以下のようになります。
app.py、initialize_db.py、rag.pyの３つのファイルを作成します。
```
ollama_assistant
├── app.py
├── data
│   ├── data.db
│   └── initialize_db.py
└── models
    └── rag.py
```


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



### **4. テーブルの作成 (`ollama_assistant/data/initialize_db.py`)**
ホームディレクトリにて、
dataフォルダを作成します。
さらにその配下にinitialize_db.pyというファイルを作成します。
```
mkdir data
touch data/initialize_db.py
```
initialize_db.pyに以下のコードを記載します。
コメントで１行ずつ解説しています

（実際の開発では、行ずつコメントを書くことはありませんが、初心者向けの解説用コードとして、以下のように記載しています。）
```python:initialize_db.py
import sqlite3  # sqlite3: PythonでSQLiteという軽量なデータベースを操作するためのモジュールを読み込む

# SQLiteデータベースを作成または接続（存在しなければファイルが作成される）
conn = sqlite3.connect("data/data.db")
# データベースに対してSQL操作を実行するためのカーソル（操作の窓口）を作成する
cursor = conn.cursor()


"""
# データテーブルを作成するSQL文を実行
# IF NOT EXISTS: テーブルがなければ作成する
# id: 自動で1ずつ増加する一意な番号（PRIMARY KEY: 主キー）
# text: 文章を格納するテキスト型のカラム
"""
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
)
""")

# サンプルデータを追加するためのリストを作成
documents = [
    "suzukiの年齢は50歳です",  
    "tanakaの職業はシステムエンジニアです" 
]

# サンプルデータを1件ずつテーブルに挿入する
for doc in documents:
    cursor.execute("INSERT INTO documents (text) VALUES (?)", (doc,))  # プレースホルダー「?」で安全にデータを挿入

# データベースへの変更を保存する（commit: 変更を確定する操作）
conn.commit()
# データベースとの接続を閉じる
conn.close()

# データベースの初期化が完了したことを知らせるメッセージを表示
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
```python:
import sqlite3  # sqlite3: 軽量なデータベースSQLiteを操作するためのモジュール
from llama_index.core import VectorStoreIndex, Settings  # VectorStoreIndex: 検索可能なインデックスを作成するクラス, Settings: 設定管理用クラス
from llama_index.llms.ollama import Ollama  # Ollama: ローカルの大規模言語モデル（LLM）を操作するためのクラス
from llama_index.embeddings.ollama import OllamaEmbedding  # OllamaEmbedding: テキストを数値（埋め込みベクトル）に変換するクラス
from llama_index.core.schema import Document  # Document: テキストデータを保持するオブジェクトを定義するクラス
import ollama  # ollama: Ollama APIを使ってチャット機能を実行するモジュール

# Ollamaの設定（ローカルモデルを使用）
llm = Ollama(model="mistral")  # mistralという名前のローカルモデルを使ってLLMのインスタンスを作成
embed_model = OllamaEmbedding(model_name="mistral")  # mistralモデルを使ってテキストの埋め込み変換用インスタンスを作成

# LlamaIndex のデフォルト設定を Ollama に切り替える
Settings.llm = llm  # LlamaIndexのLLM設定を上で作成したOllamaのインスタンスに変更
Settings.embed_model = embed_model  # 埋め込みモデル設定をOllamaEmbeddingに変更（OpenAIのEmbeddingではなく）

# SQLiteデータを取得する関数を定義
def fetch_data():
    conn = sqlite3.connect("data/data.db")  # 指定したパスのSQLiteデータベースに接続（なければ新規作成）
    cursor = conn.cursor()  # データベース操作を行うためのカーソル（命令窓口）を作成
    cursor.execute("SELECT text FROM documents")  # SQL文でdocumentsテーブルからtextカラムの全データを取得する
    docs = [row[0] for row in cursor.fetchall()]  # 取得した全行からテキスト（最初の列）だけをリストにまとめる
    conn.close()  # データベース接続を終了する
    
    print("📌 データ取得確認:", docs)  # デバッグ用: 取得したデータ内容をコンソールに表示
    return docs  # 取得したテキストデータのリストを返す

# 取得したデータをDocumentオブジェクトに変換し、LlamaIndexに登録する準備
documents = [Document(text=doc) for doc in fetch_data()]  # 各テキストをDocumentクラスのインスタンスに変換する
print("📌 LlamaIndex に取り込むデータ:", [doc.text for doc in documents])  # デバッグ用: Documentオブジェクト内のテキストを表示

# Documentオブジェクトから検索可能なインデックスを作成する
index = VectorStoreIndex.from_documents(documents)  # VectorStoreIndex: ドキュメントをベクトル（数値表現）に変換し、検索可能なインデックスを作成

# 検索関数
def search_query(query):
    query_engine = index.as_query_engine(similarity_top_k=3)  # 入力クエリと最も類似した上位3件のドキュメントを取得する検索エンジンを設定
    retrieved_docs = query_engine.query(query)  # クエリを実行して関連情報（ドキュメント）を取得する

    print("📌 検索結果:", retrieved_docs)  # デバッグ用: 検索で取得した結果を表示

    # Ollamaチャット機能を使って、取得した情報をもとに最終的な回答を生成する
    response = ollama.chat(
        model="mistral",  # 使用するモデルの名前を指定
        messages=[
            {"role": "system", "content": "あなたは役立つアシスタントです。"},  # システムメッセージ: AIの振る舞いを指示する
            {"role": "user", "content": f"以下の情報を参考にして質問に答えてください:\n\n{retrieved_docs}\n\n質問: {query}"}
            # ユーザーメッセージ: 検索結果とユーザーの質問をAIに渡して回答を求める
        ]
    )
    return response["message"]["content"]  # AIが生成した回答の本文を返す
```


### **6. Flet で UI を作成 (`app.py`)**
ホームディレクトリにapp.pyを作成し、以下のコードを記載します。
```python:app.py
# fletというUIライブラリをftという名前で読み込む
import flet as ft  # PythonでGUI（グラフィカル・ユーザー・インターフェース）を作成するためのライブラリ

# models/ragモジュールからsearch_query関数を読み込む
from models.rag import search_query  #「RAG（検索と生成AIを組み合わせた手法）」を使って回答を生成する関数

# main関数を定義する。引数pageはFletが生成するページ（画面）を表すオブジェクト
def main(page: ft.Page):
    # ページのタイトルを「AIアシスタント」に設定（ウィンドウ上部に表示される）
    page.title = "AIアシスタント"
    # ページのスクロール方法を「adaptive」（状況に合わせて自動調整される）に設定
    page.scroll = "adaptive"

    # チャットメッセージを縦方向に並べるためのレイアウト（Column）を作成
    chat = ft.Column()

    # ユーザーがメッセージを送信したときに実行される関数を定義する
    def send_message(e):
        # 入力ボックスからユーザーが入力したテキストを取得する
        user_input = input_box.value
        # もし入力が空文字（何も入力されていない場合）なら何もしないで関数を終了する
        if not user_input:
            return
        
        # ユーザーが入力したメッセージを画面に表示する
        # ft.Textはテキストを表示するウィジェット。f-stringで変数user_inputの値を埋め込んでいる
        chat.controls.append(ft.Text(f"👤: {user_input}", size=16))
        # ページの表示を更新して、新しいテキストが反映されるようにする
        page.update()

        # search_query関数を呼び出し、RAGで回答を取得する
        response = search_query(user_input)
        
        # AIが生成した回答を画面に表示する
        # テキストの色を"blue"に設定して区別している
        chat.controls.append(ft.Text(f"🤖: {response}", size=16, color="blue"))
        # 表示を更新して新しいメッセージを反映する
        page.update()

        # 入力ボックスの内容をクリアして、次の入力に備える
        input_box.value = ""
        # 再度ページを更新して、クリアされた状態を反映する
        page.update()

    # ユーザーインターフェース（UI）のレイアウト設定

    # ユーザーが質問を入力するためのテキストフィールドを作成する
    # labelは入力欄の上に表示される説明、widthは入力欄の幅を指定
    input_box = ft.TextField(label="質問を入力", width=500)
    # 送信ボタンを作成。ボタンがクリックされたときにsend_message関数を実行する
    send_button = ft.ElevatedButton("送信", on_click=send_message)

    # ページにチャット部分と、入力欄と送信ボタンを横並び（Row）にして追加する
    page.add(chat, ft.Row([input_box, send_button]))

# Fletのアプリケーションを起動し、main関数をエントリーポイント(プログラムが実行を開始する最初の処理場所)として指定する
ft.app(target=main)

```


### **7. ollamaを起動　&　アプリを実行**
ターミナルで新たに新たにコンソール画面を開き、
アプリのホームディレクトリに移動。
以下のコマンドでollamaを起動します
```
source venv/bin/activate
ollama serve
```
![スクリーンショット 2025-03-08 22.29.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/d71af94f-f093-4f74-85de-fb1d1b3f8c5c.png)


アプリ作成時に使っていたコンソール画面に戻り
ホームディレクトリでapp.pytを実行すると
以下のログが出力され、アプリが起動します。
```bash
python app.py
```
![スクリーンショット 2025-03-08 22.14.10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/25ffe434-7a26-4e50-aa9b-67ac693d4ec1.png)        


![スクリーンショット 2025-03-08 22.14.45.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/ca416dac-80c7-423d-a99f-941dc0b53381.png)  

initialize_db.pyで登録した
suzukiとtanakaについて入力し「送信」を押下、しばらく待つと、DBに登録した情報を検索することができます。

ただ、質問の仕方によっては「情報が提供されていません」となります。
この辺はプロンプトを修正したり別のモデルに変更する必要がありそうです。

![スクリーンショット 2025-03-08 22.17.35.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2640031/c5f0c241-665f-4b90-b30c-6ba77e4a7249.png)



---

## **まとめ**
- RAGとは、LLMに追加情報を与えて、検索精度を向上させる仕組み
- **Fletを使ってPythonのみでシンプルなGUIを実装できた**
- **LlamaIndexでRAGシステムを実装できた**


今回はRAGってどんな仕組み？をサンプルアプリを通して解説してみました。
ollamaが商用利用には適しませんが、
OpenAIのようにアカウント作ることなく無料で使えるので、ローカルで生成AIアプリを動かして遊ぶには良いと思います。

興味があったらぜひ上記コード動かしてみてください。

次は商用でも使えるAzule Open AIとなどでも遊んでみたいと思います。


---

## **参考文献**
- [Flet公式ドキュメント](https://flet.dev/)
- [LlamaIndex公式ドキュメント](https://gpt-index.readthedocs.io/)
