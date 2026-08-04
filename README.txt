法嘉致富双人商业合作手册网站 V0.13

部署：将本文件夹全部内容上传到 GitHub Pages 仓库根目录。
首页：index.html
PDF：downloads/fajia-business-media-kit-v0.13.pdf
统一数据文件：assets/social-data.json

公开数据更新说明
1. 页面加载时会从 social-data.json 自动计算：两位艺人三平台粉丝合计、抖音累计获赞，以及已抓取作品互动汇总。
2. scripts/update_public_metrics.py 会尝试读取公开页面/API；平台风控、验证码或接口变更时会保留现有数据，不会清空。
3. .github/workflows/update-public-metrics.yml 支持每天定时运行，也可在 GitHub Actions 中手动运行。
4. 抖音、小红书对自动访问限制较多，无法保证每次更新成功；微博公开接口相对稳定。
5. “6条代表性抖音共创内容获赞”目前仍保留人工汇总值。只有在 social-data.json 中配置满6条作品且全部抓取成功后，脚本才会自动覆盖该总数。
6. 不要将账号密码、Cookie 或授权令牌写入公开仓库。

人物资料说明
MBTI 当前标注为“待本人公开”；动物塑采用页面策划中的粉丝常见称呼，正式对外前仍建议由运营方确认。
