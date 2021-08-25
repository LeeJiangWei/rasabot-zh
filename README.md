 # RASABOT-ZH

进行语言理解（提取意图、实体等），然后使用模板作出回复。

## 环境依赖

```bash
pip install rasa==1.10.11
pip install rasa[transformers] rasa_sdk
```

## 训练数据

训练数据分为两个部分，一个负责语言理解，一个负责对话模板。

文档：https://legacy-docs-v1.rasa.com/nlu/training-data-format/

### 语言理解

处理输入的文字，主要是 3 个动作：

+ 提取语句的意图（意图分类）
+ 提取文字中的关键信息（实体提取）
+ 将提取出来的实体信息保存下来方便我们使用（槽填充）

#### 文件位置

`./data/nlu.md`

#### 格式示例

```markdown
## intent:ask_object_position
- [黑色](color)的[椅子](object)在哪里
- [绿色](color)的[排插](object)在什么地方
```

+ ask_object_position 就是一类文字的意图，可以理解为文本分类的标签
+ 中括号 \[ \] 括起来的内容表示一种实体，紧接着的小括号 \( \) 表示这种实体的标签
+ 仿照已有的数据，考虑到时候可能会问什么话，需要提取话中的哪些实体来设计即可

#### 在设置文件中注册意图和实体

在 `./domain.yml` 文件中告诉系统有哪些意图和哪些实体。

```yaml
session_config:
  session_expiration_time: 60
  carry_over_slots_to_new_session: false
intents:  # 在这里把所有意图的类别写进去，跟上面的一致
- out_of_scope
- ask_weather
- ask_object_color
- ask_object_position
entities:  # 在这里把所有实体的类别写进去，跟上面小括号内的一致
- artist
- song_title
- location
- time
- object
- color
- on
- near
slots:  # 在这里把实体的类别以及对应的类型填进去，这样在程序中能够获取实体的值
  object:
    type: text
  position:
    type: text
  color:
    type: text
responses:  # 这里是一些固定回复的话
  utter_greet:
  - text: 你好！今天过得怎么样？
  - text: 你好，很高兴见到你！
  utter_cheer_up:
  - text: 我来给你讲个笑话吧：下水道很郁闷的说：我想不通！于是它堵了。
  utter_did_that_help:
  - text: 这帮助到你了吗？
actions:  # 自定义动作的名字
- action_search_song
- action_search_weather
- action_response_command
```

### 对话模板

由于我们的系统需要整合视觉信息，而这些信息是没办法参与对话系统的训练的（因为是实时获取的），所以这部分没有办法利用视觉信息。如果编写不需要视觉信息的模板，可以在这里编写。

#### 文件位置

`./data/stories.md`

#### 格式示例

```markdown
## ask weather without location
* ask_weather
  - utter_ask_location
* inform{"location":"somewhere"}
  - action_search_weather
  - reset_slots  
```

+ \#\# 后面的字符表示这一个样本的名字，可以随便起，没有要求
+ \* 后面的字符表示用户的输入意图，跟上面的那些意图是对应的
  + 下面两个则是遇到这个输入时做出的回复（可以对一个输入作出多个回复）
  + utter\_开头的就是在 `domain.yml` 里硬编码的回复，action\_开头的则是自定义的动作

## 自定义动作

文档：https://legacy-docs-v1.rasa.com/api/rasa-sdk/

回复不一定只能回复文字，可以在回复的同时做其他动作（执行自己的代码，例如向天气API查询天气）或者直接返回意图等信息，在客户端（开发板）上再来拼接文字。

可以在`actions.py`里编写这样的自定义动作。现在，对于视觉问题（诸如黄色的水杯在哪里这样的问题），自定义动作直接返回意图的名字，以及提取出来的实体。代码如下所示：

```python
class ResponseCommandAction(Action):
    def name(self) -> Text:
        return "action_response_command"  # action的名字，需要和domain.yml中的一致

    def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        # 从槽中提取各种同名的实体，以及意图的名字
        obj = tracker.get_slot("object")
        color = tracker.get_slot("color")
        on = tracker.get_slot("on")
        near = tracker.get_slot("near")
        intent = tracker.latest_message["intent"]["name"]

        # 用这些值构建字典
        reply = {"intent": intent, "object": obj, "color": color, "on": on, "near": near}
        print(reply)
        
        dispatcher.utter_message(json_message=reply)  # 直接返回这个字典作为回复

        return [AllSlotsReset()]  # 重置槽的值
```

## 文字拼接

目前做出的回复是就基于上面这个action返回的信息，是在开发板中完成的，具体要看那个项目中的`utils.py`里的代码。因为都是根据 if-else 判断，所以比较僵硬。参数 query 就是上面这个 action 所返回的那个字典。

```python
def visual_to_sentence(query, info):
    intent, query_category, query_color, query_on, query_near = [query[i] for i in
                                                                 ("intent", "object", "color", "on", "near")]

    objects = json.loads(info)
    for obj in objects:
        category, color, on, near = [EN_ZH_MAPPING[obj[i]] if obj[i] else None
                                     for i in ("category", "color", "on", "near")]

        if (category == query_category or category in SYNONYM.keys() and query_category in SYNONYM[category]) \
                and (not query_color or color == query_color):
            sentence = category
            if intent == "ask_object_position":
                if on:
                    sentence += f"在{on}上，"
                if near:
                    sentence += f"在{near}旁边，"
                if query_color:
                    sentence = f"{color}的" + sentence
                elif color:
                    sentence = sentence + f"它是{color}的，"
            elif intent == "ask_object_color":
                sentence += f"是{color}的。"

            return sentence

    return f"没有看到{query_color if query_color else ''}{query_category}。"
```

## 启动命令

| 命令             | 说明                   |
| ---------------- | ---------------------- |
| rasa run         | 启动服务器             |
| rasa train       | 训练整个对话系统       |
| rasa shell       | 在命令行中测试对话系统 |
| rasa run actions | 启动自定义动作服务器   |
