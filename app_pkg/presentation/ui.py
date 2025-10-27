import gradio as gr
from app_pkg.presentation.handlers import fetch_and_translate, poll_now_playing

LANG_CHOICES = [
    ("日本語 (ja)", "ja"),
    ("English (en)", "en"),
    ("한국어 (ko)", "ko"),
    ("简体中文 (zh)", "zh"),
    ("Français (fr)", "fr"),
    ("Deutsch (de)", "de"),
    ("Español (es)", "es"),
    ("Italiano (it)", "it"),
    ("Português (pt)", "pt"),
    ("Bahasa Indonesia (id)", "id"),
    ("Tiếng Việt (vi)", "vi"),
    ("Polski (pl)", "pl"),
    ("Suomi (fi)", "fi"),
    ("Русский (ru)", "ru"),
    ("Українська (uk)", "uk"),
]

def build_ui():
    with gr.Blocks(css="""
    .mono { white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;}
    .tight textarea { line-height: 1.35; }
    """) as demo:
        gr.Markdown("## 🎧 Spotify Lyrics Translator (Personal Use)\nNo built-in player. Please start playback on Spotify before using this app.")

        with gr.Row():
            gr.HTML('<a class="gr-button gr-button-lg" href="/login">Connect with Spotify</a>')
            gr.HTML('<a class="gr-button" href="/logout">Logout</a>')
            lang = gr.Dropdown(LANG_CHOICES, value="ja", label="Target language")

        with gr.Row():
            with gr.Column():
                title = gr.Textbox(label="Title", interactive=False)
                artists = gr.Textbox(label="Artists", interactive=False)
                original = gr.Textbox(label="Lyrics (original)", lines=16, elem_classes=["mono", "tight"], interactive=False)
            with gr.Column():
                translated = gr.Textbox(label="Lyrics (translated)", lines=16, elem_classes=["mono", "tight"], interactive=False)
        status = gr.Markdown("Status: idle")

        btn = gr.Button("Fetch / Translate now", variant="primary")
        btn.click(fn=fetch_and_translate, inputs=[lang], outputs=[title, artists, original, translated, status])

        # Auto refresh every 10 seconds
        timer = gr.Timer(10, active=True)
        timer.tick(fn=poll_now_playing, inputs=[lang], outputs=[title, artists, original, translated, status])

        gr.Markdown("> ⚠️ Lyrics availability depends on external APIs. Commercial use is prohibited. Translation requires an API key for OpenAI or HF Inference.")
    return demo
