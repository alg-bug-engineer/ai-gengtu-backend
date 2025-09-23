import re
pattern = r'```json(.*?)```'
raw_text = """### 谜底

炸弹

-----

### 谜题截图提示词

```json
A vertically stacked diptych, split-screen composition, a complete mobile puzzle game screen, screenshot, 16-bit retro video game style, pixel art.

The top panel shows a detailed pixel art of a boy wearing a bomber jacket and a beanie, holding a skateboard. There is a small, cute sprite of a family icon in the upper right corner with the text "猜人物". The image is overlayed with the clean, legible Chinese text "这是弟弟", in a clear font. The background is simple and clean.

The bottom panel shows a frantic pixel art scene. The same boy from the top panel, "弟弟", is in the foreground. He is nervously running away from a large, stylized pixel art bomb with a lit fuse. The boy's face shows panic, and he is looking back at the bomb. The bomb is "炸弹" in a frantic, cartoonish way. The ground is cracked and there are small smoke puffs behind the bomb. The image is overlayed with the clean, legible Chinese text "这是_ _", in the same font.

NO garbled text, NO incorrect characters, NO merged panels, NO blurry image.
```

```json
一个垂直堆叠的两联画，分屏构图，一张完整的手机益智游戏截图，截图，16位复古电子游戏风格，像素艺术。

上半部分展示了一幅精细的像素艺术画，画中是一个穿着飞行员夹克和毛线帽的男孩，手里拿着滑板。右上角有一个可爱的家庭小图标，上面写着“猜人物”。图像上覆盖着清晰、易读的中文文本“这是弟弟”，字体清晰。背景简洁干净。

下半部分展示了一个狂乱的像素艺术场景。上半部分出现的“弟弟”在前景中，他正惊慌地从一个巨大的、卡通化的像素艺术炸弹前跑开，炸弹的引信已经点燃。男孩脸上流露出恐慌，他正回头看着炸弹。炸弹以一种狂乱、卡通的方式呈现。地面裂开，炸弹后方有小小的烟雾。图像上覆盖着清晰、易读的中文文本“这是 _ _”，字体相同。

不要乱码，不要错别字，不要合并图块，不要模糊图像。
```

-----

### 设计思路解析

这个谜题的核心设计是利用谐音梗将看似不相关的两个概念联系起来：**“弟弟”** 和 **“炸弹”**。

1.  **纯粹的线索：** 线索图的设计遵循了“纯粹性”原则。它只展示一个男孩，并用明确的文字“这是弟弟”来定义这个角色。这个设计避免了任何歧义，确保玩家获得一个坚实的逻辑起点。右上角的“猜人物”标签进一步强化了线索的指向性，引导玩家将注意力集中在这个角色身上。

2.  **有趣的谜面：** 谜题图则利用了谐音梗的舞台特性。它将“弟弟”这个角色，与另一个在中文里发音相同的词汇\*\*“炸弹”\*\*，放在同一个场景中进行互动。通过设计一个“弟弟被炸弹追赶”的动态、略带荒诞感的场景，这个谜题既提供了视觉上的趣味性，也巧妙地暗示了谜底。玩家将线索图中的“弟弟”（dì di）与谜题图中的“炸弹”（zhà dàn）联系起来，通过音近联想最终得出正确答案。

整个设计不仅通过像素艺术风格统一了视觉，更通过**纯粹的线索**和**完整的谜面叙事**，构建了一个既有趣又充满逻辑的解谜体验。谜面图中的“\_ \_”下划线则明确地告诉玩家谜底是一个二字词汇，为解谜提供了额外的关键信息。"""
matches = re.findall(pattern, raw_text, re.DOTALL)
results= [match.strip() for match in matches]
print(results)