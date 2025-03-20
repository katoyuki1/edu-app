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