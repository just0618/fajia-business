法嘉致富｜星遇企划档案网站 V0.27

部署方式
1. 将压缩包内文件覆盖到 GitHub Desktop 克隆的 fajia-business 仓库根目录。
2. 在 GitHub Desktop 中提交并 Push origin。
3. GitHub Pages 部署完成后，网页即更新。

本版本调整
1. 个人信息页音乐作品之间的分号已删除。
2. 《小英雄》播放器缩小并默认收起，电脑端与手机端均固定在左侧；仍可拖动、展开、播放和暂停。
3. 微博作品卡片的“前往微博查看”下划线只与文字等宽。
4. 阿芙与方里的高仿微博卡片删除底部黑色条，原微博入口移至卡片顶部。
5. 阿芙微博改为贺嘉述与 AFU 阿芙等 3 人的共创微博，链接指向官方官宣微博。
6. 阿芙官宣视频在电脑端与同排卡片等高显示。

公开数据更新
- 网页中的官方账号粉丝数、获赞数及内容互动数据，均通过 script.js 读取 assets/social-data.json。
- scripts/update_public_metrics.py 负责尝试抓取平台公开数据并更新该 JSON。
- GitHub Actions 工作流 .github/workflows/update-public-metrics.yml 每天北京时间 12:20 自动运行，也支持手动运行。
- 若平台触发登录、验证码或风控，脚本会保留上一次有效数据，不会把已有数据覆盖为 0。
- 网页请求 social-data.json 时加入时间戳并禁用缓存，GitHub Actions 提交新数据后，重新打开或刷新网页即可读取最新版。

注意
不要把账号密码、Cookie、验证码或授权令牌写入公开仓库。
