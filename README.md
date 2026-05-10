# 🌌 超级穿越模拟器 / Super Cross-World Simulator

> AI驱动的沉浸式多人在线角色扮演世界 | AI-Powered Immersive Multiplayer Role-Playing World

[English](#english) | [中文](#中文)

---

## English

### Overview

**Super Cross-World Simulator** is an AI-native interactive fiction platform where you step into procedurally generated worlds. Powered by DeepSeek's large language models, every world is unique — from cyberpunk cultivation realms to interstellar wasteland civilizations. You create a character, choose your talents, and dive into a living narrative where every NPC has their own personality, memories, and goals.

### Key Features

#### 🎲 Random Talent System (156 Talents)
Before entering a world, 7 random talents are drawn from a pool of 156. You pick 3 to carry into your adventure. Talents span 20 categories:
- **Combat**: Sword Heart Enlightenment, Martial Saint, Berserker
- **Cultivation**: Heavenly Spiritual Root, Immortal Body, Chaos Root
- **Bloodline**: Dragon Blood, Elven Heritage, Werewolf Blood
- **Divine**: Creator's Power, God Slayer's Mark, Elder God Patron
- **Curse**: Hated by All, Mute, Ugly, Disaster Magnet
- **Artifact**: Mysterious Ring, Phoenix Feather, Space Storage
- **Social**: Silver Tongue, Born Leader, Bard's Voice
- **Destiny**: Emperor Star, War Star, Wisdom Star
- And many more...

Each talent affects stats, unlocks abilities, and influences plot development.

#### 🌍 AI-Generated Worlds
- **100+ world themes** randomly selected (cyberpunk cultivation, post-apocalyptic wasteland, Lovecraftian fairy tales, steampunk wuxia...)
- Worlds include complete rules, history, scenes with immersive descriptions
- Multiple NPCs with distinct personalities, backgrounds, goals, and speaking styles
- Characters remember interactions and build relationships over time

#### 🎭 Dual Experience Modes
- **Normal Mode**: Transparent information — see world rules, NPC personalities, full stats
- **Immersive Mode**: Sensory-only descriptions — visual, auditory, tactile, olfactory details. No spoilers.

#### ⚔️ RPG Systems
- **8 Core Stats**: HP, Strength, Intelligence, Charisma, Agility, Luck, Sanity + custom stats
- **Inventory & Skills**: Collect items, learn abilities, carry artifacts
- **Status Effects**: Restrained, poisoned, dead, revived — affects gameplay
- **Death & Revival**: Multiple revival types based on world theme (game respawn, magic revival, plot rescue, permanent death)

#### 🎬 Director AI System
- **Scene Director**: Analyzes player input, decides which NPCs should respond
- **Action Reviewer**: Validates actions against world rules, optimizes dialogue, generates narrator descriptions
- **Plot Engine**: Drives story forward with periodic checks and random twists (25% chance per round)

#### 🎤 Four Narrator Types
| Type | Icon | Color | Purpose |
|------|------|-------|---------|
| Action | 🎭 | Purple | Scene descriptions, NPC reactions, atmosphere changes |
| Plot | ⚡ | Green | Death, revival, arrests, rescues, major events |
| Hint | 💡 | Yellow | Plain-language suggestions for what to do next |
| Talent | ✨ | Blue | Descriptions when your talents activate during gameplay |

#### 📖 Novel Generation
- AI automatically compiles your adventure into web-novel style chapters
- Chapters triggered by scene changes, NPC joins/leaves, plot twists, or round milestones
- Professional formatting with chapter tabs and reading panel

#### 🎲 Random Plot Twists
- 25% chance per dialogue round of triggering an unexpected event
- NPCs can suddenly betray, new characters appear, environments change
- Keeps the narrative unpredictable and exciting

#### 💾 Persistent Worlds
- All worlds stored in SQLite database
- Continue previous adventures with full message history
- Worlds can be permanently deleted when finished

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask + Flask-SocketIO |
| Frontend | Vanilla HTML/CSS/JS + Socket.IO |
| Database | SQLite (SQLAlchemy ORM) |
| AI Model | DeepSeek API (v4-pro / v4-flash) |
| Real-time | WebSocket (bidirectional communication) |

### Quick Start

```bash
# 1. Clone & enter directory
cd super-cross-world-simulator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python run.py

# 4. Open browser
# http://localhost:5000
```
Or download the EXE version directly.
### Architecture

```
app/
├── main.py              # Flask routes & Socket.IO events
├── agent.py             # Scene Director & Character Agent
├── action_reviewer.py   # Action validation & narrator generation
├── world_engine.py      # World/character generation
├── plot_engine.py       # Story advancement & random twists
├── novel_engine.py      # Web-novel chapter generation
├── llm_client.py        # LLM API client
├── runtime_config.py    # Runtime configuration
├── database.py          # Database connection
└── models.py            # ORM models (World, Character, Message, etc.)

templates/
└── index.html           # Single-page application

config.py                # All configuration constants
run.py                   # Entry point
```

### Configuration

All settings in `config.py` and runtime overrides via model settings UI:
- API Key & URL
- Model selection (reasoner vs chat)
- Temperature parameters for different generation tasks
- Max tokens for each pipeline stage

---

## 中文

### 概述

**超级穿越模拟器**是一个AI原生的交互式小说平台。基于DeepSeek大语言模型，每个世界都是独特生成的——从赛博朋克修仙界到星际废土文明。你可以创建角色、选择天赋，沉浸在一个由鲜活NPC构成的叙事世界中。

### 核心功能

#### 🎲 随机天赋系统（156个天赋）
进入世界前，从156个天赋池中随机抽取7个，选择其中3个带入冒险。天赋覆盖20个类别：
- **战斗类**：剑心通明、武圣之姿、狂战士
- **修仙类**：天灵根、仙人体、混沌根骨
- **血脉类**：龙族血统、精灵血脉、狼人血统
- **神性类**：创造神之力、弑神者之印、邪神眷属
- **诅咒类**：人间人憎、哑巴、丑陋、天灾之子
- **宝物类**：神秘戒指、凤凰涅槃、虚空储物
- **社交类**：铁齿铜牙、天生领袖、吟游诗人
- **命格类**：紫微星、七杀星、天机星
- 以及更多...

每个天赋影响属性值、解锁能力，并影响情节发展。

#### 🌍 AI生成世界
- **100+世界主题**随机抽取（赛博修仙、末日废土、克苏鲁童话、蒸汽武侠...）
- 完整的世界规则、历史、场景描写
- 多个NPC各有独立的性格、背景、目标和说话风格
- 角色记住互动历史，关系随时间演变

#### 🎭 双模式体验
- **常规扮演**：信息透明——可看到世界规则、NPC性格、完整属性
- **深度体验**：纯感官描写——视觉、听觉、触觉、嗅觉细节。无剧透。

#### ⚔️ RPG系统
- **8项核心属性**：HP、力量、智力、魅力、敏捷、幸运、理智 + 扩展属性
- **物品与技能**：收集道具、学习技能、携带宝物
- **状态效果**：束缚、中毒、死亡、复活——影响游戏进程
- **死亡与复活**：根据世界观有多种复活方式（网游重生、魔法复活、剧情获救、永久死亡）

#### 🎬 导演AI系统
- **场景导演**：分析玩家输入，决定哪些NPC应该回应及回应顺序
- **行动审查者**：验证行为是否符合世界规则，优化话语表达，生成旁白
- **情节引擎**：定期检查并推动故事发展，配合随机剧情转折（每轮25%概率）

#### 🎤 四种旁白类型
| 类型 | 图标 | 颜色 | 用途 |
|------|------|------|------|
| 行为旁白 | 🎭 | 紫色 | 场景描写、NPC反应、氛围变化 |
| 剧情旁白 | ⚡ | 绿色 | 死亡、复活、被缚、营救等重大事件 |
| 提示旁白 | 💡 | 黄色 | 用白话告诉玩家接下来可以做什么 |
| 天赋旁白 | ✨ | 蓝色 | 天赋在游戏中触发时的效果描写 |

#### 📖 小说自动生成
- AI自动将冒险历程编写为网文风格的小说章节
- 场景切换、角色进出、剧情转折或回合数达标时触发新章节
- 专业的章节标签页和阅读面板

#### 🎲 随机剧情转折
- 每轮对话有25%概率触发意外事件
- NPC突然背叛、新角色闯入、环境突变
- 保证叙事不可预测、充满张力

#### 💾 持久化世界
- 所有世界存储在SQLite数据库中
- 可继续之前的冒险，保留完整对话历史
- 世界结束后可永久删除

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python + Flask + Flask-SocketIO |
| 前端 | 原生 HTML/CSS/JS + Socket.IO |
| 数据库 | SQLite（SQLAlchemy ORM） |
| AI模型 | DeepSeek API（v4-pro / v4-flash） |
| 实时通信 | WebSocket（双向通信） |

### 快速开始

```bash
# 1. 进入项目目录
cd super-cross-world-simulator

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务器
python run.py

# 4. 打开浏览器
# http://localhost:5000
```
或者直接下载exe版本
### 项目架构

```
app/
├── main.py              # Flask 路由 & Socket.IO 事件处理
├── agent.py             # 场景导演 & 角色代理
├── action_reviewer.py   # 行为审查 & 旁白生成
├── world_engine.py      # 世界/角色生成
├── plot_engine.py       # 情节推进 & 随机转折
├── novel_engine.py      # 小说章节生成
├── llm_client.py        # LLM API 客户端
├── runtime_config.py    # 运行时配置
├── database.py          # 数据库连接
└── models.py            # ORM 模型

templates/
└── index.html           # 单页应用

config.py                # 配置常量
run.py                   # 入口文件
```

### 配置说明

所有配置见 `config.py`，运行时可通过模型设置界面覆盖：
- API Key 和 URL
- 模型选择（推理模型 vs 对话模型）
- 各环节的温度参数
- 各管道的最大 token 数

ᯠ _ ̫  _ ̥ ᯄ 