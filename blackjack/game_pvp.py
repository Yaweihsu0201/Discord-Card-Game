from .cards import new_deck, hand_value

class PvPBlackjackGame:
    def __init__(self, p1, p2):
        self.players = [p1, p2]
        self.hands = {p1: [], p2: []}
        self.stand = {p1: False, p2: False}
        self.turn = p1
        self.deck = new_deck()
        self.finished = False

        for _ in range(2):
            self.hands[p1].append(self.deck.pop())
            self.hands[p2].append(self.deck.pop())

    def hit(self, pid):
        self.hands[pid].append(self.deck.pop())
        if hand_value(self.hands[pid]) > 21:
            self.stand[pid] = True

    def next_turn(self):
        i = self.players.index(self.turn)
        self.turn = self.players[(i + 1) % 2]

    def all_stand(self):
        return all(self.stand.values())

    def result(self):
        scores = {
            pid: hand_value(hand)
            for pid, hand in self.hands.items()
            if hand_value(hand) <= 21
        }
        if not scores:
            return "🤝 雙方爆牌，平手"
        winner = max(scores, key=scores.get)
        return f"🎉 <@{winner}> 勝利！"
