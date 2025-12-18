import discord

class CardBet:
    def __init__(self, owner: discord.member, card_name: str, card_rank: str):
        self.owner = owner
        self.card_name = card_name
        self.card_rank = card_rank


class BlackjackInviteState:
    def __init__(self, inviter: discord.member, invitee: discord.member, inviter_bet: CardBet):
        self.inviter = inviter
        self.invitee = invitee
        self.inviter_bet = inviter_bet
        self.invitee_bet: CardBet | None = None
