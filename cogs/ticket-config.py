import discord
from discord.ext import commands
from discord import app_commands
import database

class TicketConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_tester(self, interaction: discord.Interaction):
        """Kiểm tra nếu user là Admin HOẶC có Role Tester"""
        is_admin = interaction.user.guild_permissions.administrator
        return is_admin

    @app_commands.command(name="ticket-folder-set", description="Thiết lập danh mục (Category) để chứa các kênh ticket test")
    @app_commands.describe(category="Chọn Danh mục (Folder) mà bạn muốn chứa các kênh ticket")
    async def ticket_folder_set(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if not self.check_tester(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)

        database.ticket_category_id = category.id
        database.save()
        await interaction.response.send_message(f"✅ Đã thiết lập danh mục chứa Ticket là: **{category.name}**", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketConfigCog(bot))