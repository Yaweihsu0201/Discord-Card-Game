import discord
from discord.ext import commands
from discord import app_commands

from blackjack.game_pvp import PvPBlackjackGame
from blackjack.cards import hand_value


def fmt(hand):
    return " ".join(f"{r}{s}" for r, s in hand)


active_games = {}  # channel_id -> game


class PvPBlackjackView(discord.ui.View):
    def __init__(self, game: PvPBlackjackGame):
        super().__init__(timeout=None)
        self.game = game
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id not in self.game.players:
            await interaction.response.send_message(
                "❌ 你不是這場遊戲的玩家", ephemeral=True
            )
            return False

        if interaction.user.id != self.game.turn:
            await interaction.response.send_message(
                "⏳ 現在不是你的回合", ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        pid = interaction.user.id
        game = self.game

        game.hit(pid)
        value = hand_value(game.hands[pid])

        # 私密顯示自己的牌
        await interaction.response.send_message(
            f"🎴 你的牌：{fmt(game.hands[pid])}（{value}）",
            ephemeral=True
        )

        if game.stand[pid]:
            game.next_turn()
        # 沒爆牌仍然是自己回合

        await interaction.followup.edit_message(
            message_id=self.message.id,
            content=f"目前輪到 <@{game.turn}>",
            view=self
        )

        if game.all_stand():
            await self.end_game(interaction)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        pid = interaction.user.id
        game = self.game

        game.stand[pid] = True
        game.next_turn()

        await interaction.response.edit_message(
            content=f"<@{pid}> 停牌\n目前輪到 <@{game.turn}>",
            view=self
        )

        if game.all_stand():
            await self.end_game(interaction)

    async def end_game(self, interaction: discord.Interaction):
        self.game.finished = True
        result = self.game.result()

        for item in self.children:
            item.disabled = True

        await interaction.followup.edit_message(
            message_id=self.message.id,
            content=f"🏁 遊戲結束\n{result}",
            view=None
        )


class BlackjackPVPCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    """
    @app_commands.command(name="bj_duel", description="和另一名玩家對戰 21 點")
    @app_commands.describe(opponent="你的對手")
    async def bj_duel(
        self,
        interaction: discord.Interaction,
        opponent: discord.Member
    ):
        if opponent.bot or opponent.id == interaction.user.id:
            return await interaction.response.send_message(
                "❌ 無效的對手", ephemeral=True
            )

        game = PvPBlackjackGame(interaction.user.id, opponent.id)
        view = PvPBlackjackView(game)

        await interaction.response.send_message(
            content=(
                f"🎴 **21 點對戰開始**\n"
                f"<@{game.players[0]}> vs <@{game.players[1]}>\n"
                f"目前輪到 <@{game.turn}>"
            ),
            view=view
        )

        view.message = await interaction.original_response()
        """

async def setup(bot):
    await bot.add_cog(BlackjackPVPCog(bot))
