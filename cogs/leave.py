import discord
from discord.ext import commands
from discord import app_commands
import database

class LeaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leave", description="Rời khỏi hàng chờ kiểm tra hiện tại")
    async def leave_queue(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in database.waitlist:
            database.waitlist.remove(user_id)
            await interaction.response.send_message("✅ Bạn đã rời khỏi hàng chờ thành công.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Bạn hiện không có mặt trong hàng chờ.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LeaveCog(bot))