法嘉致富｜星遇企划档案网站 V0.32

部署方式
1. 将压缩包内 fajia-business-v0.32 文件夹中的全部内容，覆盖到 GitHub Desktop 克隆的 fajia-business 仓库根目录。
2. 在 GitHub Desktop 中检查改动，填写 Summary 后提交到 main。
3. 点击 Push origin；GitHub Pages / EdgeOne 完成部署后，网页与下载 PDF 即会更新。

本版本核心更新
1. GitHub Actions 升级为 actions/checkout@v5、actions/setup-python@v6 与 actions/upload-artifact@v6，消除旧 Node.js 20 运行时警告。
2. 爬虫运行后先检查 assets/social-data.json 是否真的发生变化。
3. 只有公开数据发生变化时，Actions 才安装 PDF 依赖和中文字体并重新生成 PDF。
4. 自动生成 downloads/fajia-business-media-kit-v0.32.pdf。
5. Actions 会把 assets/social-data.json 与新版 PDF 一起提交并推送。
6. 若数据没有变化，将跳过 PDF 重建和提交，避免产生无意义的每日提交。
7. 手动运行 Actions 与每日定时运行使用同一套自动更新流程。

自动更新链路
定时或手动启动 Actions
→ 抓取公开数据
→ 更新 assets/social-data.json
→ 检测 JSON 是否变化
→ 有变化时重新生成 PDF
→ 同时提交 JSON 与 PDF
→ GitHub Pages / EdgeOne 自动部署

注意
- GitHub Actions 无法使用你电脑本地保存的小红书登录状态；小红书精确数据仍更适合本地手动更新后 Push。
- 平台触发登录、验证码或风控时，爬虫会保留上一次有效数据，不会覆盖成 0。
- 不要把账号密码、Cookie、验证码或授权令牌写入公开仓库。
