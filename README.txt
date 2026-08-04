法嘉致富双人商业合作手册网站 V0.16（融合版）

部署：将本文件夹全部内容覆盖上传到 GitHub Pages 仓库根目录。
首页：index.html
PDF：downloads/fajia-business-media-kit-v0.15.pdf
统一数据文件：assets/social-data.json
自动更新脚本：scripts/update_public_metrics.py
GitHub Actions：.github/workflows/update-public-metrics.yml

本版本说明
1. 页面主体、排版、图片、视频与 PDF 来自 V0.15。
2. 社交数据结构与自动更新功能来自当前爬虫测试版。
3. 页面加载时会从 social-data.json 自动计算和显示公开数据。
4. 抖音、微博、小红书可能触发平台风控；失败时保留上一次有效数据，不会写成 0。
5. 抖音前两条作品目前仅保留已确认的点赞数，其他指标显示“—”。
6. 不要将账号密码、Cookie 或授权令牌写入公开仓库。
