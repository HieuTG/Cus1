import discord
from discord.ext import commands
from discord import app_commands
import database
import time

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Xem hồ sơ thông tin và tier kiểm tra của bạn hoặc thành viên khác")
    @app_commands.describe(user="Thành viên bạn muốn xem (để trống nếu muốn xem hồ sơ của chính mình)")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        # Nếu không truyền user thì mặc định lấy chính người bấm lệnh
        target_user = user or interaction.user
        
        # Lấy hồ sơ từ database
        profile = database.user_profiles.get(target_user.id, {})
        
        ingame = profile.get("ingame", "Chưa nhập")
        region = profile.get("region", "Chưa nhập")
        server = profile.get("server", "Chưa nhập")
        tier = profile.get("tier", "Chưa xếp hạng")
        last_test = profile.get("last_test_time", None)

        # Kiểm tra trạng thái có đang ở trong hàng chờ hay không
        in_waitlist = target_user.id in database.waitlist
        waitlist_status = "🟢 Đang ở trong hàng chờ" if in_waitlist else "⚪ Không trong hàng chờ"

        # Tính toán trạng thái Cooldown (7 ngày = 604800 giây)
        cooldown_seconds = 7 * 24 * 60 * 60
        current_time = time.time()
        
        if last_test:
            last_test_str = f"<t:{int(last_test)}:F>"
            if current_time - last_test < cooldown_seconds:
                next_test_time = int(last_test + cooldown_seconds)
                cooldown_status = f"⏳ Có thể vào hàng chờ lại: <t:{next_test_time}:R>"
            else:
                cooldown_status = "✅ Sẵn sàng vào hàng chờ"
        else:
            last_test_str = "Chưa từng tham gia test"
            cooldown_status = "✅ Sẵn sàng vào hàng chờ"

        # Tạo Embed hiển thị giao diện đẹp mắt
        embed = discord.Embed(
            title=f"📋 Profile - {target_user.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(name="🎮 Tên Ingame", value=ingame, inline=True)
        embed.add_field(name="🌍 Region", value=region, inline=True)
        embed.add_field(name="🖥️ Server", value=server, inline=True)
        
        embed.add_field(name="🏆 Tier Hiện Tại", value=f"**{tier}**", inline=True)
        embed.add_field(name="📌 Hàng Chờ", value=waitlist_status, inline=True)
        
        embed.add_field(name="🕒 Lần Test Gần Nhất", value=last_test_str, inline=False)
        embed.add_field(name="⏳ Trạng Thái Cooldown", value=cooldown_status, inline=False)
        
        embed.set_footer(text=f"bot tạo bởi keitou_hazime")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))