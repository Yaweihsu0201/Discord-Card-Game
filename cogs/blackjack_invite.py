import discord
from discord.ext import commands
from discord import app_commands
from utils.database import DatabaseManager  # Importing your class
from blackjack.game_pvp import PvPBlackjackGame
from cogs.blackjack_pvp import PvPBlackjackView  # 重用遊戲 View
from blackjack.invite_model import CardBet, BlackjackInviteState

db = DatabaseManager("game.db")

class BlackjackInviteView(discord.ui.View):
    def __init__(self, invite: BlackjackInviteState):
        super().__init__(timeout=60)
        self.inviter = invite.inviter
        self.invitee = invite.invitee
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.invitee.id:
            await interaction.response.send_message(
                "❌ 只有被邀請者可以回應邀請",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        game = PvPBlackjackGame(self.inviter.id, self.invitee.id)
        view = PvPBlackjackView(game)

        await interaction.response.edit_message(
            content=(
                f"🎴 **21 點對戰開始！**\n"
                f"<@{self.inviter.id}> vs <@{self.invitee.id}>\n"
                f"目前輪到 <@{game.turn}>"
            ),
            view=view
        )

        view.message = await interaction.original_response()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="❌ 邀請已被拒絕",
            view=None
        )

    async def on_timeout(self):
        if self.message:
            await self.message.edit(
                content="⏱️ 邀請已逾時",
                view=None
            )

class BlackjackInviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="bj_invite",
        description="邀請一名玩家進行 21 點對戰"
    )
    @app_commands.describe(opponent="你要邀請的玩家",card_name="你要賭的卡牌名稱")
    async def bj_invite(
        self,
        interaction: discord.Interaction,
        opponent: discord.Member,
        card_name: str
    ):  
        card = db.get_card_by_name(interaction.user.id, card_name)
        if not card:
            return await interaction.response.send_message(
                "❌ 你沒有這張卡牌",
                ephemeral=True
        )
        if opponent.bot or opponent.id == interaction.user.id:
            return await interaction.response.send_message(
                "❌ 無效的邀請對象",
                ephemeral=True
            )
        inviter_bet = CardBet(
            owner=interaction.user,
            card_name=card['name'],
            card_rank=card['rank']
        )
        
        invite = BlackjackInviteState(
            inviter=interaction.user,
            invitee=opponent,
            inviter_bet=inviter_bet
        )
       
        view = BlackjackInviteView(invite)

        await interaction.response.send_message(
        content=(
            f"🎴 <@{interaction.user.id}> 邀請 <@{opponent.id}> 進行 21 點對戰\n"
            f"賭注：**{card.rank} 級卡牌 – {card.name}**\n\n"
            f"<@{opponent.id}> 必須賭上一張 **{card.rank} 級卡牌** 才能接受"
        ),
        view=view
    )

        view.message = await interaction.original_response()

class SelectBetCardModal(discord.ui.Modal, title="選擇你的賭注卡牌"):
    card_name = discord.ui.TextInput(
        label="卡牌名稱",
        placeholder="請輸入一張同等級卡牌名稱"
    )

    def __init__(self, invite_state):
        super().__init__()
        self.invite_state = invite_state

    async def on_submit(self, interaction: discord.Interaction):
        card = db.get_card_by_name(
            interaction.user.id,
            self.card_name.value
        )

        if not card:
            return await interaction.response.send_message(
                "❌ 你沒有這張卡牌",
                ephemeral=True
            )

        if card.rank != self.invite_state.inviter_bet.card_rank:
            return await interaction.response.send_message(
                f"❌ 卡牌等級不符，必須是 {self.invite_state.inviter_bet.card_rank} 級",
                ephemeral=True
            )

        self.invite_state.invitee_bet = CardBet(
            owner_id=interaction.user.id,
            card_name=card.name,
            card_rank=card.rank
        )

        await start_blackjack_game(interaction, self.invite_state)

async def start_blackjack_game(interaction, invite_state):
    game = PvPBlackjackGame(
        invite_state.inviter_id,
        invite_state.invitee_id
    )

    game.bet = invite_state  # 掛上賭注資訊

    view = PvPBlackjackView(game)

    await interaction.response.edit_message(
        content=(
            "🎴 **21 點對戰開始！**\n"
            f"賭注：\n"
            f"- <@{invite_state.inviter_id}>：{invite_state.inviter_bet.card_name}\n"
            f"- <@{invite_state.invitee_id}>：{invite_state.invitee_bet.card_name}\n\n"
            f"目前輪到 <@{game.turn}>"
        ),
        view=view
    )

    view.message = await interaction.original_response()

def settle_bet(game: PvPBlackjackGame):
    invite = game.bet
    winner_id = game.winner_id
    loser_id = invite.inviter_id if winner_id == invite.invitee_id else invite.invitee_id

    winner_card = invite.inviter_bet if invite.inviter_id == winner_id else invite.invitee_bet
    loser_card = invite.invitee_bet if invite.inviter_id == winner_id else invite.inviter_bet

    # 從輸家移除卡牌
    db.remove_card(loser_id, loser_card.card_name)

    # 加到贏家
    db.add_card(winner_id, loser_card.card_name)


async def setup(bot):
    await bot.add_cog(BlackjackInviteCog(bot))
