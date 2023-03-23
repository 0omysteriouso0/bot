import discord
from discord.ext import commands
import pymongo
import json
import random
import copy
import datetime

url = 'mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
rpg = cluster["RPG"]["game"]
fboss = cluster["RPG"]["fightboss"]
bossrpg = cluster["RPG"]["boss"]

with open("monster.json", "r", encoding="utf-8") as data:
    mondata = json.load(data)
with open("weapon.json", "r", encoding="utf-8") as data:
    weapdata = json.load(data)
with open("pet.json", "r", encoding="utf-8") as data:
    petdata = json.load(data)
with open("skill.json", "r", encoding="utf-8") as data:
    skilldata = json.load(data)
with open("boss.json", "r", encoding="utf-8") as data:
    bossdata = json.load(data)


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.rareColor = {
            "basic": 0x16d070,
            "uncommon": 0x6bc6ff,
            "rare": 0xff9500,
            "exrare": 0xfff1ad,
            "boss": 0x7700b8,
            "active": 0xd558c4,
            "tomato": 0xf96c81
        }
        #1普通 綠, 2稀有 藍, 3罕見 橘, 4極罕見 淺黃, 5王 紅紫, 6特殊 紫, 7番茄 番茄色

        self.explore_bonus = 1

        #活動
        #活動名
        self.active = "程式之路"
        #活動素材
        activeMaterial = ["散落的程式碼", "散落的程式碼", "散落的程式碼"]
        activeboss = None
        activebossPet = []
        activebossWeapon = ""

        #Area
        self.allArea = [
            "休憩小鎮", "啟程草原", "礦石洞窟", "迷霧森林", "荒涼之地", "赤炎山谷", "寒霜高原", self.active
        ]
        #["休憩小鎮","啟程草原",
        # "礦石洞窟","迷霧森林","荒涼之地",
        # "炙炎山谷","寒霜高原","幻夢鄉都",
        # "惡魔地獄","眾神天堂","隱藏的世界",self.active]
        #areacolor = ["town", "grass", "cave", "forest", "marsh", "active"]
        self.areaColor = {
            "休憩小鎮": 0xffa8fc,
            "啟程草原": 0xafff4d,
            "礦石洞窟": 0x1c2ca6,
            "迷霧森林": 0x2a8609,
            "荒涼之地": 0xccbe66,
            "赤炎山谷": 0xf05400,
            "寒霜高原": 0x85f7ff,
            self.active: 0xbf70ff
        }

        #Weapon
        self.basicWeapon = weapdata["空手"]
        self.fieldWeapon = [
            weapdata["初心者長劍"], weapdata["初心者長弓"], weapdata["初心者魔杖"]
        ]

        #skill
        self.basicSkill = {"衝擊": skilldata["衝擊"]}

        #Material
        #goodMaterial
        basicMaterial = ["樹枝", "石頭", "鐵"]
        self.areaMaterial = {
            "休憩小鎮": basicMaterial,
            "啟程草原": ["番茄"] + basicMaterial,
            "礦石洞窟": ["鐵", "鑽石", "黑曜石"] + basicMaterial,
            "迷霧森林": ["樹枝", "絲綢", "線"] + basicMaterial,
            "荒涼之地": ["骨頭"] + basicMaterial,
            self.active: activeMaterial + basicMaterial
        }

        #Boss

        self.areaboss = {
            "休憩小鎮": {
                "Boss": bossdata["幸運之神莉潔絲汀"],
                "pet": [petdata["小番茄醬"], petdata["番茄醬"]],
                "godWeapon": weapdata["女神智杖"],
                "item": ["女神頭髮"]
            },
            "啟程草原": {
                "Boss": bossdata["番茄史萊姆王"],
                "pet": [petdata["番茄醬"], petdata["小番茄醬"]],
                "godWeapon": weapdata["蔬果劍"],
                "item": ["番茄"]
            },
            "礦石洞窟": {
                "Boss": bossdata["伊索斯科"],
                "pet": [petdata["水晶靈"], petdata["螢光塵仙"]],
                "godWeapon": weapdata["靈魂權杖"],
                "item": []
            },
            "迷霧森林": {
                "Boss": bossdata["遠古靈像"],
                "pet": [petdata["寵物南瓜"], petdata["寵物南瓜"]],
                "godWeapon": weapdata["石製長劍"],
                "item": ["遠古靈像武器兌換券", "遠古靈像寵物兌換券"]
            },
            "荒涼之地": {
                "Boss": None,
                "pet": ["小番茄醬", "番茄醬"],
                "godWeapon": "女神智杖",
                "item": []
            },
            self.active: {
                "Boss": bossdata.get(activeboss),
                "pet": activebossPet,
                "godWeapon": activebossWeapon
            },
        }

        allskillkey = set(skilldata.keys())
        #skill
        Warrior = {"斬擊", "十字斬", "劈砍", "複合斬"}
        Berserker = {"重擊", "狂傲亂舞", "咆嘯", "覺醒"} | Warrior
        Paladin = {"防禦強化", "光之加護", "聖光彈", "聖王的制裁", "神之軀"} | Warrior
        Elementer = {"星斬", "烈焰斬", "寒冰斬", "魂斬"} | Warrior

        Archer = {"射擊", "二重矢", "狙擊", "隱匿", "敏捷"}
        Assassin = {"突刺", "割裂", "貫穿", "劇毒矢"} | Archer
        Thief = {"煙霧", "撒菱", "奇幻禮包", "虛晃一擊"} | Archer
        Ranger = {"疾風矢", "烈焰箭", "寒冰箭"} | Archer

        Wizard = {"爆炎彈", "波濤", "風刃斬", "急凍術"}
        Priest = {"冰雪風", "燦炎星火", "聖光彈", "痊癒光輝", "大地治癒", "禱祝", "天籟"} | Wizard
        Summoner = {"冰雪風"} | Wizard
        Mage = {"冰雪風"} | Wizard

        bakulaze = {"爆裂魔法"}

        positionskill = set(
            (*Warrior, *Berserker, *Paladin, *Elementer, *Archer, *Assassin,
             *Thief, *Ranger, *Wizard, *Priest, *Summoner, *Mage, *bakulaze))

        lv5skill = {"治癒"}
        lv7skill = {"水流", "微風", "火焰"}
        lv50skill = {"毒龍"}

        lvskill = set((*lv7skill, *lv50skill))
        self.skill_list = {
            "cannotlearn":
            {"魔力彈", "打擊", "自爆", "康康海星", "挑釁", "コーヒーの祝福", "萬聖齊聚"},
            "alllv": allskillkey - lvskill,
            "lvskill": {
                5: lv5skill,
                7: lv7skill,
                50: lv50skill
            },
            "通用": allskillkey - positionskill,
            "劍士": Warrior,
            "狂戰士": Berserker,
            "聖騎士": Paladin,
            "魔劍士": Elementer,
            "遊俠": Archer,
            "刺客": Assassin,
            "盜賊": Thief,
            "幻影遊俠": Ranger,
            "法師": Wizard,
            "牧師": Priest,
            "魔導師": Mage
        }

    def monsterSet(self, area):
        self.area = area
        monsters = []
        for monster in mondata[self.area]:
            monsters.extend([monster] * monster["機率"])
        self.monster = random.choice(monsters)
        self.monName = self.monster["名稱"]
        self.monPfp = self.monster.get("頭像")
        self.monAtk = self.monster["攻擊力"]
        self.monDef = self.monster["防禦力"]
        self.monExp = self.monster["經驗值"]
        self.monMoney = self.monster["金錢"]

    def playerSet(self, player):
        if player == None:
            return "你還沒有登入過啦"
        self.result = player
        self.teamid = self.result["teamid"]
        self.team = self.result["teamName"]
        self.teamMember = self.result["teamMember"]
        self.id = self.result["id"]
        self.name = self.result["name"]
        self.tag = self.result["tag"]
        self.area = str(self.result["地區"])
        self.state = self.result["狀態"]
        self.huntedBoss = self.result["已狩獵boss"]
        self.boss = self.result["boss"]
        self.hunted = self.result["已狩獵"]
        self.deaths = self.result["死亡數"]
        self.achievement = self.result["成就"]
        self.title = self.result["稱號"]
        self.pet = self.result["寵物"]
        self.position = self.result["職位"]
        self.parttime = self.result["副職"]
        self.bag = self.result["背包"]
        self.weapon = self.result["武器"]
        self.skill = self.result["技能"]
        self.lv = int(self.result["等級"])
        self.exp = int(self.result["exp"])
        self.nowHp = int(self.result["nowHp"])
        self.maxHp = int(self.result["maxHp"]) + self.result['maxHp點']
        self.nowSta = self.result["nowSta"]
        self.useSta = self.result["useSta"]
        self.maxSta = self.result["maxSta"] + self.result['maxSta點']
        self.basicAtk = self.result["Atk"] + self.result['Atk點']
        self.basicDef = self.result["Def"] + self.result['Def點']
        self.basicAgi = self.result["Agi"] + self.result['Agi點']
        self.basicLuc = self.result["Luc"] + self.result['Luc點']
        self.AP = self.result["技能點"]
        self.Atk = self.basicAtk + (self.weapon["攻擊力"] *
                                    (1 + self.weapon["熟練度"] / 150))
        self.Def = self.basicDef + (self.weapon["防禦力"] *
                                    (1 + self.weapon["熟練度"] / 1000))
        self.Agi = self.basicAgi + (self.weapon["敏捷度"] *
                                    (1 + self.weapon["熟練度"] / 1000))
        self.Luc = self.basicLuc + (self.weapon["運氣值"] *
                                    (1 + self.weapon["熟練度"] / 1000))
        self.money = int(self.result["money"])
        self.pfp = self.result["頭像"]
        self.worktime = self.result["打工時間"]
        self.advenrest = self.result["探險休息"]
        self.huntrest = self.result["狩獵休息"]
        self.enemy = self.result["對戰對象"]
        self.turn = self.result["對戰"]

    def weaponSet(self, weapon):
        weapon["品質顏色"] = self.rareColor[weapon["品質"]]
        for x, y in weapon.items():
            if type(y) == list:
                weapon[x] = random.randint(y[0], y[1])
        return weapon

    def petSet(self, pet):
        with open("boss.json", "r", encoding="utf-8") as i:
            mypet = json.load(i)[pet]
        mypet["品質"] = self.rareColor[mypet["品質"]]
        return mypet

    def bossSet(self, boss):
        result = boss
        self.bossId = result["_id"]
        self.bossName = result["名稱"]
        self.bossLv = result["lv"]
        self.bossState = result["狀態"]
        self.bossStoring = result["蓄力"]
        self.bossPet = result["pet"]
        #list(map(lambda x :Core.petSet(self,x), result["pet"]))
        self.bossItem = result["item"]
        self.bossWeapon = Core.weaponSet(self, result["godWeapon"])
        self.bossSkill = result["普攻"]
        self.bossDodgeSkill = result.get("迴避", [])
        self.bossSpecial = result["大招"]
        self.bossExp = int(result["經驗值"])
        self.bossNowHp = int(result["nowHp"])
        self.bossMaxHp = int(result["maxHp"])
        self.bossAtk = int(result["Atk"])
        self.bossDef = int(result["Def"])
        self.bossAgi = int(result["Spd"])
        self.bossLuc = int(result["Luc"])
        self.bossMoney = int(result["金錢"])
        self.bossPfp = result["頭像"]
        self.bossPicture = result["大圖"]

    def getAch(self, newAchivement, color, type=""):
        self.achievement[f"《{type}成就》" + newAchivement] = color
        rpg.update_one({"id": self.id}, {"$set": {"成就": self.achievement}})
        return f"✨{self.name} 獲得{type}成就✨\n「{newAchivement}」"

    def isdead(self):
        embed = discord.Embed(title=f"您現在為死亡狀態", color=0x8a8a8a)
        embed.set_author(name=f"{self.name}")
        embed.set_footer(text="輸入 /resurrect 來復活喔")
        return embed

    def check(self):
        if "死亡" in self.state:
            embed = discord.Embed(title=f"您現在為死亡狀態", color=0x8a8a8a)
            embed.set_author(name=f"{self.name}")
            embed.set_footer(text="輸入 /resurrect 來復活喔")
            return embed

        elif fboss.count_documents({"id": self.id}) != 0:
            return f"{self.name}別在打王途中分心"

        elif "打工" in self.state:
            delta_time = datetime.datetime.now() - self.worktime
            workingtime = str(delta_time).replace("days,", ":")
            workingtime = workingtime.split(":")
            if len(workingtime) == 4: day, hr, m, sec = workingtime
            else:
                day = 0
                hr, m, sec = workingtime
            works = random.choice(["塗水泥", "澆花", "點餐", "結帳", "幫史萊姆按摩"])
            day = "" if day == 0 else f"{day}天"
            hr = "" if hr == 0 else f"{hr}小時"
            m = "" if m == 0 else f"{m}分鐘"
            sec = "" if sec == 0 else f"{int(float(sec))}秒"
            worktime = day + hr + m + sec

            getmoney = int(self.useSta * 10)
            return f"{self.name}正在幫忙{works}\n目前工作了{worktime},賺了{getmoney}元"

        elif self.money < 0:
            return f"{self.name}負債累累啊...\n用/work賺錢吧"
        else:
            return None

    def fightcheck(self):
        if self.weapon["耐久度"] != "無法破壞":
            if self.weapon["耐久度"] <= 0:
                rpg.update_one({"id": self.id},
                               {"$set": {
                                   "武器": self.basicWeapon
                               }})
                return {
                    "content": f"{self.name}的{self.weapon['名稱']}壞掉了",
                    "type": None
                }

        if self.nowSta <= 0:
            return {"content": f"{self.name}累倒了...", "type": "stop"}
        rpg.update_one({"id": self.id},
                       {"$inc": {
                           "nowSta": random.randint(-2, 0)
                       }})

        if self.weapon["耐久度"] != "無法破壞":
            self.weapon["耐久度"] -= random.randint(1, 2)

        self.weapon["熟練度"] += random.randint(1, 2)
        rpg.update_one({"id": self.id}, {"$set": {"武器": self.weapon}})
        return {"content": None, "type": None}

    def dead(self, killer, pfp=None):
        if "重生水晶" not in self.bag:
            if pfp == None:
                pfp = self.pfp
            print(self.id)
            embed = discord.Embed(title=f'你被{killer}打倒了...', color=0x8a8a8a)
            embed.set_thumbnail(url=pfp)
            # embed.add_field(name=f"/b",value="",inline=False)
            embed.set_footer(text="輸入 /resurrect 來復活喔")
            rpg.update_one({"id": self.id}, {"$set": {"狀態": ["死亡"]}})
            return embed
        else:
            Core.usedItem(self, "重生水晶")
            rpg.update_one({"id": self.id}, {"$set": {"nowHp": self.maxHp}})
            return f"{self.name}因為背包中的重生水晶而復活了"

    def lvup(self, player):
        #update lv & exp
        self.exp -= (self.lv) * 20
        self.lv += 1
        rpg.update_one({"id": self.id}, {"$set": {"exp": self.exp}})
        rpg.update_one({"id": self.id}, {"$set": {"等級": self.lv}})
        #Each one Values
        lvValues = [
            random.randint(30, 40),
            random.randint(3, 6),
            random.randint(2, 4),
            random.randint(4, 7),
            random.randint(1, 3),
            random.randint(2, 4)
        ]
        #lvValues = maxHp, Def, Agi, Atk, Luc, Sta
        positionValues = {
            "冒險者": {},
            "劍士": {
                "Atk": 1,
                "Def": 1
            },
            "聖騎士": {
                "Def": 4
            },
            "狂戰士": {
                "Atk": 6,
                "Def": -2
            },
            "魔劍士": {
                "Atk": 2,
                "Def": 2
            },
            "遊俠": {
                "Agi": 2
            },
            "刺客": {
                "Agi": 2,
                "Atk": 2
            },
            "盜賊": {
                "Agi": 2,
                "Luc": 2
            },
            "幻影遊俠": {
                "Agi": 4
            },
            "法師": {
                "Atk": 2
            },
            "牧師": {
                "Luc": 4
            },
            "召喚師": {
                "Atk": 2,
                "Luc": 2
            },
            "爆裂法師": {
                "Atk": 7
            },
        }

        rpg.update_one({"id": self.id},
                       {"$inc": positionValues[self.position]})

        #update sp
        rpg.update_one({"id": self.id}, {
            "$inc": {
                "maxHp": lvValues[0],
                "Atk": lvValues[3],
                "Def": lvValues[1],
                "Agi": lvValues[2],
                "Luc": lvValues[4],
                "maxSta": lvValues[5]
            }
        })
        playerinfo = rpg.find_one({"_id": self.id})
        newHp = playerinfo["maxHp"]

        rpg.update_one({"_id": self.id}, {"$set": {"nowHp": newHp}})
        maxHp = lvValues[0] + positionValues[self.position].get("Hp", 0)
        Def = lvValues[1] + positionValues[self.position].get("Def", 0)
        Agi = lvValues[2] + positionValues[self.position].get("Agi", 0)
        Atk = lvValues[3] + positionValues[self.position].get("Atk", 0)
        Luc = lvValues[4] + positionValues[self.position].get("Luc", 0)
        maxSta = lvValues[5] + positionValues[self.position].get("Sta", 0)
        self.maxHp = maxHp
        self.Atk = Atk
        self.Def = Def
        self.Agi = Agi
        self.Luc = Luc
        self.maxSta = maxSta
        rpg.update_one({"id": self.id}, {"$inc": {"技能點": 2}})
        if self.lv % 5 == 0:
            self.getSomething(playerinfo, "技能卷軸")

        if self.lv % 10 == 0:
            rpg.update_one({"id": self.id}, {"$inc": {"技能點": 3}})
        n = None
        if self.lv == 3:
            n = "魔力彈"
            rpg.update_one({"id": self.id},
                           {"$set": {
                               "技能." + n: skilldata[n]
                           }})
        elif self.lv == 5:
            n = "打擊"
            rpg.update_one({"id": self.id},
                           {"$set": {
                               "技能." + n: skilldata[n]
                           }})
        elif self.lv == 10:
            n = "自爆"
            rpg.update_one({"id": self.id},
                           {"$set": {
                               "技能." + n: skilldata[n]
                           }})
        if n:
            content = "恭喜你習得了" + n
        else:
            content = ""

        #lvup embed
        embed = discord.Embed(title=f"{self.name}你已升級成等級: Lv.{self.lv}",
                              color=0x16d070)
        embed.set_thumbnail(url=self.pfp)
        embed.add_field(name="生命值", value=f"+{maxHp}", inline=False)
        embed.add_field(name="體力值", value=f"+{maxSta}", inline=False)
        embed.add_field(name="攻擊力", value=f"+{Atk}", inline=False)
        embed.add_field(name="防禦力", value=f"+{Def}", inline=False)
        embed.add_field(name="敏捷度", value=f"+{Agi}", inline=False)
        embed.add_field(name="運氣值", value=f"+{Luc}", inline=False)
        if content:
            return (embed, content)
        else:
            return embed

    def getSomething(self, player, item, num = 1):
        if type(item) == dict:
          n = 0
          for i in range(num):
            if self.bag.get(item["名稱"]) == None:
                self.bag[item["名稱"]] = item
            else:
                while self.bag.get(item["名稱"] + f"({n})") != None:
                    n += 1
                item["名稱"] = item["名稱"] + f"({n})"
                self.bag[item["名稱"]] = item

        elif item in self.bag.keys():
            self.bag[item] += num

        else:
            self.bag[item] = num
        rpg.update_one({"_id": self.id}, {"$set": {"背包": self.bag}})

    def usedItem(self, item):
        if type(self.bag[item]) == dict:
            del self.bag[item]
            rpg.update_one({"_id": self.id}, {"$set": {"背包": self.bag}})
        elif self.bag[item] > 1:
            self.bag[item] -= 1
            rpg.update_one({"_id": self.id}, {"$set": {"背包": self.bag}})
        else:
            del self.bag[item]
            rpg.update_one({"_id": self.id}, {"$set": {"背包": self.bag}})
