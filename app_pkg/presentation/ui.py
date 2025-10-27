import gradio as gr
from app_pkg.presentation.handlers import fetch_and_translate, poll_now_playing

LANG_CHOICES = [
    ("日本語 (ja)", "ja"),
    ("英語 (en)", "en"),
    ("韓国語 (ko)", "ko"),
    ("中国語簡体字 (zh)", "zh"),
    ("フランス語 (fr)", "fr"),
    ("ドイツ語 (de)", "de"),
    ("スペイン語 (es)", "es"),
    ("イタリア語 (it)", "it"),
    ("ポルトガル語 (pt)", "pt"),
    ("インドネシア語 (id)", "id"),
    ("ベトナム語 (vi)", "vi"),
]

def build_ui():
    with gr.Blocks(css="""
    .mono { white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;}
    .tight textarea { line-height: 1.35; }
    """) as demo:
        gr.Markdown("## 🎧 Spotify 歌詞翻訳（個人利用）\nプレイヤー機能はありません。Spotify で曲を再生してからお使いください。")

        with gr.Row():
            gr.HTML('<a class="gr-button gr-button-lg" href="/login">Spotify と連携</a>')
            gr.HTML('<a class="gr-button" href="/logout">ログアウト</a>')
            lang = gr.Dropdown(LANG_CHOICES, value="ja", label="翻訳先言語")

        with gr.Row():
            with gr.Column():
                title = gr.Textbox(label="曲名", interactive=False)
                artists = gr.Textbox(label="アーティスト", interactive=False)
                original = gr.Textbox(label="歌詞（原文）", lines=16, elem_classes=["mono", "tight"], interactive=False)
            with gr.Column():
                translated = gr.Textbox(label="歌詞（翻訳）", lines=16, elem_classes=["mono", "tight"], interactive=False)
        status = gr.Markdown("状態: 未実行")

        btn = gr.Button("今すぐ取得 / 翻訳", variant="primary")
        btn.click(fn=fetch_and_translate, inputs=[lang], outputs=[title, artists, original, translated, status])

        # 10秒ごとに自動更新
        timer = gr.Timer(10, active=True)
        timer.tick(fn=poll_now_playing, inputs=[lang], outputs=[title, artists, original, translated, status])

        gr.Markdown("> ⚠️ 歌詞は外部APIの提供状況に依存します。商用利用は禁止です。翻訳には OpenAI または HF Inference のAPIキーが必要です。")
    return demo
