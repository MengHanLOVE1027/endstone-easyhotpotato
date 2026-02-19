<div align="center">

![EndStone-EasyHotPotato](https://socialify.git.ci/MengHanLOVE1027/endstone-easyhotpotato/image?custom_language=Python&description=1&font=Inter&forks=1&issues=1&language=1&logo=https://zh.minecraft.wiki/images/Potato_JE3_BE2.png&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)
<h3>EndStone-EasyHotPotato</h3>

<p>
  <b>一个基于 EndStone 的烫手山芋游戏插件</b>

Powered by EndStone.<br>
</p>
</div>
<div align="center">

[![README](https://img.shields.io/badge/README-中文|Chinese-blue)](README.md) [![README_EN](https://img.shields.io/badge/README-英文|English-blue)](README_EN.md)

[![Github Version](https://img.shields.io/github/v/release/MengHanLOVE1027/endstone-easyhotpotato)](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/releases) [![GitHub License](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0) [![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/) [![Platform](https://img.shields.io/badge/Platform-EndStone-9cf.svg)](https://endstone.io) [![Downloads](https://img.shields.io/github/downloads/MengHanLOVE1027/endstone-easyhotpotato/total.svg)](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/releases)

</div>

---

## 📖 简介

EasyHotPotato 是一个专为 EndStone 服务器设计的烫手山芋游戏插件，提供了一个刺激有趣的多人竞技游戏体验。玩家需要在限定时间内将"烫手山芋"传递给其他玩家，避免在自己手中爆炸。插件支持自动游戏流程管理、玩家战绩记录、排行榜系统、粒子特效、音效反馈和BossBar倒计时等功能，为服务器玩家提供完整的游戏体验。

---

## ✨ 核心特性

| 特性              | 描述                              |
| ----------------- | --------------------------------- |
| 🎮**自动游戏流程** | 完整的游戏生命周期管理，自动处理加入、等待、开始、结束等流程 |
| 📊**战绩记录系统** | 记录玩家胜场、总场次和胜率等数据 |
| 🏆**排行榜功能**   | 按胜场数和胜率自动排序的玩家排行榜 |
| 📜**战局记录**     | 记录每场游戏的详细信息，包括参与玩家、游戏时长、获胜者等 |
| 🎨**粒子特效**     | 山芋持有者火焰粒子效果和淘汰时爆炸效果 |
| 🔊**音效反馈**     | 传递山芋、山芋爆炸等游戏事件的音效提示 |
| 📊**BossBar显示**  | 实时显示游戏状态、倒计时和山芋持有者信息 |
| 🌈**彩虹跑马灯**   | 精美的BossBar彩虹循环效果 |
| 🗺️**区域管理**     | 灵活的等待区域和竞技区域设置 |
| ⚙️**可配置参数**   | 支持自定义游戏时长、最低人数、活动半径等参数 |
| 🎯**位置检测**     | 自动检测玩家是否离开竞技区域 |
| 🌍**多语言界面**   | 支持中文、英文等多语言显示 |
| 📝**完整日志系统** | 彩色日志输出，按日期分割存储 |

---

## 🗂️ 目录结构

```
服务器根目录/
├── logs/
│   └── EasyHotPotato/                    # 日志目录
│       └── easyhotpotato_YYYYMMDD.log    # 主日志文件
├── plugins/
│   ├── endstone_easyhotpotato-x.x.x-py3-none-any.whl  # 插件主文件
│   └── EasyHotPotato/                    # 插件资源目录
│       ├── config/
│       │   └── config.json               # 配置文件
│       └── data/                         # 数据目录
│           ├── player_stats.json         # 玩家战绩数据
│           └── game_history.json         # 战局记录数据
```

---

## 🚀 快速开始

### 安装步骤

1. **下载插件**
   - 从 [Release页面](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/releases) 下载最新版本
   - 或从 [MineBBS](https://www.minebbs.com/resources/easyhotpotato-eb-minecraft.14897/) 获取

2. **安装插件**
   ```bash
   # 将插件主文件复制到服务器 plugins 目录
   cp endstone_easyhotpotato-x.x.x-py3-none-any.whl plugins/
   ```

3. **启动服务器**
   - 重启服务器或使用 `/reload` 命令
   - 插件会自动生成默认配置文件和数据目录

---

## ⚙️ 配置详解

配置文件位于：`plugins/EasyHotPotato/config/config.json`

### 📋 主要配置项

```json
{
  // 📍 等待中心坐标
  "waitPos": {
    "x": 0,
    "y": 0,
    "z": 0,
    "dimid": 0
  },

  // 📍 竞技中心坐标
  "gamePos": {
    "x": 100,
    "y": 64,
    "z": 100,
    "dimid": 0
  },

  // 📏 活动半径
  "areaSize": {
    "x": 10,
    "z": 10
  },

  // ⏰ 游戏参数
  "waitTime": 120,    // 满人后的预备等待时间（秒）
  "preTime": 10,      // 正式开赛前的热身倒计时（秒）
  "gameTime": 180,    // 游戏时长（秒）

  // 👥 玩家数量设置
  "minPlayers": 2,    // 触发自动开赛的最低人数
  "maxPlayers": 0     // 最大参与人数，0表示无上限
}
```

---

## 🎮 命令手册

### 玩家命令

| 命令             | 权限 | 描述               |
| ---------------- | ---- | ------------------ |
| `/easyhotpotato` | 所有玩家 | 打开游戏主菜单 |
| `/easyhotpotato status` | 所有玩家 | 查看游戏状态 |
| `/easyhotpotato stats [玩家]` | 所有玩家 | 查看战绩，可指定玩家名称 |
| `/easyhotpotato help` | 所有玩家 | 查看帮助 |

### 管理员命令

| 命令             | 权限 | 描述               |
| ---------------- | ---- | ------------------ |
| `/easyhotpotato` | OP | 打开游戏主菜单（包含后台管理选项） |

---

## 🎯 游戏规则

1. **加入游戏**：通过主菜单进入战场，等待其他玩家加入
2. **游戏开始**：达到最低人数后，经过等待时间和热身倒计时后游戏正式开始
3. **传递山芋**：持有山芋的玩家必须通过物理攻击其他玩家来传递山芋
4. **山芋爆炸**：每轮都有随机的倒计时，计时器归零时山芋爆炸，淘汰当前持有者
5. **区域限制**：离开比赛区域将立即判负
6. **游戏胜利**：最后剩下的玩家获得胜利
7. **战绩记录**：胜场最多的玩家将登上排行榜

---

## 🔧 高级功能

### 🎨 粒子特效

插件为山芋持有者提供持续的火焰粒子效果，并在淘汰时播放爆炸粒子效果，增强游戏视觉体验。

### 🔊 音效反馈

- **传递音效**：山芋传递时播放火焰射击音效
- **爆炸音效**：山芋爆炸时播放爆炸音效
- **倒计时音效**：最后5秒播放经验音效，声调逐渐升高

### 📊 BossBar显示

- **等待阶段**：显示当前玩家数量和所需最低人数
- **倒计时阶段**：显示游戏开始倒计时
- **游戏进行中**：显示山芋持有者和剩余时间
- **淘汰提示**：显示被淘汰玩家信息

---

## 🛠️ 故障排除

### 常见问题

<details>
<summary><b>❓ 游戏无法开始</b></summary>

**检查步骤：**
1. 确认参与玩家数量达到最低要求
   ```bash
   /easyhotpotato status
   ```
2. 检查配置文件中的等待时间和热身时间设置
3. 查看日志文件
   ```bash
   cat logs/EasyHotPotato/easyhotpotato_*.log
   ```
</details>

<details>
<summary><b>❓ 玩家无法加入游戏</b></summary>

**排查方法：**
1. 检查是否达到最大人数限制
2. 确认玩家是否已经在游戏中
3. 查看日志文件了解详细错误信息
</details>

<details>
<summary><b>❓ 玩家被意外淘汰</b></summary>

**排查方法：**
1. 检查玩家是否离开了活动区域
2. 确认活动半径设置是否合理
3. 查看日志文件了解淘汰原因
</details>

### 📊 日志文件说明

| 日志文件 | 位置 | 用途 |
| -------- | ----------------------------------------------------- | -------------------------- |
| 主日志 | `logs/EasyHotPotato/easyhotpotato_YYYYMMDD.log` | 记录游戏操作、玩家行为等常规信息 |

---

## 📄 许可证

本项目采用 **AGPL-3.0** 许可证开源。

```
版权所有 (c) 2023 梦涵LOVE

本程序是自由软件：您可以自由地重新发布和修改它，
但必须遵循AGPL-3.0许可证的条款。
```

完整许可证文本请参阅 [LICENSE](LICENSE) 文件。

---

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

1. **Fork 项目仓库**
2. **创建功能分支**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **提交更改**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **推送分支**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **创建 Pull Request**

---

## 🌟 支持与反馈

- **GitHub Issues**: [提交问题](https://github.com/MengHanLOVE1027/endstone-easyhotpotato/issues)
- **MineBBS**: [讨论帖](https://www.minebbs.com/resources/easyhotpotato-eb-minecraft.14897/)
- **作者**: 梦涵LOVE

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

[![Star History Chart](https://api.star-history.com/svg?repos=MengHanLOVE1027/endstone-easyhotpotato&type=Date)](https://star-history.com/#MengHanLOVE1027/endstone-easyhotpotato&Date)

**Made with ❤️ by MengHanLOVE**

</div>