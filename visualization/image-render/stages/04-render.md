# 阶段 4：检查 → 拼提示词 → 出图 → 核对

脚本都在 `scripts/`，参数是任务目录。

```bash
S=<本 skill 目录>/scripts
python3 $S/render_codex.py <任务目录>          # 内部先跑 check_prompts + build_prompts，再出还没出的图，最后逐字核对
python3 $S/make_page.py    <任务目录> --title "标题"  &&  open <任务目录>/review.html   # 出图后会自动生成对比页；想改标题再跑这条
```

- 提示词结构：【风格基准（唯一允许）】风格块 + 「整张图只用这一种风格」→【画面与版式】→【必须逐字放入的文字（唯一真值）】→【强制约束】（`templates/common.txt`；任务目录放 `common.txt` 可覆盖）。
- `check_prompts.py` 有错误会直接停：画幅不是实测过的、画面描述里有清单外的「」、清单格式不对、文件名不合法。先改 `adapt/`。
- `build_prompts.py` 会删掉 `adapt/` 里已不存在的画面对应的旧提示词；拼好后再查一遍整份提示词里的「」。
- `render_codex.py`：默认用你 Codex 自己配置的模型（`--model` / `--effort` 可指定）；每批 8 张、同时 3 批、每批最长 40 分钟；`--only 2-` 只画某些；`--ref` 或任务目录 `ref.png` 垫图；`--dry-run` 只生成任务文件。已出且能解码的图跳过；空文件、损坏文件会重画；提示词或参考图改过的，旧图自动移到 `_v1/` 再重画。同一任务目录同时只能跑一个。
- 退出码：0 = 全部成功且本次新出的都核到逐字；1 = 有失败或没核到；2 = 输入错误。明细在 `logs/report.json`。
- Codex 满载（`Selected model is at capacity`）会整批失败，脚本自动重跑（默认 2 次）；还不行就过一会儿再跑同一条命令。
- 耗时：约 12 张 / 6–10 分钟。长跑放后台，跑完再做对比页。

## 第一次用 / 刚换默认风格：先出 1 张

`python3 $S/render_codex.py <任务目录> --only 1-`，给用户看第 1 张，**等用户说可以**再不带 `--only` 跑一次出剩下的（已出的会跳过）。

`--only` 按文件名开头匹配：`--only 1-` 只出 `1-xxx` 那张，`--only 2-` 只出第 2 张；不带 `--only` 就出所有还没出的。第二次运行时，已出好的图显示「之前已出好，本次不核」，汇报逐字结果时把两次合起来算。

## 改了画面要重画

改 `adapt/<名>.txt` → 重跑 `render_codex.py`。脚本记得每张图用的提示词指纹，变了就把旧图移到 `_v1/` 再重画，不用手动删。

## Codex 自己跑本 skill 时（不调用 render_codex.py，否则会再起一个 Codex）

1. `python3 $S/check_prompts.py <任务目录>`，有错先改 `adapt/`。
2. `python3 $S/build_prompts.py <任务目录>`。
3. 对 `prompts/` 里每个文件调用内置 imagegen：prompt = 文件全文原样，不翻译不润色；不垫图时只传 prompt；垫图时 `referenced_image_paths` 传参考图绝对路径，**不传** `num_last_images_to_include`（只能 1–5，传 0 报错）；每个文件只调一次。
4. 把生成的图原样保存为 `out/<同名>.png`。
5. `python3 $S/verify_log.py <任务目录>` 核对图能解码、prompt 逐字一致（写 `logs/report.json`）。
6. `python3 $S/make_page.py <任务目录>` 生成对比页。

## 交付前自查（必须做）

脚本报的「提示词逐字」只说明 imagegen 收到的提示词没被改写，**不代表图上的字画对了**。Claude 要逐张打开图看：

- 错字、漏字、多字（清单外的符号、拟声词、角色说明）、自己加的小动物。
- 标点画成半角样式（「，」变「,」）不算错字，提一句即可，用户在意再重出。
- 给用户汇报时分两项说：提示词逐字 N/N；图上文字 Claude 看过、发现的问题逐条列出（没看的写「未核验」）。
- 有问题的那张按「改了画面要重画」处理。

## 已知局限

- 逐字核对只看 imagegen 收到的 prompt（首尾空白忽略），不核对它最终存成了哪个文件；两张图提示词全文完全相同时分不出是哪一张。
- 图片由 Codex 直接写进 `out/`，脚本无法保证原子写入；损坏文件下次运行会被识别并重画。
