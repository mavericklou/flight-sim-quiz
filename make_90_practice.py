#!/usr/bin/env python3
"""合并90题初级练习 - 16:9宽屏 + 显示答案按钮"""
import json, re, os, random

WORK = os.path.expanduser("~/fsx_timu")

# ========== 加载现有题库用于查重 ==========
base = json.load(open(os.path.join(WORK, '金数据_基础_全部采集结果.json')))
mid = json.load(open(os.path.join(WORK, '金数据_中级_全部采集结果.json')))
with open(os.path.join(WORK, '模拟飞行理论题库_182题_打印版.html'), 'r') as f:
    html182 = f.read()

existing_all = set()
for d in base + mid:
    existing_all.add(d['q'])
for m in re.finditer(r'<span class="q-num">\d+\.</span>\s*(.+?)</div>', html182):
    existing_all.add(m.group(1).strip())

def norm(q):
    q = q.lower()
    q = re.sub(r'[\[\]【】()\u300c\u300d、，。？?：:；;\s"\'"\'\-—–]', '', q)
    return q

existing_norm = {norm(q) for q in existing_all}
CHECKED = set(existing_norm)  # 已检查过的题（含现有题库）

def is_new(q):
    n = norm(q)
    for en in CHECKED:
        common = len(set(n) & set(en))
        if common / max(len(n), len(en)) > 0.75:
            return False
    return True

def check_and_add(q):
    """验证新题不重复，加入检查集合"""
    global CHECKED
    if not is_new(q):
        return False
    CHECKED.add(norm(q))
    return True

# ========== PART 1: 新增30题中的小学组10题 ==========
part1 = [
    ("航空史", "世界上第一种量产的超音速客机是下列哪一款？",
     ["协和号（Concorde）", "波音747", "图-144", "C919"], 0),
    ("飞机结构", "飞机机翼上安装的翼尖小翼（Winglet）的主要作用是？",
     ["增加飞机长度", "减少诱导阻力", "增加燃油容量", "提高起落架强度"], 1),
    ("飞机操纵面", "安装在机翼后缘靠近机身一侧的操纵面，用于在起飞和着陆时增加升力的是？",
     ["副翼", "襟翼", "升降舵", "方向舵"], 1),
    ("飞行仪表", "飞机上用于测量飞机相对于周围空气速度的仪表是？",
     ["高度表", "空速表", "姿态仪", "垂直速度表"], 1),
    ("机场标志", "跑道上用于标示跑道中心线的白色虚线叫做？",
     ["跑道边线", "跑道中心线标志", "瞄准点标志", "接地带标志"], 1),
    ("陆空通话", "在陆空通话中，数字9的标准英文读法是？",
     ["nine", "niner", "ninth", "nein"], 1),
    ("英文词汇", "航空术语中Take-off的中文意思是？",
     ["着陆", "滑行", "起飞", "爬升"], 2),
    ("航空史", "我国自主研制的第一款喷气式支线客机的型号是？",
     ["C919", "运-20", "ARJ21", "AG600"], 2),
    ("飞机结构", "飞机机身的主要功能不包括以下哪项？",
     ["容纳乘客和货物", "连接机翼和尾翼", "产生升力", "安装各种设备和系统"], 2),
    ("机场标志", "机场滑行道上的黄色中心线的作用是？",
     ["引导飞机沿滑行道行驶", "标示滑行道边界", "指示停机位位置", "标示跑道入口"], 0),
]
print(f"PART1 加载: {len(part1)} 题")

# ========== PART 2: 薄弱领域30题 ==========
part2 = [
    ("陆空通话", "陆空通话中，飞行员回答「Roger」表示什么？",
     ["可以着陆", "已收到并明白", "请求复飞", "信号不好"], 1),
    ("陆空通话", "塔台指令「Line up and wait」的意思是？",
     ["进入跑道等待起飞许可", "立即起飞", "滑出跑道", "返回停机位"], 0),
    ("陆空通话", "通话中「Contact tower 118.1」的意思是？",
     ["联系塔台，频率118.1", "请求放行118.1", "跑道编号118", "高度118.1"], 0),
    ("陆空通话", "飞行员需要重新拉起飞机、绕一圈再次进近时，通话中使用的词是？",
     ["Go around", "Touch and go", "Hold short", "Line up"], 0),
    ("陆空通话", "空管指令「Maintain 3000 feet」的意思是？",
     ["爬升到3000英尺", "保持3000英尺高度", "下降到3000英尺", "离开3000英尺"], 1),
    ("飞行规则", "两架飞机迎面相遇时，正确的避让方法是？",
     ["各自向右转弯", "各自向左转弯", "高的避让低的", "快的避让慢的"], 0),
    ("飞行规则", "飞机在空中被另一架飞机超越时，正确的避让规则是？",
     ["被超越的飞机保持航向速度，超越飞机负责避让", "超越的飞机保持航向，被超越飞机让路", "两架飞机同时爬升", "速度快的永远优先"], 0),
    ("飞行规则", "夜间飞行时，飞机必须开启的灯光是？",
     ["客舱阅读灯", "航行灯和防撞灯", "着陆灯", "仪表背光"], 1),
    ("飞行规则", "客机巡航时选择在平流层底部飞行，主要原因是？",
     ["空气温度更高", "气流平稳、天气现象少", "飞机发动机效率最低", "便于看到地面"], 1),
    ("飞行安全", "起飞和着陆阶段要求乘客系好安全带，原因是？",
     ["防止起飞时睡着", "此阶段速度变化和颠簸最剧烈", "空乘便于服务", "法律规定必须系"], 1),
    ("英文词汇", "英文「cockpit」指的是飞机的？",
     ["客舱", "货舱", "驾驶舱", "行李舱"], 2),
    ("英文词汇", "缩写「ATC」的全称是？",
     ["Air Traffic Control", "Air Transport Company", "Aviation Training Center", "Airport Tower Control"], 0),
    ("英文词汇", "飞行速度术语中「V1」代表的是？",
     ["起飞决断速度", "抬轮速度", "失速速度", "最大巡航速度"], 0),
    ("英文词汇", "英文「aircraft」的中文意思是？",
     ["机场", "航空公司", "航空器", "空乘人员"], 2),
    ("英文词汇", "英文「runway」的中文意思是？",
     ["滑行道", "跑道", "停机坪", "航站楼"], 1),
    ("导航仪表", "飞机驾驶舱内的磁罗盘指示的是哪个方向？",
     ["地理北极", "磁北极", "正东方向", "航迹方向"], 1),
    ("导航仪表", "GPS的中文全称是？",
     ["全球定位系统", "全球导航卫星", "地理坐标系统", "卫星通信系统"], 0),
    ("导航仪表", "仪表着陆系统（ILS）中，提供左右方向引导的航向信标英文是？",
     ["Glide Slope", "Localizer", "Marker Beacon", "DME"], 1),
    ("导航仪表", "飞机起飞前，飞行员需要在导航系统中设置的关键信息是？",
     ["目的地机场和航线", "飞机涂装颜色", "乘客人数", "油箱容量"], 0),
    ("导航仪表", "机场二次雷达依靠机载什么设备应答识别飞机？",
     ["应答机（Transponder）", "广播电台", "手机信号", "气象雷达"], 0),
    ("民航机型", "国产大型运输机「运-20」的绰号是？",
     ["鲲龙", "鲲鹏", "飞豹", "猛龙"], 1),
    ("民航机型", "波音B737属于什么类型的客机？",
     ["单通道窄体客机", "双通道宽体客机", "支线涡桨客机", "水陆两栖飞机"], 0),
    ("民航机型", "世界两大干线客机制造商波音和空客的总部所在国是？",
     ["美国和法国", "美国和德国", "英国和法国", "美国和英国"], 0),
    ("民航机型", "支线客机通常指载客量在多少座以下？",
     ["50座", "100座", "200座", "300座"], 1),
    ("航空气象", "飞机飞行中遇到颠簸，最常见的诱因是？",
     ["穿越云层或对流天气区", "高空风平浪静", "飞机速度太慢", "燃油不足"], 0),
    ("航空气象", "夏季晴天午后，天空出现的像棉花糖一样的云叫？",
     ["层云", "积云", "卷云", "雨层云"], 1),
    ("航空气象", "跑道上有积雪时，机场在飞机起降前通常会？",
     ["除雪并检查跑道刹车效应", "等雪自然融化", "降低跑道限速", "关闭跑道灯"], 0),
    ("领航基础", "「航向」与「航迹」的主要区别是？",
     ["航向是机头指向，航迹是实际移动路径方向", "两者完全相同", "航向指地面方向，航迹指空中方向", "航向固定不变，航迹会变"], 0),
    ("领航基础", "无风条件下飞行时，地速与真空速的关系是？",
     ["地速大于真空速", "地速等于真空速", "地速小于真空速", "无法比较"], 1),
    ("领航基础", "磁罗盘上的「N」指示的是？",
     ["地理北极方向", "磁北极方向", "航向90度方向", "飞机机头方向"], 1),
]
print(f"PART2 加载: {len(part2)} 题")

# ========== PART 3: 新出50题初级题 ==========
part3 = [
    ("航空史", "世界第一架飞机「飞行者一号」的首次试飞地点是？",
     ["美国北卡罗莱纳州基蒂霍克", "法国巴黎", "英国伦敦", "德国柏林"], 0),
    ("航空史", "中国航空之父冯如的飞机是在哪里完成试飞成功的？",
     ["广州", "美国奥克兰", "北京", "上海"], 1),
    ("航空史", "世界上第一架喷气式客机是？",
     ["波音707", "德哈维兰彗星", "图-104", "卡拉维尔"], 1),
    ("航空史", "波音747客机的著名绰号是？",
     ["梦幻客机", "珍宝机（Jumbo Jet）", "环球霸王", "空中女王"], 1),
    ("航空史", "国产大飞机C919的制造商是？",
     ["中国商飞（COMAC）", "中国航空工业集团", "中航通飞", "上海飞机设计院"], 0),
    ("航空史", "被誉为「直升机之父」的航空先驱是？",
     ["莱特兄弟", "伊戈尔·西科斯基", "艾德温·林克", "冯如"], 1),
    ("航空史", "世界上最大的运输机安-225「梦幻」是由哪国设计制造的？",
     ["美国", "苏联（现乌克兰）", "中国", "法国"], 1),
    ("航空史", "世界上第一架实用型隐形战斗机F-117的绰号是？",
     ["夜鹰", "猛禽", "闪电", "战隼"], 0),
    ("飞机结构", "飞机机翼前缘可伸缩的「缝翼」主要作用是？",
     ["增加高速时的稳定性", "改善低速大迎角时的升力", "减小飞行阻力", "增加燃油容量"], 1),
    ("飞机结构", "飞机的水平尾翼由哪两部分组成？",
     ["水平安定面和升降舵", "垂直安定面和方向舵", "襟翼和副翼", "翼尖和整流罩"], 0),
    ("飞机结构", "飞机垂直安定面的主要作用是？",
     ["保持飞机方向稳定、防止偏航摆动", "产生升力", "控制俯仰", "承载货物"], 0),
    ("飞机结构", "大型客机的机身横截面最常用的形状是？",
     ["方形", "圆形或蛋形", "三角形", "梯形"], 1),
    ("飞机结构", "飞机的「翼展」指的是？",
     ["机翼前缘到后缘的距离", "左右翼尖之间的直线距离", "机翼的厚度", "机翼的面积"], 1),
    ("飞机结构", "前三点起落架相对于后三点的主要优势是？",
     ["地面滑跑视野好、方向稳定", "更适合土跑道", "重量更轻", "结构更简单"], 0),
    ("飞机结构", "飞机蒙皮的主要作用是？",
     ["承受气动载荷、保持机身外形", "装饰美观", "隔绝噪音", "储存燃油"], 0),
    ("操纵面", "飞机着陆瞬间将机头轻轻拉起的动作（拉平/Flare）主要使用？",
     ["副翼", "升降舵", "方向舵", "襟翼"], 1),
    ("操纵面", "方向舵偏转时，飞机的机头会？",
     ["绕纵轴滚转", "绕立轴左右偏转", "绕横轴俯仰", "保持不变"], 1),
    ("操纵面", "襟翼的三种常见类型不包括以下哪项？",
     ["简单襟翼", "富勒襟翼", "劈裂襟翼", "副翼襟翼"], 3),
    ("操纵面", "飞机起飞滑跑时，用来保持滑跑方向的主要操纵是？",
     ["副翼", "升降舵", "方向舵和前轮转向", "减速板"], 2),
    ("操纵面", "当升降舵配平片向上偏转时，升降舵会向哪个方向偏转？",
     ["同方向向上", "反方向向下", "不偏转", "左右偏转"], 1),
    ("飞行仪表", "空速表表盘上的白色弧线表示的是？",
     ["襟翼操作速度范围", "失速速度", "最大巡航速度", "不可超越速度"], 0),
    ("飞行仪表", "起飞前，飞行员需要在高度表上设定的气压基准是？",
     ["QNH（修正海压）", "标准大气压", "场压", "任意值"], 0),
    ("飞行仪表", "垂直速度表的读数单位通常是？",
     ["节", "英尺/分钟", "米/秒", "公里/小时"], 1),
    ("飞行仪表", "航向仪（陀螺罗盘）与磁罗盘相比的优势是？",
     ["靠陀螺稳定，转弯时不摆动", "更便宜", "不需要电源", "体积更小"], 0),
    ("飞行仪表", "「黑匣子」记录仪被设计成能够承受的条件不包括？",
     ["高温燃烧", "深海压力", "强烈撞击", "长期浸泡在强酸中"], 3),
    ("飞行仪表", "采用电子屏幕显示的飞机仪表系统（EFIS）俗称？",
     ["玻璃驾驶舱", "液晶面板", "数码座舱", "触摸屏系统"], 0),
    ("飞行仪表", "飞机上最基本的备用仪表通常包括？",
     ["磁罗盘和备用姿态仪", "GPS和手机", "雷达和应答机", "自动驾驶仪"], 0),
    ("机场标志", "跑道入口处白色横向条纹标志的作用是？",
     ["标示跑道入口位置", "指示着陆点", "标示跑道中心", "警告有障碍物"], 0),
    ("机场标志", "跑道上「瞄准点标志」的作用是？",
     ["标示接地区域", "标示跑道中点", "标示滑行道入口", "指示等待位置"], 0),
    ("机场标志", "机场风向袋（风斗）的作用是？",
     ["指示风向和大致风速", "装饰机场", "标示跑道方向", "指示停机位"], 0),
    ("机场标志", "机场三字代码「PEK」代表的是？",
     ["北京首都国际机场", "上海浦东机场", "广州白云机场", "成都天府机场"], 0),
    ("机场标志", "跑道编号「09/27」中，「09」端的磁航向约为？",
     ["9度", "90度", "09度", "270度"], 1),
    ("机场标志", "跑道等待线（holding position）标志的颜色和样式是？",
     ["白色实线", "黄色实线加虚线", "红色双线", "蓝色单线"], 1),
    ("机场标志", "停机坪（apron）的主要用途是？",
     ["飞机停放、上下旅客和装卸货物", "飞机起飞", "飞机着陆", "飞机维修"], 0),
    ("陆空通话", "陆空通话中「Wilco」的意思是？",
     ["收到了，将照办", "收到", "不同意", "稍等"], 0),
    ("陆空通话", "陆空通话中，字母「T」的标准读音是？",
     ["Tango", "Tower", "Tiger", "Tank"], 0),
    ("陆空通话", "通话指令「Squawk 7500」中的「Squawk」意思是？",
     ["设置应答机编码", "报告航向", "改变频率", "请求高度"], 0),
    ("陆空通话", "通话中「Stand by」的意思是？",
     ["稍等", "可以起飞", "请重复", "收到"], 0),
    ("陆空通话", "通话中「Say again」的意思是？",
     ["请重复一遍", "再见", "再说一次再见", "稍等"], 0),
    ("陆空通话", "通话中「Flight level 350」表示飞机高度为？",
     ["3500英尺", "35000英尺", "350米", "35000米"], 1),
    ("英文词汇", "英文「propeller」指的是飞机的？",
     ["螺旋桨", "机翼", "起落架", "发动机"], 0),
    ("英文词汇", "英文「navigation」的中文意思是？",
     ["通信", "导航", "气象", "维修"], 1),
    ("英文词汇", "英文「communication」的中文意思是？",
     ["导航", "通信", "管制", "调度"], 1),
    ("英文词汇", "英文「instrument」在航空中通常指？",
     ["仪表", "乐器", "工具", "设备"], 0),
    ("英文词汇", "英文「pilot」指的是？",
     ["飞行员", "乘客", "空乘", "地勤"], 0),
    ("飞行规则", "飞机在地面滑行时，接受谁的指挥？",
     ["塔台或地面管制", "航空公司", "机长独自决定", "机场广播"], 0),
    ("飞行规则", "下列哪种物品属于乘机禁止携带的？",
     ["打火机和易燃易爆品", "手机", "笔记本电脑", "书本"], 0),
    ("飞行规则", "飞机起降时要求打开遮光板的主要原因是？",
     ["便于乘客观察外部情况、协助发现异常", "让阳光晒进客舱", "方便空乘拍摄", "降低客舱亮度"], 0),
    ("飞行规则", "飞机高空飞行时在机尾留下白色凝结尾迹的成因是？",
     ["发动机废气中的水汽遇低温凝结", "飞机喷出的烟雾", "空气中的灰尘", "燃油泄漏"], 0),
]
print(f"PART3 加载: {len(part3)} 题")

# ========== 查重验证 ==========
print("\n=== 全部90题查重验证 ===")
all_questions = []
dup_found = False
for part_name, part in [("PART1", part1), ("PART2", part2), ("PART3", part3)]:
    for cat, q, opts, ans_idx in part:
        if not check_and_add(q):
            print(f"  ❌ [{part_name}] 重复: {q[:40]}")
            dup_found = True
        else:
            all_questions.append((cat, q, opts, ans_idx))

if dup_found:
    print("\n存在重复，请修改")
    exit(1)

print(f"✅ 全部 {len(all_questions)} 题通过查重（含3套题库+新增30题）")

# ========== 打乱 ==========
random.seed(20260730)
shuffled = all_questions[:]
random.shuffle(shuffled)

# ========== 生成HTML（16:9宽屏+答案按钮） ==========
OUT = os.path.join(WORK, "初级题库90题_练习版_宽屏.html")

html_parts = []
html_parts.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>模拟飞行 · 初级题库90题练习</title>
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
  color: #999;
  background: #f0f0f0;
  padding: 2px 12px;
  border-radius: 12px;
  margin-left: auto;
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
}
.opt-correct {
  background: #e8f8e8;
  border-color: #27ae60;
  color: #1e7a34;
  font-weight: bold;
  box-shadow: 0 0 0 1px #27ae60 inset;
}
.opt-correct::after { content: " ✅"; }
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
.ans-btn:hover { background: #1a4a80; }
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
.show { display: block; }
.footer {
  text-align: center;
  color: #999;
  font-size: 15px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}
</style>
</head>
<body>
<div class="container">
<h1>模拟飞行 · 初级题库90题练习</h1>
<div class="subtitle">含：新增10题 + 薄弱领域30题 + 全新50题 | 难度对标基础题库（小学组）| 点击「显示答案」查看解析</div>
<div class="grid">
''')

for i, (cat, q, opts, ans_idx) in enumerate(shuffled, 1):
    html_parts.append(f'<div class="q-card">')
    html_parts.append(f'<div class="q-top"><span class="q-num">{i}</span><span class="q-cat">{cat}</span></div>')
    html_parts.append(f'<div class="q-text">{q}</div>')
    for j, opt in enumerate(opts):
        # 点击前不标记正确项，用 data-correct 记录
        html_parts.append(f'<div class="opt" data-correct="{"true" if j == ans_idx else "false"}">{chr(65+j)}. {opt}</div>')
    html_parts.append(f'<div class="ans-area">')
    html_parts.append(f'<button class="ans-btn" onclick="toggleAns(this)">显示答案</button>')
    html_parts.append(f'<div class="ans-reveal">正确答案：<span class="correct-text">{chr(65+ans_idx)}</span>（{opts[ans_idx]}）</div>')
    html_parts.append(f'</div>')
    html_parts.append('</div>')

html_parts.append('''
</div>
<div class="footer">共 90 题 · 全部与三套现有题库及新增30题无重复 · 16:9宽屏适配 · 点击按钮显示答案</div>
</div>
<script>
function toggleAns(btn) {
  var card = btn.closest('.q-card');
  var reveal = card.querySelector('.ans-reveal');
  if (reveal.classList.contains('show')) {
    reveal.classList.remove('show');
    // 移除正确选项的高亮
    card.querySelectorAll('.opt-correct').forEach(function(el) {
      el.classList.remove('opt-correct');
    });
    btn.textContent = '显示答案';
  } else {
    reveal.classList.add('show');
    // 高亮正确选项
    card.querySelectorAll('.opt').forEach(function(el) {
      if (el.getAttribute('data-correct') === 'true') {
        el.classList.add('opt-correct');
      }
    });
    btn.textContent = '隐藏答案';
  }
}
</script>
</body>
</html>''')

with open(OUT, "w", encoding="utf-8") as f:
    f.write(''.join(html_parts))

print(f"\nHTML已生成: {OUT}")
print(f"共 {len(shuffled)} 题（打乱顺序）")
