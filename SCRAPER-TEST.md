# 社交数据抓取测试说明

## 为什么改成“两层抓取”

抖音页面的 CSS class 会变化，不能依赖类似 `NoBOOMd6` 的类名。测试版优先监听页面自己发出的 JSON 请求；若没有拿到 JSON，再依据相对稳定的 `data-e2e` 属性读取页面上四个可见数字。

微博优先调用公开移动端 JSON；若失败，再读取帖子底部 `footer[aria-label]`。在当前桌面页面中，这个属性的顺序是：转发、评论、点赞。

## 在 GitHub 上测试

1. 上传本文件夹覆盖仓库对应文件。
2. 打开仓库 `Actions` → `Update public metrics`。
3. 点击 `Run workflow`，保持 debug 为 true。
4. 完成后查看 `assets/social-data.json` 是否更新。
5. 若没有更新，下载本次运行生成的 `social-metric-debug-*` artifact；里面有页面截图、HTML 和失败说明。

## 本地测试

```bash
python -m pip install requests playwright
python -m playwright install chromium
python scripts/test_metric_parsers.py
python scripts/update_public_metrics.py --headed --debug
```

`--headed` 会显示真实浏览器，便于确认是否出现登录或验证码。脚本不会保存账号密码或 Cookie。

## 失败时的行为

出现登录、验证码、风控或字段变化时，脚本保留上一次有效数据，不会写成 0；调试文件默认只在手动运行时保留 7 天。
