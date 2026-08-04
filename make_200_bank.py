#!/usr/bin/env python3
"""汇总全部初级题 → 排除争议 → 去重 → 不足200补题 → 生成HTML"""
import json, re, os, random
from html import escape

WORK = os.path.expanduser("~/fsx_timu")

# ========== 1. 加载数据 ==========
base = json.load(open(os.path.join(WORK, '金数据_基础_全部采集结果.json')))
mid = json.load(open(os.path.join(WORK, '金数据_中级_全部采集结果.json')))
with open(os.path.join(WORK, '模拟飞行理论题库_182题_打印版.html'), 'r') as f:
    html182 = f.read()

# 解析182
items182 = []
for b in html182.split('<div class="q-block">')[1:]:
    m = re.search(r'<span class="q-num">(\d+)\.</span>\s*(.+?)</div>', b)
    if not m: continue
    num = m.group(1)
    q = m.group(2).strip()
    opts = re.findall(r'<span class="opt-item">(?:<strong>)?[A-D]\.\s*(?:\u2705\s*)?(.+?)(?:</strong>)?</span>', b)
    ans_m = re.search(r'答案：<span class="ans-correct">([A-D])</span>', b)
    letter = ans_m.group(1) if ans_m else '?'
    ans = opts[ord(letter)-65] if letter != '?' and len(opts) > ord(letter)-65 else ''
    items182.append({'num': num, 'q': q, 'opts': opts, 'ans': ans})

# 90题练习集（从生成脚本提取数据）
import importlib.util
spec = importlib.util.spec_from_file_location("mk90", os.path.join(WORK, "make_90_practice.py"))
# 不执行，直接定义90题数据（复制自脚本）
practice90 = []  # 实际从脚本加载

# 从 make_90_practice.py 提取三个part（执行一次但跳过HTML生成）
exec_globals = {'__name__': '__main__', 'WORK': WORK}
with open(os.path.join(WORK, 'make_90_practice.py'), 'r') as f:
    src = f.read()
# 截取到HTML生成之前
cut = src.find('# ========== 打乱 ==========')
exec(compile(src[:cut], 'mk90', 'exec'), exec_globals)
practice90 = exec_globals['part1'] + exec_globals['part2'] + exec_globals['part3']
print(f"90题练习集: {len(practice90)} 题")

# ========== 2. 争议题排除清单 ==========
# 基础题库争议（按题目文本匹配）
base_doubt_kws = [
    '气压式高度表的英文',      # 存疑
    '“黑匣子”全称',           # 存疑（全称，FDR+CVR）
    'country',                 # 国家词汇三连
    '正确表述“国家”',
    'nation',
    '图中表示飞机',            # 看图题
    '六大仪表',
    '第3个图标',
    '高度表2',
]
# 中级题库额外争议（未被高级关键词覆盖的）
mid_doubt_kws = [
    '第十届珠海航展',          # 争议：应为歼-31
    '左侧滑',                  # 争议：与182冲突
]
# 中级题库争议（已在高级筛选中排除，这里不处理）
# 182题库争议（新编号）
q182_doubt_nums = {26, 53, 54, 99, 109, 160}  # 被初级筛选保留但属争议

# ========== 3. 初级筛选 ==========
# 高级特征关键词（中级/182筛选用）
advanced_kws = ['磁差', '偏流', '下降率', '风三角形', '航行速度三角形', '激波', '跨音速', '伯努利',
    '雷诺', 'DME', 'VOR', 'localizer', '下滑道', '陀螺', '静压', '动压', '逆温', '急流',
    '风切变', '火山灰', '积雨云', '结冰', '雷暴', '应答机', '高度层', 'QNH', 'VFR', 'IFR',
    '目视飞行', '氧气', '缺氧', '磁罗盘', 'Su33', 'FC2', '航母着舰', '阻拦索', '滑跃',
    '五边', '侧风', '跑道入口', '三边', '过载', '坡度', '失速速度', '迎角', '攻角',
    '真空速', '地速', '指示空速', '马赫', '翼尖涡', '重心', '襟翼放下', 'V1', 'V2',
    '音速', '超音速', '节（knot）', '能见度', 'A380', 'F-117', '苏-27', '米格-17',
    '飞行高度层', '着陆滑跑', '夜间', '遮光板', '凝结尾迹', '经济舱', '刹车效应', '跑道磁',
    '全静压', '最佳爬升', '螺旋桨', '滑流', '左转弯', '倒飞', '地面效应', '下降时', '空速管',
    'FL', 'Flight level', 'Squawk', '应答机']

def is_advanced(q):
    return any(kw in q for kw in advanced_kws)

# 基础题库：全部保留（小学组），只排除争议，难度=初级
base_keep = []
for d in base:
    if any(kw in d['q'] for kw in base_doubt_kws):
        continue
    base_keep.append({'srcs': ['基础题库'], 'diff': '初级', 'q': d['q'], 'opts': d['opts'], 'ans': d['correct']})

# 中级题库：初级筛选 + 排除争议
mid_keep = []
mid_adv = []  # 中级难度部分
for d in mid:
    if any(kw in d['q'] for kw in mid_doubt_kws):
        continue
    if is_advanced(d['q']):
        mid_adv.append({'srcs': ['中级题库'], 'diff': '中级', 'q': d['q'], 'opts': d['opts'], 'ans': d['correct']})
    else:
        mid_keep.append({'srcs': ['中级题库'], 'diff': '初级', 'q': d['q'], 'opts': d['opts'], 'ans': d['correct']})

# 182题库：初级筛选 + 排除争议
q182_keep = []
q182_adv = []  # 中级难度部分
for i in items182:
    if int(i['num']) in q182_doubt_nums:
        continue
    if is_advanced(i['q']):
        q182_adv.append({'srcs': ['182题库'], 'diff': '中级', 'q': i['q'], 'opts': i['opts'], 'ans': i['ans']})
    else:
        q182_keep.append({'srcs': ['182题库'], 'diff': '初级', 'q': i['q'], 'opts': i['opts'], 'ans': i['ans']})

# 90题练习：全部保留（初级）
p90_keep = [{'srcs': ['练习90题'], 'diff': '初级', 'q': q, 'opts': opts, 'ans': opts[ans_idx]} for cat, q, opts, ans_idx in practice90]

print(f"\n基础题库(初级): {len(base_keep)}")
print(f"中级题库 初级: {len(mid_keep)}, 中级: {len(mid_adv)}")
print(f"182题库 初级: {len(q182_keep)}, 中级: {len(q182_adv)}")
print(f"练习90题(初级): {len(p90_keep)}")
print(f"去重前合计: {len(base_keep)+len(mid_keep)+len(mid_adv)+len(q182_keep)+len(q182_adv)+len(p90_keep)}")

# ========== 4. 去重（标准化） ==========
def norm(q):
    q = q.lower().strip()
    # 去掉所有标点符号差异：括号【】（）()、引号、空格、标点（含英文句点）
    q = re.sub(r'[（()）【】\[\]\s、，。？?：:；;.\u201c\u201d\u2018\u2019"\'\-—–·]', '', q)
    return q

seen = set()
all_items = []
for item in base_keep + mid_keep + q182_keep + p90_keep + mid_adv + q182_adv:
    n = norm(item['q'])
    if n in seen:
        # 重复题：合并来源标记（不丢弃，保证每个来源都能筛选到）
        for kept in all_items:
            if norm(kept['q']) == n:
                for s in item['srcs']:
                    if s not in kept['srcs']:
                        kept['srcs'].append(s)
                break
        continue
    seen.add(n)
    all_items.append(item)

print(f"去重后合计: {len(all_items)}")

# ========== 6. 考纲薄弱领域补题 ==========
weak_fill = [
    # L. 飞行规则/安全 (14)
    ("飞行安全", "民航客机上，下列哪项救生设备乘客一般用不到？", ["救生衣", "氧气面罩", "个人降落伞", "应急滑梯"], 2),
    ("飞行安全", "飞机遇到紧急情况时，乘客首先应当？", ["听从机组人员指挥", "自行打开舱门", "解开安全带走动", "拨打急救电话"], 0),
    ("飞行安全", "在飞机客舱内吸烟，后果是？", ["违反规定，可能受到处罚", "没有任何限制", "只能在洗手间吸", "只要不呛到人就可以"], 0),
    ("飞行安全", "飞机应急滑梯（逃生滑梯）的作用是？", ["紧急撤离时快速离机", "装卸行李", "登机使用", "空中滑翔"], 0),
    ("飞行安全", "飞机在地面加油时，乘客在候机厅等候，此时禁止在加油区域附近？", ["使用手机等电子设备", "喝水", "看书", "聊天"], 0),
    ("飞行安全", "飞机在地面滑行阶段，乘客应当？", ["系好安全带坐在座位上", "起身拿行李", "打开行李架", "在过道走动"], 0),
    ("飞行安全", "飞机巡航中遇到轻微颠簸时，客舱服务通常会？", ["暂停服务", "加快送餐", "开香槟庆祝", "让乘客站起来"], 0),
    ("飞行安全", "飞机着陆后尚未停稳时，乘客应当？", ["保持系好安全带", "立即解开安全带", "站起来取行李", "打开手机"], 0),
    ("飞行安全", "行李架上的物品放置不稳，颠簸时可能？", ["掉落砸伤乘客", "自动消失", "变轻", "被吸走"], 0),
    ("飞行安全", "飞机紧急撤离时，乘客应当？", ["丢弃高跟鞋等尖锐物品快速撤离", "带上所有行李", "排队慢慢走", "先拍照留念"], 0),
    ("飞行安全", "飞机在水上迫降时，乘客需要穿上的设备是？", ["救生衣", "降落伞", "防弹衣", "潜水服"], 0),
    ("飞行安全", "客舱失压氧气面罩掉落后，正确的做法是？", ["先戴好自己的，再帮身边的人", "先帮别人戴", "拿起来当玩具", "不戴面罩跑向驾驶舱"], 0),
    ("飞行安全", "飞机客舱冒烟或起火时，乘客应当？", ["听从机组指挥，弯腰低姿撤离", "打开窗户通风", "用水泼向烟雾", "躲进洗手间"], 0),
    ("飞行安全", "坐在紧急出口座位的乘客，额外承担的责任是？", ["紧急时协助打开舱门组织撤离", "负责发餐", "看管行李", "给机长报信"], 0),
    # A. 百年航空经典机型 (6)
    ("航空史", "我国自行研制的教练-8（K-8）教练机主要用于？", ["飞行学员训练", "民航客运", "农业喷洒", "太空飞行"], 0),
    ("航空史", "世界上第一种投入实用的喷气式战斗机是？", ["德国Me 262", "美国F-86", "苏联米格-15", "英国流星"], 0),
    ("航空史", "莱特兄弟「飞行者一号」首次试飞飞行的距离大约是？", ["约36米", "约360米", "约3.6公里", "约36公里"], 0),
    ("航空史", "世界上第一种量产的四发喷气式客机是？", ["波音707", "波音737", "空客A320", "麦道DC-9"], 0),
    ("航空史", "我国自主研制的「运-10」大型客机首次试飞成功是在哪一年？", ["1980年", "1960年", "2000年", "2010年"], 0),
    ("航空史", "空客A320系列客机是哪个公司的产品？", ["欧洲空中客车公司", "美国波音公司", "中国商飞", "巴西航空工业"], 0),
    # F. 陆空通话 (5)
    ("陆空通话", "通话中「Read back」的意思是？", ["复诵指令", "读报纸", "查看地图", "记录航班"], 0),
    ("陆空通话", "塔台指令「Report position」的意思是？", ["报告当前位置", "改变高度", "准备着陆", "请求加油"], 0),
    ("陆空通话", "通话中「Hold short of runway」的意思是？", ["在跑道外等待", "立即起飞", "穿越跑道", "滑入跑道"], 0),
    ("陆空通话", "通话中「Request」的意思是？", ["请求", "拒绝", "收到", "完成"], 0),
    ("陆空通话", "通话中「Approach」指的是飞行中的哪个阶段？", ["进近（准备着陆）", "起飞", "巡航", "滑行"], 0),
    # H. 空气动力学（初级）(5)
    ("飞行原理", "飞机机翼产生升力的主要原因是？", ["上下表面气流速度不同形成压差", "机翼本身很轻", "发动机吹起飞机", "地面推力"], 0),
    ("飞行原理", "飞机转弯时，升力要额外提供一部分力作为？", ["向心力", "重力", "阻力", "摩擦力"], 0),
    ("飞行原理", "机翼更薄、速度更快的飞机，通常更适合？", ["高速飞行", "低速慢飞", "垂直起降", "水面降落"], 0),
    ("飞行原理", "飞机飞行中不断消耗燃油，重量减轻后，所需的升力会？", ["减小", "增大", "不变", "消失"], 0),
    ("飞行原理", "滑翔机没有动力，它是依靠什么保持飞行的？", ["用高度换速度（下滑）", "靠风筝线牵引", "靠气球浮力", "靠太阳能电池"], 0),
    # J. 导航仪表（初级）(4)
    ("导航仪表", "飞机上的「无线电罗盘」（ADF）依靠什么信号确定方位？", ["地面无方向信标（NDB）信号", "手机信号", "电视信号", "北斗短信"], 0),
    ("导航仪表", "飞机的自动驾驶仪（Autopilot）主要功能是？", ["自动保持航向、高度和速度", "自动放行李", "自动卖票", "自动加油"], 0),
    ("导航仪表", "飞机航线上的「航路点」（Waypoint）是指？", ["航线上的关键位置点", "飞机终点", "加油站", "维修点"], 0),
    ("导航仪表", "飞机上的「空中防撞系统」（TCAS）的作用是？", ["警告飞行员附近有飞机，避免相撞", "防止被雷击", "防止结冰", "防止迷航"], 0),
    # K. 航空气象（初级）(4)
    ("航空气象", "天空出现浓积云（顶部隆起像花椰菜）时，预示天气将？", ["可能发展为雷雨", "马上放晴", "下雪", "起雾"], 0),
    ("航空气象", "地面有大风时，飞机起降会选择？", ["逆风方向的跑道", "顺风方向的跑道", "任意跑道", "关闭机场"], 0),
    ("航空气象", "飞机在雨中飞行时，驾驶舱风挡玻璃靠什么保持视线清晰？", ["雨刷和除水系统", "打开窗户", "乘客擦玻璃", "降低高度"], 0),
    ("航空气象", "夏季遇到雷雨天气时，飞机通常会？", ["绕飞或避开雷雨区", "直接穿入积雨云", "原地降落", "立即返航加油"], 0),
]

print(f"\n=== 考纲薄弱补题（{len(weak_fill)}题）===")
used_norms = set(seen)
added_weak = 0
for q, opts, ans_idx in [(w[1], w[2], w[3]) for w in weak_fill]:
    n = norm(q)
    dup = False
    for un in used_norms:
        common = len(set(n) & set(un))
        if common / max(len(n), len(un)) > 0.75:
            dup = True
            break
    if dup:
        print(f"  跳过重复: {q[:35]}")
        continue
    used_norms.add(n)
    all_items.append({'srcs': ['考纲补充'], 'diff': '初级', 'q': q, 'opts': opts, 'ans': opts[ans_idx]})
    added_weak += 1
print(f"考纲补充新增: {added_weak} 题")

# ========== 4.5 第二轮去重：高相似且答案相同 ==========
from difflib import SequenceMatcher
items_clean = []
for item in all_items:
    n = norm(item['q'])
    na = norm(item['ans'])
    dup = False
    for kept in items_clean:
        kn = norm(kept['q'])
        if len(n) < 6 or len(kn) < 6:
            continue
        sim = SequenceMatcher(None, n, kn).ratio()
        if sim > 0.75 and na == norm(kept['ans']) and na:
            dup = True
            break
    if not dup:
        items_clean.append(item)
all_items = items_clean
print(f"第二轮去重（高相似+同答案）后合计: {len(all_items)}")

# ========== 5. 不足200补题 ==========
new_fill = []  # 需要时补充
if len(all_items) < 200:
    print(f"不足200题，需补 {200-len(all_items)} 题")
    # 补充题（验证与现有不重复）
    fill_questions = [
        ("航空史", "世界上第一架全金属客机「容克F13」诞生于哪个国家？", ["德国", "美国", "英国", "法国"], 0),
        ("航空史", "我国第一架自行研制的直升机型号是？", ["直-5", "直-9", "直-10", "直-20"], 0),
        ("航空史", "「冯如一号」试飞成功的时间是？", ["1909年", "1911年", "1903年", "1919年"], 0),
        ("航空史", "飞机的发明者莱特兄弟的名字是？", ["威尔伯和奥维尔", "约翰和亨利", "威廉和乔治", "罗伯特和查理"], 0),
        ("航空史", "世界上第一家航空公司成立于哪个国家？", ["英国", "美国", "德国", "法国"], 2),
        ("飞机结构", "飞机机翼上表面的形状通常是？", ["向上拱起（凸面）", "向下凹陷", "完全平直", "波浪形"], 0),
        ("飞机结构", "飞机的「翼剖面」（翼型）决定飞机的？", ["升力特性", "颜色", "座位数", "航程"], 0),
        ("飞机结构", "飞机的机轮刹车装置位于？", ["起落架机轮内", "发动机舱", "机翼前缘", "尾翼"], 0),
        ("飞机结构", "飞机的「油箱」通常布置在飞机的哪个部位？", ["机翼内部和机身", "机轮", "机头", "尾翼"], 0),
        ("飞机结构", "飞机驾驶舱的窗户玻璃通常是？", ["多层加厚防鸟击玻璃", "普通单层玻璃", "塑料薄膜", "金属网"], 0),
        ("操纵面", "飞机副翼向下偏转的一侧，机翼升力会？", ["增大", "减小", "不变", "消失"], 0),
        ("操纵面", "飞机着陆前放下起落架后，需要检查的指示是？", ["起落架锁定指示", "发动机温度", "客舱灯光", "机翼角度"], 0),
        ("操纵面", "飞机的减速板（扰流板）展开后，飞机？", ["阻力增大、速度降低", "升力增大", "速度加快", "高度升高"], 0),
        ("飞行仪表", "飞机高度表上「ALT」代表的是？", ["高度（Altitude）", "速度", "航向", "温度"], 0),
        ("飞行仪表", "飞机的「航向仪」指示的是飞机机头的？", ["磁航向", "飞行速度", "飞行高度", "燃油量"], 0),
        ("飞行仪表", "飞机的「空速表」单位为？", ["节（knot）或公里/小时", "米", "秒", "磅"], 0),
        ("飞行仪表", "飞机「姿态仪」上蓝色的区域代表？", ["天空", "地面", "云层", "海洋"], 0),
        ("飞行仪表", "飞机仪表板上「VOR」仪表用于显示？", ["飞机相对导航台的方位", "飞机速度", "飞机高度", "飞机温度"], 0),
        ("机场标志", "机场跑道的「入口」标志形状是？", ["白色横向条纹", "黄色圆圈", "红色方块", "蓝色三角"], 0),
        ("机场标志", "机场「滑行道」与「跑道」交叉处通常设有什么？", ["等待线和停止牌", "加油站", "候机楼", "雷达"], 0),
        ("机场标志", "机场跑道两端的「跑道号码」标志颜色是？", ["白色", "黄色", "红色", "蓝色"], 0),
        ("机场标志", "机场「风向袋」通常安装在？", ["跑道边的高杆上", "候机楼屋顶", "机库内", "停车场"], 0),
        ("机场标志", "机场「塔台」通常位于？", ["机场最高建筑", "跑道中央", "机库内部", "地下"], 0),
        ("陆空通话", "陆空通话中「Copy」的意思是？", ["收到、抄收", "复制", "起飞", "降落"], 0),
        ("陆空通话", "陆空通话中「Negative」的意思是？", ["不行、不同意", "可以", "收到", "再见"], 0),
        ("陆空通话", "陆空通话中「Affirm」的意思是？", ["是的、同意", "不行", "收到", "请求"], 0),
        ("陆空通话", "陆空通话中「Over」的意思是？", ["通话结束、等待回答", "越界", "起飞", "下降"], 0),
        ("陆空通话", "陆空通话中「Climb to 5000 feet」的意思是？", ["爬升到5000英尺", "下降到5000英尺", "保持5000英尺", "离开5000英尺"], 0),
        ("英文词汇", "英文「airport」的中文意思是？", ["机场", "港口", "火车站", "公交站"], 0),
        ("英文词汇", "英文「terminal」在航空中指？", ["航站楼", "终点站", "终端", "航站"], 0),
        ("英文词汇", "英文「flight」的中文意思是？", ["航班/飞行", "机场", "飞机", "跑道"], 0),
        ("英文词汇", "英文「boarding」在机场指？", ["登机", "候机", "下机", "转机"], 0),
        ("英文词汇", "英文「departure」的中文意思是？", ["出发/离港", "到达", "中转", "延误"], 0),
        ("英文词汇", "英文「arrival」的中文意思是？", ["到达/进港", "出发", "中转", "登机"], 0),
        ("飞行规则", "飞机在跑道上有另一架飞机正在起飞时，应当？", ["等待其起飞完成", "同时起飞", "跟在后面立即起飞", "绕行跑道"], 0),
        ("飞行规则", "乘客在飞机起飞前手机应当？", ["调成飞行模式或关机", "保持通话", "随意使用", "静音"], 0),
        ("飞行规则", "飞机「应急出口」的位置在？", ["机身两侧（机翼上方和尾部）", "机头", "货舱", "驾驶舱"], 0),
        ("飞行规则", "飞机起飞前播放安全须知视频的目的是？", ["告知乘客安全设备和应急程序", "娱乐乘客", "介绍目的地", "宣传航空公司"], 0),
        ("飞行规则", "飞机飞行途中遇到气流颠簸时，乘客应当？", ["系好安全带留在座位", "站起来走动", "打开行李架", "去洗手间"], 0),
        ("航空常识", "飞机的「机长」和「副驾驶」的分工是？", ["机长负责决策，副驾驶协助操纵", "两人完全独立", "副驾驶休息", "机长不操纵"], 0),
        ("航空常识", "飞机降落时乘客打开手机记录飞行数据，哪种说法正确？", ["应遵守航空公司规定，起飞着陆阶段关闭", "可以随意使用", "只有拍照可以", "无任何限制"], 0),
        ("航空常识", "飞机的「飞行时间」一般指？", ["从起飞滑跑到着陆停止的时间", "登机时间", "候机时间", "订票时间"], 0),
        ("航空常识", "飞机「安检」时，下列哪项需要单独取出检查？", ["笔记本电脑", "书本", "衣服", "食物"], 0),
        ("航空常识", "飞机「登机牌」上最重要的信息是？", ["登机口和座位号", "天气", "油价", "日期"], 0),
        ("航空常识", "飞机的「航班号」中「MU」代表？", ["中国东方航空", "中国国际航空", "中国南方航空", "海南航空"], 0),
        ("航空常识", "飞机「值机」（check-in）的主要目的是？", ["办理乘机手续、托运行李", "买机票", "安检", "登机"], 0),
        ("航空常识", "飞机的「行李托运」时，下列哪项属于危险品不能托运？", ["充电宝", "衣物", "书籍", "食品"], 0),
        ("航空常识", "飞机「驾驶舱」门的特殊设计是？", ["防弹防冲击", "透明玻璃", "随时敞开", "无锁"], 0),
        ("航空常识", "飞机「客舱」的窗户为什么是圆角形？", ["分散应力、防止裂纹", "美观", "省材料", "方便安装"], 0),
        ("航空常识", "飞机的「尾翼」标记通常显示？", ["航空公司标志和机身号", "目的地", "航班号", "票价"], 0),
    ]
    fill_items = []
    used_norms = set(seen)
    for cat, q, opts, ans_idx in fill_questions:
        n = norm(q)
        # 与现有题查重
        dup = False
        for un in used_norms:
            common = len(set(n) & set(un))
            if common / max(len(n), len(un)) > 0.75:
                dup = True
                break
        if dup:
            print(f"  跳过重复补题: {q[:35]}")
            continue
        used_norms.add(n)
        fill_items.append({'src': '补充新题', 'q': q, 'opts': opts, 'ans': opts[ans_idx]})
        if len(fill_items) >= (200 - len(all_items)):
            break
    all_items.extend(fill_items)
    print(f"补充后合计: {len(all_items)}")

print(f"\n最终题目数: {len(all_items)}")

print(f"\n最终题目数: {len(all_items)}")

# ========== 6. 打乱 + 生成HTML ==========
random.seed(20260731)
shuffled = all_items[:]
random.shuffle(shuffled)

OUT = os.path.join(WORK, "fsx-quiz.html")

html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>模拟飞行 · 初级中级题库372题交互练习</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  font-size: 19px;
  line-height: 1.8;
  color: #222;
  background: linear-gradient(160deg, #f0f4fa 0%, #e8edf5 100%);
  min-height: 100vh;
  padding: 40px 60px;
}
.container { max-width: 1500px; margin: 0 auto; }
h1 {
  font-size: 34px;
  color: #16213e;
  text-align: center;
  margin-bottom: 8px;
  letter-spacing: 2px;
}
.subtitle {
  text-align: center;
  color: #888;
  font-size: 17px;
  margin-bottom: 30px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}
.q-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px 28px;
  box-shadow: 0 4px 16px rgba(15, 52, 96, 0.12);
  border-top: 5px solid #e94560;
  transition: transform 0.15s;
  display: flex;
  flex-direction: column;
}
.q-card:hover { transform: translateY(-3px); }
.q-top { display: flex; align-items: center; margin-bottom: 4px; }
.q-num {
  display: inline-block;
  background: #e94560;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  width: 34px;
  height: 34px;
  line-height: 34px;
  text-align: center;
  border-radius: 50%;
  margin-right: 10px;
  flex-shrink: 0;
}
.q-cat {
  font-size: 14px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 12px;
  border-radius: 12px;
  margin-left: auto;
  white-space: nowrap;
}
.q-text {
  font-weight: bold;
  font-size: 20px;
  color: #1a1a2e;
  margin: 12px 0 14px 0;
  min-height: 60px;
}
.opt {
  padding: 8px 14px;
  margin: 4px 0;
  border-radius: 8px;
  font-size: 18px;
  background: #f8f9fa;
  border: 1px solid #e5e5e5;
  transition: all 0.25s;
  cursor: pointer;
  user-select: none;
}
.opt:hover { border-color: #2196f3; background: #f0f7ff; }
.opt-selected {
  background: #e3f0ff;
  border-color: #2196f3;
  color: #0d47a1;
  font-weight: bold;
  box-shadow: 0 0 0 1px #2196f3 inset;
}
.opt-correct {
  background: #e8f8e8;
  border-color: #27ae60;
  color: #1e7a34;
  font-weight: bold;
  box-shadow: 0 0 0 1px #27ae60 inset;
}
.opt-correct::after { content: " ✅"; }
.opt-wrong {
  background: #fde8e8;
  border-color: #e74c3c;
  color: #c0392b;
  font-weight: bold;
  box-shadow: 0 0 0 1px #e74c3c inset;
}
.opt-wrong::after { content: " ❌"; }
.card-wrong { border-top-color: #e74c3c !important; }
.card-right { border-top-color: #27ae60 !important; }
.q-status {
  font-size: 14px;
  font-weight: bold;
  margin-left: 10px;
  white-space: nowrap;
}
.q-status.right { color: #27ae60; }
.q-status.wrong { color: #e74c3c; }
.q-diff {
  font-size: 13px;
  color: #27ae60;
  background: #e8f8e8;
  border: 1px solid #27ae60;
  padding: 1px 10px;
  border-radius: 12px;
  margin-left: 8px;
  white-space: nowrap;
}
.q-diff.mid {
  color: #e67e22;
  background: #fef5e7;
  border-color: #e67e22;
}
.ans-area {
  margin-top: auto;
  padding-top: 12px;
}
.ans-btn {
  background: #0f3460;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 17px;
  padding: 8px 22px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
}
.ans-btn:hover:not(:disabled) { background: #1a4a80; }
.ans-btn:disabled {
  background: #bbb;
  cursor: not-allowed;
}
.ans-reveal {
  display: none;
  margin-top: 10px;
  font-size: 18px;
  color: #c0392b;
  font-weight: bold;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 8px 14px;
}
.ans-reveal .correct-text { color: #1e7a34; }
.ans-reveal .wrong-tag { color: #e74c3c; }
.ans-reveal .right-tag { color: #27ae60; }
.show { display: block; }
#score-float {
  position: fixed;
  right: 24px;
  bottom: 24px;
  background: #0f3460;
  color: #fff;
  padding: 16px 24px;
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.35);
  z-index: 999;
  font-size: 18px;
  text-align: center;
  min-width: 190px;
  border: 2px solid rgba(255,255,255,0.25);
}
#score-float .score-num { font-size: 30px; font-weight: bold; color: #ffd166; }
#score-float .score-detail { font-size: 14px; color: #cbd5e0; margin-top: 2px; }
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.reset-btn {
  background: #e94560;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 17px;
  padding: 10px 24px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
}
.reset-btn:hover { background: #c73550; }
.source-select {
  font-family: inherit;
  font-size: 17px;
  padding: 10px 14px;
  border-radius: 10px;
  border: 2px solid #0f3460;
  background: #fff;
  color: #16213e;
  cursor: pointer;
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}
.source-select:focus { outline: none; border-color: #e94560; }
.history-box {
  background: #fff;
  border-radius: 14px;
  padding: 20px 28px;
  box-shadow: 0 4px 16px rgba(15, 52, 96, 0.12);
  margin-bottom: 30px;
}
.history-box h3 { font-size: 20px; color: #16213e; margin-bottom: 12px; }
.history-box table {
  width: 100%;
  border-collapse: collapse;
  font-size: 16px;
}
.history-box th, .history-box td {
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
  text-align: center;
}
.history-box th { background: #0f3460; color: #fff; }
.history-box tr:nth-child(even) { background: #f8f9fa; }
.history-empty { color: #999; font-size: 15px; padding: 8px 0; }
.bottom-reset {
  text-align: center;
  margin: 30px 0;
}
.footer {
  text-align: center;
  color: #999;
  font-size: 15px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}
/* ===== 手机端适配（单列 + 大字体 + 大按钮） ===== */
@media (max-width: 900px) {
  body {
    padding: 12px 10px 30px 10px;
    font-size: 18px;
  }
  .container { max-width: 100%; }
  h1 { font-size: 22px; line-height: 1.4; }
  .subtitle { font-size: 14px; line-height: 1.6; }
  .grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .q-card { padding: 16px; border-radius: 14px; }
  .q-text { font-size: 20px; min-height: 0; line-height: 1.6; }
  .q-num { width: 34px; height: 34px; line-height: 34px; font-size: 16px; }
  .q-cat { font-size: 14px; padding: 2px 10px; }
  .opt { font-size: 17px; padding: 11px 14px; margin: 5px 0; line-height: 1.5; }
  .ans-btn { font-size: 18px; padding: 11px 0; width: 100%; border-radius: 10px; }
  .ans-reveal { font-size: 16px; padding: 10px 14px; line-height: 1.5; }
  .reset-btn { font-size: 15px; padding: 11px 18px; width: 100%; }
  .q-status { font-size: 14px; }
  .top-bar { margin-bottom: 12px; }
  .history-box { padding: 10px 8px; overflow-x: auto; }
  .history-box h3 { font-size: 15px; }
  .history-box table { font-size: 11px; min-width: 440px; }
  .history-box th, .history-box td { padding: 5px 6px; }
  .bottom-reset { margin: 16px 0; }
  .footer { font-size: 11px; margin-top: 20px; }
  #score-float {
    right: 8px;
    bottom: 8px;
    padding: 8px 12px;
    min-width: 110px;
    font-size: 12px;
    border-radius: 10px;
  }
  #score-float .score-num { font-size: 22px; }
  #score-float .score-detail { font-size: 10px; }
}
</style>
</head>
<body>
<div class="container">
<h1>模拟飞行 · 初级中级题库372题交互练习</h1>
<div class="subtitle">汇总：基础题库（小学）+ 中级/182题库初级题 + 练习90题 + 考纲薄弱领域补充38题 | 已排除争议题 | 先选答案，再点「显示答案」判定对错</div>
<div class="top-bar">
  <select id="source-select" class="source-select" onchange="changeSource(this)">
    <option value="全部">📚 全部题目</option>
''')
# 动态生成来源选项
src_set = []
for item in all_items:
    for s in item['srcs']:
        if s not in src_set:
            src_set.append(s)
for src in src_set:
    html_parts.append(f'    <option value="{src}">{src}</option>\n')
html_parts.append('''  </select>
  <select id="diff-select" class="source-select" onchange="changeDiff(this)">
    <option value="全部">🎯 全部难度</option>
    <option value="初级">初级</option>
    <option value="中级">中级</option>
  </select>
  <button class="reset-btn" onclick="clearAndShuffle()">🗑 清除进度重新开始</button>
</div>
<div class="history-box">
  <h3>📊 历史成绩记录（每次清除进度的成绩）</h3>
  <div id="history-content"></div>
</div>
<div class="grid">
''')

for i, item in enumerate(shuffled, 1):
    q = item['q']
    opts = item['opts']
    ans_text = item['ans']
    srcs = item['srcs']
    src_label = '/'.join(srcs)
    srcs_attr = ','.join(srcs)
    # 找答案在选项中的位置
    ans_idx = -1
    for j, o in enumerate(opts):
        if norm(o) == norm(ans_text):
            ans_idx = j
            break
    if ans_idx == -1:
        # 尝试包含匹配
        for j, o in enumerate(opts):
            if ans_text and (ans_text in o or o in ans_text):
                ans_idx = j
                break
    if ans_idx == -1:
        print(f"  ⚠️ 答案未匹配选项: {q[:40]} | ans={ans_text[:20]}")
        ans_idx = 0
    html_parts.append(f'<div class="q-card" data-idx="{i-1}" data-diff="{item["diff"]}" data-srcs="{srcs_attr}" data-answer="{escape(opts[ans_idx], quote=True)}" data-letter="{chr(65+ans_idx)}">')
    diff_tag = '<span class="q-diff mid">中级</span>' if item['diff'] == '中级' else '<span class="q-diff">初级</span>'
    html_parts.append(f'<div class="q-top"><span class="q-num">{i}</span><span class="q-cat">{src_label}</span>{diff_tag}<span class="q-status"></span></div>')
    html_parts.append(f'<div class="q-text">{q}</div>')
    for j, opt in enumerate(opts):
        html_parts.append(f'<div class="opt" data-correct="{"true" if j == ans_idx else "false"}" onclick="selectOpt(this)">{chr(65+j)}. {opt}</div>')
    html_parts.append(f'<div class="ans-area">')
    html_parts.append(f'<button class="ans-btn" onclick="toggleAns(this)" disabled>显示答案</button>')
    html_parts.append(f'<div class="ans-reveal"></div>')
    html_parts.append(f'</div>')
    html_parts.append('</div>')

html_parts.append('''
</div>
<div class="footer">初级题库汇总 · 已排除争议题 · 16:9宽屏适配 · 先选答案后判定 · 进度自动保存
<br>
<span id="busuanzi_container_site_pv" style="color:#999;">👁 本页累计访问 <span id="busuanzi_value_site_pv">0</span> 次</span>
</div>
</div>
<div class="bottom-reset">
  <button class="reset-btn" onclick="clearAndShuffle()">🗑 清除进度重新开始</button>
</div>
<div id="score-float">
  <div class="score-num">--%</div>
  <div class="score-detail">答对 <span id="score-correct">0</span> / 已判 <span id="score-graded">0</span></div>
  <div class="score-detail">共 <span id="score-total">0</span> 题</div>
</div>
<script>
var gradedCount = 0;
var correctCount = 0;
var STORE_KEY = 'fsx_progress_v1';
var HIST_KEY = 'fsx_history_v1';
var SOURCE_KEY = 'fsx_source_v1';
var DIFF_KEY = 'fsx_diff_v1';

function getSelectedSource() {
  try { return localStorage.getItem(SOURCE_KEY) || '全部'; } catch (e) { return '全部'; }
}

function getSelectedDiff() {
  try { return localStorage.getItem(DIFF_KEY) || '全部'; } catch (e) { return '全部'; }
}

function changeSource(sel) {
  try { localStorage.setItem(SOURCE_KEY, sel.value); } catch (e) {}
  location.reload();
}

function changeDiff(sel) {
  try { localStorage.setItem(DIFF_KEY, sel.value); } catch (e) {}
  location.reload();
}

// 按来源+难度联合过滤卡片，返回可见题数
function applySourceFilter() {
  var sel = getSelectedSource();
  var diff = getSelectedDiff();
  var cards = document.querySelectorAll('.q-card');
  var visible = 0;
  cards.forEach(function(card) {
    var cardSrcs = (card.getAttribute('data-srcs') || '').split(',');
    var cardDiff = card.getAttribute('data-diff');
    var show = (sel === '全部' || cardSrcs.indexOf(sel) >= 0) && (diff === '全部' || cardDiff === diff);
    if (show) {
      card.style.display = '';
      visible++;
    } else {
      card.style.display = 'none';
    }
  });
  // 重新编号
  var n = 0;
  cards.forEach(function(card) {
    if (card.style.display !== 'none') {
      n++;
      card.querySelector('.q-num').textContent = n;
    }
  });
  return visible;
}

function initSourceSelect() {
  var sel = document.getElementById('source-select');
  if (sel) sel.value = getSelectedSource();
  var diff = document.getElementById('diff-select');
  if (diff) diff.value = getSelectedDiff();
}

function selectOpt(opt) {
  var card = opt.closest('.q-card');
  if (card.dataset.graded === 'true') return; // 已判定，锁定
  // 清除该题其他选中
  card.querySelectorAll('.opt').forEach(function(el) {
    el.classList.remove('opt-selected');
  });
  opt.classList.add('opt-selected');
  card.dataset.chosen = opt.getAttribute('data-correct');
  card.querySelector('.ans-btn').disabled = false;
  saveProgress();
}

function toggleAns(btn) {
  var card = btn.closest('.q-card');
  var reveal = card.querySelector('.ans-reveal');
  var answerText = card.getAttribute('data-answer');
  var letter = card.getAttribute('data-letter');
  var statusEl = card.querySelector('.q-status');

  if (card.dataset.graded === 'true') {
    // 已判定，只切换显示/隐藏
    if (reveal.classList.contains('show')) {
      reveal.classList.remove('show');
      btn.textContent = '显示答案';
    } else {
      reveal.classList.add('show');
      btn.textContent = '隐藏答案';
    }
    return;
  }

  var chosen = card.dataset.chosen;
  if (!chosen) return; // 未选答案，按钮本就禁用

  var isCorrect = (chosen === 'true');
  gradedCount++;
  if (isCorrect) correctCount++;
  card.dataset.graded = 'true';

  // 高亮正确答案
  card.querySelectorAll('.opt').forEach(function(el) {
    if (el.getAttribute('data-correct') === 'true') {
      el.classList.add('opt-correct');
    }
  });

  // 判定结果
  if (isCorrect) {
    card.classList.add('card-right');
    statusEl.textContent = '✓ 做对';
    statusEl.className = 'q-status right';
    reveal.innerHTML = '<span class="right-tag">✓ 答对了！</span> 正确答案：<span class="correct-text">' + letter + '</span>（' + answerText + '）';
  } else {
    card.classList.add('card-wrong');
    // 用户选错的项标红
    card.querySelectorAll('.opt').forEach(function(el) {
      if (el.classList.contains('opt-selected')) {
        el.classList.add('opt-wrong');
      }
    });
    statusEl.textContent = '✗ 做错';
    statusEl.className = 'q-status wrong';
    reveal.innerHTML = '<span class="wrong-tag">✗ 答错了！</span> 正确答案：<span class="correct-text">' + letter + '</span>（' + answerText + '）';
  }

  reveal.classList.add('show');
  btn.textContent = '隐藏答案';
  btn.disabled = false;
  updateScore();
  saveProgress();
}

function updateScore() {
  var pct = gradedCount > 0 ? Math.round(correctCount / gradedCount * 100) : 0;
  document.querySelector('#score-float .score-num').textContent = pct + '%';
  document.getElementById('score-correct').textContent = correctCount;
  document.getElementById('score-graded').textContent = gradedCount;
  // 只统计可见卡片
  var visible = 0;
  document.querySelectorAll('.q-card').forEach(function(c) {
    if (c.style.display !== 'none') visible++;
  });
  document.getElementById('score-total').textContent = visible;
}

function saveProgress() {
  var answers = {};
  document.querySelectorAll('.q-card').forEach(function(card) {
    var idx = card.getAttribute('data-idx');
    answers[idx] = {
      chosen: card.dataset.chosen || null,
      graded: card.dataset.graded === 'true',
      correct: card.dataset.chosen === 'true'
    };
  });
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify({answers: answers, lastPos: window.scrollY, ts: Date.now()}));
  } catch (e) {}
}

function loadProgress() {
  var data = null;
  try {
    data = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
  } catch (e) { return; }
  if (!data || !data.answers) return;

  document.querySelectorAll('.q-card').forEach(function(card) {
    if (card.style.display === 'none') return; // 跳过被来源过滤隐藏的题
    var idx = card.getAttribute('data-idx');
    var st = data.answers[idx];
    if (!st) return;

    if (st.chosen) {
      card.querySelectorAll('.opt').forEach(function(el) {
        if (el.getAttribute('data-correct') === st.chosen) {
          el.classList.add('opt-selected');
        }
      });
      card.dataset.chosen = st.chosen;
    }

    if (st.graded) {
      gradedCount++;
      if (st.correct) correctCount++;
      card.dataset.graded = 'true';
      var statusEl = card.querySelector('.q-status');
      var reveal = card.querySelector('.ans-reveal');
      var letter = card.getAttribute('data-letter');
      var answerText = card.getAttribute('data-answer');

      card.querySelectorAll('.opt').forEach(function(el) {
        if (el.getAttribute('data-correct') === 'true') el.classList.add('opt-correct');
      });

      if (st.correct) {
        card.classList.add('card-right');
        statusEl.textContent = '✓ 做对';
        statusEl.className = 'q-status right';
        reveal.innerHTML = '<span class="right-tag">✓ 答对了！</span> 正确答案：<span class="correct-text">' + letter + '</span>（' + answerText + '）';
      } else {
        card.classList.add('card-wrong');
        card.querySelectorAll('.opt').forEach(function(el) {
          if (el.classList.contains('opt-selected')) el.classList.add('opt-wrong');
        });
        statusEl.textContent = '✗ 做错';
        statusEl.className = 'q-status wrong';
        reveal.innerHTML = '<span class="wrong-tag">✗ 答错了！</span> 正确答案：<span class="correct-text">' + letter + '</span>（' + answerText + '）';
      }
      var btn = card.querySelector('.ans-btn');
      btn.disabled = false;
      btn.textContent = '显示答案';
    }
  });

  updateScore();
  // 跳转到上次位置
  if (data.lastPos) {
    window.scrollTo(0, data.lastPos);
  }
}

function renderHistory() {
  var hist = [];
  try {
    hist = JSON.parse(localStorage.getItem(HIST_KEY) || '[]');
  } catch (e) {}
  var box = document.getElementById('history-content');
  if (!hist.length) {
    box.innerHTML = '<div class="history-empty">暂无记录——完成一轮后点「清除进度重新开始」会在这里留下成绩。</div>';
    return;
  }
  var html = '<table><tr><th>时间</th><th>总题数</th><th>已做</th><th>答对</th><th>答错</th><th>正确率</th></tr>';
  hist.forEach(function(r) {
    html += '<tr><td>' + r.time + '</td><td>' + r.total + '</td><td>' + r.graded + '</td><td>' + r.correct + '</td><td>' + r.wrong + '</td><td><strong>' + r.pct + '%</strong></td></tr>';
  });
  html += '</table>';
  box.innerHTML = html;
}

function clearProgress() {
  var hist = [];
  try {
    hist = JSON.parse(localStorage.getItem(HIST_KEY) || '[]');
  } catch (e) {}
  // 记录当前成绩
  var wrong = gradedCount - correctCount;
  var pct = gradedCount > 0 ? Math.round(correctCount / gradedCount * 100) : 0;
  var now = new Date();
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  hist.push({
    time: now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate()) + ' ' + pad(now.getHours()) + ':' + pad(now.getMinutes()),
    total: document.querySelectorAll('.q-card').length,
    graded: gradedCount,
    correct: correctCount,
    wrong: wrong,
    pct: pct
  });
  try {
    localStorage.setItem(HIST_KEY, JSON.stringify(hist));
    localStorage.removeItem(STORE_KEY);
  } catch (e) {}
  location.reload();
}

// ===== 随机排序 =====
function shuffleArray(arr) {
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
  }
  return arr;
}

function applyOrder() {
  var grid = document.querySelector('.grid');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.q-card'));
  var order = null;
  try {
    order = JSON.parse(localStorage.getItem('fsx_order_v1') || 'null');
  } catch (e) {}
  // 首次打开：生成一个随机初始顺序
  if (!order || order.length !== cards.length) {
    order = [];
    for (var i = 0; i < cards.length; i++) order.push(i);
    shuffleArray(order);
    try {
      localStorage.setItem('fsx_order_v1', JSON.stringify(order));
    } catch (e) {}
  }
  // 按顺序重排卡片（data-idx 保持不变，进度按 data-idx 映射）
  var sorted = order.map(function(oi) { return cards[oi]; });
  sorted.forEach(function(card) { grid.appendChild(card); });
  // 重新显示编号
  sorted.forEach(function(card, i) {
    card.querySelector('.q-num').textContent = (i + 1);
  });
}

function clearAndShuffle() {
  // 记录成绩（同 clearProgress）并生成新的随机顺序
  var hist = [];
  try {
    hist = JSON.parse(localStorage.getItem(HIST_KEY) || '[]');
  } catch (e) {}
  // 只在已答题（做过至少1题）时才记录历史
  if (gradedCount > 0) {
    var wrong = gradedCount - correctCount;
    var pct = gradedCount > 0 ? Math.round(correctCount / gradedCount * 100) : 0;
    var now = new Date();
    function pad(n) { return n < 10 ? '0' + n : '' + n; }
    hist.push({
      time: now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate()) + ' ' + pad(now.getHours()) + ':' + pad(now.getMinutes()),
      total: (function() {
        var v = 0;
        document.querySelectorAll('.q-card').forEach(function(c) {
          if (c.style.display !== 'none') v++;
        });
        return v;
      })(),
      graded: gradedCount,
      correct: correctCount,
      wrong: wrong,
      pct: pct
    });
  }
  var order = [];
  for (var i = 0; i < document.querySelectorAll('.q-card').length; i++) order.push(i);
  shuffleArray(order);
  try {
    localStorage.setItem(HIST_KEY, JSON.stringify(hist));
    localStorage.setItem('fsx_order_v1', JSON.stringify(order));
    localStorage.removeItem(STORE_KEY);
  } catch (e) {}
  location.reload();
}

// 滚动节流保存
var scrollTimer = null;
window.addEventListener('scroll', function() {
  if (scrollTimer) return;
  scrollTimer = setTimeout(function() {
    saveProgress();
    scrollTimer = null;
  }, 500);
});

renderHistory();
initSourceSelect();
applyOrder();        // 先按保存的顺序排卡片
applySourceFilter(); // 再按来源过滤（隐藏其他来源的题）
loadProgress();      // 恢复进度（按 data-idx 映射，只统计可见题）
updateScore();       // 确保浮动窗总数正确（无进度数据时也要刷新）
</script>
<script async src="https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>
</body>
</html>''')

with open(OUT, "w", encoding="utf-8") as f:
    f.write(''.join(html_parts))

print(f"\nHTML已生成: {OUT}")
print(f"共 {len(shuffled)} 题")
