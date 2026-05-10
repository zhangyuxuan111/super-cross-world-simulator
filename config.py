import os
import sys

if getattr(sys, 'frozen', False):
    _ROOT = sys._MEIPASS
else:
    _ROOT = os.path.dirname(os.path.abspath(__file__))

# ==================== DeepSeek API 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-e7d70e198163494aa088705653de7194")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

MODEL_REASONER = "deepseek-v4-pro"
MODEL_CHAT = "deepseek-v4-flash"

# ==================== 模型用途分配 ====================
MODEL_WORLD_GEN = MODEL_REASONER       # 世界观生成（需要深度推理）
MODEL_PLOT = MODEL_REASONER            # 情节推进（需要深度推理）
MODEL_NARRATOR = MODEL_CHAT            # 旁白叙述
MODEL_CHARACTER = MODEL_CHAT           # 角色对话
MODEL_SCENE_DIRECTOR = MODEL_REASONER  # 场景导演（决定谁说话）
MODEL_USER_CHAR_GEN = MODEL_CHAT       # 用户角色生成

# ==================== 生成参数 ====================
TEMPERATURE_CREATIVE = 0.95    # 世界观/角色生成
TEMPERATURE_NARRATIVE = 0.85   # 旁白/情节
TEMPERATURE_DIALOGUE = 0.8     # 角色对话
TEMPERATURE_DIRECTOR = 0.3     # 场景导演（低温度保证稳定）

MAX_TOKENS_WORLD = 4096
MAX_TOKENS_PLOT = 4096
MAX_TOKENS_DIALOGUE = 2048
MAX_TOKENS_NARRATOR = 2048
MAX_TOKENS_DIRECTOR = 1024

# ==================== 数据库配置（使用SQLite便于部署） ====================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///world_simulator.db")

# ==================== 世界生成配置 ====================
DEFAULT_NPC_COUNT_MIN = 3
DEFAULT_NPC_COUNT_MAX = 6
WORLD_GEN_THEME_POOL = [
    "正常修仙",
    "正常科幻",
    "正常都市",
    "正常魔法",
    "赛博朋克修仙",
    "末日废土",
    "克苏鲁童话",
    "蒸汽朋克武侠",
    "现代都市异能",
    "星际殖民废土",
    "魔法学院体制",
    "深海文明",
    "时间囚笼世界",
    "梦境共享社会",
    "植物文明",
    "反穿越共存世界",
    "AI治理乌托邦",
    "地底世界",
    "平行宇宙交汇点",
    "修仙产业化世界",
    "丧尸农耕末世",
    "地府行政体系",
    "妖怪都市共存",
    "神话基因觉醒",
    "没落龙族世界",
    "星际虫族文明",
    "机械天使纪元",
    "魔法少女",
    "梦境商业社会",
    "虚拟网游世界",
    "沙漠玻璃文明",
    "核冬童话幸存",
    "星际海盗文化",
    "偶像成神体系",
    "巨龙财阀世界",
    "巫术直播文化",
    "血族世界",
    "量子占卜社会",
    "轨道都市",
    "数字冥府",
    "灵魂资产社会",
    "海洋游牧冰川",
    "霓虹修真界",
    "科技登神",
    "末世物流世界",
    "灵能工业时代",
    "魔兽契约文明",
    "地脉共鸣都市",
    "记忆商品化世界",
    "精灵科技垄断",
    "平行自我战争",
    "废土美食世界",
    "时间移民社会",
    "咒术编程文明",
    "冥界民政体系",
    "修仙基层生态",
    "魔法辐射废土",
    "地下城地产世界",
    "神话军工世界",
    "寄生植物共生体",
    "机甲佣兵社会",
    "末日知识保存",
    "星际农耕文明",
    "穿越管制世界",
    "梦境执法世界",
    "元素创世神话",
    "恐惧情绪能源",
    "机械虫群生态",
    "死星拾荒世界",
    "液态金属社会",
    "咒具商业化",
    "战后妖族融合",
    "鲸骨云端城市",
    "轮回枢纽世界",
    "蜂群意识社会",
    "虚拟偶像自治",
    "灵魂货币经济",
    "诡秘公共交通",
    "机械飞升禅修",
    "亡灵建设者",
    "念力工程文明",
    "永生者社区",
    "算法神谕社会",
    "虫洞经济",
    "灵体能源社会",
    "龙息料理界",
    "修仙科举世界",
    "末日娱乐社会",
    "变异宠物文明",
    "现代符咒修炼",
    "意识备份社会",
    "无魔科技世界",
    "深海龙族遗存",
    "废土通讯网络",
    "星际宗教联盟",
    "机械佛法世界",
    "基因神话世界",
    "冥界邮递网络",
    "位面关卡世界",
    "灵异保险体系",
    "魔法专利经济",
    "城市根系巨兽",
    "时间线回收社会",
    "毒雾都市文化",
    "尸解仙宇宙",
    "云海浮岛游牧",
    "科技修真界",
    "佣兵退休社会",
    "梦境建造世界",
    "机甲农耕文明",
    "古神碎片能源",
    "元素仆役文明",
    "地心锻造文明",
    "冰期温泉庇护",
    "修仙保险业",
    "星际鬼市",
    "重力紊乱星球",
    "魔法粒子科学",
    "灵气复苏民生",
    "妖族互联网",
    "机械神遗民",
    "符文农耕世界",
    "星际追猎者社会",
    "魔法乐园经济",
    "龙裔教育体系",
    "时停服务业",
    "末日食品生产",
    "芯片灵魂世界",
    "道术自动化物流",
    "哥布林金融世界",
    "仙侠维和",
    "异界语言统一",
    "魔导载具竞速",
    "古墓探险业",
    "宇宙道教",
    "地狱观光业",
    "龙族繁育产业",
    "超能幼教社会",
    "灵异房产市场",
    "神明通讯时代",
    "妖怪心灵产业",
    "星舰自循环生态",
    "虚拟修真界",
    "符文机甲战斗艺术",
    "异星植物文明",
    "星际物种伦理",
    "诅咒经济",
    "巫毒工艺世界",
    "念力家政业",
    "魔法物流系统",
    "修仙学术界",
    "妖精重工",
    "异能对抗体制",
    "魔法轨道交通网",
    "亡灵丧葬文化",
    "方舟漂流文明",
    "神血经济",
    "时间维修业",
    "异能应急体系",
    "魔素能量世界",
    "仙容保养",
    "魔法饕客世界",
    "机神演艺圈",
    "水源末世",
    "化形者秩序",
    "云端灵兽牧场",
    "神器典当业",
    "符阵气候调节",
    "妖界生态管理",
    "位面商路",
    "觉醒者学园",
    "龙语传媒",
    "星际钓客",
    "灵魂实体化制造",
    "幽灵房产市场",
    "古神精神治疗",
    "剑仙配送网",
    "魔法衣料文明",
    "异界信息网",
    "太空墓场",
    "异能害物控制",
    "虚拟神国社交",
    "星际欢场",
    "气血武道社会",
    "妖鬼姻缘世界",
    "神兽驯养世界",
    "机神博彩",
    "修仙财税体系",
    "废土公路武士",
    "灵能电网社会",
    "神明偶像生态",
    "地精工程文明",
    "法术知识产权争斗",
    "废土实况世界",
    "神话竞速产业",
    "水晶球通讯时代",
    "魔法灾害防治",
    "龙鳞防护产业",
    "时间信件网络"
]

# ==================== 主角属性系统 ====================
USER_STATS_TEMPLATE = {
    "hp": 100,
    "max_hp": 100,
    "strength": 10,
    "intelligence": 10,
    "charisma": 10,
    "agility": 10,
    "luck": 5,
    "sanity": 100,
    "inventory": [],
    "skills": [],
    "status_effects": []
}

# ==================== 天赋池 ====================
TALENT_POOL = [
    {"name": "创造神之力", "desc": "可以无视系统审查3次，强行改变剧情走向", "type": "divine", "effects": {"divine_interventions": 3}},
    {"name": "人间人憎", "desc": "不知道为什么，别人第一眼就会厌恶你", "type": "curse", "effects": {"charisma": -5, "npc_default_attitude": "hostile"}},
    {"name": "神秘戒指", "desc": "穿越一年内不会死亡，伤害最多将你打至濒死", "type": "artifact", "effects": {"death_immune_months": 12}},
    {"name": "武圣之姿", "desc": "练武天赋极高，学习任何武技的速度是常人的三倍", "type": "combat", "effects": {"strength": 5, "agility": 3, "combat_learning_rate": 3.0}},
    {"name": "三灵根", "desc": "拥有金木火三灵根的修仙天赋，可修炼三系功法", "type": "cultivation", "effects": {"cultivation_talent": "三灵根", "spiritual_power": 5}},
    {"name": "丑陋", "desc": "你的相貌极其丑陋，NPC对你的态度会受影响", "type": "curse", "effects": {"charisma": -4, "appearance_impact": "ugly"}},
    {"name": "天灵根", "desc": "万中无一的天灵根，修炼速度极快但容易招致嫉妒", "type": "cultivation", "effects": {"cultivation_talent": "天灵根", "spiritual_power": 10, "jealousy_risk": "high"}},
    {"name": "富可敌国", "desc": "开局携带大量财富，在任何世界都不愁吃穿", "type": "wealth", "effects": {"gold": 100000, "charisma": 1}},
    {"name": "不死小强", "desc": "生命力极其顽强，受伤后恢复速度翻倍", "type": "survival", "effects": {"hp_regen_rate": 2.0, "max_hp": 20}},
    {"name": "魅惑之眼", "desc": "你的眼神有轻微魅惑效果，谈判时更容易说服对方", "type": "social", "effects": {"charisma": 4, "persuasion_bonus": "high"}},
    {"name": "过目不忘", "desc": "你能记住所有看到和听到的细节，在推理和信息搜集中有巨大优势", "type": "mental", "effects": {"intelligence": 4, "memory_perfect": True}},
    {"name": "野兽直觉", "desc": "你能感知到附近的危险，在战斗中获得先手优势", "type": "instinct", "effects": {"danger_sense": True, "combat_initiative": 3}},
    {"name": "锻造大师", "desc": "你精通各种武器和装备的锻造，可以自己制造和强化装备", "type": "crafting", "effects": {"crafting_talent": "weaponsmith", "strength": 2}},
    {"name": "神医再世", "desc": "你拥有高超的医术，能治疗大多数伤病", "type": "healing", "effects": {"healing_skill": "master", "intelligence": 2}},
    {"name": "毒师体质", "desc": "你对大多数毒素免疫，且善于制毒和用毒", "type": "survival", "effects": {"poison_immune": True, "poison_crafting": "expert"}},
    {"name": "影之步", "desc": "你的脚步无声无息，潜行和偷窃几乎不会被发现", "type": "stealth", "effects": {"stealth_mastery": "high", "agility": 3}},
    {"name": "符箓天才", "desc": "你在符箓绘制上有惊人天赋，画符成功率极高", "type": "cultivation", "effects": {"talisman_mastery": "genius", "spiritual_power": 3}},
    {"name": "语言通晓", "desc": "你能快速学会任何语言，与任何智慧生物无障碍交流", "type": "mental", "effects": {"language_mastery": True, "intelligence": 2}},
    {"name": "铁胃", "desc": "你能消化任何有机物，在任何环境中都能找到食物", "type": "survival", "effects": {"survival_bonus": "high", "food_immune": True}},
    {"name": "天生领袖", "desc": "你天生具有领袖气质，更容易招募追随者", "type": "social", "effects": {"charisma": 3, "leadership_bonus": True}},
    {"name": "赌徒直觉", "desc": "你在赌博和概率性事件中有莫名的好运", "type": "luck", "effects": {"luck": 5, "gambling_bonus": True}},
    {"name": "铁匠之躯", "desc": "你的身体如同钢铁，皮肉极为坚韧", "type": "combat", "effects": {"defense": 5, "max_hp": 15}},
    {"name": "风水大师", "desc": "你懂得风水术数，能识破阵法机关和地脉走向", "type": "mystical", "effects": {"fengshui_mastery": True, "intelligence": 2}},
    {"name": "剑心通明", "desc": "你对剑道的领悟远超常人，剑术境界一日千里", "type": "combat", "effects": {"sword_mastery": "genius", "strength": 3, "agility": 3}},
    {"name": "鬼语者", "desc": "你能看见并沟通亡灵，死者会向你透露秘密", "type": "mystical", "effects": {"spirit_sight": True, "sanity": -5}},
    {"name": "命运之骰", "desc": "每天一次，你可以重掷一次对你产生负面影响的概率事件", "type": "luck", "effects": {"luck_reroll_daily": 1, "luck": 3}},
    {"name": "血怒", "desc": "受伤越重战斗力越强，最多提升50%", "type": "combat", "effects": {"berserker_rage": True, "max_hp": 10}},
    {"name": "天眼通", "desc": "你能看到远方的景象和常人看不见的东西", "type": "mystical", "effects": {"clairvoyance": True, "sanity": -3}},
    {"name": "龙族血统", "desc": "你体内流淌着稀薄的龙族血脉，身体素质超越凡人", "type": "bloodline", "effects": {"strength": 4, "max_hp": 25, "dragon_blood": True}},
    {"name": "精灵血脉", "desc": "你拥有一丝精灵血统，感知敏锐且寿命极长", "type": "bloodline", "effects": {"agility": 4, "intelligence": 2, "elf_blood": True}},
    {"name": "机械之心", "desc": "你能理解并操控任何机械设备，在科技世界如鱼得水", "type": "tech", "effects": {"tech_mastery": "genius", "intelligence": 3}},
    {"name": "契约使", "desc": "你能与灵兽缔结契约，最多可同时拥有三只契约兽", "type": "mystical", "effects": {"beast_taming": "master", "max_contracts": 3}},
    {"name": "梦行者", "desc": "你能进入他人的梦境，窥探秘密或传递信息", "type": "mystical", "effects": {"dream_walking": True, "sanity": -2}},
    {"name": "时间感知", "desc": "你能模糊感知未来3秒内发生的危险，获得额外的反应时间", "type": "instinct", "effects": {"precognition_3s": True, "agility": 2}},
    {"name": "金刚不坏", "desc": "你的身体可以短暂进入金刚不坏状态，刀枪不入", "type": "combat", "effects": {"invulnerability_skill": True, "defense": 8}},
    {"name": "幻术精通", "desc": "你擅长制造幻觉，可以迷惑敌人的感官", "type": "mystical", "effects": {"illusion_mastery": "high", "intelligence": 2}},
    {"name": "气运之子", "desc": "你的运气好得不像话，遇到机缘的概率大幅增加", "type": "luck", "effects": {"luck": 8, "encounter_rate_boost": True}},
    {"name": "不死鸟之羽", "desc": "你拥有一根不死鸟的羽毛，死亡时可以复活一次", "type": "artifact", "effects": {"auto_revive": 1}},
    {"name": "空间感知", "desc": "你能感知周围空间的细微变化，发现隐藏的通道和密室", "type": "instinct", "effects": {"spatial_awareness": True, "intelligence": 2}},
    {"name": "药王体", "desc": "你的身体是天然的药引，百毒不侵且炼丹成功率极高", "type": "cultivation", "effects": {"alchemy_mastery": "genius", "poison_immune": True}},
    {"name": "雷灵体", "desc": "天生雷属性灵体，修炼雷系功法事半功倍", "type": "cultivation", "effects": {"lightning_body": True, "spiritual_power": 4}},
    {"name": "火灵体", "desc": "天生火属性灵体，对火焰有极高的亲和力", "type": "cultivation", "effects": {"fire_body": True, "fire_immune": True, "spiritual_power": 4}},
    {"name": "冰肌玉骨", "desc": "体表温润如玉，不畏寒暑，冰系功法修炼速度翻倍", "type": "cultivation", "effects": {"ice_body": True, "cold_immune": True, "charisma": 2}},
    {"name": "阵法师", "desc": "你在阵法布置上有极高的天赋，能迅速破解或布置各类阵法", "type": "mystical", "effects": {"array_mastery": "expert", "intelligence": 3}},
    {"name": "厨神转世", "desc": "你的厨艺出神入化，做出的食物有微弱的增益效果", "type": "crafting", "effects": {"cooking_mastery": "divine", "food_buff": True}},
    {"name": "酒神", "desc": "你千杯不醉，且酿的酒有特殊效果，在酒馆中消息灵通", "type": "social", "effects": {"alcohol_immune": True, "brewing_mastery": True, "charisma": 1}},
    {"name": "弑神者之印", "desc": "你身上带有弑神者留下的印记，对神性生物有额外伤害", "type": "divine", "effects": {"god_slayer": True, "strength": 2}},
    {"name": "悲天悯人", "desc": "你的善良能感化他人，NPC更容易对你产生信任", "type": "social", "effects": {"charisma": 3, "npc_trust_boost": True}},
    {"name": "冷血", "desc": "你对杀戮没有心理负担，但NPC会感受到你的冷酷", "type": "personality", "effects": {"intimidation_bonus": True, "charisma": -2, "combat_efficiency": 1.2}},
    {"name": "乞丐王", "desc": "你在地下世界有广泛的人脉，消息极为灵通", "type": "social", "effects": {"underworld_connections": True, "intelligence": 1}},
    {"name": "天纵奇才", "desc": "你学习任何技能的速度都比常人快50%", "type": "mental", "effects": {"learning_rate": 1.5, "intelligence": 3}},
    {"name": "傀儡师", "desc": "你擅长制作和操控傀儡，最多同时操控三个", "type": "crafting", "effects": {"puppet_mastery": "expert", "max_puppets": 3}},
    {"name": "驭兽者", "desc": "你对动物有天然的亲和力，能驯服大多数野兽", "type": "social", "effects": {"animal_affinity": True, "beast_taming": "high"}},
    {"name": "虚空行者", "desc": "你可以在虚空中短距离闪现，逃脱大多数围困", "type": "mystical", "effects": {"blink_skill": True, "escape_bonus": "high"}},
    {"name": "尸语者", "desc": "你能与尸体短暂沟通，获得死者生前的最后记忆碎片", "type": "mystical", "effects": {"corpse_speak": True, "sanity": -3}},
    {"name": "炼金术士", "desc": "你精通炼金术，能将普通材料转化为珍贵物品", "type": "crafting", "effects": {"alchemy_mastery": "expert", "intelligence": 2}},
    {"name": "灵媒", "desc": "你是天生的灵媒，能感知到周围的超自然存在", "type": "mystical", "effects": {"medium_sense": True, "sanity": -2}},
    {"name": "界外之人", "desc": "你不属于任何世界，世界法则对你的约束较弱", "type": "divine", "effects": {"world_law_resistance": "partial", "luck": 2}},
    {"name": "绝世神偷", "desc": "你的偷窃技巧出神入化，几乎能偷到任何东西", "type": "stealth", "effects": {"steal_mastery": "divine", "agility": 4}},
    {"name": "战神后裔", "desc": "你继承了战神的血脉，在战斗中越战越勇", "type": "bloodline", "effects": {"war_blood": True, "strength": 5, "combat_stamina": "high"}},
    {"name": "元素亲和", "desc": "你对所有元素都有基本的亲和力，可以使用初级元素魔法", "type": "magic", "effects": {"elemental_affinity": "all", "spiritual_power": 3}},
    {"name": "暗影之子", "desc": "你在黑暗中如同回家，夜晚战斗力大幅提升", "type": "combat", "effects": {"night_combat_boost": True, "dark_vision": True}},
    {"name": "圣光眷顾", "desc": "你受到圣光的祝福，对黑暗生物有额外伤害且能释放治疗之光", "type": "divine", "effects": {"holy_power": True, "healing_skill": "basic"}},
    {"name": "百变面容", "desc": "你能微调自己的面容和身形，变装潜入任何地方", "type": "stealth", "effects": {"disguise_mastery": "high", "charisma": 1}},
    {"name": "武器大师", "desc": "你能熟练使用几乎所有类型的武器", "type": "combat", "effects": {"weapon_mastery": "all", "strength": 3}},
    {"name": "弓神之眼", "desc": "你的视力极佳，远程攻击命中率极高", "type": "combat", "effects": {"ranged_accuracy": "divine", "agility": 3}},
    {"name": "拳王", "desc": "你的徒手格斗能力登峰造极，拳头就是最好的武器", "type": "combat", "effects": {"unarmed_mastery": "divine", "strength": 4}},
    {"name": "天降横财", "desc": "开局随机获得一件珍贵宝物", "type": "wealth", "effects": {"random_artifact": 1, "luck": 1}},
    {"name": "吟游诗人", "desc": "你的歌声和故事能影响人心，在酒馆中白吃白喝", "type": "social", "effects": {"bard_skill": True, "charisma": 3}},
    {"name": "狼人血统", "desc": "你拥有狼人血统，在月圆之夜力量暴涨但理智下降", "type": "bloodline", "effects": {"werewolf_blood": True, "strength": 3, "sanity": -3}},
    {"name": "吸血鬼之触", "desc": "你能通过吸血恢复生命，但对阳光敏感", "type": "bloodline", "effects": {"vampire_touch": True, "sunlight_weakness": True, "hp_drain": True}},
    {"name": "天算", "desc": "你的心算能力超群，能瞬间计算出最优策略", "type": "mental", "effects": {"tactical_genius": True, "intelligence": 5}},
    {"name": "命运之眼", "desc": "你偶尔能看到命运的红线，预知重要事件的走向", "type": "mystical", "effects": {"fate_sight": True, "sanity": -4, "luck": 2}},
    {"name": "蠱术精通", "desc": "你精通蛊术，可以培养和使用蛊虫", "type": "mystical", "effects": {"gu_mastery": "expert", "poison_crafting": "high"}},
    {"name": "道心坚定", "desc": "你的道心坚如磐石，不受心魔和外物诱惑影响", "type": "cultivation", "effects": {"mind_resistance": "high", "sanity": 10}},
    {"name": "天生神力", "desc": "你天生力大无穷，力量远超常人", "type": "combat", "effects": {"strength": 6}},
    {"name": "仙人体", "desc": "你拥有传说中的仙人体质，灵气亲和度拉满", "type": "cultivation", "effects": {"immortal_body": True, "spiritual_power": 8, "cultivation_speed": 2.0}},
    {"name": "魔瞳", "desc": "你的眼睛中寄宿着魔性力量，能看到灵魂并施加威压", "type": "mystical", "effects": {"demon_eye": True, "intimidation_bonus": True, "sanity": -3}},
    {"name": "风行者", "desc": "你脚下的风会助你奔跑，速度是常人的两倍", "type": "magic", "effects": {"wind_step": True, "agility": 5}},
    {"name": "佛缘", "desc": "你与佛有缘，佛法领悟速度极快且冥冥中有佛力护体", "type": "divine", "effects": {"buddha_blessing": True, "sanity": 10, "defense": 2}},
    {"name": "妖狐血脉", "desc": "你体内有九尾狐的血脉，魅力和幻术天赋极高", "type": "bloodline", "effects": {"fox_blood": True, "charisma": 5, "illusion_mastery": "high"}},
    {"name": "石魔之躯", "desc": "受伤后伤口会石质化愈合，防御力极高但敏捷降低", "type": "bloodline", "effects": {"stone_body": True, "defense": 8, "agility": -3}},
    {"name": "读心术", "desc": "你能模糊感知到周围人对你的态度和简单想法", "type": "mental", "effects": {"mind_reading": "basic", "intelligence": 3}},
    {"name": "回春术", "desc": "你天生就会基础的治愈法术，能加速伤口愈合", "type": "healing", "effects": {"regeneration_skill": True, "healing_skill": "basic"}},
    {"name": "堕落天使", "desc": "你曾是天使但已堕落，在光明与黑暗之间游走", "type": "bloodline", "effects": {"fallen_angel": True, "charisma": 3, "dual_nature": True}},
    {"name": "饕餮之胃", "desc": "你的胃连接着异次元，可以吞食任何东西并化为能量", "type": "divine", "effects": {"devour_skill": True, "max_hp": 15}},
    {"name": "双魂", "desc": "你体内住着两个灵魂，可以切换人格获得不同能力", "type": "mystical", "effects": {"dual_soul": True, "sanity": -5, "versatility_boost": True}},
    {"name": "天灾之子", "desc": "你是不祥的预兆，所到之处灾难发生的概率提高", "type": "curse", "effects": {"disaster_magnet": True, "luck": -3, "event_rate_boost": True}},
    {"name": "命犯桃花", "desc": "异性对你格外有好感，但也容易引发感情纠葛", "type": "social", "effects": {"romance_boost": True, "charisma": 3, "jealousy_events": True}},
    {"name": "诅咒之血", "desc": "你的血脉中有古老的诅咒，每当你濒死时会爆发出恐怖之力", "type": "curse", "effects": {"curse_blood": True, "near_death_boost": "massive", "luck": -3}},
    {"name": "乞丐体", "desc": "你天生一副乞丐相，但隐藏身份时极为方便", "type": "curse", "effects": {"charisma": -3, "disguise_bonus": True}},
    {"name": "扫把星", "desc": "总是给周围人带来霉运，但你自己反而没事", "type": "curse", "effects": {"misfortune_aura": True, "luck": 2, "ally_luck": -3}},
    {"name": "天谴者", "desc": "你被天道所不容，修炼时会招来雷劫，但度过则实力暴涨", "type": "curse", "effects": {"heavenly_tribulation": True, "cultivation_risk": "high", "reward_multiplier": 2.0}},
    {"name": "哑巴", "desc": "你不能说话，但可以通过手语或写字交流", "type": "curse", "effects": {"mute": True, "charisma": -2, "intelligence": 2}},
    {"name": "文曲星降世", "desc": "你的才学惊人，科考和文书工作无往不利", "type": "mental", "effects": {"literary_genius": True, "intelligence": 5}},
    {"name": "武曲星降世", "desc": "你是武曲星下凡，兵法和武艺天赋极高", "type": "combat", "effects": {"martial_genius": True, "strength": 4, "intelligence": 2}},
    {"name": "御兽仙体", "desc": "你天生就能与妖兽沟通，妖兽对你天然亲近", "type": "cultivation", "effects": {"beast_whisperer": True, "spiritual_power": 2}},
    {"name": "煞星转世", "desc": "你身上带着浓重的煞气，战斗时敌人会心生畏惧", "type": "combat", "effects": {"killing_intent_aura": True, "intimidation_bonus": True, "strength": 3}},
    {"name": "避水珠", "desc": "你拥有一颗避水珠，在水中如履平地", "type": "artifact", "effects": {"water_walking": True, "underwater_breathing": True}},
    {"name": "凤凰涅槃", "desc": "死亡后可以化为凤凰蛋，三天后重生但会失去部分记忆", "type": "bloodline", "effects": {"phoenix_rebirth": True, "rebirth_memory_loss": True}},
    {"name": "寻宝鼠", "desc": "你天生对宝物有感应，能察觉到附近隐藏的珍贵物品", "type": "instinct", "effects": {"treasure_sense": True, "luck": 3}},
    {"name": "先知", "desc": "你偶尔会看到未来的片段，但片段往往模糊不清", "type": "mystical", "effects": {"prophecy_vision": True, "sanity": -4}},
    {"name": "祸水红颜", "desc": "你的美貌足以倾国倾城，但也因此招来无尽麻烦", "type": "social", "effects": {"charisma": 6, "trouble_magnet": True}},
    {"name": "不死之身", "desc": "你无法被常规方式杀死，但每次复活都会消耗大量生命力", "type": "divine", "effects": {"immortal": True, "revival_cost_high": True}},
    {"name": "邪神眷属", "desc": "一位古老邪神注视着你，偶尔会赐予你力量或降下试炼", "type": "divine", "effects": {"elder_god_patron": True, "sanity": -8, "random_blessing": True}},
    {"name": "棋手", "desc": "你擅长布局和谋划，能看出各种阴谋和陷阱", "type": "mental", "effects": {"strategist_mind": True, "intelligence": 4}},
    {"name": "杀破狼", "desc": "你命格杀破狼，注定一生波澜壮阔，动荡不安", "type": "destiny", "effects": {"turbulent_life": True, "luck": -2, "event_rate_boost": True, "strength": 2}},
    {"name": "紫微星", "desc": "你命格紫微星，天生有帝王之气，容易获得追随者", "type": "destiny", "effects": {"emperor_star": True, "charisma": 4, "leadership_bonus": True}},
    {"name": "七杀星", "desc": "你命格七杀星，一生多征战冲突，战力惊人但孤寡", "type": "destiny", "effects": {"war_star": True, "strength": 5, "charisma": -3}},
    {"name": "贪狼星", "desc": "你命格贪狼星，一生桃花不断且社交手腕极强", "type": "destiny", "effects": {"desire_star": True, "charisma": 5, "romance_boost": True}},
    {"name": "破军星", "desc": "你命格破军星，以破坏求新生，在困境中格外强大", "type": "destiny", "effects": {"destruction_star": True, "resilience_boost": "high", "strength": 3}},
    {"name": "天机星", "desc": "你命格天机星，智慧超群且能看透天机", "type": "destiny", "effects": {"wisdom_star": True, "intelligence": 5, "sanity": -2}},
    {"name": "太阴星", "desc": "你命格太阴星，阴柔之力掌控者，适合修炼阴属性功法", "type": "destiny", "effects": {"yin_star": True, "spiritual_power": 4, "stealth_mastery": "high"}},
    {"name": "太阳星", "desc": "你命格太阳星，阳刚之气充盈，适合修炼阳属性功法", "type": "destiny", "effects": {"yang_star": True, "spiritual_power": 4, "charisma": 2}},
    {"name": "通灵玉", "desc": "你拥有一块通灵宝玉，可以储存灵气并在需要时释放", "type": "artifact", "effects": {"spirit_jade": True, "spiritual_power": 3}},
    {"name": "混沌根骨", "desc": "你的根骨混沌不分，理论上可以兼容任何功法", "type": "cultivation", "effects": {"chaos_root": True, "cultivation_flexibility": "infinite"}},
    {"name": "霉运当头", "desc": "你天生带霉运，坏事总落在你头上，但你因此更抗揍", "type": "curse", "effects": {"bad_luck_magnet": True, "luck": -5, "defense": 3}},
    {"name": "五行灵根", "desc": "你拥有全部五行灵根，虽然每种都不算突出但全面", "type": "cultivation", "effects": {"five_elements_root": True, "spiritual_power": 2, "versatility_boost": True}},
    {"name": "无垢之体", "desc": "你的身体纯净无垢，修炼没有任何瓶颈", "type": "cultivation", "effects": {"pure_body": True, "cultivation_no_bottleneck": True, "spiritual_power": 5}},
    {"name": "兽语者", "desc": "你能听懂所有动物的语言，它们是你最好的情报网", "type": "instinct", "effects": {"animal_speech": True, "intelligence": 1}},
    {"name": "魔武双修", "desc": "你既能修炼魔法又能修炼武技，两者互不冲突", "type": "combat", "effects": {"dual_path": True, "strength": 2, "spiritual_power": 2}},
    {"name": "占星师", "desc": "你精通占星术，能通过星象预知吉凶", "type": "mystical", "effects": {"astrology_mastery": True, "intelligence": 2, "luck": 1}},
    {"name": "傀儡替身", "desc": "你有一个可以替死的傀儡，能替你承受一次致命伤害", "type": "artifact", "effects": {"death_substitute": 1}},
    {"name": "狂战士", "desc": "你在狂暴状态下战力翻倍但会失去理智", "type": "combat", "effects": {"berserk_mode": True, "strength": 4, "sanity": -3}},
    {"name": "医术圣手", "desc": "你的医术登峰造极，几乎能让死人复活", "type": "healing", "effects": {"healing_skill": "divine", "intelligence": 3}},
    {"name": "赌神附体", "desc": "你在任何赌博游戏中几乎不会输", "type": "luck", "effects": {"gambling_mastery": "divine", "luck": 6}},
    {"name": "伪装大师", "desc": "你是变装和伪装的高手，可以完美模仿他人", "type": "stealth", "effects": {"disguise_mastery": "divine", "acting_skill": True}},
    {"name": "灵巧双手", "desc": "你的双手灵巧无比，开锁、偷窃和精细操作都得心应手", "type": "stealth", "effects": {"nimble_fingers": True, "agility": 3}},
    {"name": "威压", "desc": "你能释放强大的威压，令弱者不战而退", "type": "combat", "effects": {"intimidation_aura": True, "strength": 2}},
    {"name": "铁齿铜牙", "desc": "你的口才极佳，能说会道，谈判中几乎无往不利", "type": "social", "effects": {"silver_tongue": True, "charisma": 4}},
    {"name": "御剑术", "desc": "你天生就会御剑飞行，移动速度极快", "type": "cultivation", "effects": {"sword_flight": True, "agility": 4}},
    {"name": "绝对防御", "desc": "你可以消耗大量灵力在短时间内形成无敌护盾", "type": "combat", "effects": {"absolute_shield": True, "defense": 4}},
    {"name": "虚空储物", "desc": "你拥有一个小型储物空间，可以存放物品", "type": "mystical", "effects": {"pocket_dimension": True, "inventory_slots": 20}},
    {"name": "毒抗满级", "desc": "你对所有毒素完全免疫", "type": "survival", "effects": {"poison_immune": True, "max_hp": 5}},
    {"name": "鹰眼", "desc": "你的视力是常人的五倍，能看清极远处的细节", "type": "instinct", "effects": {"eagle_eye": True, "ranged_accuracy": "high"}},
    {"name": "谈判专家", "desc": "你在任何谈判中都能占据上风", "type": "social", "effects": {"negotiation_mastery": "high", "charisma": 3}},
    {"name": "雷达感知", "desc": "你像雷达一样能感知周围50米内的所有活物", "type": "instinct", "effects": {"radar_sense": True, "intelligence": 1}},
    {"name": "神速", "desc": "你的速度快到残影，短距离冲刺几乎瞬移", "type": "combat", "effects": {"super_speed": True, "agility": 6}},
    {"name": "六道轮回眼", "desc": "你的一只眼睛能看穿生死轮回，洞察因果", "type": "mystical", "effects": {"samsara_eye": True, "sanity": -5, "intelligence": 3}},
    {"name": "天帝血脉", "desc": "传说你体内有天帝的血脉，虽然稀薄但潜力无限", "type": "bloodline", "effects": {"celestial_emperor_blood": True, "all_stats_boost": "slight", "potential": "infinite"}},
    {"name": "因果律抗性", "desc": "你部分免疫因果律的攻击和预言，未来难以被算定", "type": "divine", "effects": {"causality_resistance": "partial", "luck": 3}},
    {"name": "灵泉空间", "desc": "你体内有一个灵泉空间，可以主动修炼扩大修为", "type": "cultivation", "effects": {"inner_world": True, "spiritual_power": 5, "cultivation_speed": 1.5}},
    {"name": "天罚者", "desc": "你手中能凝聚天罚之雷，对邪恶之物有额外伤害", "type": "divine", "effects": {"divine_punishment": True, "holy_power": True, "spiritual_power": 3}},
    {"name": "无面者", "desc": "你没有固定的面孔，每次入睡后相貌都会随机改变", "type": "curse", "effects": {"faceless": True, "charisma": -2, "identity_fluid": True}},
    {"name": "稻草人", "desc": "你有一个替身稻草人，可以将伤害转移到它身上", "type": "artifact", "effects": {"voodoo_doll": True, "damage_transfer": True}},
    {"name": "阴阳眼", "desc": "你天生就能看到鬼魂和灵体", "type": "mystical", "effects": {"yin_yang_eye": True, "spirit_sight": True, "sanity": -2}},
    {"name": "元素免疫", "desc": "你对某一随机元素完全免疫（火焰/冰霜/雷电等）", "type": "magic", "effects": {"random_element_immune": True}},
    {"name": "生锈的钥匙", "desc": "你有一把能打开任何锁的生锈钥匙，但每次使用后会变得更锈", "type": "artifact", "effects": {"skeleton_key": True, "key_durability": 10}},
    {"name": "破妄之眼", "desc": "你的双眼能看破一切幻术和伪装", "type": "mystical", "effects": {"truth_sight": True, "intelligence": 2}},
    {"name": "战地医者", "desc": "你在战斗中可以快速施放治疗术，战场生存力极强", "type": "healing", "effects": {"combat_medic": True, "healing_skill": "high", "max_hp": 10}},
    {"name": "影分身", "desc": "你可以制造一个与本体相同的影分身，持续一段时间", "type": "mystical", "effects": {"shadow_clone": True, "agility": 2}},
    {"name": "瞌睡虫", "desc": "你能让人不由自主地犯困甚至入睡", "type": "mystical", "effects": {"sleep_induction": True, "intelligence": 1}},
    {"name": "内丹", "desc": "你体内有一颗未孵化的内丹，蕴藏着未知的力量", "type": "cultivation", "effects": {"inner_core": True, "spiritual_power": 6, "mystery_potential": True}},
    {"name": "双生", "desc": "你在世界上有一个双子存在，你们之间存在神秘联系", "type": "destiny", "effects": {"twin_destiny": True, "connected_fate": True}},
    {"name": "炼器宗师", "desc": "你掌握炼器术的精髓，能打造传说中的神器", "type": "crafting", "effects": {"artifact_crafting": "grandmaster", "intelligence": 3, "strength": 2}},
    {"name": "灵根变异", "desc": "你的灵根发生了变异，拥有无法预测的特殊能力", "type": "cultivation", "effects": {"mutant_root": True, "random_ability": True, "instability": True}},
]

# ==================== 情节配置 ====================
PLOT_CHECK_INTERVAL = 5  # 每N轮对话检查一次情节推进
PLOT_TWIST_CHANCE = 0.25  # 每次情节检查时，有25%概率强制触发剧情转折
MAX_MEMORY_ROUNDS = 20   # 每个角色保留最近N轮记忆
SCENE_MAX_CHARACTERS = 5  # 场景中最多同时存在的角色数

# ==================== 小说生成配置 ====================
NOVEL_CHAPTER_MIN_ROUNDS = 6     # 最少积累N轮对话后才生成新章节
NOVEL_MODEL = MODEL_REASONER      # 小说生成使用推理模型
NOVEL_TEMPERATURE = 0.9           # 小说创作温度
NOVEL_MAX_TOKENS = 4096           # 每章最大 token
NOVEL_STYLE = "网文风格"           # 小说风格描述
NOVEL_AUTHOR_NAME = "AI叙写者"    # 作者署名


# ==================== 运行时配置覆盖 ====================
def _load_runtime_overrides():
    import json as _json
    _settings_path = os.path.join(_ROOT, "user_settings.json")
    if not os.path.exists(_settings_path):
        return {}
    try:
        with open(_settings_path, "r", encoding="utf-8") as _f:
            return _json.load(_f)
    except Exception:
        return {}


_runtime = _load_runtime_overrides()


def _or(a, b):
    return a if a else b


DEEPSEEK_API_KEY = _or(_runtime.get("api_key"), DEEPSEEK_API_KEY)
DEEPSEEK_API_URL = _or(_runtime.get("api_url"), DEEPSEEK_API_URL)

MODEL_REASONER = _or(_runtime.get("model_reasoner"), MODEL_REASONER)
MODEL_CHAT = _or(_runtime.get("model_chat"), MODEL_CHAT)

MODEL_WORLD_GEN = _or(_runtime.get("model_reasoner"), MODEL_WORLD_GEN)
MODEL_PLOT = _or(_runtime.get("model_reasoner"), MODEL_PLOT)
MODEL_NARRATOR = _or(_runtime.get("model_chat"), MODEL_NARRATOR)
MODEL_CHARACTER = _or(_runtime.get("model_chat"), MODEL_CHARACTER)
MODEL_SCENE_DIRECTOR = _or(_runtime.get("model_reasoner"), MODEL_SCENE_DIRECTOR)
MODEL_USER_CHAR_GEN = _or(_runtime.get("model_chat"), MODEL_USER_CHAR_GEN)

TEMPERATURE_CREATIVE = _or(_runtime.get("temperature_creative"), TEMPERATURE_CREATIVE)
TEMPERATURE_NARRATIVE = _or(_runtime.get("temperature_narrative"), TEMPERATURE_NARRATIVE)
TEMPERATURE_DIALOGUE = _or(_runtime.get("temperature_dialogue"), TEMPERATURE_DIALOGUE)
TEMPERATURE_DIRECTOR = _or(_runtime.get("temperature_director"), TEMPERATURE_DIRECTOR)

MAX_TOKENS_WORLD = _or(_runtime.get("max_tokens_world"), MAX_TOKENS_WORLD)
MAX_TOKENS_PLOT = _or(_runtime.get("max_tokens_plot"), MAX_TOKENS_PLOT)
MAX_TOKENS_DIALOGUE = _or(_runtime.get("max_tokens_dialogue"), MAX_TOKENS_DIALOGUE)
MAX_TOKENS_NARRATOR = _or(_runtime.get("max_tokens_narrator"), MAX_TOKENS_NARRATOR)
MAX_TOKENS_DIRECTOR = _or(_runtime.get("max_tokens_director"), MAX_TOKENS_DIRECTOR)

NOVEL_MODEL = _or(_runtime.get("model_reasoner"), NOVEL_MODEL)
NOVEL_TEMPERATURE = _or(_runtime.get("temperature_novel"), NOVEL_TEMPERATURE)
NOVEL_MAX_TOKENS = _or(_runtime.get("max_tokens_novel"), NOVEL_MAX_TOKENS)