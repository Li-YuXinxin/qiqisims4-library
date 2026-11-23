# 柒柒的 Sims4 资源库 · 静态站（Cloudflare Pages）

纯静态：HTML + JSON，无后端、无数据库、无构建。资源本体全部放网盘，网站只存索引。

## 文件清单

| 文件 | 作用 |
| ---- | ---- |
| `index.html` | 网站页面（样式和逻辑全部内联，直接可用） |
| `data.json` | 数据源，网站从这里读所有资源 |
| `editor.py` | 本地可视化编辑器，改完自动写回 data.json |
| `push.bat` | Windows 一键提交并推送 GitHub，触发 Pages 自动部署 |
| `README.md` | 本说明 |

> 全部文件放在**同一个文件夹根目录**，不要套子目录。

## 一、日常更新流程（三步）

1. 双击 `editor.py` → 新增 / 修改 / 删除资源 → 点「保存修改」或「新增条目」，已自动写进 `data.json`
2. 双击 `push.bat` → 自动 commit + push 到 GitHub
3. 等约 30 秒，Cloudflare Pages 自动重新部署，刷新网站（Ctrl+F5）即可看到新内容

## 二、编辑器使用说明

```bash
python editor.py
```

- 上方表格列出所有条目，点一行即在下方表单载入
- **新增条目**：填好表单点「新增条目」（标题和分类必填）
- **保存修改**：选中某行，改完点「保存修改」
- **删除选中**：确认后删除
- **上移 / 下移**：调整展示顺序（网站按数组顺序展示）
- **复制本条 JSON**：把当前条目 JSON 复制到剪贴板，方便手动改文件
- **批量操作**：在表格中按 Ctrl / Shift 选中多条；批量编辑窗口勾选需要统一修改的字段（未勾选的保留原值），或批量删除、批量上移 / 下移（保持选中条目的相对顺序）
- 每次保存会自动生成 `data.json.bak` 备份，改坏可回退

## 三、字段说明

| 字段 | 含义 | 是否必填 |
| ---- | ---- | ---- |
| `title` | 资源标题 | 必填 |
| `cover` | 封面图直链，留空显示占位图 | 可选 |
| `author` | 原作者 | 建议填 |
| `category` | 分类：模组推荐 / 房屋分享 / 家具CC / 服装CC / 实用工具 / 作者推荐（“全部”仅用于浏览，不是条目分类） | 必填 |
| `authorCategory` | 作者推荐的子分类：房屋作者 / 家具作者 / 服装作者 / 动画作者；编辑器选“作者推荐”后填写 | 作者推荐必填 |
| `gameVer` | 游戏版本，如 `1.129`，只展示不筛选 | 可选 |
| `tags` | 标签数组，编辑器里用 `,` `，` `、` 分隔均可 | 可选 |
| `link` | 网盘分享链接 | 建议填 |
| `code` | 提取码，留空则不显示复制按钮 | 可选 |
| `desc` | 详情介绍，支持简易 Markdown | 可选 |

`desc` 支持的 Markdown 写法：

```
## 小标题
- 无序列表
1. 有序列表

空行分段。
```

> 卡片上只显示压缩后的纯文本摘要，完整排版在右侧详情抽屉里渲染。

### data.json 结构

```json
{
  "site": {
    "emoji": "📚",
    "title": "站点名称",
    "notice": "顶部公告文字",
    "categories": ["全部", "房屋分享", "家具CC", "服装CC", "作者推荐", "模组推荐", "实用工具"],
    "authorCategories": ["房屋作者", "家具作者", "服装作者", "动画作者"],
    "pageSize": 12
  },
  "items": [
    {
      "title": "示例资源",
      "cover": "https://图片直链.jpg",
      "author": "作者名",
      "category": "家具CC",
      "gameVer": "1.129",
      "tags": ["NOCC", "现代"],
      "link": "https://pan.baidu.com/s/xxxx",
      "code": "abcd",
      "desc": "## 说明\n- 解压到 Mods 文件夹"
    }
  ]
}
```

> 页面同时兼容纯数组格式 `[ {...}, {...} ]`，两种都能读。

## 四、本地预览

```bash
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

直接双击 `index.html` 也可打开，但浏览器会拦截本地 fetch，此时页面用内置兜底数据；部署上线后正常读取 `data.json`。

## 五、Cloudflare Pages 部署

**首次部署**

1. GitHub 新建仓库（Public，不要勾 README / .gitignore）
2. 本文件夹内打开 cmd，依次执行：

```bash
git init
git add .
git commit -m "初次上线"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

3. Cloudflare Dashboard → Workers & Pages → Create application → Pages → Connect to Git
4. 选中该仓库，构建配置：

| 项 | 值 |
| ---- | ---- |
| Production branch | `main` |
| Framework preset | `None` |
| Build command | 留空 |
| Build output directory | `/` |

5. Save and Deploy，几十秒后得到 `xxx.pages.dev` 网址

**之后更新** 就用 `push.bat`。

## 六、常见问题

- **页面空白 / 404**：确认 `index.html` 在仓库根目录、文件名全小写（`data.json` 不能写成 `Data.json`）
- **推送要密码**：GitHub 不接受账号密码，需用 Personal Access Token（Settings → Developer settings → Personal access tokens，勾 `repo` 权限）
- **推了但网站没变**：等 30 秒；仍不变则进 Pages 项目清缓存（Purge Everything），浏览器 Ctrl+F5
- **国内访问偶尔慢**：`*.pages.dev` 为海外节点，属正常网络现象，可后续绑自定义域名

## 七、风险提示

- 公告中的版权声明建议保留；收到作者下架要求应及时删除对应条目
- 成人向 / 违规模组可能触发 Cloudflare 内容审核导致项目被下架
- 图片建议用图床直链，不要堆进静态仓库，避免超出体积限制
- 网盘链接会失效，需要定期巡检
