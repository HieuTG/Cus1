import discord
from discord.ext import commands
from discord import app_commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Hiển thị danh sách các lệnh hướng dẫn sử dụng bot")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 BẢNG HƯỚNG DẪN SỬ DỤNG BOT KIỂM TRA TRÌNH ĐỘ",
            description="Dưới đây là danh sách toàn bộ các lệnh hiện có trên hệ thống đã được cập nhật mới nhất:",
            color=discord.Color.blue()
        )
        
        # Section 1: Dành cho Thành viên
        member_commands = (
            "• `/profile [user]` : Xem hồ sơ, thông tin Ingame, Region, Server, Tier và Cooldown.\n"
            "• `/leave` : Rời khỏi hàng chờ kiểm tra hiện tại.\n"
            "> *Lưu ý: Để tham gia hàng chờ, bạn cần tạo Hồ sơ tại bảng của lệnh `/testing_set`, sau đó bấm nút **Join Queue** tại bảng hàng chờ.*"
        )
        embed.add_field(
            name="👤 Dành Cho Thành Viên",
            value=member_commands,
            inline=False
        )

        # Section 2: Dành cho Tester & Admin
        tester_commands = (
            "**1. Quản lý hệ thống & Cài đặt:**\n"
            "• `/ticket-folder-set <category>` : Cài đặt Danh mục (Folder) chứa các kênh Ticket test.\n"
            "• `/result-set <channel>` : Cài đặt kênh tự động đăng thông báo kết quả test.\n"
            "• `/testing_set [channel]` : Gửi bảng tin nhắn nhận Role Verify Mace & Đăng ký Hồ sơ.\n\n"
            "**2. Quản lý Hàng chờ (Queue):**\n"
            "• `/open-queue` : Mở hàng chờ, xóa toàn bộ tin nhắn trong kênh và gửi bảng Queue (tự động cập nhật).\n"
            "• `/close-queue` : Đóng hàng chờ, xóa tin nhắn trong kênh và gửi thông báo Đóng.\n\n"
            "**3. Quản lý Kiểm tra (Test):**\n"
            "• `/test-player` : Rút người đứng đầu hàng chờ ra test và tạo kênh Ticket riêng.\n"
            "• `/result <user> <new_tier>` : Trả kết quả, tự động cập nhật Role Tier, lưu Database và đóng Ticket.\n"
            "• `/skip-player <reason>` : Skip trực tiếp người đầu hàng chờ (kèm lý do).\n"
            "• `/skip-cooldown <user>` : Xóa thời gian chờ 7 ngày để người chơi có thể test lại ngay lập tức."
        )
        embed.add_field(
            name="🛠️ Dành Cho Tester & Admin",
            value=tester_commands,
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name} | Bot tạo bởi keitou_hazime", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))