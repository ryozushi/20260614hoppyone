# =============================================================
#  HoppyOne  ―  デジタル原っぱ大学のなかま Bot  (bot.py)
#  - みんなの「試行錯誤ログ」を残し、励ます、原っぱの相棒です。
#  - 24時間クラウド稼働(Koyeb)対応版。
#
#  v1の機能:
#    !log  [今日やったこと]  … 試行錯誤を記録（Discordに残るので消えません）
#    !mylog                  … 自分のこれまでのログを振り返る
#    !cheer                  … コーチ風の励ましをランダムに
#    !help                   … 使い方一覧
#    !ping                   … 動いているか確認（おまけ）
#
#  ※ ログは「このチャンネルのメッセージ」として残ります。
#    別の保存先を使わないので、無料クラウドでもデータが消えません。
# =============================================================

import os
import random
import threading
from datetime import timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord.ext import commands

# -------------------------------------------------------------
# 【1】 トークン（合言葉）
#   ・クラウド(Koyeb)では環境変数 DISCORD_TOKEN から自動で読み込みます。
#   ・自分のPCで試すなら "..." に直接貼ってもOK。
#   ※トークンは「Botのパスワード」。誰にも教えないこと。
# -------------------------------------------------------------
TOKEN = os.environ.get("DISCORD_TOKEN", "ここにあなたのトークンを貼り付け")

# 日本時間(JST)で日付を表示するための設定（触らなくてOK）
JST = timezone(timedelta(hours=9))


# -------------------------------------------------------------
# 【おまけ】 無料クラウドで「眠らせない」ための小さな窓口（触らない）
# -------------------------------------------------------------
class _AliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HoppyOne is alive!")

    def log_message(self, *args):
        pass


def _start_keepalive_server():
    port = int(os.environ.get("PORT", "8000"))
    HTTPServer(("0.0.0.0", port), _AliveHandler).serve_forever()


# -------------------------------------------------------------
# 【2】 基本設定（触らなくてOK）
# -------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# -------------------------------------------------------------
# 【3】 起動時に1回だけ動く処理
# -------------------------------------------------------------
@bot.event
async def on_ready():
    print("------------------------------------------")
    print(f"HoppyOne 起動！  Bot名: {bot.user}")
    print("準備OK。Discordで !help と打ってみてください。")
    print("------------------------------------------")


# -------------------------------------------------------------
# 【4】 コマンド本体
# -------------------------------------------------------------

# --- 試行錯誤ログを記録 ---  使い方: !log 今日やったこと
@bot.command(name="log")
async def log_command(ctx, *, content: str = ""):
    if not content.strip():
        await ctx.send(
            "記録したいことを書いてね📝  例: `!log Claudeでログイン画面を作った。詰まったけど動いた！`"
        )
        return
    today = ctx.message.created_at.astimezone(JST).strftime("%-m/%-d")
    await ctx.send(
        f"📝 **ログ記録したよ！**（{today}・{ctx.author.display_name}さん）\n"
        f"> {content}\n"
        f"手を動かした証拠、ちゃんと残りました。えらい！この積み重ねがURLになる🌱"
    )


# --- 自分のログを振り返る ---  使い方: !mylog
@bot.command(name="mylog")
async def mylog_command(ctx):
    # このチャンネルの履歴から、自分が打った「!log ...」を拾い集めます。
    found = []
    async for msg in ctx.channel.history(limit=400):
        if msg.author.id != ctx.author.id:
            continue
        text = msg.content.strip()
        # "!log 〜" または "！log 〜"(全角!)で始まるメッセージを対象に
        for prefix in ("!log ", "！log "):
            if text.startswith(prefix):
                body = text[len(prefix):].strip()
                date = msg.created_at.astimezone(JST).strftime("%-m/%-d")
                found.append((date, body))
                break

    if not found:
        await ctx.send(
            f"{ctx.author.display_name}さんのログはまだこのチャンネルに見つからなかったよ。\n"
            f"`!log 今日やったこと` で最初の一歩を残してみよう！🌱"
        )
        return

    # 履歴は新しい順に取れるので、古い順に並べ直す
    found.reverse()
    lines = [f"・{date}  {body}" for date, body in found[-15:]]  # 最新15件まで表示
    body_text = "\n".join(lines)
    await ctx.send(
        f"📖 **{ctx.author.display_name}さんのログ（最新{len(lines)}件 / 累計{len(found)}件）**\n"
        f"{body_text}\n\n"
        f"ここまでよく走ってきたね。完成度は問わない、続けた事実が力になる🔥"
    )


# --- 励ましガチャ ---  使い方: !cheer
@bot.command(name="cheer")
async def cheer_command(ctx):
    messages = [
        "とにかくやってみること。それがすべて。まず1行、手を動かそう🔥",
        "完成度は問わない。今日も「自分の手でURLを生む」に一歩近づいてる🌱",
        "詰まった時間は、溶けてない。ぜんぶ実装力として積み上がってるよ💪",
        "エラーは敵じゃなくて道しるべ。読んでみると、次の一手が見えてくる👀",
        "想像を具現化する喜びを、一緒に。あなたの言葉からアプリは生まれる✨",
        "失敗も楽しさの一部。つくるを遊ぼう。原っぱはそういう場所☀️",
        "迷ったら、まず動くものを1個。小さく動けば、勝手に火がつく🔥",
        "コーヒー淹れて深呼吸。焦らなくていい、海風のペースでいこう☕🌊",
        "今日の試行錯誤、`!log` に残しておこう。未来のあなたが喜ぶよ📝",
        "あなたは消費者じゃなく創造者。今この瞬間も、世界を記述してる🖊️",
        "コードが書けなくても、論理と情熱があれば前に進める。大丈夫👍",
        "クロージングDayの自分は、今日のあなたに感謝してる。いってらっしゃい🚀",
    ]
    await ctx.send(f"🎁 **今日のひと押し**\n{random.choice(messages)}")


# --- 動作確認（おまけ） ---  使い方: !ping
@bot.command(name="ping")
async def ping_command(ctx):
    await ctx.send(f"pong! 元気に動いてるよ（応答 {round(bot.latency*1000)}ms）")


# --- 使い方一覧 ---  使い方: !help
@bot.command(name="help")
async def help_command(ctx):
    text = (
        "**やあ！HoppyOne だよ🌱 原っぱのなかまBotです。**\n"
        "使えるコマンドはこちら：\n"
        "`!log [内容]` … 今日の試行錯誤を記録（例: `!log ログイン画面ができた！`）\n"
        "`!mylog`      … 自分のこれまでのログを振り返る\n"
        "`!cheer`      … 手が止まったら…コーチ風の励ましをひとつ\n"
        "`!ping`       … ちゃんと動いてるか確認\n"
        "`!help`       … この一覧\n"
        "\n完成度は問わない。まず手を動かそう。応援してるよ🔥"
    )
    await ctx.send(text)


# -------------------------------------------------------------
# 【5】 起動（触らなくてOK）
# -------------------------------------------------------------
if __name__ == "__main__":
    if TOKEN == "ここにあなたのトークンを貼り付け":
        print("⚠️ トークンが未設定です。")
        print("   クラウドなら環境変数 DISCORD_TOKEN を設定してください（手順書参照）。")
        print("   PCで試すなら bot.py の TOKEN に直接貼り付けてください。")
    else:
        threading.Thread(target=_start_keepalive_server, daemon=True).start()
        bot.run(TOKEN)
