# CoreNews.AI

CoreNews.AI 是一套使用 Python 開發的自動化新聞彙整系統，結合爬蟲技術與 HTML Email 模板，透過 crontab 排程每日自動蒐集多個網站的 AI 新聞，並寄送格式精美的新聞摘要郵件。



## 功能特色

### ✅ 多站台 AI 新聞聚合

- 整合多個網站資料來源進行 AI 新聞彙整
- 支援動態 HTML 結構與 meta 描述擷取

### ✅ HTML 格式郵件發送

- 精緻卡片式排版，郵件閱讀體驗佳
- 一鍵寄送新聞摘要至指定收件人

### ✅ 雲端爬蟲防擋設計

- 採用 `cloudscraper` 模擬瀏覽器繞過 Cloudflare 機制
- 隨機延遲與 UA 偽裝，降低封鎖風險

### ✅ 自動化排程支援

- 可搭配 crontab 實現每日 00:00 抓取，09:00 寄出
- 支援一鍵命令手動執行：`crawl` / `email`

## 技術棧

- 語言：Python
- 爬蟲框架：cloudscraper, BeautifulSoup
- RSS 處理：內建解析器
- 郵件服務：yagmail
- 密碼管理：dotenv
- 排程機制：crontab / CLI 入口

## 專案挑戰

- 結構差異化：各新聞網站使用不同的網頁結構與 class 命名，需針對 selector 與 URL 模板做客製化調整。
- 防爬機制應對：部分站台啟用 Cloudflare，傳統 requests 無法成功請求，改用 cloudscraper 模擬瀏覽器行為繞過防擋。
- 摘要資訊不足：主頁多數未提供文章摘要，需透過二次請求進入詳細頁面擷取段落內容，並加入 fallback 防呆處理。
- HTML 郵件一致性：Email 樣式使用 inline CSS 硬編排，避免不同郵件平台造成版型走樣或斷行。
- 郵件發送授權限制：為因應 Gmail 封鎖低安全性應用，需建立 App Password 並以密碼保護方式注入環境變數。

## 本專案結合多站網頁爬蟲、RSS 處理、HTML 郵件模板與定時任務排程，架構清晰、易於維護，適合作為自動化新聞彙整系統的實作入門範例。
