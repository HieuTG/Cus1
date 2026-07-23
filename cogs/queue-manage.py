import discord
from discord.ext import commands, tasks
from discord import app_commands
import database
import config
import time

class JoinQueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary, custom_id="btn_join_queue_main")
    async def join_queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Kiểm tra hàng chờ mở hay đóng
        if not database.queue_open:
            return await interaction.response.send_message("🛑 Hàng chờ hiện đang **ĐÓNG**!", ephemeral=True)

        user_id = interaction.user.id

        # 2. Kiểm tra đã tạo hồ sơ chưa
        if user_id not in database.user_profiles:
            return await interaction.response.send_message("⚠️ Bạn cần cập nhật **Hồ sơ** trước khi tham gia hàng chờ!", ephemeral=True)

        # 3. Kiểm tra Cooldown 7 ngày
        profile = database.user_profiles[user_id]
        last_test = profile.get("last_test_time", 0)
        cooldown_seconds = 7 * 24 * 60 * 60
        current_time = time.time()

        if current_time - last_test < cooldown_seconds:
            available_time = int(last_test + cooldown_seconds)
            return await interaction.response.send_message(
                f"⏳ Bạn đang trong thời gian chờ. Có thể quay lại vào <t:{available_time}:F>.", 
                ephemeral=True
            )

        # 4. Kiểm tra xem đã ở trong queue hoặc đang test chưa
        if user_id in database.waitlist:
            return await interaction.response.send_message("ℹ️ Bạn đã ở sẵn trong hàng chờ rồi!", ephemeral=True)
        
        if user_id in database.active_tests:
            return await interaction.response.send_message("⚠️ Bạn hiện đang trong lượt test (đang mở ticket)!", ephemeral=True)

        # 5. GIỚI HẠN TỐI ĐA 20 NGƯỜI
        if len(database.waitlist) >= 20:
            return await interaction.response.send_message("🛑 Hàng chờ đã **ĐẦY** (Tối đa 20/20 người). Vui lòng đợi lượt sau!", ephemeral=True)

        # Thêm vào hàng chờ thành công
        database.waitlist.append(user_id)
        database.save()
        await interaction.response.send_message("✅ Bạn đã tham gia hàng chờ thành công!", ephemeral=True)


class QueueManageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(JoinQueueView())
        self.update_queue_loop.start()

    def cog_unload(self):
        self.update_queue_loop.cancel()

    # --- HÀM TẠO EMBED HIỂN THỊ HÀNG CHỜ ---
    def build_queue_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Tester(s) Available!",
            description="⏰ The queue updates every 1 minute.\nUse `/leave` if you wish to be removed from the waitlist or queue.",
            color=discord.Color.blue()
        )

        # 1. Tên 20 người trong hàng chờ
        if database.waitlist:
            queue_lines = [f"{i+1}. <@{uid}>" for i, uid in enumerate(database.waitlist[:20])]
            queue_text = "\n".join(queue_lines)
        else:
            queue_text = "*No players currently in queue.*"

        embed.add_field(name="Queue:", value=queue_text, inline=False)

        # 2. Active Tester: Người mở queue (dùng lệnh /open-queue)
        if database.queue_opener_id:
            tester_text = f"1. <@{database.queue_opener_id}>"
        else:
            tester_text = "*No active tester.*"

        embed.add_field(name="Active Tester:", value=tester_text, inline=False)

        # 3. Người đang được test (đang mở ticket)
        if database.active_tests:
            active_lines = [f"{i+1}. <@{uid}>" for i, uid in enumerate(database.active_tests)]
            active_text = "\n".join(active_lines)
        else:
            active_text = "*Không có ai đang trong lượt test.*"

        embed.add_field(name="Currently Being Tested:", value=active_text, inline=False)

        return embed

    # --- TASK TỰ ĐỘNG REFRESH MỖI 1 PHÚT ---
    @tasks.loop(minutes=1.0)
    async def update_queue_loop(self):
        if not database.queue_open:
            return

        ch_id = database.queue_message_info["channel_id"]
        msg_id = database.queue_message_info["message_id"]

        if ch_id and msg_id:
            try:
                channel = self.bot.get_channel(ch_id) or await self.bot.fetch_channel(ch_id)
                message = await channel.fetch_message(msg_id)
                embed = self.build_queue_embed()
                await message.edit(embed=embed, view=JoinQueueView())
            except Exception:
                pass

    @update_queue_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    # --- LỆNH /open-queue ---
    @app_commands.command(name="open-queue", description="Mở hàng chờ, xóa toàn bộ tin nhắn trong kênh và gửi bảng mới")
    async def open_queue(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        database.queue_open = True
        database.queue_opener_id = interaction.user.id  # Ghi nhận Tester mở queue

        # Xóa tất cả tin nhắn cũ trong kênh
        try:
            await interaction.channel.purge()
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot thiếu quyền xóa tin nhắn (`Manage Messages`) trong kênh này!", ephemeral=True)

        # Gửi bảng thông tin mới
        embed = self.build_queue_embed()
        msg = await interaction.channel.send(embed=embed, view=JoinQueueView())

        # Lưu lại ID để tự động edit
        database.queue_message_info["channel_id"] = interaction.channel.id
        database.queue_message_info["message_id"] = msg.id
        database.save()

        await interaction.followup.send("✅ Đã MỞ hàng chờ thành công!", ephemeral=True)

    # --- LỆNH /close-queue ---
    @app_commands.command(name="close-queue", description="Đóng hàng chờ, xóa toàn bộ tin nhắn trong kênh và gửi thông báo")
    async def close_queue(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        database.queue_open = False
        database.queue_opener_id = None
        database.queue_message_info["channel_id"] = None
        database.queue_message_info["message_id"] = None
        database.save()
        # Xóa tất cả tin nhắn trong kênh
        try:
            await interaction.channel.purge()
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot thiếu quyền xóa tin nhắn (`Manage Messages`) trong kênh này!", ephemeral=True)

        # Gửi Embed thông báo ĐÓNG
        close_embed = discord.Embed(
            title="🛑 HÀNG CHỜ ĐÃ ĐÓNG (QUEUE CLOSED)",
            description="Hàng chờ kiểm tra trình độ hiện tại đã đóng. Vui lòng quay lại sau khi hàng chờ được mở lại!",
            color=discord.Color.red()
        )
        await interaction.channel.send(embed=close_embed)

        await interaction.followup.send("✅ Đã ĐÓNG hàng chờ thành công!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QueueManageCog(bot))