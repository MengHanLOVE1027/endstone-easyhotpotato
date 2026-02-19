<div align="center">

![EndStone-EasyHotPotato](https://socialify.git.ci/MengHanLOVE1027/endstone-easyhotpotato/image?custom_language=Python&description=1&font=Inter&forks=1&issues=1&language=1&logo=https://zh.minecraft.wiki/images/Potato_JE3_BE2.png&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)
<h3>EndStone-EasyHotPotato</h3>

<p>
  <b>A Hot Potato Game Plugin Based on EndStone</b>

Powered by EndStone.<br>
</p>
</div>
<div align="center">

[![README](https://img.shields.io/badge/README-中文|Chinese-blue)](README.md) [![README_EN](https://img.shields.io/badge/README-英文|English-blue)](README_EN.md)

[![Github Version](https://img.shields.io/github/v/release/MengHanLOVE1027/endstone-easyhotpotato)](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/releases) [![GitHub License](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0) [![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/) [![Platform](https://img.shields.io/badge/Platform-EndStone-9cf.svg)](https://endstone.io) [![Downloads](https://img.shields.io/github/downloads/MengHanLOVE1027/endstone-easyhotpotato/total.svg)](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/releases)

</div>

---

## 📖 Introduction

EasyHotPotato is a hot potato game plugin designed specifically for EndStone servers, providing an exciting and fun multiplayer competitive gaming experience. Players need to pass the "hot potato" to other players within a limited time to avoid it exploding in their hands. The plugin supports automatic game flow management, player statistics tracking, leaderboard system, particle effects, sound feedback, and BossBar countdown, providing a complete gaming experience for server players.

---

## ✨ Core Features

| Feature              | Description                              |
| ----------------- | --------------------------------- |
| 🎮**Automatic Game Flow** | Complete game lifecycle management, automatically handling join, wait, start, end, etc. |
| 📊**Statistics System** | Records player wins, total games, and win rate |
| 🏆**Leaderboard**   | Player leaderboard automatically sorted by wins and win rate |
| 📜**Game History**     | Records detailed information for each game, including participating players, game duration, winner, etc. |
| 🎨**Particle Effects**     | Flame particle effects for potato holder and explosion effect on elimination |
| 🔊**Sound Feedback**     | Sound effects for game events like passing potato, potato explosion |
| 📊**BossBar Display**  | Real-time display of game status, countdown, and potato holder info |
| 🌈**Rainbow BossBar**   | Beautiful rainbow cycling effect on BossBar |
| 🗺️**Area Management**     | Flexible waiting area and arena area settings |
| ⚙️**Configurable Parameters**   | Supports customizing game duration, minimum players, activity radius, etc. |
| 🎯**Position Detection**     | Automatically detects if players leave the arena area |
| 🌍**Multi-language Interface**   | Supports Chinese, English, and other languages |
| 📝**Complete Logging System** | Colorful log output, split by date |

---

## 🗂️ Directory Structure

```
Server Root/
├── logs/
│   └── EasyHotPotato/                    # Log directory
│       └── easyhotpotato_YYYYMMDD.log    # Main log file
├── plugins/
│   ├── endstone_easyhotpotato-x.x.x-py3-none-any.whl  # Main plugin file
│   └── EasyHotPotato/                    # Plugin resource directory
│       ├── config/
│       │   └── config.json               # Configuration file
│       └── data/                         # Data directory
│           ├── player_stats.json         # Player statistics data
│           └── game_history.json         # Game history data
```

---

## 🚀 Quick Start

### Installation Steps

1. **Download Plugin**
   - Download the latest version from [Release page](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/releases)
   - Or get it from [MineBBS](https://www.minebbs.com/resources/easyhotpotato-ehp-endstone.15329/)

2. **Install Plugin**
   ```bash
   # Copy the main plugin file to the server plugins directory
   cp endstone_easyhotpotato-x.x.x-py3-none-any.whl plugins/
   ```

3. **Start Server**
   - Restart the server or use `/reload` command
   - The plugin will automatically generate default configuration files and data directories

---

## ⚙️ Configuration Guide

Configuration file location: `plugins/EasyHotPotato/config/config.json`

### 📋 Main Configuration Items

```json
{
  // 📍 Waiting center coordinates
  "waitPos": {
    "x": 0,
    "y": 0,
    "z": 0,
    "dimid": 0
  },

  // 📍 Arena center coordinates
  "gamePos": {
    "x": 100,
    "y": 64,
    "z": 100,
    "dimid": 0
  },

  // 📏 Activity radius
  "areaSize": {
    "x": 10,
    "z": 10
  },

  // ⏰ Game parameters
  "waitTime": 120,    // Preparation wait time after full players (seconds)
  "preTime": 10,      // Warm-up countdown before official start (seconds)
  "gameTime": 180,    // Game duration (seconds)

  // 👥 Player count settings
  "minPlayers": 2,    // Minimum players to trigger automatic game start
  "maxPlayers": 0     // Maximum participants, 0 means no limit
}
```

---

## 🎮 Command Manual

### Player Commands

| Command             | Permission | Description               |
| ---------------- | ---- | ------------------ |
| `/easyhotpotato` | All players | Open game main menu |
| `/easyhotpotato status` | All players | View game status |
| `/easyhotpotato stats [player]` | All players | View statistics, can specify player name |
| `/easyhotpotato help` | All players | View help |

### Admin Commands

| Command             | Permission | Description               |
| ---------------- | ---- | ------------------ |
| `/easyhotpotato` | OP | Open game main menu (includes admin options) |

---

## 🎯 Game Rules

1. **Join Game**: Enter the battlefield through the main menu and wait for other players to join
2. **Game Start**: After reaching the minimum number of players, the game officially starts after the waiting time and warm-up countdown
3. **Pass Potato**: The player holding the potato must pass it to other players by physically attacking them
4. **Potato Explosion**: Each round has a random countdown; when the timer reaches zero, the potato explodes, eliminating the current holder
5. **Area Restriction**: Leaving the arena area will result in immediate disqualification
6. **Game Victory**: The last remaining player wins
7. **Statistics Recording**: Players with the most wins will appear on the leaderboard

---

## 🔧 Advanced Features

### 🎨 Particle Effects

The plugin provides continuous flame particle effects for the potato holder and plays explosion particle effects when eliminated, enhancing the visual experience of the game.

### 🔊 Sound Feedback

- **Pass Sound**: Plays flame shooting sound when potato is passed
- **Explosion Sound**: Plays explosion sound when potato explodes
- **Countdown Sound**: Plays experience sound for the last 5 seconds with gradually rising pitch

### 📊 BossBar Display

- **Waiting Phase**: Shows current player count and minimum required players
- **Countdown Phase**: Shows game start countdown
- **In-Game**: Shows potato holder and remaining time
- **Elimination Alert**: Shows eliminated player information

---

## 🛠️ Troubleshooting

### Common Issues

<details>
<summary><b>❓ Game Won't Start</b></summary>

**Check Steps:**
1. Confirm that the number of participating players meets the minimum requirement
   ```bash
   /easyhotpotato status
   ```
2. Check the wait time and warm-up time settings in the configuration file
3. Check the log file
   ```bash
   cat logs/EasyHotPotato/easyhotpotato_*.log
   ```
</details>

<details>
<summary><b>❓ Players Can't Join Game</b></summary>

**Troubleshooting:**
1. Check if the maximum player limit has been reached
2. Confirm if the player is already in the game
3. Check the log file for detailed error messages
</details>

<details>
<summary><b>❓ Players Unexpectedly Eliminated</b></summary>

**Troubleshooting:**
1. Check if the player left the activity area
2. Confirm if the activity radius setting is reasonable
3. Check the log file for elimination reasons
</details>

### 📊 Log File Description

| Log File | Location | Purpose |
| -------- | ----------------------------------------------------- | -------------------------- |
| Main Log | `logs/EasyHotPotato/easyhotpotato_YYYYMMDD.log` | Records game operations, player behaviors, and other常规信息 |

---

## 📄 License

This project is open-sourced under the **AGPL-3.0** license.

```
Copyright (c) 2023 MengHanLOVE

This program is free software: you can redistribute and modify it freely,
but must follow the terms of the AGPL-3.0 license.
```

For the full license text, please refer to the [LICENSE](LICENSE) file.

---

## 👥 Contributing Guide

Issues and Pull Requests are welcome!

1. **Fork the project repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Create a Pull Request**

---

## 🌟 Support & Feedback

- **GitHub Issues**: [Submit Issue](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/issues)
- **MineBBS**: [Discussion Thread](https://www.minebbs.com/resources/easyhotpotato-ehp-endstone.15329/)
- **Author**: MengHanLOVE

---

<div align="center">

**⭐ If this project helps you, please give us a Star!**

[![Star History Chart](https://api.star-history.com/svg?repos=MengHanLOVE1027/endstone-easyhotpotato&type=Date)](https://star-history.com/#MengHanLOVE1027/endstone-easyhotpotato&Date)

**Made with ❤️ by MengHanLOVE**

</div>
