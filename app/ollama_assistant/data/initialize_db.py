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