import discord
from discord.ext import commands
from dislash import InteractionClient
import pymongo
import random,asyncio
import os 
import subprocess
import json
import datetime
import asyncio
import keep_alive
import dns


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='sf-', intents = intents, help_command = None)
inter_client = InteractionClient(bot)

url='mongodb+srv://bot0:ZhlzqNks0ADgkE8l@cluster0.pkbt3.mongodb.net/Cluster0?retryWrites=true&w=majority'
cluster = pymongo.MongoClient(url)
# db = cluster["bot"]["money"]
# rpg = cluster["bot"]["game"]
# rpgBoss= cluster["bot"]["game_boss"]
# shop= cluster["bot"]["shop"]
# save= cluster["bot"]["save"]
# rpgset= cluster["bot"]["rpgset"]
rpg = cluster["RPG"]["game"]
fboss = cluster["RPG"]["fightboss"]
bossdata = cluster["RPG"]["boss"]

with open("weapon.json","r",encoding="utf-8") as data:
    weapdata = json.load(data)
with open("skill.json","r",encoding="utf-8") as data:
    skilldata = json.load(data)

async def startcode(inter):
    user = bot.get_user(inter)
    if rpg.count_documents({"id": user.id}) != 0:
      await inter.reply(f'{user.name}你已登入過')
      return
    print(inter)
    #Hp, Atk, Def, Agi, Luc, Sta
    basicValues=[random.randint(100,125),
                  random.randint(10,15),
                  random.randint(7,10),
                  random.randint(5,7),
                  random.randint(2,5),
                  random.randint(20,40)]
    post = {
        "_id": user.id, 
        "id": user.id, "tag":user.mention.replace("!",""),
        "name":user.name, "職位":"冒險者", "頭像":str(user.avatar_url),
        "等級":1, "exp":0,
        "maxHp":basicValues[0], "nowHp":basicValues[0],
        "Atk":basicValues[1], "Def":basicValues[2],
        "Agi":basicValues[3], "Luc":basicValues[4],
        "maxSta":basicValues[5], "nowSta":basicValues[5],"useSta" : 0,
        "money":200, "背包":{},
        "武器":weapdata["空手"], "裝備":None,'寵物':None, 
        "技能":{"衝擊":skilldata["衝擊"]}, "狀態":[],"回合":0,
        "地區":"啟程草原", "副職":None,
        "成就":{}, "稱號":None, "職位列表":[],
        "teamid":user.id,"teamName":None,"teamMember":[user.mention.replace("!","")],
        "boss":False, "已狩獵boss":{}, "已狩獵":{},
        "對戰對象":int(), "對戰":False,
        "死亡數":0, 
        "狩獵休息":[datetime.datetime.now(), 0], 
        "探險休息":[datetime.datetime.now(), 0], 
        "打工時間":0,
        "技能點":0, "每日登入":0, "連續登入":0, "每日爆裂":0,
        'maxHp點':0, "Atk點":0, "Def點":0, "Agi點":0, "Luc點":0, "maxSta點":0
        }
    rpg.insert_one(post)
    await inter.reply('登入成功')
    return
'''
class MyNewHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():
           command_signatures = [self.get_command_signature(c) for c in commands]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

bot.help_command = MyNewHelp()
'''

    


@bot.event
async def on_ready():

    for all in rpg.find():
      rpg.update_many({}, {"$set":{"狩獵休息":(datetime.datetime.now(), 0)}})
      rpg.update_many({}, {"$set":{"探險休息":(datetime.datetime.now(), 0)}})
    print(f'目前登入身份：{bot.user}')
    channel = bot.get_channel(951448851120812094)
    await channel.send("我復活啦\\\\(･◡･)/")
    status_w = discord.Status.idle
    restOn = 0
    while True:
      rabbit=random.choice(["請問您今天要來點兔子嗎?","請問您今天要來點兔子嗎??","請問您今天要來點兔子嗎?~BLOOM~","請問您今天要來點兔子嗎？？ 〜Sing For You〜","請問您今天要來點兔子嗎？？ 〜Dear My Sister〜"])
      kerei=random.choice(["美味的麻婆拉麵","如何在家做出麻婆拉麵","星爆氣流斬的安全事項","關於爆裂魔法你不知道的兩三事","三秒升級麻婆拉麵小撇步"])
      kereiGame=random.choice(["可以吃的魔法海星","工作小遊戲","星爆臉","星爆棄療傘","番茄醬","智乃的臉","惠惠說"])
      rabbitCD=random.choice(["ぽっぴんジャンプ♪","Daydream café","宝箱のジェットコースター","ノーポイッ！","ときめきポポロン♪","cup of chino","チマメ隊&千マメ隊","セカイがカフェになっちゃった！","しんがーそんぐぱやぽやメロディー","天空カフェテリア","なかよし！○！なかよし！","魔法少女チノ","怪盗ラパン"])
      await asyncio.sleep(30)
      activity_w0 = discord.Activity(type=discord.ActivityType.watching, name=rabbit)
      activity_w1 = discord.Activity(type=discord.ActivityType.listening, name=rabbitCD)
      activity_w=random.choice([activity_w0,activity_w1])
      activity_w3 = discord.Activity(type=discord.ActivityType.watching, name=kerei)
      activity_w4 = discord.Activity(type=discord.ActivityType.playing, name=kereiGame)
      activity_w=random.choice([activity_w3,activity_w4])
      await bot.change_presence(status= status_w, activity=activity_w)

      rpg.update_many({"狀態":{"$in": ["打工"]}, "地區":"休憩小鎮"}, {"$inc":{"nowSta":-1, "useSta":1, "money":10}}) 
      
      restOn+=1

      if restOn == 3:
        for player in rpg.find():
          player = {"id": player["id"]}
          playerdata = rpg.find_one(player)
          if playerdata["nowSta"]<playerdata["maxSta"] and "打工" not in playerdata["狀態"] and playerdata["地區"] == "休憩小鎮":
            rpg.update_one(player, {"$inc":{"nowSta":1}})

          elif playerdata["nowSta"]<=0 and playerdata["地區"] == "休憩小鎮":
            if len(playerdata["狀態"]) == 1:
              newstate = []
            else:
              newstate = playerdata["狀態"].remove("打工")
            rpg.update_one(player, {"$set":{"狀態":newstate}})
            print(bot.get_user(playerdata["id"]))
            author = bot.get_user(playerdata["id"])
            await author.send("打工結束，你沒體力了")
            rpg.update_one(player, {"$set":{"nowSta":0}})
        restOn = 0

      
      

@bot.command(hidden=True)
async def test(ctx, words=None):
  print("Hi")
  if not words:
    words = "Hello"
  # for player in rpg.find():
  #   player = {"id": player["id"]}
  #   playerdata = rpg.find_one(player)
  #   print(playerdata["name"])
  #   if type(playerdata["探險休息"]) == int:
  #     rpg.update_one({"id":player},{"$set":{"探險休息":(datetime.datetime.now(), 30)}})
  #   if type(playerdata["狩獵休息"]) == int:
  #     rpg.update_one({"id":player},{"$set":{"狩獵休息":(datetime.datetime.now(), 0)}})
  await ctx.send(words)
  await ctx.message.delete()
  
@bot.command(hidden=True)
async def load(ctx,extension):
  try:
    bot.load_extension(f"cmds.{extension}")
  except discord.ext.commands.errors.ExtensionNotFound:
    await ctx.send(f"there isn't {extension} extension")
  except discord.ext.commands.errors.ExtensionAlreadyLoaded:
    await ctx.send(f"{extension} is already loaded")
  else:
    await ctx.send(f"Load {extension} done")

@bot.command(hidden=True)
async def unload(ctx,extension):
  try:
    bot.unload_extension(f"cmds.{extension}")
  except discord.ext.commands.errors.ExtensionNotFound:
    await ctx.send(f"there isn't {extension} extension")
  except discord.ext.commands.errors.ExtensionNotLoaded:
    await ctx.send(f"{extension} is already unloaded")
  else:
    await ctx.send(f"Unload {extension} done")

@bot.command(hidden=True)
async def reload(ctx,extension):
  try:
    bot.reload_extension(f"cmds.{extension}")
  except discord.ext.commands.errors.ExtensionNotLoaded:
    await ctx.send(f"there isn't {extension} extension")
  else:
    await ctx.send(f"Re-Load {extension} done")

@bot.command()
async def help(ctx, *input):
  version = "beta 2.0.0"
  if len(input)== 0:
    embed=discord.Embed(title='\*\***指令列表**\*\*', description="前墜為sf-\n(可使用 sf-help <command> 獲取該指令更多資訊)")
    embed.set_author(name="番茄醬小助手",    
                      icon_url='https://cdn.discordapp.com/attachments/870850786131853343/944966728784445510/tomato_girl.gif')
    embed.add_field(name=f"初始設定",
      value = "-"*20 + "\n" +
      "start" + " "*4 + "開始遊戲" + "\n" +
      "position" + " "*4 + "職位表" + "\n" +
      "transfer" + " "*4 + "轉職" + "\n" +
      "restart" + " "*4 + "轉生" + "\n" +
      "rename" + " "*4 + "改名" + "\n" +
      "pfp" + " "*4 + "修改頭像" + "\n" +
      "weaponname" + " "*4 + "改武器名" + "\n" +
      "petname" + " "*4 + "改寵物名" + "\n" +
      "-"*20 ,
      inline=False
    )

    embed.add_field(name=f"**查看自我訊息**",
      value = "-"*20 + "\n" +
      "info" + " "*4 + "確認能力" + "\n" +
      "bag" + " "*4 + "背包" + "\n" +
      "weapon" + " "*4 + "查看武器" + "\n" +
      "pet" + " "*4 + "查看寵物" + "\n" +
      "-"*20 ,
      inline=False
    )

    embed.add_field(name=f"**使用物品**",
      value = "-"*20 + "\n" +
      "eat" + " "*4 + "吃東西" + "\n" +
      "skillup" + " "*4 + "強化技能" + "\n" +
      "weaponup" + " "*4 + "查看武器" + "\n" +
      "equip" + " "*4 + "裝備武器" + "\n" +
      "summon" + " "*4 + "裝備寵物" + "\n" +
      "-"*20 ,
      inline=False
    )
    
    embed.add_field(name=f"**行動**",
      value = "-"*20 + "\n" +
      "hunt" + " "*4 + "狩獵" + "\n" +
      "explore" + " "*4 + "探險" + "\n" +
      "heal" + " "*4 + "回復" + "\n" +
      "work" + " "*4 + "打工" + "\n" +
      "rest" + " "*4 + "取消打工" + "\n" +
      "-"*20 ,
      inline=False
    )

    embed.add_field(name=f"**戰鬥**",
      value = "-"*20 + "\n" +
      "boss" + " "*4 + "打王" + "\n" +
      "skill" + " "*4 + "使用技能/技能列表" + "\n" +
      "-"*20 ,
      inline=False
    )
    
    embed.add_field(name=f"**區域**",
      value = "-"*20 + "\n" +
      "map" + " "*4 + "地圖" + "\n" +
      "teleport" + " "*4 + "傳送" + "\n" +
      "-"*20 ,
      inline=False
    )

    embed.add_field(name=f"**other**",
      value = "-"*20 + "\n" +
      "other" + " "*4 + "一些鮮為人知的功能" + "\n" +
      "question" + " "*4 + "常見問題" + "\n" +
      "-"*20 ,
      inline=False
    )

    embed.timestamp = datetime.datetime.utcnow()
    url = random.choice(["https://cdn.discordapp.com/avatars/825730483601276929/ebeb37bf8ec00ad257b17e8411580931.webp?size=1024",
    "https://cdn.discordapp.com/avatars/712814606363394169/e3449cab76089ec95d64ecb1d7abdade.webp?size=1024",
    'https://cdn.discordapp.com/attachments/870850786131853343/944965966993981510/dotpict_animation_20211017_000239.gif'
    ])
    #text=random.choice(["繪師 moooooon","特別感謝 可可"])
    text="繪師 moooooon"
    embed.set_footer(icon_url = url,
    text="Bot made by starfish"+" "*4 + text+" "*4 + "\nBot version: "+version)
    await ctx.reply(embed = embed)
    
  elif len(input)== 1:
    pass

  elif len(input)> 1:
    pass

  else:
    pass
    

    
    
    
  
  return

@bot.event
async def on_message(message):
  
 #print(message.content)
  #if 
  if message.author.id in [825730483601276929, 712814606363394169]:
    if message.content == 'gm-test':
      await message.channel.send("hi")
    elif message.content == 'gm-resistance':
      rpg.update_one({"id":message.author.id},
        {"$inc":{"Def": 10000000}})
      await message.channel.send("you are invincible now", reference=message)
    elif message.content == 'gm-unresistance':
      rpg.update_one({"id":message.author.id},
        {"$inc":{"Def": -10000000}})
      await message.channel.send("OK, undo", reference=message)
      
    elif message.content == 'gm-resurrect':
      state = rpg.find_one({"id":message.author.id})["狀態"]
      maxhp = rpg.find_one({"id":message.author.id})["maxHp"]
      try:
        state.remove('死亡')
      except:
        pass
      rpg.update_one({"id":message.author.id},
        {"$set":{"nowHp": maxhp}})
      rpg.update_one({"id":message.author.id},
        {"$set":{"狀態": state}})
      await message.channel.send("you are alive", reference=message)
      
    elif message.content == 'gm-rest':
      maxSta = rpg.find_one({"id":message.author.id})["maxSta"]
      rpg.update_one({"id":message.author.id},
        {"$set":{"nowSta": maxSta}})
      await message.channel.send("you have full Sta now", reference=message)
      
    elif message.content.startswith('gm-learn'):
      tmp = message.content.split(" ")
      with open("skill.json","r",encoding="utf-8") as data:
        skilldata = json.load(data)
      skill = tmp[1]
      id = message.author.id 
      if len(tmp)==3: id = int(tmp[2])
      me = rpg.find_one({"id":id})
      myskill = me["技能"]
      if skilldata.get(skill) == None:
        await message.channel.send(f"並沒有=v=", reference=message)
        return
      #skilldata[skill]["CD"] = 0
      myskill[skill] = skilldata[skill]
      myskill = rpg.update_one({"id":id}, {"$set":{"技能":myskill}})
      await message.channel.send(f"{me['name']}習得了{skill}", reference=message)

  elif message.author.id == 916529064200781825:
    # print(message.content)
    if message.content.startswith(f"gm-start"):
      inter = int(message.content.split(" ")[1])
      await startcode(inter)
    elif message.content.endswith(f"獲得成就✨\n「冷血殺手」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》冷血殺手"] = 0x8f1e1e
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})
      
    elif message.content.endswith(f"獲得**隱藏**成就✨\n「請問您今天要來點兔子嗎?」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《隱藏成就》請問您今天要來點兔子嗎?"] = 0xc3ecef
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得**隱藏**成就✨\n「佐佐木小次郎?」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《隱藏成就》佐佐木小次郎?"] = 0xc4c0ea
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})
      
    elif message.content.endswith(f"獲得成就✨\n「初心冒險者」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》初心冒險者"] = 0xfff4e0
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})
      
    elif message.content.endswith(f"獲得成就✨\n「中級冒險者」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》中級冒險者"] = 0x70ffa2
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得成就✨\n「老練冒險者」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》老練冒險者"] = 0x70e7ff
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得成就✨\n「頂尖冒險者」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》頂尖冒險者"] = 0x767bfe
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得成就✨\n「終極冒險者」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》終極冒險者"] = 0xc885ff
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得成就✨\n「大師」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》大師"] = 0xff85c6
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得成就✨\n「頂點的王者」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《成就》頂點的王者"] = 0xff5252
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})

    elif message.content.endswith(f"獲得**特殊**成就✨\n「Lv.Max」"):
      tag = message.content.split(" ")[0].replace("✨", "")
      achievement = rpg.find_one({"tag":tag})["成就"]
      achievement[f"《特殊成就》Lv.Max"] = 0xffc800
      rpg.update_one({"tag":tag}, {"$set":{"成就":achievement}})
      
    
  await bot.process_commands(message)
  
  

for cmdFile in os.listdir("./cmds"):
  if cmdFile.endswith(".py"):    
    bot.load_extension(f"cmds.{cmdFile[:-3]}")

keep_alive.keep_alive()
try:
   print("okk")
   bot.run("OTE2NTI5MDY0MjAwNzgxODI1.YareNQ.qKFtdvI0d3tuEdUmhr48tG7Ahw0")
except discord.errors.HTTPException: 
  print("error")
  subprocess.call("kill 1", shell=True)
  bot.run("OTE2NTI5MDY0MjAwNzgxODI1.YareNQ.qKFtdvI0d3tuEdUmhr48tG7Ahw0")