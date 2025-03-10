import discord
from discord.ext import commands
from discord import app_commands
import keep_alive
import os

# Инициализация бота и намерений
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Цвет для всех embeds
EMBED_COLOR = discord.Color.from_rgb(113, 8, 211)  # #7108d3

# --- Меню выбора ---
class CityMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="🎫 Плагин майнкрафт",
                description="Заказ плагина майнкрафт"
            ),
            discord.SelectOption(
                label="🤖 Дс бот",
                description="Заказ дискорд бота"
            ),
            discord.SelectOption(
                label="🤖 Тг бот",
                description="Заказ телеграм бота"
            ),
            discord.SelectOption(
                label="⚙️ Сборка сервера",
                description="Заказ сборку сервера"
            )
        ]
        super().__init__(placeholder="Выберите, что вы хотите сделать", options=options, custom_id="city_menu_select")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "🎫 Плагин майнкрафт":
            await interaction.response.send_modal(CityApplicationModal())
        elif self.values[0] == "🤖 Дс бот":
            await interaction.response.send_modal(DiscordBotApplicationModal())
        elif self.values[0] == "🤖 Тг бот":
            await interaction.response.send_modal(TelegramBotApplicationModal())
        elif self.values[0] == "⚙️ Сборка сервера":
            await interaction.response.send_modal(ServerBuildApplicationModal())

class CityMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CityMenu())

# --- Модальные окна для заявок ---
class CityApplicationModal(discord.ui.Modal, title="Плагин майнкрафт"):
    username = discord.ui.TextInput(
        label="Название плагина",
        placeholder="Введите название плагина",
        style=discord.TextStyle.short
    )
    hours_played = discord.ui.TextInput(
        label="Что должно быть в нём (или укажите в тикете)",
        placeholder="Опишите функционал",
        style=discord.TextStyle.short
    )
    plugin_version = discord.ui.TextInput(
        label="Какая версия плагина должна быть?",
        placeholder="Укажите версию плагина.",
        style=discord.TextStyle.short
    )
    core_name = discord.ui.TextInput(
        label="Название ядра",
        placeholder="Введите название ядра (например, Spigot, Paper, Bukkit)",
        style=discord.TextStyle.short
    )
    java_version = discord.ui.TextInput(
        label="Какая версия Java у сервера?",
        placeholder="Укажите версию Java (например, Java 8, Java 11, Java 17)",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()  # Отложить ответ

            guild = interaction.guild
            applicant = interaction.user

            category = discord.utils.get(guild.categories, name="💼 • Тикеты")
            if not category:
                category = await guild.create_category("💼 • Тикеты")

            ticket_channel = await guild.create_text_channel(
                name=f"тикет-{applicant.name}",
                category=category
            )
            await ticket_channel.set_permissions(guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(applicant, view_channel=True, send_messages=True, read_message_history=True)

            embed = discord.Embed(
                title="Новый заказ!",
                color=EMBED_COLOR
            )
            embed.add_field(name="Название плагина", value=self.username.value, inline=False)
            embed.add_field(name="Описание", value=self.hours_played.value, inline=False)
            embed.add_field(name="Версия плагина", value=self.plugin_version.value, inline=False)
            embed.add_field(name="Название ядра", value=self.core_name.value, inline=False)
            embed.add_field(name="Версия Java", value=self.java_version.value, inline=False)
            embed.set_footer(text=f"Отправлено: {applicant}")

            view = ApplicationResponseView(ticket_channel)
            await ticket_channel.send(embed=embed, view=view)

            await interaction.followup.send(
                f"Ваш тикет создан: {ticket_channel.mention}. Перейдите туда, чтобы продолжить.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Ошибка при обработке модального окна: {e}")
            await interaction.followup.send("Произошла ошибка при обработке вашего запроса.", ephemeral=True)

class DiscordBotApplicationModal(discord.ui.Modal, title="Дс бот"):
    usernames = discord.ui.TextInput(
        label="Описание (можно написать в тикете)",
        placeholder="Описание бота",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()  # Отложить ответ

            guild = interaction.guild
            applicant = interaction.user

            category = discord.utils.get(guild.categories, name="💼 • Тикеты")
            if not category:
                category = await guild.create_category("💼 • Тикеты")

            test_channel = await guild.create_text_channel(
                name=f"тикет-{applicant.name}",
                category=category
            )
            await test_channel.set_permissions(guild.default_role, view_channel=False)
            await test_channel.set_permissions(applicant, view_channel=True, send_messages=True, read_message_history=True)

            embed = discord.Embed(
                title="Новая заявка!",
                color=EMBED_COLOR
            )
            embed.add_field(name="Описание", value=self.usernames.value, inline=False)
            embed.set_footer(text=f"Отправлено: {applicant}")

            view = ApplicationResponseView(test_channel)
            await test_channel.send(embed=embed, view=view)

            await interaction.followup.send(
                f"Ваш тикет создан: {test_channel.mention}. Вы можете перейти туда, чтобы продолжить.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Ошибка при обработке модального окна: {e}")
            await interaction.followup.send("Произошла ошибка при обработке вашего запроса.", ephemeral=True)

class TelegramBotApplicationModal(discord.ui.Modal, title="Тг бот"):
    usernames = discord.ui.TextInput(
        label="Описание (можно написать в тикете)",
        placeholder="Описание бота",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()  # Отложить ответ

            guild = interaction.guild
            applicant = interaction.user

            category = discord.utils.get(guild.categories, name="💼 • Тикеты")
            if not category:
                category = await guild.create_category("💼 • Тикеты")

            test_channel = await guild.create_text_channel(
                name=f"тикет-{applicant.name}",
                category=category
            )
            await test_channel.set_permissions(guild.default_role, view_channel=False)
            await test_channel.set_permissions(applicant, view_channel=True, send_messages=True, read_message_history=True)

            embed = discord.Embed(
                title="Новая заявка!",
                color=EMBED_COLOR
            )
            embed.add_field(name="Описание", value=self.usernames.value, inline=False)
            embed.set_footer(text=f"Отправлено: {applicant}")

            view = ApplicationResponseView(test_channel)
            await test_channel.send(embed=embed, view=view)

            await interaction.followup.send(
                f"Ваш тикет создан: {test_channel.mention}. Вы можете перейти туда, чтобы продолжить.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Ошибка при обработке модального окна: {e}")
            await interaction.followup.send("Произошла ошибка при обработке вашего запроса.", ephemeral=True)

class ServerBuildApplicationModal(discord.ui.Modal, title="Сборка сервера"):
    build_name = discord.ui.TextInput(
        label="Название сборки",
        placeholder="Введите название сборки",
        style=discord.TextStyle.short
    )
    build_description = discord.ui.TextInput(
        label="Что должно быть в сборке (можно в тикете)",
        placeholder="Опишите функционал",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()  # Отложить ответ

            guild = interaction.guild
            applicant = interaction.user

            category = discord.utils.get(guild.categories, name="💼 • Тикеты")
            if not category:
                category = await guild.create_category("💼 • Тикеты")

            ticket_channel = await guild.create_text_channel(
                name=f"тикет-{applicant.name}",
                category=category
            )
            await ticket_channel.set_permissions(guild.default_role, view_channel=False)
            await ticket_channel.set_permissions(applicant, view_channel=True, send_messages=True, read_message_history=True)

            embed = discord.Embed(
                title="Новый заказ!",
                color=EMBED_COLOR
            )
            embed.add_field(name="Название сборки", value=self.build_name.value, inline=False)
            embed.add_field(name="Описание", value=self.build_description.value, inline=False)
            embed.set_footer(text=f"Отправлено: {applicant}")

            view = ApplicationResponseView(ticket_channel)
            await ticket_channel.send(embed=embed, view=view)

            await interaction.followup.send(
                f"Ваш тикет создан: {ticket_channel.mention}. Перейдите туда, чтобы продолжить.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Ошибка при обработке модального окна: {e}")
            await interaction.followup.send("Произошла ошибка при обработке вашего запроса.", ephemeral=True)

# --- Взаимодействие с тикетами (/отклонить/закрыть) ---
class ApplicationResponseView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Завершить", style=discord.ButtonStyle.success, custom_id="approve_button")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (interaction.user.guild_permissions.administrator or
                any(role.name in ["👑┃Owner", "Афганец"] for role in interaction.user.roles)):
            await interaction.response.send_message("У вас нет прав для принятия заявок.", ephemeral=True)
            return

        guild = interaction.guild
        applicant = next(
            (member for member in interaction.channel.overwrites if isinstance(member, discord.Member)), None)

        if applicant:
            resident_role = discord.utils.get(guild.roles, name="⭐┃Заказчик")
            guest_role = discord.utils.get(guild.roles, name="⚡┃Гость")

            if resident_role:
                await applicant.add_roles(resident_role)
            if guest_role:
                await applicant.remove_roles(guest_role)

        await interaction.response.send_message("Заявка одобрена. Тикет закрывается.", ephemeral=True)
        await self.ticket_channel.delete()

    @discord.ui.button(label="Закрыть", style=discord.ButtonStyle.danger, custom_id="reject_button")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (interaction.user.guild_permissions.administrator or
                any(role.name in ["👑┃Owner", "Афганец"] for role in interaction.user.roles)):
            await interaction.response.send_message("У вас нет прав для отклонения заявок.", ephemeral=True)
            return

        await interaction.response.send_message("Заявка отклонена. Тикет закрывается.", ephemeral=True)
        await self.ticket_channel.delete()

class CloseTicketView(discord.ui.View):
    def __init__(self, ticket_channel):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Закрыть", style=discord.ButtonStyle.danger, custom_id="close_ticket_button")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("У вас нет прав для закрытия тикета.", ephemeral=True)
            return

        await interaction.response.send_message("Тикет закрыт.", ephemeral=True)
        await self.ticket_channel.delete()

# --- Команда для создания меню ---
@bot.command(name="создать_меню")
@commands.has_permissions(administrator=True)
async def create_menu(ctx):
    embed = discord.Embed(
        title="Сделать заказ",
        description=(
            "**Для заказа вы должны оформить заявку ниже ⬇️**\n\n"
            "*Выберите нужный вариант, чтобы подать заявку!*"
        ),
        color=EMBED_COLOR
    )
    view = CityMenuView()
    await ctx.send(embed=embed, view=view)

# --- Обработка запуска бота ---
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}!")

    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд.")
    except Exception as e:
        print(f"Ошибка при синхронизации команд: {e}")

    bot.add_view(CityMenuView())

# --- Запуск бота ---
keep_alive.keep_alive()

bot.run(os.environ.get('TOKEN'), reconnect=True)
