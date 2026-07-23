import discord
from discord.ext import commands
from discord import app_commands
import database
import config

class ProfileModal(discord.ui.Modal, title='Cập nhật thông tin hồ sơ'):
    ingame_name = discord.ui.TextInput(label='Tên Ingame', placeholder='Nhập tên nhân vật...', required=True)
    region = discord.ui.TextInput(label='Region (Khu vực)', placeholder='Ví dụ: VN, SEA, NA...', required=True)
    server = discord.ui.TextInput(label='Server mong muốn', placeholder='Nhập server bạn muốn test...', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        database.user_profiles[interaction.user.id] = {
            "ingame": self.ingame_name.value,
            "region": self.region.value,
            "server": self.server.value
        }
        await interaction.response.send_message("✅ Đã cập nhật hồ sơ thành công! Bạn hiện có thể tham gia hàng chờ.", ephemeral=True)

class TestingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify Account", style=discord.ButtonStyle.primary, custom_id="btn_profile")
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ProfileModal())

    @discord.ui.button(label="Enter Waitlist", style=discord.ButtonStyle.secondary, custom_id="btn_enter_waitlist")
    async def enter_waitlist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Nút này HIỆN TẠI CHỈ CẤP ROLE VERIFY MACE
        guild = interaction.guild
        role = guild.get_role(config.VERIFY_MACE_ROLE_ID) or discord.utils.get(guild.roles, name="Verify Mace") or discord.utils.get(guild.roles, name="verify mace")
        
        if not role:
            return await interaction.response.send_message("⚠️ Không tìm thấy Role 'Verify Mace' trong server.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.response.send_message(f"ℹ️ Bạn đã sở hữu role **{role.name}** từ trước!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ Bạn đã được cấp role **{role.name}** thành công!", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("⚠️ Bot không có quyền cấp Role. Hãy kiểm tra vị trí Role của Bot trong Cài đặt Server.", ephemeral=True)

class TestingSetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TestingView()) 

    @app_commands.command(name="testing_set", description="Thiết lập tin nhắn nhận Role Verify Mace & Hồ sơ")
    async def testing_set(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="📝 Đăng Ký Hồ Sơ",
            description=(
                "Khi đăng ký, bạn sẽ được đưa vào kênh hàng chờ.\n"
                "Tại đây, bạn sẽ được tag khi có Tester thuộc khu vực của bạn sẵn sàng.\n\n"
                "• **Region (Khu vực)** là khu vực của máy chủ bạn muốn kiểm tra.\n"
                "• **Username (Tên Ingame)** là tên tài khoản bạn sẽ sử dụng để kiểm tra.\n\n"
                "🛑 **Việc cung cấp thông tin không xác thực sẽ dẫn đến việc bị từ chối bài test.**"
            ),
            color=discord.Color.dark_theme()
        )

        await target_channel.send(embed=embed, view=TestingView())
        await interaction.response.send_message(f"✅ Đã gửi bảng đăng ký vào {target_channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TestingSetCog(bot))