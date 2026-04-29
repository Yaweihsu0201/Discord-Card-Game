# 🎴 Discord Card Game Bot

A Discord bot that allows players to play card-based games directly inside a discord server.

---

## 🎮 Demo

### Gameplay Preview
![demo](docs/demo.gif)

### Screenshot
![screenshot](docs/demo_img.png)

---

## ✨ Features

- 🎲 Random card drawing
- 👥 Multiplayer interaction in Discord
- 🃏 Custom card decks
- ⚙️ Command-based gameplay
- 🔄 Game state management

---

## 📜 Commands

| Command | Description |
|--------|------------|
| `?start` | Start a new game |
| `?draw` | Draw a card |
| `?reset` | Reset the game |
| `?size` | Check deck size |
| `?clear` | Clear messages |
| `?help` | Show help |

---

## 🛠 Tech Stack

- Node.js
- Discord.js
- JavaScript

---

## ⚙️ Installation

```bash
npm install
```

### Setup

Create a `.env` file:

```env
KEY=YOUR_DISCORD_BOT_TOKEN
```

Prepare card decks:

```txt
decks/
├── ExtraDirty
├── HappyHour
├── LastCall
├── OnTheRocks
└── WithATwist
```

Run the bot:

```bash
npm run start
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/Yaweihsu0201/Discord-Card-Game
cd Discord-Card-Game
npm install
npm run start
```

---

## 📁 Project Structure

```txt
.
├── decks/
├── docs/
├── index.js
├── Game.js
├── Decks.js
└── Admin.js
```

---

## 🎯 Future Improvements

- Web UI interface
- More game modes
- Better card system
- Ranking system

---

## 👨‍💻 Author

Created by Yawei Hsu
