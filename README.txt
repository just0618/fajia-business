法嘉致富｜星遇企划档案网站 V0.28

部署方式
1. 将压缩包内 fajia-business-v0.28 文件夹中的全部内容，覆盖到 GitHub Desktop 克隆的 fajia-business 仓库根目录。
2. 在 GitHub Desktop 中检查改动，填写 Summary 后提交到 main。
3. 点击 Push origin；GitHub Pages / EdgeOne 完成部署后，网页与下载 PDF 即会更新。

本版本调整
1. 网站 LEECN 莉肯页面增加“新序美学大使”与 Coming Soon 卡片之间的留白。
2. 网站首页两段寄语中的“法宣阁”“贺嘉述”署名改为更清晰的强调标签。
3. PDF 首页同步加强两位姓名署名的视觉识别。
4. PDF“法嘉致富”介绍文案与网站完全同步，并补充“小发夹”取自“法嘉”谐音。
5. PDF 个人信息页将“动物塑”拆分为与 MBTI 同级的独立字段。
6. PDF 将“官方账号｜抖音”和“官方账号｜多平台”合并为一页“官方账号｜全平台”。
7. PDF 将 LEECN 与 ARENA 合并到同一“即将公开”页面，使用相同面积和层级展示。
8. PDF 演唱会页面替换重复图片；见面会页面交换两张现场图的位置。
9. PDF 末页删除重复的合作建联说明，仅保留版权说明，并放大突出联系邮箱。
10. 网站“下载最新版 PDF”按钮已指向 fajia-business-media-kit-v0.28.pdf。

公开数据更新
- 网页中的官方账号粉丝数、获赞数及内容互动数据，通过 script.js 读取 assets/social-data.json。
- scripts/update_public_metrics.py 负责尝试抓取平台公开数据并更新该 JSON。
- GitHub Actions 工作流每天自动运行，也支持手动运行。
- 若平台触发登录、验证码或风控，脚本会保留上一次有效数据，不会把已有数据覆盖为 0。

注意
不要把账号密码、Cookie、验证码或授权令牌写入公开仓库。
