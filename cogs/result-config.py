import discord
from discord.ext import commands
from discord import app_commands
import database
import config

class ResultConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_tester(self, interaction: discord.Interaction):
        """Kiểm tra nếu user là Admin"""
        is_admin = interaction.user.guild_permissions.administrator
        return is_admin

    @app_commands.command(name="result-set", description="Cài đặt kênh tự động đăng thông báo kết quả test")
    @app_commands.describe(channel="Chọn kênh để gửi thông báo kết quả test")
    async def result_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self.check_tester(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)

        database.result_channel_id = channel.id
        await interaction.response.send_message(f"✅ Đã cài đặt kênh thông báo kết quả test là: {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ResultConfigCog(bot))