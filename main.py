import discord
from discord.ext import commands
import os
import json
import sys
import subprocess

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="z!", intents=intents, help_command=None)

# ===== 許可するユーザーID =====
ALLOWED_USER_IDS = [
    1262439270488997991, 1012652131003682837, 1195288310189404251, 1393933102727958579

]

# ===== コマンド制限デコレータ =====
def is_owner_user():
    async def predicate(ctx):
        return ctx.author.id in ALLOWED_USER_IDS
    return commands.check(predicate)

# ===== 起動時イベント =====
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded cog: {filename}")


    # スラッシュコマンドを同期
    await bot.tree.sync()
    print("Synced slash commands.")

# ===== Cog管理コマンド群 =====

@bot.command(name="load")
@is_owner_user()
async def load_cog(ctx, cog: str):
    try:
        await bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully loaded {cog}!")
    except Exception as e:
        await ctx.send(f"Error while loading `{cog}`: `{e}`")

@bot.command(name="reload")
@is_owner_user()
async def reload_cog(ctx, cog: str):
    try:
        await bot.reload_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully reloaded {cog}!")
    except Exception as e:
        await ctx.send(f"Error while reloading `{cog}`: `{e}`")

@bot.command(name="unload")
@is_owner_user()
async def unload_cog(ctx, cog: str):
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await ctx.send(f"Successfully unloaded {cog}!")
    except Exception as e:
        await ctx.send(f"Error while unloading `{cog}`: `{e}`")

@bot.command(name="listcogs")
@is_owner_user()
async def list_cogs(ctx):
    loaded = list(bot.extensions.keys())
    if not loaded:
        await ctx.send("No Cogs are currently loaded.")
    else:
        cog_list = "\n".join(f"- {cog}" for cog in loaded)
        await ctx.send(f"Cogs currently loading:\n```\n{cog_list}\n```")

@bot.command(name="shutdown")
@is_owner_user()
async def shutdown_bot(ctx):
    await ctx.send("Shutting down...")
    await bot.close()

@bot.command(name="restart")
@is_owner_user()
async def restart_bot(ctx):
    await ctx.send("Restarting bot...")
    await bot.close()
    # Pythonを再実行（実行ファイルパス・引数を保持）
    subprocess.Popen([sys.executable] + sys.argv)
    # 注意: subprocess の直後に return しないと二重起動になる可能性あり
    return

# ===== 権限エラー時のメッセージ =====
@load_cog.error
@reload_cog.error
@unload_cog.error
@list_cogs.error
async def cog_permission_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("⚠️You don't have permission to execute this command!")
    else:
        raise error

# ===== Bot起動 =====
with open('config.json') as f:
    config = json.load(f)
    TOKEN = config["token"]

bot.run(TOKEN)
