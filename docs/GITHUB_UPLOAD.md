# 发布到 GitHub 与分享给朋友

## 朋友怎么使用

- **直接发文件**：发送 `autocut-v0.3.0.zip`。朋友把整个 ZIP 交给 Codex，说「请安装 Autocut」。安装后在新对话输入 `使用 $autocut 开始`，即可跟着提示给素材、选编辑器和档位。没有素材可以先回复「模拟」。
- **从 GitHub 下载**：公开发布后，直接发 Release 页面链接。也可在 GitHub 搜索 `autocut in:name user:你的用户名`，选 **Repositories**，点进仓库的 **Releases**，从 **Assets** 下载 `autocut-v0.3.0.zip`。GitHub 自动提供的 **Source code (zip)** 是仓库源码包。[GitHub 仓库搜索](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
- **从 GitHub 安装技能目录**：有技能安装入口的 Codex 可以用仓库目录链接。把 `你的用户名/你的仓库` 与分支名换成实际值。私有仓库需要先有阅读权限。

```text
请从 https://github.com/你的用户名/你的仓库/tree/main/skills/autocut 安装 Autocut，保留完整技能目录。已有同名技能时先比较版本。
```

安装和剪辑器连接方式见[新手图文手册](../skills/autocut/assets/guide/quickstart.pdf)及[安装说明](../skills/autocut/INSTALL.md)。

## 仓库维护者怎么发布

1. 创建或打开专用的 `autocut` 仓库。需要让所有朋友都能搜索和下载时，选公开仓库。
2. 解压 `autocut-v0.3.0-github.zip`，把里面 `autocut/` 的内容提交到仓库根目录。首页应该能看到 `README.md`、`LICENSE.md`、`docs/` 与 `skills/autocut/SKILL.md`。按该版本的许可文件发布，避免再添加冲突的许可模板。[GitHub 文件上传](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)
3. 打开 **Releases → Draft a new release**，新建标签 `v0.3.0`，指向刚提交的分支，标题写 `Autocut v0.3.0`，附上 `autocut-v0.3.0.zip` 和 `SHA256SUMS.txt`。说明三档口播、章程、喜好库和更新的图文指南。[GitHub Release 说明](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
4. 发布后核对权限、安装包能下载、首页文档链接能打开。发给朋友的是 Release 链接或单独的安装 ZIP。上传内容应来自打包后的源码，私人喜好库、真实客户或个人素材、工程和登录信息留在本机。

更新时沿用同一技能名。同步更新技能版本与变更记录，再重新校验安装 ZIP 与 Release 版本。新版本的技能可以替换，朋友的个人喜好库和工程继续沿用。
