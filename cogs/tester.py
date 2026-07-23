import discord
from discord.ext import commands
from discord import app_commands
import database
import config
import time
import asyncio

# 1. BẢNG FORM ĐIỀN LÝ DO SKIP TRONG TICKET
class SkipModal(discord.ui.Modal, title="Lý do Skip"):
    reason = discord.ui.TextInput(
        label="Lý do",
        style=discord.TextStyle.paragraph,
        placeholder="Nhập lý do bạn skip người này...",
        required=True
    )

    def __init__(self, tested_member: discord.Member):
        super().__init__()
        self.tested_member = tested_member

    async def on_submit(self, interaction: discord.Interaction):
        # Xóa khỏi danh sách đang test
        if self.tested_member.id in database.active_tests:
            database.active_tests.remove(self.tested_member.id)

        dm_message = f"🛑 Người kiểm tra **{interaction.user.display_name}** đã skip Phần test của bạn với lí do: {self.reason.value}"
        
        try:
            await self.tested_member.send(dm_message)
        except discord.Forbidden:
            pass

        await interaction.response.send_message("✅ Đã gửi lý do skip cho người chơi. Ticket sẽ tự động đóng sau 2 giây...", ephemeral=True)
        
        await asyncio.sleep(2)
        try:
            await interaction.channel.delete()
        except discord.NotFound:
            pass

# 2. GIAO DIỆN NÚT BẤM TRONG TICKET
class TicketControlView(discord.ui.View):
    def __init__(self, tested_member: discord.Member):
        super().__init__(timeout=None)
        self.tested_member = tested_member

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.danger, custom_id="btn_skip_ticket")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_admin = interaction.user.guild_permissions.administrator
        has_tester_role = any(role.id == config.TESTER_ROLE_ID for role in interaction.user.roles)
        
        if not (is_admin or has_tester_role):
            return await interaction.response.send_message("❌ Chỉ Admin hoặc Verify Tester mới có quyền bấm nút này.", ephemeral=True)
        
        await interaction.response.send_modal(SkipModal(self.tested_member))

# 3. CLASS CHÍNH
class TesterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_tester(self, interaction: discord.Interaction):
        is_admin = interaction.user.guild_permissions.administrator
        has_tester_role = any(role.id == config.TESTER_ROLE_ID for role in interaction.user.roles)
        return is_admin or has_tester_role

    # --- LỆNH 1: /test-player ---
    @app_commands.command(name="test-player", description="Tạo ticket để test người đứng đầu trong hàng chờ")
    async def test_player(self, interaction: discord.Interaction):
        if not self.check_tester(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)

        if not database.waitlist:
            return await interaction.response.send_message("⚠️ Hàng chờ hiện đang trống!", ephemeral=True)

        tested_user_id = database.waitlist.pop(0)
        
        # Thêm người chơi vào danh sách ĐANG ĐƯỢC TEST
        if tested_user_id not in database.active_tests:
            database.active_tests.append(tested_user_id)

        database.save()

        tested_member = interaction.guild.get_member(tested_user_id)
        
        if not tested_member:
            if tested_user_id in database.active_tests:
                database.active_tests.remove(tested_user_id)
            return await interaction.response.send_message("❌ Không tìm thấy người chơi này trong server. Họ có thể đã rời đi.", ephemeral=True)

        profile = database.user_profiles.get(tested_user_id, {})
        old_tier = profile.get("tier", "Chưa xếp hạng")
        last_test = profile.get("last_test_time", None)

        last_test_str = f"<t:{int(last_test)}:F>" if last_test else "Đây là lần test đầu tiên"

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            tested_member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Lấy Category ticket nếu có
        category = None
        if database.ticket_category_id:
            category = interaction.guild.get_channel(database.ticket_category_id)

        channel_name = f"ticket-mace-{tested_member.name}"
        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name, 
            overwrites=overwrites,
            category=category
        )

        await interaction.response.send_message(f"✅ Đã tạo ticket {ticket_channel.mention} cho {tested_member.mention}.", ephemeral=True)

        embed = discord.Embed(
            title=f"📋 Hồ Sơ Kiểm Tra Của {tested_member.display_name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Tên Ingame", value=profile.get("ingame", "Chưa cập nhật"), inline=True)
        embed.add_field(name="Khu Vực", value=profile.get("region", "Chưa cập nhật"), inline=True)
        embed.add_field(name="Server", value=profile.get("server", "Chưa cập nhật"), inline=True)
        
        embed.add_field(
            name="Lịch Sử Kiểm Tra", 
            value=f"• **Lần test trước:** {last_test_str}\n• **Tier cũ:** {old_tier}", 
            inline=False
        )

        await ticket_channel.send(
            content=f"🔔 {tested_member.mention} | Tester {interaction.user.mention} sẽ phụ trách bài test của bạn.",
            embed=embed,
            view=TicketControlView(tested_member)
        )

    # --- LỆNH 2: /result ---
    @app_commands.command(name="result", description="Cập nhật kết quả test cho người chơi và đóng ticket")
    @app_commands.describe(user="Người chơi vừa được test", new_tier="Chọn Tier mới được cấp")
    @app_commands.choices(new_tier=[
        app_commands.Choice(name="HT1 (High Tier 1)", value="HT1"),
        app_commands.Choice(name="LT1 (Low Tier 1)", value="LT1"),
        app_commands.Choice(name="HT2 (High Tier 2)", value="HT2"),
        app_commands.Choice(name="LT2 (Low Tier 2)", value="LT2"),
        app_commands.Choice(name="HT3 (High Tier 3)", value="HT3"),
        app_commands.Choice(name="LT3 (Low Tier 3)", value="LT3"),
        app_commands.Choice(name="HT4 (High Tier 4)", value="HT4"),
        app_commands.Choice(name="LT4 (Low Tier 4)", value="LT4"),
        app_commands.Choice(name="HT5 (High Tier 5)", value="HT5"),
        app_commands.Choice(name="LT5 (Low Tier 5)", value="LT5"),
    ])
    async def result(self, interaction: discord.Interaction, user: discord.Member, new_tier: app_commands.Choice[str]):
        if not self.check_tester(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)

        tier_value = new_tier.value

        if user.id not in database.user_profiles:
            database.user_profiles[user.id] = {}
            
        profile = database.user_profiles[user.id]
        
        # Lấy thông tin Ingame và Region
        ingame_name = profile.get("ingame", "Chưa cập nhật")
        region = profile.get("region", "Chưa cập nhật")
        old_tier = profile.get("tier", "Chưa xếp hạng")
        
        # Cập nhật thông tin profile mới
        profile["tier"] = tier_value
        profile["last_test_time"] = time.time()
        database.user_profiles[user.id] = profile

        # Xóa khỏi danh sách ĐANG ĐƯỢC TEST
        if user.id in database.active_tests:
            database.active_tests.remove(user.id)
            
        database.save()  # Lưu dữ liệu sau khi sửa đổi


        guild = interaction.guild
        
        # 1. Xóa Role Tier cũ (nếu có)
        old_tier_role_id = config.TIER_ROLES.get(old_tier)
        if old_tier_role_id:
            old_role = guild.get_role(old_tier_role_id)
            if old_role and old_role in user.roles:
                try:
                    await user.remove_roles(old_role)
                except discord.Forbidden:
                    print(f"⚠️ Thiếu quyền xóa role {old_role.name}")

        # 2. Cấp Role Tier mới
        new_tier_role_id = config.TIER_ROLES.get(tier_value)
        if new_tier_role_id:
            new_role = guild.get_role(new_tier_role_id)
            if new_role and new_role not in user.roles:
                try:
                    await user.add_roles(new_role)
                except discord.Forbidden:
                    print(f"⚠️ Thiếu quyền cấp role {new_role.name}")


        # 1. Tạo Embed Kết Quả (ĐÃ THÊM INGAME & REGION)
        result_embed = discord.Embed(
            title="🎉 KẾT QUẢ KIỂM TRA (TEST RESULT)",
            color=discord.Color.gold()
        )
        result_embed.add_field(name="👤 Người được test", value=user.mention, inline=True)
        result_embed.add_field(name="🧑‍🏫 Người test", value=interaction.user.mention, inline=True)
        result_embed.add_field(name="\u200b", value="\u200b", inline=True) # Khoảng trống để căn chỉnh 3 cột đẹp hơn
        
        # Thêm 2 field mới cho Ingame và Region
        result_embed.add_field(name="🎮 Tên Ingame", value=ingame_name, inline=True)
        result_embed.add_field(name="🌍 Khu vực", value=region, inline=True)
        result_embed.add_field(name="\u200b", value="\u200b", inline=True)
        
        # Hiển thị Tier cũ và Tier mới
        result_embed.add_field(name="📉 Tier cũ", value=old_tier, inline=True)
        result_embed.add_field(name="📈 Tier mới", value=f"**{tier_value}**", inline=True)
        
        result_embed.set_thumbnail(url=user.display_avatar.url)
        result_embed.set_footer(text=f"Cảm ơn bạn đã tham gia test tại {interaction.guild.name}! - Bot tạo bởi keitou_hazime")

        # 2. Gửi DM riêng cho người chơi
        try:
            await user.send(embed=result_embed)
        except discord.Forbidden:
            pass

        # 3. Gửi bảng kết quả vào Kênh Kết Quả (nếu đã cài /result-set)
        if database.result_channel_id:
            res_channel = interaction.guild.get_channel(database.result_channel_id)
            if res_channel:
                try:
                    await res_channel.send(embed=result_embed)
                except discord.Forbidden:
                    pass

        await interaction.response.send_message(f"✅ Đã cập nhật tier **{tier_value}** cho {user.mention} và ticket sẽ đóng sau 5 giây.")
        
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except discord.NotFound:
            pass

    # --- LỆNH 3: /skip-player ---
    @app_commands.command(name="skip-player", description="Skip trực tiếp người đứng đầu trong hàng chờ")
    @app_commands.describe(reason="Lý do skip người này")
    async def skip_player(self, interaction: discord.Interaction, reason: str):
        if not self.check_tester(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)

        if not database.waitlist:
            return await interaction.response.send_message("⚠️ Hàng chờ hiện đang trống!", ephemeral=True)

        tested_user_id = database.waitlist.pop(0)
        
        if tested_user_id in database.active_tests:
            database.active_tests.remove(tested_user_id)

        database.save()

        tested_member = interaction.guild.get_member(tested_user_id)
        
        if tested_member:
            try:
                await tested_member.send(f"🛑 Người kiểm tra **{interaction.user.display_name}** đã skip Phần test của bạn với lí do: {reason}")
            except discord.Forbidden:
                pass
        
        await interaction.response.send_message(f"✅ Đã skip <@{tested_user_id}> với lý do: {reason}", ephemeral=True)

    # --- LỆNH 4: /skip-cooldown ---
    @app_commands.command(name="skip-cooldown", description="Bỏ qua thời gian chờ (cooldown 7 ngày) cho người chơi")
    @app_commands.describe(user="Người chơi bạn muốn xóa cooldown")
    async def skip_cooldown(self, interaction: discord.Interaction, user: discord.Member):
        if not self.check_tester(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True)

        profile = database.user_profiles.get(user.id, {})
        last_test = profile.get("last_test_time", 0)

        cooldown_seconds = 7 * 24 * 60 * 60
        if time.time() - last_test >= cooldown_seconds or last_test == 0:
            return await interaction.response.send_message(f"ℹ️ {user.mention} hiện tại **không có cooldown**.", ephemeral=True)

        database.user_profiles[user.id]["last_test_time"] = 0
        database.save()
        await interaction.response.send_message(f"✅ Đã xóa cooldown 7 ngày cho {user.mention}!")

async def setup(bot):
    await bot.add_cog(TesterCog(bot))