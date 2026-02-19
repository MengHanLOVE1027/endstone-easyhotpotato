# python 库
import time, random
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from threading import Lock
import logging
import json

# endstone 库
from endstone.plugin import Plugin
from endstone.command import CommandSenderWrapper, Command
from endstone import Player
from endstone.event import *
from endstone.form import ActionForm, MessageForm, ModalForm, Button, TextInput, Slider, Toggle, Dropdown, Header, Label, Divider
from endstone.boss import BarColor, BarStyle


# 游戏状态常量
GAME_STATE_IDLE = 0      # 游戏空闲
GAME_STATE_WAITING = 1   # 等待玩家
GAME_STATE_PREPARING = 2 # 准备阶段
GAME_STATE_RUNNING = 3   # 游戏进行中
GAME_STATE_ENDING = 4    # 游戏结束

# 默认配置常量
DEFAULT_MIN_PLAYERS = 2      # 最低玩家数
DEFAULT_GAME_TIME = 180      # 默认游戏时长（秒）
DEFAULT_PRE_TIME = 10        # 默认预热时间（秒）
DEFAULT_WAIT_TIME = 120      # 默认等待时间（秒）
DEFAULT_AREA_SIZE_X = 10     # 默认活动区域X轴半径
DEFAULT_AREA_SIZE_Z = 10     # 默认活动区域Z轴半径

# 物品ID常量
POTATO_ITEM_ID = "minecraft:potato"

# 音效常量
SOUND_TRANSFER = "mob.blaze.shoot"    # 传递音效
SOUND_EXPLODE = "random.explode"      # 爆炸音效
SOUND_XP = "random.orb"                # 经验音效

# 粒子效果常量
PARTICLE_FLAME = "minecraft:basic_flame_particle"      # 火焰粒子
PARTICLE_EXPLODE = "minecraft:explode_particle"        # 爆炸粒子

# 颜色代码常量
COLOR_RED = "§c"
COLOR_GREEN = "§a"
COLOR_BLUE = "§b"
COLOR_YELLOW = "§e"
COLOR_GOLD = "§6"
COLOR_WHITE = "§f"
COLOR_GRAY = "§7"

# TAG: 全局常量
plugin_name = "EasyHotPotato"
plugin_name_smallest = "easyhotpotato"
plugin_description = "基于 EndStone 的烫手山芋插件 / The Python hot potato plugin based on EndStone."
plugin_version = "0.1.0"
plugin_author = ["梦涵LOVE"]
plugin_the_help_link = "https://www.minebbs.com/resources/easyhotpotato-ehp-endstone.15329/"
plugin_website = "https://www.minebbs.com/resources/easyhotpotato-ehp-endstone.15329/"
plugin_github_link = "https://github.com/MengHanLOVE1027/endstone-easyhotpotato"
plugin_license = "AGPL-3.0"
plugin_copyright = "务必保留原作者信息！"

success_plugin_version = "v" + plugin_version
plugin_full_name = plugin_name + " " + success_plugin_version

plugin_path = Path(f"./plugins/{plugin_name}")

# 嘲讽语录列表
TAUNT_MESSAGES = [
    "哈哈！烫手山芋传给你了！",
    "快接住这个热土豆！",
    "祝你好运,烫手的家伙！",
    "享受这个热土豆吧！",
    "你现在是土豆的主人了！",
    "小心别被烫伤哦！",
    "快传给下一个倒霉蛋！",
    "热土豆来咯！",
    "接住这个会爆炸的礼物！",
    "你中奖了！土豆归你了！"
]


# 创建一个锁对象，用于线程安全
print_lock = Lock()

# 创建logs目录
log_dir = Path("./logs/EasyBackuper")
if not log_dir.exists():
    log_dir.mkdir(parents=True, exist_ok=True)

# 设置日志文件名，按日期分割
log_file = log_dir / f"{plugin_name_smallest}_{datetime.now().strftime('%Y%m%d')}.log"

# 配置日志系统
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)

# 创建插件专用的logger
logger = logging.getLogger(plugin_name)

def plugin_print(text, level="INFO") -> bool:
    """
    自制 print 日志输出函数
    :param text: 文本内容
    :param level: 日志级别 (DEBUG, INFO, WARNING, ERROR, SUCCESS)
    :return: True
    """
    # 日志级别颜色映射
    level_colors = {
        "DEBUG": "\x1b[36m",    # 青色
        "INFO": "\x1b[37m",     # 白色
        "WARNING": "\x1b[33m",  # 黄色
        "ERROR": "\x1b[31m",    # 红色
        "SUCCESS": "\x1b[32m"   # 绿色
    }
    
    # 获取日志级别颜色
    level_color = level_colors.get(level, "\x1b[37m")
    
    # 自制Logger消息头
    logger_head = f"[\x1b[32m{plugin_name}\x1b[0m] [{level_color}{level}\x1b[0m] "
    
    # 使用锁确保线程安全
    with print_lock:
        print(logger_head + str(text))
    
    # 记录到日志文件
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "SUCCESS": logging.INFO
    }
    
    # 将SUCCESS级别映射为INFO级别记录到日志
    log_level = log_level_map.get(level, logging.INFO)
    logger.log(log_level, str(text))
    
    return True


class DataManager:
    """数据管理器类"""
    
    def __init__(self, plugin):
        """
        初始化数据管理器
        
        Args:
            plugin: 插件实例
        """
        self.plugin = plugin
        self.stats_file = None
        self.player_stats: Dict[str, Dict] = {}
        self.game_history_file = None
        self.game_history: List[Dict] = []
    
    def load_player_stats(self):
        """加载玩家战绩数据"""
        try:
            if self.stats_file and self.stats_file.exists():
                # 检查文件是否为空
                if self.stats_file.stat().st_size == 0:
                    plugin_print("战绩文件为空，将创建默认数据", "WARNING")
                    self.player_stats = {}
                    self.save_player_stats()
                    return
                
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        plugin_print("战绩文件内容为空，将创建默认数据", "WARNING")
                        self.player_stats = {}
                        self.save_player_stats()
                        return
                    
                    self.player_stats = json.loads(content)
                    plugin_print(f"成功加载 {len(self.player_stats)} 个玩家的战绩数据", "SUCCESS")
            else:
                plugin_print("战绩文件不存在，将创建新文件", "WARNING")
                self.player_stats = {}
                self.save_player_stats()
        except Exception as e:
            plugin_print(f"加载玩家战绩失败: {e}", "ERROR")
            self.player_stats = {}
    
    def save_player_stats(self):
        """保存玩家战绩数据"""
        try:
            if self.stats_file:
                # 确保目录存在
                self.stats_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.player_stats, f, ensure_ascii=False, indent=2)
                plugin_print(f"成功保存 {len(self.player_stats)} 个玩家的战绩数据", "SUCCESS")
        except Exception as e:
            plugin_print(f"保存玩家战绩失败: {e}", "ERROR")
    
    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """
        获取玩家战绩
        
        Args:
            player_name: 玩家名称
            
        Returns:
            玩家战绩字典，如果不存在则返回None
        """
        return self.player_stats.get(player_name)
    
    def update_player_stats(self, player_name: str, wins: int = 0, games: int = 0):
        """
        更新玩家战绩
        
        Args:
            player_name: 玩家名称
            wins: 增加的胜场数
            games: 增加的总场次
        """
        if player_name not in self.player_stats:
            self.player_stats[player_name] = {
                "wins": 0,
                "games": 0,
                "win_rate": 0.0
            }
        
        stats = self.player_stats[player_name]
        stats["wins"] += wins
        stats["games"] += games
        
        # 计算胜率
        if stats["games"] > 0:
            stats["win_rate"] = round(stats["wins"] / stats["games"] * 100, 2)
        else:
            stats["win_rate"] = 0.0
        
        plugin_print(f"更新玩家 {player_name} 战绩: 胜场 {stats['wins']}, 总场次 {stats['games']}, 胜率 {stats['win_rate']}%", "INFO")
    
    def get_top_players(self, limit: int = 10) -> list:
        """
        获取排行榜前N名玩家
        
        Args:
            limit: 返回的玩家数量
            
        Returns:
            排序后的玩家列表，每个元素为 (玩家名, 战绩字典) 元组
        """
        # 按胜场数排序，胜场数相同则按胜率排序
        sorted_players = sorted(
            self.player_stats.items(),
            key=lambda x: (x[1]["wins"], x[1]["win_rate"]),
            reverse=True
        )
        
        return sorted_players[:limit]
    
    def reset_player_stats(self, player_name: str):
        """
        重置玩家战绩
        
        Args:
            player_name: 玩家名称
        """
        if player_name in self.player_stats:
            del self.player_stats[player_name]
            plugin_print(f"已重置玩家 {player_name} 的战绩", "INFO")
            self.save_player_stats()
    
    def reset_all_stats(self):
        """重置所有玩家战绩"""
        self.player_stats = {}
        plugin_print("已重置所有玩家战绩", "INFO")
        self.save_player_stats()

    def load_game_history(self):
        """加载战局记录数据"""
        try:
            if self.game_history_file and self.game_history_file.exists():
                # 检查文件是否为空
                if self.game_history_file.stat().st_size == 0:
                    plugin_print("战局记录文件为空，将创建默认数据", "WARNING")
                    self.game_history = []
                    self.save_game_history()
                    return

                with open(self.game_history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        plugin_print("战局记录文件内容为空，将创建默认数据", "WARNING")
                        self.game_history = []
                        self.save_game_history()
                        return

                    self.game_history = json.loads(content)
                    plugin_print(f"成功加载 {len(self.game_history)} 条战局记录", "SUCCESS")
            else:
                plugin_print("战局记录文件不存在，将创建新文件", "WARNING")
                self.game_history = []
                self.save_game_history()
        except Exception as e:
            plugin_print(f"加载战局记录失败: {e}", "ERROR")
            self.game_history = []

    def save_game_history(self):
        """保存战局记录数据"""
        try:
            if self.game_history_file:
                # 确保目录存在
                self.game_history_file.parent.mkdir(parents=True, exist_ok=True)

                with open(self.game_history_file, 'w', encoding='utf-8') as f:
                    json.dump(self.game_history, f, ensure_ascii=False, indent=2)
                plugin_print(f"成功保存 {len(self.game_history)} 条战局记录", "SUCCESS")
        except Exception as e:
            plugin_print(f"保存战局记录失败: {e}", "ERROR")

    def add_game_record(self, game_record: Dict):
        """添加一条战局记录

        Args:
            game_record: 战局记录字典，包含以下字段:
                - game_id: 游戏ID
                - start_time: 开始时间
                - end_time: 结束时间
                - players: 参与玩家列表
                - winner: 获胜者
                - duration: 游戏时长（秒）
                - reason: 游戏结束原因
        """
        self.game_history.append(game_record)
        self.save_game_history()
        plugin_print(f"已添加战局记录: 游戏ID {game_record.get('game_id', '未知')}, 获胜者 {game_record.get('winner', '无')}", "INFO")

    def get_game_history(self, limit: int = 10) -> list:
        """获取最近的战局记录

        Args:
            limit: 返回的记录数量

        Returns:
            最近的战局记录列表
        """
        # 返回最近的记录（按时间倒序）
        return self.game_history[-limit:][::-1]

    def get_game_history_by_player(self, player_name: str, limit: int = 10) -> list:
        """获取指定玩家的战局记录

        Args:
            player_name: 玩家名称
            limit: 返回的记录数量

        Returns:
            该玩家参与的战局记录列表
        """
        # 筛选出该玩家参与的记录
        player_games = [
            record for record in self.game_history
            if player_name in record.get('players', [])
        ]
        # 返回最近的记录（按时间倒序）
        return player_games[-limit:][::-1]


# TAG: 插件入口点
class EasyHotPotatoPlugin(Plugin):
    """
    插件入口点
    """

    api_version = "0.5"
    name = plugin_name_smallest
    full_name = plugin_full_name
    description = plugin_description
    version = plugin_version
    authors = plugin_author
    website = plugin_website

    # NOTE: 注册命令
    commands = {
        # 烫手山芋游戏命令
        "easyhotpotato": {
            "description": "烫手山芋游戏命令",
            "usages": [
                "/easyhotpotato",
                "/easyhotpotato status",
                "/easyhotpotato stats [target: player]",
                "/easyhotpotato help"
            ],
            "permissions": ["easyhotpotato.command.use"],
        },
    }

    # NOTE: 权限组
    permissions = {
        # 烫手山芋游戏权限
        "easyhotpotato.command.use": {
            "description": "允许使用烫手山芋命令",
            "default": "true",
        },
        "easyhotpotato.admin": {
            "description": "烫手山芋管理员权限",
            "default": "op",
        },
    }

    def __init__(self):
        super().__init__()
        # 游戏状态
        self.game_active = False
        self.game_start_time = 0
        self.game_time = 180  # 默认游戏时长（秒）
        self.game_start_timestamp = 0  # 游戏开始的时间戳
        self.game_id = 0  # 游戏ID
        self.potato_holder = None  # 当前持有山芋的玩家
        self.potato_item_id = "minecraft:potato"  # 山芋物品ID
        self.game_task = None  # 游戏计时器任务
        self.countdown_task = None  # 倒计时任务
        self.pre_game_task = None  # 赛前倒计时任务
        self.players_in_game = set()  # 参与游戏的玩家集合（当前还在游戏中）
        self.all_players_in_game = set()  # 所有参与游戏的玩家集合（包括被淘汰的）
        self.min_players = 2  # 触发自动开赛的最低人数
        self.max_players = 0  # 最大参与人数，0表示无上限
        self.pre_time = 10  # 正式开赛前的热身倒计时
        self.wait_time = 120  # 满人后的预备等待
        self.particle_task = None  # 粒子效果任务
        self.position_check_task = None  # 位置检查任务
        self.stop_game_task = None
        
        # BossBar相关
        self.bossbar = None  # BossBar对象
        self.bossbar_task = None  # BossBar更新任务
        self.wait_countdown_task = None  # 等待倒计时BossBar任务
        
        # 地理信息
        self.wait_pos = {"x": 0, "y": 0, "z": 0, "dimid": 0}  # 等待中心
        self.game_pos = {"x": 100, "y": 64, "z": 100, "dimid": 0}  # 竞技中心
        self.area_size = {"x": 10, "z": 10}  # 活动半径
        
        # 数据管理
        self.data_manager = None  # 数据管理器实例，在on_load中初始化
        self.config_file = None  # 配置文件路径，在on_load中初始化

    def on_load(self):
        """插件加载时调用"""
        plugin_print(f"{self.full_name} 正在加载...")
        
        # 初始化数据目录
        self.data_dir = Path(self.data_folder)
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)

        # 初始化数据管理器
        self.data_manager = DataManager(self)
        self.data_manager.stats_file = self.data_dir / "player_stats.json"
        self.data_manager.load_player_stats()
        self.data_manager.game_history_file = self.data_dir / "game_history.json"
        self.data_manager.load_game_history()

        # 初始化配置文件路径
        self.config_file = self.data_dir / "config.json"

        # 加载配置文件
        self.load_config()

        plugin_print(f"{self.full_name} 已加载!")

    def on_enable(self):
        """插件启用时调用"""
        plugin_print(f"{self.full_name} 正在启用...")
        plugin_print(f"{self.full_name} 已启用!")
        self.register_events(self)
        
        # 初始化默认BossBar
        self.init_default_bossbar()

    def on_disable(self):
        """插件禁用时调用"""
        plugin_print(f"{self.full_name} 正在禁用...")
        if self.data_manager:
            self.data_manager.save_player_stats()
        self.save_config()
        
        # 清理BossBar
        self.cleanup_bossbar()
        
        plugin_print(f"{self.full_name} 已禁用!")

    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                # 检查文件是否为空
                if self.config_file.stat().st_size == 0:
                    plugin_print("配置文件为空，将创建默认配置", "WARNING")
                    self.save_config()
                    return

                with open(self.config_file, 'r', encoding='utf-8') as f:
                    import json
                    content = f.read()
                    if not content.strip():
                        plugin_print("配置文件内容为空，将创建默认配置", "WARNING")
                        self.save_config()
                        return

                    config = json.loads(content)
                    self.wait_pos = config.get("waitPos", {"x": 0, "y": 0, "z": 0, "dimid": 0})
                    self.game_pos = config.get("gamePos", {"x": 100, "y": 64, "z": 100, "dimid": 0})
                    self.area_size = config.get("areaSize", {"x": 10, "z": 10})
                    self.wait_time = config.get("waitTime", 120)
                    self.pre_time = config.get("preTime", 10)
                    self.game_time = config.get("gameTime", 180)
                    self.min_players = config.get("minPlayers", 2)
                    self.max_players = config.get("maxPlayers", 0)  # 0表示无上限
                    plugin_print("配置文件加载成功", "SUCCESS")
            else:
                # 创建默认配置
                self.save_config()
                plugin_print("未找到配置文件，已创建默认配置", "WARNING")
        except Exception as e:
            plugin_print(f"加载配置文件失败: {e}，将使用默认配置", "ERROR")
            self.save_config()

    def save_config(self):
        """保存配置文件"""
        try:
            config = {
                "waitPos": self.wait_pos,
                "gamePos": self.game_pos,
                "areaSize": self.area_size,
                "waitTime": self.wait_time,
                "preTime": self.pre_time,
                "gameTime": self.game_time,
                "minPlayers": self.min_players,
                "maxPlayers": self.max_players
            }
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            plugin_print("配置文件已保存", "SUCCESS")
        except Exception as e:
            plugin_print(f"保存配置文件失败: {e}", "ERROR")

    def reload_config(self, player: Optional[Player] = None):
        """重新加载配置文件
        
        Args:
            player: 操作的管理员玩家
        """
        try:
            self.load_config()
            if player:
                player.send_message("§a配置文件重新加载成功！")
            plugin_print("配置文件重新加载成功", "SUCCESS")
        except Exception as e:
            if player:
                player.send_message("§c配置文件重新加载失败！")
            plugin_print(f"配置文件重新加载失败: {e}", "ERROR")
        # 重新显示管理员菜单
        if player:
            self.show_admin_menu(player)

    @event_handler
    def on_player_drop_item(self, event: PlayerDropItemEvent):
        """玩家丢弃物品事件 - 阻止丢弃山芋"""
        try:
            if not self.game_active:
                return

            # 检查是否是玩家
            if not hasattr(event, 'player') or not isinstance(event.player, Player):
                return

            player = event.player

            # 如果玩家不在游戏中，不阻止
            if player not in self.players_in_game:
                return

            # 检查是否是山芋持有者
            if self.potato_holder == player:
                # 取消丢弃事件
                event.is_cancelled = True
                player.send_message("§c你不能丢弃烫手山芋！")
                plugin_print(f"阻止玩家 {player.name} 丢弃山芋", "INFO")
        except Exception as e:
            plugin_print(f"处理玩家丢弃物品事件失败: {e}", "ERROR")

    @event_handler
    def on_actor_damage(self, event: ActorDamageEvent):
        """实体受伤事件 - 实现绝对传递机制"""
        try:
            if not self.game_active:
                return

            # 检查伤害来源和受害者是否都是玩家
            damage_source = event.damage_source
            if not hasattr(damage_source, 'actor') or not isinstance(damage_source.actor, Player):
                return

            if not isinstance(event.actor, Player):
                return

            attacker = damage_source.actor
            victim = event.actor

            plugin_print(f"玩家 {attacker.name} 攻击了玩家 {victim.name}", "INFO")

            # 只有持有山芋的玩家攻击未持有山芋的玩家时才传递
            if self.potato_holder == attacker and victim in self.players_in_game and victim != self.potato_holder:
                plugin_print(f"山芋将从 {attacker.name} 传递到 {victim.name}", "INFO")
                self.transfer_potato_to(attacker, victim)
        except Exception as e:
            self.logger.error(f"处理实体受伤事件失败: {e}")

    def on_command(self, sender: CommandSenderWrapper, command: Command, args: list[str]) -> bool:
        """处理命令"""
        # 处理烫手山芋命令
        if command.name == "easyhotpotato":
            self.handle_easyhotpotato_command(sender, args)

    def handle_easyhotpotato_command(self, sender: CommandSenderWrapper, args: list):
        """处理烫手山芋命令
        
        Args:
            sender: 命令发送者
            args: 命令参数
        """
        # 检查权限
        if not sender.has_permission("easyhotpotato.command.use"):
            sender.send_message("§c你没有权限使用此命令！")
            return
        
        # 检查是否是玩家
        if not isinstance(sender, Player):
            sender.send_message("§c只有玩家才能使用此命令！")
            return
        
        # 没有参数，显示主菜单
        if not args:
            self.show_main_menu(sender)
            return
        
        # 处理子命令
        subcommand = args[0].lower()
        
        if subcommand == "status":
            # 显示游戏状态
            sender.send_message(self.get_game_status())

        elif subcommand == "stats":
            # 查看战绩
            if len(args) > 1:
                target_name = args[1]
            else:
                target_name = sender.name
            self.show_player_stats_form(sender, target_name)

        elif subcommand == "help":
            # 显示帮助
            self.show_easyhotpotato_help(sender)
        
        else:
            sender.send_message("§c未知的子命令！")
            self.show_easyhotpotato_help(sender)

    def show_main_menu(self, player: Player):
        """显示主菜单
        
        Args:
            player: 玩家对象
        """
        form = ActionForm(
            title="§6EasyHotPotato 烫手山芋",
            content="§e请选择你要执行的操作:",
            on_close=lambda p: p.send_message("§c你关闭了菜单")
        )

        form.add_label(f"§6当前状态: {'§a游戏进行中' if self.game_active else '§c游戏未开始'}")
        form.add_label(f"§e参与玩家: §f{len(self.players_in_game)}人")
        if self.game_active and self.potato_holder:
            form.add_label(f"§e当前持有者: §c{self.potato_holder.name}")
        
        form.add_divider()

        # 核心功能按钮
        if player in self.players_in_game:
            form.add_button(text="§c离开战场", icon="textures/ui/icon_import", on_click=lambda p: self.leave_game(p))
        else:
            form.add_button(text="§a进入战场", icon="textures/ui/color_plus", on_click=lambda p: self.join_game(p))
        form.add_button(text="§e查看排行", icon="textures/ui/icon_steve", on_click=lambda p: self.show_rankings_form(p))
        form.add_button(text="§b战局记录", icon="textures/ui/icon_bookshelf", on_click=lambda p: self.show_game_history_form(p))
        
        # 管理员功能
        if player.is_op:
            form.add_button(text="§c后台管理", icon="textures/ui/icon_setting", on_click=lambda p: self.show_admin_menu(p))

        player.send_form(form)

    def show_admin_menu(self, player: Player):
        """显示管理员菜单
        
        Args:
            player: 玩家对象
        """
        form = ActionForm(
            title="§6后台管理",
            content="§e请选择管理操作:",
            on_close=lambda p: self.show_main_menu(p)
        )

        form.add_button(text="§a地理信息设置", icon="textures/ui/paste", on_click=lambda p: self.show_geo_settings_form(p))
        form.add_button(text="§e参数调优", icon="textures/ui/pencil_edit_icon", on_click=lambda p: self.show_param_settings_form(p))
        form.add_button(text="§c停止游戏", icon="textures/ui/cancel", on_click=lambda p: self.show_stop_game_confirm_form(p))
        form.add_button(text="§b重新加载配置", icon="textures/ui/refresh", on_click=lambda p: self.reload_config(p))
        form.add_button(text="§e返回主菜单", icon="textures/ui/arrow_left", on_click=lambda p: self.show_main_menu(p))
        player.send_form(form)

    def show_geo_settings_form(self, player: Player):
        """显示地理信息设置菜单
        
        Args:
            player: 玩家对象
        """
        form = ActionForm(
            title="§6地理信息设置",
            content="§e请选择要设置的位置:",
            on_close=lambda p: self.show_admin_menu(p)
        )

        form.add_button(text="§a设置等待中心", icon="textures/ui/pencil_edit_icon", on_click=lambda p: self.set_wait_pos(p))
        form.add_button(text="§b设置竞技中心", icon="textures/ui/pencil_edit_icon", on_click=lambda p: self.set_game_pos(p))
        form.add_button(text="§e设置活动半径", icon="textures/ui/pencil_edit_icon", on_click=lambda p: self.show_area_size_form(p))
        form.add_button(text="§e返回管理菜单", icon="textures/ui/arrow_left", on_click=lambda p: self.show_admin_menu(p))
        player.send_form(form)

    def set_wait_pos(self, player: Player):
        """设置等待中心
        
        Args:
            player: 玩家对象
        """
        loc = player.location
        self.wait_pos = {
            "x": int(loc.x),
            "y": int(loc.y),
            "z": int(loc.z),
            "dimid": 0  # 简化处理，默认维度
        }
        self.save_config()
        player.send_message(f"§a等待中心已设置为当前位置: X={loc.x}, Y={loc.y}, Z={loc.z}")
        self.show_geo_settings_form(player)

    def set_game_pos(self, player: Player):
        """设置竞技中心
        
        Args:
            player: 玩家对象
        """
        loc = player.location
        self.game_pos = {
            "x": int(loc.x),
            "y": int(loc.y),
            "z": int(loc.z),
            "dimid": 0  # 简化处理，默认维度
        }
        self.save_config()
        player.send_message(f"§a竞技中心已设置为当前位置: X={loc.x}, Y={loc.y}, Z={loc.z}")
        self.show_geo_settings_form(player)

    def show_area_size_form(self, player: Player):
        """显示活动半径设置表单
        
        Args:
            player: 玩家对象
        """
        form = ModalForm(
            title="§6设置活动半径",
            submit_button="§a确认",
            on_submit=lambda p, data: self.handle_area_size_form(p, data),
            on_close=lambda p: self.show_geo_settings_form(p)
        )

        form.add_control(TextInput(label="§eX轴半径", default_value=str(self.area_size["x"]), placeholder="输入X轴最大活动范围"))
        form.add_control(TextInput(label="§eZ轴半径", default_value=str(self.area_size["z"]), placeholder="输入Z轴最大活动范围"))
        player.send_form(form)

    def handle_area_size_form(self, player: Player, data):
        """处理活动半径设置表单
        
        Args:
            player: 玩家对象
            data: 表单数据
        """
        try:
            # 检查数据是否有效
            if data is None:
                player.send_message("§c表单数据不完整，请重新填写！")
                self.show_geo_settings_form(player)
                return
            
            # 检查data是否是字符串，如果是，尝试解析为JSON
            if isinstance(data, str):
                import json
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    player.send_message("§c数据格式错误，请重试！")
                    self.show_geo_settings_form(player)
                    return
            
            # 确保data是列表
            if not isinstance(data, list) or len(data) < 2:
                player.send_message("§c表单数据不完整，请重新填写！")
                self.show_geo_settings_form(player)
                return
            
            # 处理元素，转换为整数
            x_size = None
            z_size = None
            
            for i, item in enumerate(data[:2]):
                # 处理None值
                if item is None:
                    player.send_message("§c请输入有效的数字！")
                    self.show_geo_settings_form(player)
                    return
                
                # 处理字符串，去除空格
                if isinstance(item, str):
                    item = item.strip()
                    if not item:
                        player.send_message("§c请输入有效的数字！")
                        self.show_geo_settings_form(player)
                        return
                
                # 转换为整数并验证
                try:
                    int_value = int(item)
                    if int_value <= 0:
                        field_name = "X轴半径" if i == 0 else "Z轴半径"
                        player.send_message(f"§c{field_name}必须大于0！")
                        self.show_geo_settings_form(player)
                        return
                    if i == 0:
                        x_size = int_value
                    else:
                        z_size = int_value
                except (ValueError, TypeError):
                    field_name = "X轴半径" if i == 0 else "Z轴半径"
                    player.send_message(f"§c{field_name}必须是有效的数字！")
                    self.show_geo_settings_form(player)
                    return
            
            # 检查是否成功获取值
            if x_size is None or z_size is None:
                player.send_message("§c表单数据不完整，请重新填写！")
                self.show_geo_settings_form(player)
                return
            
            # 更新活动半径并保存
            self.area_size = {"x": x_size, "z": z_size}
            self.save_config()
            player.send_message(f"§a活动半径已设置为: X={x_size}, Z={z_size}")
        except Exception as e:
            plugin_print(f"处理活动半径设置表单失败: {e}", "ERROR")
            player.send_message("§c处理表单时发生错误，请重试！")
        finally:
            self.show_geo_settings_form(player)

    def show_param_settings_form(self, player: Player):
        """显示参数调优表单
        
        Args:
            player: 玩家对象
        """
        form = ModalForm(
            title="§6参数调优",
            submit_button="§a确认",
            on_submit=lambda p, data: self.handle_param_settings_form(p, data),
            on_close=lambda p: self.show_admin_menu(p)
        )

        form.add_control(TextInput(label="§e最低人数", default_value=str(self.min_players), placeholder="触发自动开赛的最低人数"))
        form.add_control(TextInput(label="§e游戏时长", default_value=str(self.game_time), placeholder="游戏时长（秒）"))
        form.add_control(TextInput(label="§e热身时间", default_value=str(self.pre_time), placeholder="正式开赛前的热身倒计时（秒）"))
        form.add_control(TextInput(label="§e等待时间", default_value=str(self.wait_time), placeholder="满人后的预备等待（秒）"))
        player.send_form(form)

    def handle_param_settings_form(self, player: Player, data):
        """处理参数调优表单
        
        Args:
            player: 玩家对象
            data: 表单数据
        """
        try:
            plugin_print(f"原始数据: {data}")
            
            # 检查数据是否有效
            if data is None or len(data) < 4:
                player.send_message("§c表单数据不完整，请重新填写！")
                self.show_admin_menu(player)
                return
            
            # 将data转换为数字列表
            try:
                # 检查data是否是字符串，如果是，尝试解析为JSON
                if isinstance(data, str):
                    import json
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        player.send_message("§c数据格式错误，请重试！")
                        self.show_admin_menu(player)
                        return
                
                # 确保data是列表
                if not isinstance(data, list) or len(data) < 4:
                    player.send_message("§c表单数据不完整，请重新填写！")
                    self.show_admin_menu(player)
                    return
                
                # 对每个元素进行处理，确保是有效的数字字符串
                processed_data = []
                for i, item in enumerate(data[:4]):  # 只处理前4个元素
                    # 处理None值
                    if item is None:
                        player.send_message("§c请输入有效的数字！")
                        self.show_admin_menu(player)
                        return
                    # 处理字符串，去除空格
                    if isinstance(item, str):
                        item = item.strip()
                        if not item:
                            player.send_message("§c请输入有效的数字！")
                            self.show_admin_menu(player)
                            return
                    # 转换为整数
                    try:
                        processed_data.append(int(item))
                    except (ValueError, TypeError):
                        player.send_message(f"§c第{i+1}个字段必须是有效的数字！")
                        self.show_admin_menu(player)
                        return
                data = processed_data
            except Exception as e:
                plugin_print(f"转换数据时发生错误: {e}", "ERROR")
                player.send_message("§c处理数据时发生错误，请重试！")
                self.show_admin_menu(player)
                return
            
            # 逐个字段检查和转换
            fields = [
                ("最低人数", data[0], lambda x: x >= 2, "§c最低人数不能小于2！"),
                ("游戏时长", data[1], lambda x: x >= 10, "§c游戏时长不能小于10秒！"),
                ("热身时间", data[2], lambda x: x >= 1, "§c热身时间不能小于1秒！"),
                ("等待时间", data[3], lambda x: x >= 10, "§c等待时间不能小于10秒！")
            ]
            
            for field_name, value, validator, error_msg in fields:
                if not validator(value):
                    player.send_message(error_msg)
                    self.show_admin_menu(player)
                    return
            
            # 更新参数
            self.min_players = data[0]
            self.game_time = data[1]
            self.pre_time = data[2]
            self.wait_time = data[3]
            
            # 保存配置
            self.save_config()
            
            player.send_message("§a参数设置成功！")
            plugin_print(f"参数已更新: 最低人数={self.min_players}, 游戏时长={self.game_time}, 热身时间={self.pre_time}, 等待时间={self.wait_time}", "SUCCESS")
        except Exception as e:
            plugin_print(f"处理参数设置表单失败: {e}", "ERROR")
            player.send_message("§c处理表单时发生错误，请重试！")
        finally:
            self.show_admin_menu(player)

    def show_stop_game_confirm_form(self, player: Player):
        """显示停止游戏确认表单
        
        Args:
            player: 玩家对象
        """
        form = MessageForm(
            title="§6停止游戏确认",
            content="§c你确定要停止当前游戏吗？\n§e这将结束正在进行的游戏并清空所有玩家状态。",
            button1="§a确认停止",
            button2="§c取消",
            on_submit=lambda p, choice: self.handle_stop_game_confirm(p, choice)
        )
        player.send_form(form)

    def show_custom_wait_time_form(self, player: Player):
        """显示自定义准备时间选择表单

        Args:
            player: 玩家对象
        """
        form = ActionForm(
            title="§6选择准备时间",
            content=f"§e当前参与人数: §f{len(self.players_in_game)}人\n§e最低要求人数: §f{self.min_players}人\n§e最大人数限制: §f{'无限制' if self.max_players == 0 else str(self.max_players) + '人'}\n\n§e请选择游戏开始前的准备时间:",
            on_close=lambda p: p.send_message("§c你取消了准备时间选择")
        )

        # 添加准备时间选项
        wait_time_options = [
            {"text": "§a立即开始", "time": 0, "icon": "textures/ui/check"},
            {"text": "§e等待10秒", "time": 10, "icon": "textures/ui/clock_icon"},
            {"text": "§e等待30秒", "time": 30, "icon": "textures/ui/clock_icon"},
            {"text": "§e等待60秒", "time": 60, "icon": "textures/ui/clock_icon"},
            {"text": "§e等待120秒", "time": 120, "icon": "textures/ui/clock_icon"},
            {"text": "§e等待180秒", "time": 180, "icon": "textures/ui/clock_icon"},
        ]

        for option in wait_time_options:
            form.add_button(
                text=option["text"],
                icon=option["icon"],
                on_click=lambda p, time=option["time"]: self.start_game_with_wait_time(p, time)
            )

        form.add_button(text="§c取消", icon="textures/ui/cancel", on_click=lambda p: p.send_message("§c你取消了准备时间选择"))
        player.send_form(form)

    def start_game_with_wait_time(self, player: Player, wait_time: int):
        """使用指定的准备时间开始游戏

        Args:
            player: 选择准备时间的玩家
            wait_time: 准备时间（秒）
        """
        if wait_time == 0:
            player.send_message("§a游戏即将开始！")
            self.server.broadcast_message(f"§e{player.name} §a选择了立即开始游戏！")
            self.start_pre_game_countdown()
        else:
            player.send_message(f"§a游戏将在 §e{wait_time} §a秒后开始！")
            self.server.broadcast_message(f"§e{player.name} §a选择了等待 §e{wait_time} §a秒后开始游戏！")
            # 延迟指定时间后开始预热倒计时
            self.server.scheduler.run_task(
                self,
                lambda: self.start_pre_game_countdown(),
                delay=wait_time * 20  # 转换为ticks（1秒=20ticks）
            )

    def handle_stop_game_confirm(self, player: Player, choice: int):
        """处理停止游戏确认
        
        Args:
            player: 玩家对象
            choice: 选择的按钮 (0=确认, 1=取消)
        """
        if choice == 0:  # 确认停止
            if self.game_active:
                self.stop_game("管理员强制停止")
                player.send_message("§a游戏已停止！")
            else:
                player.send_message("§c当前没有正在进行的游戏！")
        else:  # 取消
            player.send_message("§e已取消停止游戏操作")
        
        # 返回管理员菜单
        self.show_admin_menu(player)

    def show_rankings_form(self, player: Player):
        """显示排行榜
        
        Args:
            player: 玩家对象
        """
        top_players = self.data_manager.get_top_players(10)
        
        form = ActionForm(
            title="§6烫手山芋排行榜",
            content="§e以下是胜场最多的玩家:",
            on_close=lambda p: self.show_main_menu(p)
        )
        
        if not top_players:
            form.add_label("§c暂无排行数据")
        else:
            for i, (player_name, stats) in enumerate(top_players, 1):
                medal = ""
                if i == 1:
                    medal = "§6NO.1 "
                elif i == 2:
                    medal = "§7NO.2 "
                elif i == 3:
                    medal = "§cNO.3 "
                
                form.add_label(
                    f"{medal}§e{i}. §f{player_name} §7- "
                    f"§a胜场: {stats['wins']} §7| "
                    f"§e总场次: {stats['games']} §7| "
                    f"§b胜率: {stats['win_rate']}%"
                )
        
        form.add_divider()
        form.add_button(text="§e返回主菜单", icon="textures/ui/arrow_left", on_click=lambda p: self.show_main_menu(p))
        player.send_form(form)

    def show_player_stats_form(self, player: Player, target_name: str):
        """显示玩家战绩
        
        Args:
            player: 查看战绩的玩家
            target_name: 目标玩家名称
        """
        stats = self.data_manager.get_player_stats(target_name)
        
        form = ActionForm(
            title=f"§6{target_name} 的战绩",
            content="",
            on_close=lambda p: self.show_main_menu(p)
        )
        
        if stats:
            form.add_label(f"§e玩家名称: §f{target_name}")
            form.add_label(f"§a胜场数: §f{stats['wins']}")
            form.add_label(f"§e总场次: §f{stats['games']}")
            form.add_label(f"§b胜率: §f{stats['win_rate']}%")
        else:
            form.add_label(f"§c玩家 {target_name} 还没有战绩记录")
        
        form.add_divider()
        form.add_button(text="§e返回主菜单", icon="textures/ui/arrow_left", on_click=lambda p: self.show_main_menu(p))
        player.send_form(form)

    def start_game(self) -> bool:
        """开始游戏
        
        Returns:
            bool: 是否成功开始游戏
        """
        if self.game_active:
            return False
            
        if len(self.players_in_game) < self.min_players:
            self.server.broadcast_message(f"§c玩家数量不足，至少需要 {self.min_players} 人！")
            return False
            
        self.game_active = True
        self.game_start_time = time.time()
        self.game_start_timestamp = time.time()  # 记录游戏开始的时间戳
        self.game_id += 1  # 递增游戏ID
        
        # 停止彩虹跑马灯
        self.stop_rainbow_marquee()
        
        # 随机选择一个玩家作为初始山芋持有者
        self.potato_holder = random.choice(list(self.players_in_game))
        
        # 随机分配玩家位置
        for player in self.players_in_game:
            # 在游戏区域内随机生成位置（基于游戏中心坐标）
            # 确保玩家不会出界，使用浮点数计算
            x_offset = random.uniform(-self.area_size["x"] + 0.5, self.area_size["x"] - 0.5)
            z_offset = random.uniform(-self.area_size["z"] + 0.5, self.area_size["z"] - 0.5)
            
            # 计算新位置（基于游戏中心坐标）
            new_x = self.game_pos["x"] + x_offset
            new_z = self.game_pos["z"] + z_offset
            new_y = self.game_pos["y"]
            
            # 使用Location对象传送玩家
            try:
                from endstone._internal.endstone_python import Location
                location = Location(dimension=player.dimension, x=new_x, y=new_y, z=new_z)
                player.teleport(location)
                player.send_message(f"§a你已被传送到游戏区域: X={new_x:.2f}, Y={new_y:.2f}, Z={new_z:.2f}")
            except Exception as e:
                plugin_print(f"传送玩家失败: {e}", "WARNING")

        # 给持有者填充山芋
        self.give_potato_to_player(self.potato_holder)
        
        # 广播游戏开始
        self.server.broadcast_message("§6===== 烫手山芋游戏开始 =====")
        self.server.broadcast_message(f"§e初始持有者: §c{self.potato_holder.name}")
        self.server.broadcast_message(f"§e游戏时长: §f{self.game_time}秒")
        
        # 通知持有者
        self.potato_holder.send_message("§c你是初始的山芋持有者！快传给别人！")
        
        # 启动游戏计时器
        self.start_countdown()
        
        # 启动粒子效果任务
        self.start_particle_task()
        
        # 启动位置检查任务
        self.start_position_check_task()
        
        plugin_print("游戏已开始", "SUCCESS")
        return True
        
    def stop_game(self, reason: str = "游戏结束") -> bool:
        """停止游戏
        
        Args:
            reason: 停止原因
            
        Returns:
            bool: 是否成功停止游戏
        """
        if self.stop_game_task:
            self.stop_game_task.cancel()
        if not self.game_active:
            return False
            
        self.game_active = False
        
        # 停止所有任务
        if self.countdown_task:
            self.countdown_task.cancel()
            self.countdown_task = None
            
        if self.pre_game_task:
            self.pre_game_task.cancel()
            self.pre_game_task = None
            
        # 停止粒子效果任务
        self.stop_particle_task()
        
        # 停止位置检查任务
        self.stop_position_check_task()
        
        # 将玩家传送回等待中心
        # 移除所有参与游戏玩家的山芋（包括被淘汰的玩家）
        for player in self.all_players_in_game:
            try:
                self.remove_potato_from_inventory(player)
                # 将玩家传送回等待中心
                self.teleport_to_wait_pos(player)
            except Exception as e:
                plugin_print(f"传送玩家 {player.name} 失败: {e}", "WARNING")
            
        # 广播游戏结束
        self.server.broadcast_message("§6===== 烫手山芋游戏结束 =====")
        self.server.broadcast_message(f"§e原因: §f{reason}")
        
        # 如果只剩一个玩家，宣布获胜者
        winner = None
        if len(self.players_in_game) == 1:
            winner = list(self.players_in_game)[0]
            self.server.broadcast_message(f"§a恭喜 §e{winner.name} §a获得了胜利！")
            # 更新获胜者的战绩
            self.data_manager.update_player_stats(winner.name, wins=1, games=1)
            
        # 保存玩家战绩数据
        self.data_manager.save_player_stats()

        # 记录战局信息
        end_time = time.time()
        duration = int(end_time - self.game_start_timestamp)
        # 保存玩家ID和名称
        players_info = [{"id": str(player.id), "name": player.name} for player in self.all_players_in_game]
        game_record = {
            "game_id": self.game_id,
            "start_time": self.game_start_timestamp,
            "end_time": end_time,
            "players": players_info,
            "winner": winner.name if winner else None,
            "duration": duration,
            "reason": reason
        }
        self.data_manager.add_game_record(game_record)

        # 清空所有玩家集合
        self.all_players_in_game.clear()

        # 重新启动彩虹跑马灯
        self.start_rainbow_marquee()

        plugin_print(f"游戏已停止，原因: {reason}", "INFO")
        return True
        
    def get_game_status(self) -> str:
        """获取游戏状态
        
        Returns:
            str: 游戏状态信息
        """
        if not self.game_active:
            return "§c游戏未在进行中！"
            
        elapsed_time = int(time.time() - self.game_start_time)
        remaining_time = self.game_time - elapsed_time
        
        status = f"§6===== 烫手山芋游戏状态 =====\n"
        status += f"§e游戏时长: §f{self.game_time}秒\n"
        status += f"§e已过时间: §f{elapsed_time}秒\n"
        status += f"§e剩余时间: §f{remaining_time}秒\n"
        status += f"§e当前持有者: §c{self.potato_holder.name if self.potato_holder else '无'}\n"
        status += f"§e剩余玩家: §f{len(self.players_in_game)}人"
        
        return status
        
    def start_countdown(self):
        """开始游戏倒计时"""
        self.countdown_task = self.server.scheduler.run_task(self, self.game_tick, delay=20, period=20)
        
    def game_tick(self):
        """游戏每秒执行的逻辑"""
        if not self.game_active:
            return
            
        elapsed_time = int(time.time() - self.game_start_time)
        remaining_time = self.game_time - elapsed_time
        
        # 更新BossBar
        self.update_bossbar_game(remaining_time, self.game_time)

        # 山芋爆炸
        if remaining_time <= 0:
            self.explode_potato()
            return
            
        # 倒计时提示（只在特定时间点发送一次）
        if remaining_time in [60, 30, 10, 5, 4, 3, 2, 1]:
            # 使用一个标志确保每个时间点只发送一次
            if not hasattr(self, 'last_announced_time') or self.last_announced_time != remaining_time:
                self.last_announced_time = remaining_time
                self.server.broadcast_message(f"§e距离山芋爆炸还有 §c{remaining_time} §e秒！")
            
    def explode_potato(self):
        """山芋爆炸，淘汰当前持有者"""
        if not self.game_active or not self.potato_holder:
            return
            
        # 立即重置游戏时间，防止重复触发爆炸
        self.game_start_time = time.time()

        # 淘汰持有者
        eliminated_player = self.potato_holder

        # 先播放爆炸音效和效果（在淘汰玩家之前）
        # 为所有玩家（包括被淘汰的玩家）制造爆炸效果
        all_players = self.players_in_game.copy()
        all_players.add(eliminated_player)

        # 播放爆炸音效
        self.play_explode_sound(all_players, eliminated_player)

        # 为所有玩家制造爆炸效果
        self.create_explosion_effect(all_players, eliminated_player)

        # 淘汰持有者
        self.players_in_game.discard(eliminated_player)

        # 确保被淘汰玩家在 all_players_in_game 集合中
        self.all_players_in_game.add(eliminated_player)
        
        # 更新被淘汰玩家的战绩
        self.data_manager.update_player_stats(eliminated_player.name, games=1)

        # 清空被淘汰玩家的山芋
        self.remove_potato_from_inventory(eliminated_player)


        
        # 广播淘汰信息
        self.server.broadcast_message(f"§c山芋爆炸了！§e{eliminated_player.name} §c被淘汰！")
        
        # 更新BossBar显示淘汰信息
        self.update_bossbar_eliminated(eliminated_player.name)
        
        # 检查游戏是否结束
        if len(self.players_in_game) <= 1:
            self.server.broadcast_message("§e游戏正在结束，5秒后进行传送...")
            # 清除所有玩家的山芋
            for player in self.players_in_game:
                self.remove_potato_from_inventory(player)
            # 停止game_tick任务，防止继续更新BossBar
            if self.countdown_task:
                self.countdown_task.cancel()
                self.countdown_task = None
            self.stop_game_task = self.server.scheduler.run_task(self, lambda: self.stop_game("游戏结束"), delay=100)  # 5秒后停止游戏
            return
            
        # 选择新的山芋持有者
        self.potato_holder = random.choice(list(self.players_in_game))
        
        # 给新的持有者填充山芋
        self.give_potato_to_player(self.potato_holder)
        
        self.potato_holder.send_message("§c你拿到了烫手山芋！快传给别人！")
        self.server.broadcast_message(f"§e山芋从 §f{eliminated_player.name} §e转移到了 §c{self.potato_holder.name} §e手中！")

    def transfer_potato_to(self, from_player: Player, to_player: Player):
        """将山芋从一个玩家转移到指定的玩家

        Args:
            from_player: 山芋当前持有者
            to_player: 山芋的新持有者
        """
        if not self.game_active or not self.potato_holder:
            return

        if from_player != self.potato_holder:
            return

        if to_player not in self.players_in_game:
            return

        if to_player == from_player:
            return

        self.potato_holder = to_player

        # 取消原持有者的山芋填充
        self.remove_potato_from_inventory(from_player)
        
        # 给新持有者填充山芋
        self.give_potato_to_player(to_player)

        # 发送嘲讽消息
        taunt = random.choice(TAUNT_MESSAGES)
        from_player.send_message(f"§e{taunt}")
        to_player.send_message(f"§c{from_player.name}: {taunt}")
        
        # 广播传递信息
        self.server.broadcast_message(f"§e山芋从 §f{from_player.name} §e转移到了 §c{to_player.name} §e手中！")
        plugin_print(f"山芋从 {from_player.name} 转移到了 {to_player.name} 手中！")

        # 播放传递音效
        self.play_transfer_sound(to_player)

    def give_potato_to_player(self, player: Player):
        """给玩家快捷栏填充山芋

        Args:
            player: 要填充山芋的玩家
        """
        try:
            # 获取玩家的背包
            inventory = player.inventory
            if inventory is None:
                return
                
            # 创建山芋物品堆
            from endstone.inventory import ItemStack
            potato = ItemStack(self.potato_item_id, 64)

            # 设置物品元数据
            item_meta = potato.item_meta
            if item_meta is not None:
                item_meta.display_name = "§c烫手山芋"
                potato.set_item_meta(item_meta)
            
            # 将山芋填充到整个快捷栏（强制覆盖）
            for slot in range(9):  # 快捷栏有9个槽位
                inventory.set_item(slot, potato)
        except Exception as e:
            plugin_print(f"给玩家填充山芋失败: {e}", "ERROR")

    def remove_potato_from_inventory(self, player: Player):
        """从玩家背包中移除山芋

        Args:
            player: 要移除山芋的玩家
        """
        try:
            # 获取玩家的背包
            inventory = player.inventory
            if inventory is None:
                return
                
            # 从所有槽位中移除山芋
            inventory.remove(self.potato_item_id)
        except Exception as e:
            plugin_print(f"从玩家背包移除山芋失败: {e}", "ERROR")

    def play_transfer_sound(self, player: Player):
        """播放山芋传递音效

        Args:
            player: 山芋持有者
        """
        try:
            # 为所有参与游戏的玩家播放传递音效
            for p in self.players_in_game:
                p.play_sound(
                    location=player.location,
                    sound="mob.blaze.shoot",
                    volume=1.0,
                    pitch=1.0
                )
        except Exception as e:
            plugin_print(f"播放传递音效失败: {e}", "ERROR")

    def play_explode_sound(self, players: set, location_player: Player):
        """播放山芋爆炸音效

        Args:
            players: 要播放音效的玩家集合
            location_player: 播放音效的位置所在的玩家
        """
        try:
            for p in players:
                p.play_sound(
                    location=location_player.location,
                    sound="random.explode",
                    volume=1.0,
                    pitch=1.0
                )
        except Exception as e:
            plugin_print(f"播放爆炸音效失败: {e}", "ERROR")

    def create_explosion_effect(self, players: set, location_player: Player):
        """为所有玩家制造爆炸效果

        Args:
            players: 要显示效果的玩家集合
            location_player: 爆炸效果位置所在的玩家
        """
        try:
            # 获取玩家位置
            loc = location_player.location
            if loc is None:
                plugin_print(f"玩家 {location_player.name} 的位置为空", "WARNING")
                return

            # 为所有玩家生成爆炸粒子效果
            import random
            for p in players:
                for i in range(50):
                    offset_x = random.uniform(-2.5, 2.5)
                    offset_y = random.uniform(0, 3)
                    offset_z = random.uniform(-2.5, 2.5)
                    p.spawn_particle(
                        name="minecraft:explosion_particle",
                        x=loc.x + offset_x,
                        y=loc.y + offset_y,
                        z=loc.z + offset_z
                    )
        except Exception as e:
            plugin_print(f"制造爆炸效果失败: {e}", "ERROR")

    def spawn_particle_effect(self, player: Player):
        """为山芋持有者生成粒子效果

        Args:
            player: 山芋持有者
        """
        try:
            # 获取玩家位置
            loc = player.location
            if loc is None:
                plugin_print(f"玩家 {player.name} 的位置为空", "WARNING")
                return

            # 为所有参与游戏的玩家生成火焰粒子
            for p in self.players_in_game:
                for i in range(10):
                    offset_x = random.uniform(-1, 1)
                    offset_y = random.uniform(0.5, 1)
                    offset_z = random.uniform(-1, 1)
                    p.spawn_particle(
                        name="minecraft:basic_flame_particle",
                        x=loc.x + offset_x,
                        y=loc.y + offset_y,
                        z=loc.z + offset_z
                    )
        except Exception as e:
            plugin_print(f"生成粒子效果失败: {e}", "ERROR")

    def particle_tick(self):
        """粒子效果每0.5秒执行的逻辑"""
        if not self.game_active:
            return
        if not self.potato_holder:
            return

        # 生成粒子效果
        self.spawn_particle_effect(self.potato_holder)

        # 持续给予山芋持有者山芋
        self.give_potato_to_player(self.potato_holder)

    def start_particle_task(self):
        """启动粒子效果任务"""
        # plugin_print("正在启动粒子效果任务", "INFO")
        if self.particle_task is not None:
            self.particle_task.cancel()
            plugin_print("已取消旧的粒子效果任务", "INFO")

        self.particle_task = self.server.scheduler.run_task(self, self.particle_tick, delay=0, period=10)  # 每0.5秒执行一次（10 ticks）
        # plugin_print("粒子效果任务已启动", "INFO")

    def stop_particle_task(self):
        """停止粒子效果任务"""
        # plugin_print("正在停止粒子效果任务", "INFO")
        if self.particle_task is not None:
            self.particle_task.cancel()
            self.particle_task = None
            # plugin_print("粒子效果任务已停止", "INFO")
        else:
            plugin_print("没有正在运行的粒子效果任务", "INFO")
    
    def start_position_check_task(self):
        """启动位置检查任务，检测玩家是否离开比赛区域"""
        # plugin_print("正在启动位置检查任务", "INFO")
        if self.position_check_task is not None:
            self.position_check_task.cancel()
            plugin_print("已取消旧的位置检查任务", "INFO")

        self.position_check_task = self.server.scheduler.run_task(self, self.check_player_positions, delay=20, period=20)  # 每秒检查一次（20 ticks）
        plugin_print("位置检查任务已启动", "INFO")

    def stop_position_check_task(self):
        """停止位置检查任务"""
        plugin_print("正在停止位置检查任务", "INFO")
        if self.position_check_task is not None:
            self.position_check_task.cancel()
            self.position_check_task = None
            plugin_print("位置检查任务已停止", "INFO")
        else:
            plugin_print("没有正在运行的位置检查任务", "INFO")
    
    def check_player_positions(self):
        """检查玩家位置，检测是否离开比赛区域"""
        if not self.game_active:
            return
        
        # 复制玩家列表，避免在迭代时修改
        players_copy = list(self.players_in_game)
        for player in players_copy:
            try:
                loc = player.location
                if loc is None:
                    continue
                
                # 检查玩家是否在活动范围内 (增加 2.0 的容差以防误判)
                distance_x = abs(loc.x - self.game_pos["x"])
                distance_z = abs(loc.z - self.game_pos["z"])
                
                if distance_x > (self.area_size["x"] + 2.0) or distance_z > (self.area_size["z"] + 2.0):
                    # 玩家离开比赛区域，判负
                    # 先播放爆炸音效和效果（在淘汰玩家之前）
                    all_players = self.players_in_game.copy()
                    all_players.add(player)

                    # 播放爆炸音效
                    self.play_explode_sound(all_players, player)

                    # 为所有玩家制造爆炸效果
                    self.create_explosion_effect(all_players, player)

                    # 淘汰玩家
                    self.players_in_game.discard(player)

                    # 确保被淘汰玩家在 all_players_in_game 集合中
                    self.all_players_in_game.add(player)
                    
                    # 将玩家传送到等待中心，防止留在竞技场外被反复判定
                    self.teleport_to_wait_pos(player)
                    
                    # 移除玩家的山芋
                    self.remove_potato_from_inventory(player)
                    
                    # 如果玩家持有山芋，转移山芋
                    if self.potato_holder == player:
                        if self.players_in_game:
                            self.potato_holder = random.choice(list(self.players_in_game))
                            self.give_potato_to_player(self.potato_holder)
                            self.potato_holder.send_message("§c你拿到了烫手山芋！快传给别人！")
                            self.server.broadcast_message(f"§e山芋从 §f{player.name} §e转移到了 §c{self.potato_holder.name} §e手中！")
                        else:
                            self.potato_holder = None
                    
                    # 广播淘汰信息
                    self.server.broadcast_message(f"§c{player.name} §e离开了比赛区域，被淘汰！")
                    
                    # 更新被淘汰玩家的战绩
                    self.data_manager.update_player_stats(player.name, games=1)
                    
                    # 检查游戏是否结束
                    if len(self.players_in_game) <= 1:
                        self.stop_game("游戏结束")
                        return
            except Exception as e:
                plugin_print(f"检查玩家位置失败: {e}", "ERROR")

    def join_game(self, player: Player) -> bool:
        """玩家加入游戏
        
        Args:
            player: 加入游戏的玩家
            
        Returns:
            bool: 是否成功加入
        """
        if player in self.players_in_game:
            player.send_message("§c你已经在游戏中了！")
            return False

        # 检查是否达到最大人数限制
        if self.max_players > 0 and len(self.players_in_game) >= self.max_players:
            player.send_message(f"§c游戏人数已满（{self.max_players}人）！")
            return False
            
        # 清空玩家背包
        inventory = player.inventory
        if inventory:
            inventory.clear()
        
        # 传送玩家到准备区域
        self.teleport_to_wait_pos(player)
        
        self.players_in_game.add(player)
        self.all_players_in_game.add(player)  # 添加到所有玩家集合
        player.send_message("§a你已加入烫手山芋游戏！")
        self.server.broadcast_message(f"§e{player.name} §a加入了游戏！")
        
        # 停止彩虹跑马灯
        self.stop_rainbow_marquee()

        # 更新BossBar
        self.update_bossbar_waiting()
        
        # 检查是否达到最低人数，如果是则开始游戏
        if len(self.players_in_game) >= self.min_players and not self.game_active:
            player.send_message(f"§e玩家数量已达到最低要求，留有 §f{self.wait_time} §e秒来允许剩余玩家的加入！")
            self.server.broadcast_message(f"§e玩家数量已达到最低要求，留有 §f{self.wait_time} §e秒来允许剩余玩家的加入！")
            # 启动等待倒计时BossBar
            self.start_wait_countdown_bossbar()
            # 延迟指定时间后开始预热倒计时
            self.server.scheduler.run_task(
                self,
                lambda: self.start_pre_game_countdown(),
                delay=self.wait_time * 20  # 转换为ticks（1秒=20ticks）
            )
        
        return True
        
    def leave_game(self, player: Player) -> bool:
        """玩家离开游戏
        
        Args:
            player: 离开游戏的玩家
            
        Returns:
            bool: 是否成功离开
        """
        if player not in self.players_in_game:
            player.send_message("§c你不在游戏中！")
            return False
            
        # 从游戏中移除玩家
        self.players_in_game.discard(player)
        self.all_players_in_game.discard(player)  # 从所有玩家集合中移除
        
        # 移除玩家的山芋
        self.remove_potato_from_inventory(player)
        
        # 如果玩家持有山芋，转移山芋
        if self.game_active and self.potato_holder == player:
            if self.players_in_game:
                # 随机选择新的山芋持有者
                import random
                self.potato_holder = random.choice(list(self.players_in_game))
                # 给新持有者填充山芋
                self.give_potato_to_player(self.potato_holder)
                # 通知新持有者
                self.potato_holder.send_message("§c你拿到了烫手山芋！快传给别人！")
                # 广播山芋转移信息
                self.server.broadcast_message(f"§e山芋从 §f{player.name} §e转移到了 §c{self.potato_holder.name} §e手中！")
            else:
                # 游戏结束
                self.potato_holder = None
                self.stop_game("没有玩家了")
                return True
        
        # 通知玩家和广播
        player.send_message("§a你已离开烫手山芋游戏！")
        self.server.broadcast_message(f"§e{player.name} §a离开了游戏！")
        
        # 更新BossBar
        if not self.game_active:
            self.update_bossbar_waiting()
        
        # 检查游戏是否结束
        if self.game_active and len(self.players_in_game) <= 1:
            self.stop_game("游戏结束")
            
        return True
        
    def teleport_to_wait_pos(self, player: Player):
        """传送玩家到等待中心
        
        Args:
            player: 要传送的玩家
        """
        try:
            # 获取等待中心坐标
            x, y, z = self.wait_pos['x'], self.wait_pos['y'], self.wait_pos['z']
            
            # 使用Location对象传送玩家（与start_game使用相同的方式）
            try:
                from endstone._internal.endstone_python import Location
                location = Location(dimension=player.dimension, x=x, y=y, z=z)
                player.teleport(location)
                try:
                    player.send_message(f"§e已传送到等待中心: X={x}, Y={y}, Z={z}")
                except:
                    pass  # 发送消息失败不影响传送结果
            except Exception as e1:
                plugin_print(f"传送玩家 {player.name} 失败: {e1}", "WARNING")
        except Exception as e:
            plugin_print(f"传送玩家 {player.name} 到等待中心失败: {e}", "ERROR")
    
    def teleport_to_game_pos(self, player: Player):
        """
        传送玩家到竞技中心
        
        Args:
            player: 要传送的玩家
        """
        try:
            # 获取竞技中心坐标
            x, y, z = self.game_pos['x'], self.game_pos['y'], self.game_pos['z']
            
            try:
                cmd = f"tp {player.name} {x} {y} {z}"
                result = self.server.dispatch_command(player, cmd)
                if result:
                    player.send_message(f"§e已传送到等待中心: X={x}, Y={y}, Z={z}")
                    return
                elif result == "Unknown player":
                    player.send_message("§c玩家不存在，请检查玩家名是否正确！")
                    return
            except Exception as e1:
                plugin_print(f"传送失败: {e1}", "WARNING")

        except Exception as e:
            plugin_print(f"传送玩家到竞技中心失败: {e}", "ERROR")
            player.send_message("§c传送失败，请联系管理员！")
    
    def start_pre_game_countdown(self):
        """开始赛前预热倒计时"""
        if self.pre_game_task is not None:
            return
        
        # 停止等待倒计时BossBar任务
        if self.wait_countdown_task:
            self.wait_countdown_task.cancel()
            self.wait_countdown_task = None

        self.server.broadcast_message("§6===== 赛前预热 =====")
        self.server.broadcast_message(f"§e游戏将在 §c{self.pre_time} §e秒后开始！")
        self.pre_game_timer = self.pre_time
        
        # 更新BossBar
        self.update_bossbar_countdown(self.pre_time, self.pre_time)
        
        # 预热倒计时
        def pre_game_tick():
            if not hasattr(self, 'pre_game_timer'):
                self.pre_game_timer = self.pre_time
            
            self.pre_game_timer -= 1
            
            # 更新BossBar
            self.update_bossbar_countdown(self.pre_game_timer, self.pre_time)

            if self.pre_game_timer <= 0:
                # 传送所有玩家到竞技中心
                for player in self.players_in_game:
                    self.teleport_to_game_pos(player)
                
                # 开始游戏
                self.start_game()
                self.pre_game_task.cancel()  # 停止任务
            elif self.pre_game_timer in [10, 5, 4, 3, 2, 1]:
                self.server.broadcast_message(f"§e游戏将在 §c{self.pre_game_timer} §e秒后开始！")
            
            return True  # 继续任务
        
        self.pre_game_task = self.server.scheduler.run_task(self, lambda: pre_game_tick(), delay=20, period=20)
        
    def show_easyhotpotato_help(self, sender: CommandSenderWrapper):
        """显示烫手山芋命令帮助
        
        Args:
            sender: 命令发送者
        """
        sender.send_message("§6===== EasyHotPotato 烫手山芋游戏帮助 =====")
        sender.send_message("§e/easyhotpotato §f- 打开游戏主菜单")
        sender.send_message("§e/easyhotpotato status §f- 查看游戏状态")
        sender.send_message("§e/easyhotpotato stats [玩家] §f- 查看战绩，可指定玩家名称")
        sender.send_message("§e/easyhotpotato help §f- 查看帮助")
        sender.send_message("§6===== 游戏规则 =====")
        sender.send_message("§f- 持有土豆者必须通过物理攻击来完成传递")
        sender.send_message("§f- 每一轮都有随机的倒计时，计时器归零将淘汰持有者")
        sender.send_message("§f- 离开比赛区域将立即判负")
        sender.send_message("§f- 胜场最多的玩家将登上排行榜")

    def init_default_bossbar(self):
        """初始化默认BossBar"""
        try:
            # 创建BossBar
            self.bossbar = self.server.create_boss_bar(
                title="§6欢迎使用 EasyHotPotato 烫手山芋插件！",
                color=BarColor.YELLOW,
                style=BarStyle.SOLID
            )
            # 设置进度
            self.bossbar.progress = 1.0
            # 为所有在线玩家添加BossBar
            for player in self.server.online_players:
                self.bossbar.add_player(player)
            
            # 启动彩虹循环跑马灯任务
            self.start_rainbow_marquee()
            
            plugin_print("默认BossBar已初始化", "SUCCESS")
        except Exception as e:
            plugin_print(f"初始化BossBar失败: {e}", "ERROR")

    def cleanup_bossbar(self):
        """清理BossBar"""
        try:
            # 停止彩虹跑马灯
            self.stop_rainbow_marquee()
            
            if self.bossbar_task:
                self.bossbar_task.cancel()
                self.bossbar_task = None
            
            if self.bossbar:
                self.bossbar.remove_all()
                self.bossbar = None
            plugin_print("BossBar已清理", "INFO")
        except Exception as e:
            plugin_print(f"清理BossBar失败: {e}", "ERROR")

    def update_bossbar_waiting(self):
        """更新等待阶段的BossBar"""
        try:
            if not self.bossbar:
                return
            
            current_players = len(self.players_in_game)
            needed_players = self.min_players
            
            # 更新BossBar标题
            self.bossbar.title = f"§e等待玩家中... §a{current_players}§7/§a{needed_players}"
            
            # 计算进度
            progress = min(current_players / needed_players, 1.0)
            self.bossbar.progress = progress
            
            # 为所有在线玩家添加BossBar
            for player in self.server.online_players:
                if player not in self.bossbar.players:
                    self.bossbar.add_player(player)
        except Exception as e:
            plugin_print(f"更新等待BossBar失败: {e}", "ERROR")

    def update_bossbar_countdown(self, remaining_time: int, total_time: int):
        """更新倒计时阶段的BossBar
        
        Args:
            remaining_time: 剩余时间（秒）
            total_time: 总时间（秒）
        """
        try:
            if not self.bossbar:
                return
            
            # 更新BossBar标题
            self.bossbar.title = f"§e游戏将在 §c{remaining_time} §e秒后开始！"
            
            # 计算进度
            progress = max(remaining_time / total_time, 0.0)
            self.bossbar.progress = progress
            
            # 根据剩余时间改变颜色
            if remaining_time <= 3:
                self.bossbar.color = BarColor.RED
            elif remaining_time <= 5:
                self.bossbar.color = BarColor.YELLOW
            else:
                self.bossbar.color = BarColor.GREEN
            
            # 播放经验音效，声调随时间升高
            if remaining_time <= 5:
                for player in self.players_in_game:
                    player.play_sound(player.location, SOUND_XP, volume=1.0, pitch=0.4 + (5 - remaining_time) * 0.2)
        except Exception as e:
            plugin_print(f"更新倒计时BossBar失败: {e}", "ERROR")

    def update_bossbar_game(self, remaining_time: int, total_time: int):
        """更新游戏进行中的BossBar
        
        Args:
            remaining_time: 剩余时间（秒）
            total_time: 总时间（秒）
        """
        try:
            if not self.bossbar:
                return
            
            # 获取当前持有者名称
            holder_name = self.potato_holder.name if self.potato_holder else "无"
            
            # 更新BossBar标题
            self.bossbar.title = f"§e山芋持有者: §c{holder_name} §7| §e剩余时间: §c{remaining_time}§e秒"
            
            # 计算进度
            progress = max(remaining_time / total_time, 0.0)
            self.bossbar.progress = progress
            
            # 根据剩余时间改变颜色
            if remaining_time <= 5:
                self.bossbar.color = BarColor.RED
            elif remaining_time <= 10:
                self.bossbar.color = BarColor.YELLOW
            else:
                self.bossbar.color = BarColor.GREEN
            
            # 播放经验音效，声调随时间升高
            if remaining_time <= 5:
                for player in self.players_in_game:
                    player.play_sound(player.location, SOUND_XP, volume=1.0, pitch=0.4 + (5 - remaining_time) * 0.2)
        except Exception as e:
            plugin_print(f"更新游戏BossBar失败: {e}", "ERROR")

    def update_bossbar_eliminated(self, eliminated_player_name: str):
        """更新BossBar显示淘汰信息
        
        Args:
            eliminated_player_name: 被淘汰的玩家名称
        """
        try:
            if not self.bossbar:
                return
            
            # 更新BossBar标题
            self.bossbar.title = f"§c{eliminated_player_name} §e被淘汰！"
            
            # 设置进度为满
            self.bossbar.progress = 1.0
            
            # 设置颜色为红色
            self.bossbar.color = BarColor.RED
        except Exception as e:
            plugin_print(f"更新淘汰BossBar失败: {e}", "ERROR")

    def start_wait_countdown_bossbar(self):
        """启动等待倒计时BossBar
        """
        # 停止之前的等待倒计时任务
        if hasattr(self, 'wait_countdown_task') and self.wait_countdown_task:
            self.wait_countdown_task.cancel()
        
        # 初始化剩余时间
        remaining_time = self.wait_time
        
        def update_wait_bossbar():
            nonlocal remaining_time
            if remaining_time <= 0:
                return
            
            # 更新BossBar
            self.bossbar.title = f"§e游戏将在 §c{remaining_time} §e秒后开始！"
            progress = max(remaining_time / self.wait_time, 0.0)
            self.bossbar.progress = progress
            
            # 根据剩余时间改变颜色
            if remaining_time <= 3:
                self.bossbar.color = BarColor.RED
            elif remaining_time <= 5:
                self.bossbar.color = BarColor.YELLOW
            else:
                self.bossbar.color = BarColor.GREEN
            
            remaining_time -= 1
        
        # 启动倒计时任务
        self.wait_countdown_task = self.server.scheduler.run_task(
            self,
            update_wait_bossbar,
            delay=0,
            period=20  # 每秒更新一次（20ticks）
        )

    def start_rainbow_marquee(self):
        """启动彩虹循环跑马灯效果"""
        # 初始化跑马灯状态
        self.marquee_text = "欢迎使用 EasyHotPotato 烫手山芋插件！ "
        self.marquee_position = 0
        self.rainbow_colors = [
            "§c",  # 红色
            "§6",  # 金色
            "§e",  # 黄色
            "§a",  # 绿色
            "§b",  # 青色
            "§d",  # 紫色
        ]
        self.rainbow_color_index = 0
        self.marquee_active = True
        
        # 启动跑马灯任务
        self.marquee_task = self.server.scheduler.run_task(self, self.update_rainbow_marquee, delay=1, period=5)
    
    def update_rainbow_marquee(self):
        """更新彩虹循环跑马灯效果"""
        if not self.marquee_active or not self.bossbar:
            return
        
        try:
            # 更新彩虹颜色索引
            self.rainbow_color_index = (self.rainbow_color_index + 1) % len(self.rainbow_colors)
            current_color = self.rainbow_colors[self.rainbow_color_index]
            
            # 创建跑马灯效果（滚动文字）
            text_length = len(self.marquee_text)
            # 确保位置在有效范围内
            if self.marquee_position >= text_length:
                self.marquee_position = 0
            
            # 构建显示的文本（滚动效果）
            displayed_text = self.marquee_text[self.marquee_position:] + self.marquee_text[:self.marquee_position]
            
            # 更新BossBar标题（使用当前彩虹颜色）
            self.bossbar.title = f"{current_color}{displayed_text}"
            
            # 更新BossBar颜色（循环彩虹色）
            color_map = {
                "§c": BarColor.RED,
                "§6": BarColor.YELLOW,
                "§e": BarColor.YELLOW,
                "§a": BarColor.GREEN,
                "§b": BarColor.BLUE,
                "§d": BarColor.PURPLE,
            }
            self.bossbar.color = color_map.get(current_color, BarColor.YELLOW)
            
            # 更新位置（滚动速度）
            self.marquee_position = (self.marquee_position + 1) % text_length
            
        except Exception as e:
            plugin_print(f"更新彩虹跑马灯失败: {e}", "ERROR")
    
    def stop_rainbow_marquee(self):
        """停止彩虹循环跑马灯效果"""
        self.marquee_active = False
        if self.marquee_task:
            self.marquee_task.cancel()
            self.marquee_task = None

    def show_game_history_form(self, player: Player):
        """显示战局记录表单

        Args:
            player: 玩家对象
        """
        # 获取最近的战局记录
        game_history = self.data_manager.get_game_history(limit=10)
        
        if not game_history:
            player.send_message("§c暂无战局记录！")
            return
        
        # 构建战局记录内容
        content = "§e最近的战局记录:\n\n"
        for record in game_history:
            # 格式化时间
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record["start_time"]))
            duration_minutes = record["duration"] // 60
            duration_seconds = record["duration"] % 60
            
            # 构建记录内容
            content += f"§6游戏ID: §f{record['game_id']}\n"
            content += f"§e开始时间: §f{start_time}\n"
            content += f"§e游戏时长: §f{duration_minutes}分{duration_seconds}秒\n"
            content += f"§e参与玩家: §f{len(record['players'])}人\n"
            # 显示所有参赛玩家（ID和名称）
            if record['players']:
                players_list = []
                for player_info in record['players']:
                    players_list.append(f"§f{player_info['name']}§7(ID:{player_info['id']})")
                players_str = "§7, ".join(players_list)
                content += f"§e参赛玩家: {players_str}\n"
            content += f"§e获胜者: §a{record['winner'] if record['winner'] else '无'}\n"
            content += f"§e结束原因: §f{record['reason']}\n"
            content += "§7-------------------\n\n"
        
        # 创建表单
        form = ActionForm(
            title="§6战局记录",
            content=content,
            on_close=lambda p: p.send_message("§c你关闭了战局记录")
        )
        
        form.add_button(text="§e返回主菜单", icon="textures/ui/arrow_left", on_click=lambda p: self.show_main_menu(p))
        player.send_form(form)
