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