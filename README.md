# StarCraft II Copilot / 星际争霸II助手

[English](#english) | [中文](#中文)

---

## English

### Overview
StarCraft II Copilot is a real-time desktop assistant for Co-op and Versus modes. It monitors your gameplay via screen-capture technology, providing essential macro reminders, strategic advice, and tactical analysis to enhance your gaming experience.

### Core Features

#### 1. **Operational Reminders** (运营提醒)
- **Worker Production Tracking**: Automatically monitors and reminds you to continuously produce workers (SCVs, Probes, Drones)
- **Supply Management**: Alerts when you're approaching supply cap to prevent supply blocks
- **Resource Overflow Detection**: Notifies when resources are accumulating, suggesting expansion or unit production
- **Macro Timing Reminders**: Customizable alerts for key macro timings (expansions, tech upgrades)

#### 2. **Co-op Commander Tactics & Prestige** (指挥官战术/威望)
- **Commander-Specific Strategy Tips**: Tailored tactical advice for each Co-op commander
- **Prestige Talent Recommendations**: Optimal prestige talent selection based on mission and composition
- **Power Spike Timing**: Alerts for commander power spikes and ability cooldowns
- **Synergy Analysis**: Suggestions for optimal commander pairings and unit compositions

#### 3. **Attack/Defense Upgrade Tracking** (攻防升级跟踪)
- **Upgrade Progress Monitoring**: Real-time tracking of attack and defense upgrades across all unit types
- **Upgrade Priority Suggestions**: Recommendations for upgrade order based on current composition
- **Tech Path Visualization**: Visual indicators for completed and pending upgrades
- **Comparative Analysis**: Compare upgrade progress with typical benchmarks

#### 4. **Amon Red Point Analysis & Timing** (Amon红点分析/计时)
- **Attack Wave Detection**: Identifies and predicts incoming Amon attack waves
- **Red Point Tracking**: Monitors Amon base locations and expansion patterns
- **Attack Wave Timer**: Countdown timers for upcoming attack waves
- **Defense Preparation Alerts**: Early warnings to prepare defenses before attacks
- **Objective Timing**: Tracks mission-specific objectives and time-sensitive events

### Technical Architecture

```
starcraft-copilot/
├── src/
│   ├── ScreenCapture.py      # Screen capture and image processing
│   ├── OCR_Analysis.py        # OCR and game state recognition
│   ├── ReminderEngine.py      # Logic for reminders and notifications
│   └── DataStore/
│       └── CoopCommanderData.json  # Commander data and strategies
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # This file
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ProbiusOfficial/starcraft-copilot.git
   cd starcraft-copilot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Requirements
- Python 3.8+
- StarCraft II installed and running
- Windows/macOS/Linux with screen capture permissions

### How It Works

1. **Screen Capture**: Continuously captures specific regions of the game screen
2. **OCR Analysis**: Uses Optical Character Recognition to extract game state information
3. **Data Processing**: Analyzes extracted data against stored game knowledge
4. **Smart Reminders**: Generates contextual reminders and suggestions based on game state
5. **Real-time Overlay**: Displays information via non-intrusive overlay or notifications

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 中文

### 概述
星际争霸II助手是一个实时桌面辅助工具，支持合作模式和对战模式。它通过屏幕捕获技术监控您的游戏过程，提供重要的宏观提醒、战略建议和战术分析，以提升您的游戏体验。

### 核心功能

#### 1. **运营提醒**
- **工人生产跟踪**：自动监控并提醒您持续生产工人（SCV、探机、雄蜂）
- **人口管理**：在接近人口上限时发出警报，防止人口卡顿
- **资源溢出检测**：当资源积累时发出通知，建议扩张或生产单位
- **宏观时间提醒**：可自定义的关键宏观时间点提醒（扩张、科技升级）

#### 2. **指挥官战术/威望**
- **指挥官专属策略提示**：为每个合作模式指挥官量身定制的战术建议
- **威望天赋推荐**：根据任务和阵容推荐最优威望天赋选择
- **强势期提醒**：指挥官强势期和技能冷却时间提醒
- **协同分析**：推荐最优指挥官搭配和单位组合

#### 3. **攻防升级跟踪**
- **升级进度监控**：实时跟踪所有单位类型的攻击和防御升级
- **升级优先级建议**：根据当前阵容推荐升级顺序
- **科技路线可视化**：已完成和待完成升级的可视化指示器
- **对比分析**：将升级进度与标准基准进行比较

#### 4. **Amon红点分析/计时**
- **攻击波检测**：识别和预测即将到来的Amon攻击波
- **红点追踪**：监控Amon基地位置和扩张模式
- **攻击波计时器**：即将到来的攻击波倒计时
- **防御准备警报**：在攻击前提前发出警告以准备防御
- **目标计时**：跟踪任务特定目标和时间敏感事件

### 技术架构

```
starcraft-copilot/
├── src/
│   ├── ScreenCapture.py      # 屏幕捕获和图像处理
│   ├── OCR_Analysis.py        # OCR和游戏状态识别
│   ├── ReminderEngine.py      # 提醒和通知逻辑
│   └── DataStore/
│       └── CoopCommanderData.json  # 指挥官数据和策略
├── requirements.txt           # Python依赖
├── LICENSE                    # MIT许可证
└── README.md                  # 本文件
```

### 安装

1. **克隆仓库：**
   ```bash
   git clone https://github.com/ProbiusOfficial/starcraft-copilot.git
   cd starcraft-copilot
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用程序：**
   ```bash
   python main.py
   ```

### 系统要求
- Python 3.8+
- 已安装并运行的星际争霸II
- 具有屏幕捕获权限的Windows/macOS/Linux系统

### 工作原理

1. **屏幕捕获**：持续捕获游戏屏幕的特定区域
2. **OCR分析**：使用光学字符识别提取游戏状态信息
3. **数据处理**：将提取的数据与存储的游戏知识进行分析
4. **智能提醒**：根据游戏状态生成上下文相关的提醒和建议
5. **实时覆盖层**：通过非侵入式覆盖层或通知显示信息

### 许可证
本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。 
