import discord
from discord.ext import commands
from discord import app_commands
import database

class QueuePaginationView(discord.ui.View):
    def __init__(self, current_page=0):
        super().__init__(timeout=60)
        self.current_page = current_page
        self.items_per_page = 20

    def generate_embed(self):
        total_pages = max(1, (len(database.waitlist) + self.items_per_page - 1) // self.items_per_page)
        embed = discord.Embed(title="📋 Hàng chờ Kiểm tra", color=discord.Color.blue())
        
        if not database.waitlist:
            embed.description = "Hiện tại không có ai trong hàng chờ."
            return embed

        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_items = database.waitlist[start_idx:end_idx]

        description_lines = [f"**{i}.** <@{user_id}>" for i, user_id in enumerate(current_items, start=start_idx + 1)]
        embed.description = "\n".join(description_lines)
        embed.set_footer(text=f"Trang {self.current_page + 1}/{total_pages} | Tổng: {len(database.waitlist)} người | Bot tạo bởi keitou_hazime")
        return embed

    @discord.ui.button(label="⬅️ Trước", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Sau ➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_pages = (len(database.waitlist) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.generate_embed(), view=self)
        else:
            await interaction.response.defer()

class QueueCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="queue", description="Xem danh sách những người đang trong hàng chờ")
    async def show_queue(self, interaction: discord.Interaction):
        view = QueuePaginationView()
        embed = view.generate_embed()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(QueueCog(bot))