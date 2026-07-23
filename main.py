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
    print(f"🚀 Bot {bot.user} đã sẵn sàng!")
    
    # --- CHỈ HIỂN THỊ DÒNG STATUS NGUYÊN BẢN ---
    await bot.change_presence(
        activity=discord.CustomActivity(name="By keitou_hazime")
    )
    # -------------------------------------------
    try:
        synced = await bot.tree.sync()
        print(f"✅ Đã đồng bộ {len(synced)} lệnh.")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ LỖI: Không tìm thấy DISCORD_TOKEN trong file .env!")
    else:
        print("🔄 Đang kết nối tới Discord...")
        bot.run(token)