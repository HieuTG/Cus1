import discord
from discord.ext import commands
import os
import config

class TestingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Nạp tự động tất cả các cogs trong thư mục ./cogs
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py') and not filename.startswith('__'):
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"📦 Đã nạp Cog: {filename[:-3]}")
        
        # Đồng bộ Slash Commands với Discord
        print("🔄 Đang đồng bộ hóa lệnh Slash Commands...")
        await self.tree.sync()
        print("✅ Đã đồng bộ tất cả lệnh Slash Commands!")

bot = TestingBot()

@bot.event
async def on_ready():
    print(f'🚀 Bot {bot.user} đã sẵn sàng và đang hoạt động!')

if __name__ == "__main__":
    if config.DISCORD_TOKEN:
        bot.run(config.DISCORD_TOKEN)
    else:
        print("❌ LỖI: Chưa truyền DISCORD_TOKEN trong file .env!")