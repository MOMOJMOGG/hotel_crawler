# 飯店評論爬蟲分析機器人 / Hotel Review Scraper and Analysis Bot
一個自動化腳本，幫助你從 Google Maps 獲取即時的飯店評論分析結果，讓住宿選擇更有依據。

An automated script to fetch real-time hotel reviews from Google Maps, providing more reliable insights for accommodation choices.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 專案簡介 / Overview
住宿評價通常是選擇飯店時的重要參考依據，但訂房網站上的評論有時會受到促銷活動的影響，無法完全信任。相比之下，Google Maps 上的評論更加真實且具參考價值。本專案旨在開發一個自動化的爬蟲分析機器人，根據使用者輸入的飯店資訊，自動擷取 Google Maps 上的最新評論，並進行分析，提供更可靠的決策依據。

Hotel reviews often play a crucial role when choosing accommodations, but reviews on booking websites can be influenced by promotions and may not always be trustworthy. In contrast, reviews on Google Maps are often more genuine and reliable. This project aims to develop an automated scraping and analysis bot that retrieves the latest reviews from Google Maps based on user-provided hotel information, offering more trustworthy insights for decision-making.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 功能特色 / Features
* 自動化擷取 Google Maps 上的最新飯店評論
* 根據評論內容進行情感分析（正面/負面）
* 提取評論中常見的關鍵字與主題
* 串接個人的 Notion 資料庫，將分析結果自動同步儲存

- Automatically scrape the latest hotel reviews from Google Maps.
- Perform sentiment analysis on the reviews (positive/negative).
- Extract common keywords and topics from reviews.
- Integrate with your personal Notion database to automatically store and sync analysis results.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 套件使用 / Built With
這部分列出了專案中使用的主要框架和函式庫。附加的插件與工具請參考致謝部分。

This section lists the major frameworks and libraries used to bootstrap your project. Add-ons and plugins are mentioned in the acknowledgements section.

[![Selenium][selenium-badge]][selenium-url]
[![Pandas][pandas-badge]][pandas-url]
[![Notion][notion-badge]][notion-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 安裝教學 / Installation
```bash
# 安裝必要套件 / Install required packages
pip install -r requirements.txt
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 前置作業 / Prerequisites
在運行本專案之前，請確保完成以下準備工作：
a. 申請 OpenAI API Key 以進行評論數據的分析。
b. 創建 Notion 資料庫並取得 Notion API Token 和資料庫 ID。

Before running this project, ensure you have completed the following setup:
a. Apply for an OpenAI API Key for analyzing review data.
b. Create a Notion database and obtain a Notion API Token and the database ID.

```bash

```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 設定說明 / Configuration
若需要自訂 API 金鑰或代理伺服器設定，請在 .env 檔案中進行調整：

To customize API keys or proxy settings, adjust the .env file:

```
$ .env
OPAI_API_KEY=your_open_ai_api_key
NOTION_API_KEY=your_notion_integration_token
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 使用方法 / Usage
```bash
# 運行腳本並輸入飯店名稱 / Run the script and input hotel name
# to be continue
```
使用者可以透過輸入飯店名稱來獲取即時評論分析結果，並自動將結果同步至 Notion 資料庫。

Users can input the hotel name to get real-time review analysis results and automatically sync the results to their Notion database.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 專案結構 / Project Structure
```bash
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 專案展示 / Project Demo
```bash
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 授權 / License
本專案採用 MIT License 授權，詳細內容請參閱 [LICENSE][license-url] 檔案。

This project is licensed under the MIT License - see the [LICENSE][license-url] file for details.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[selenium-badge]: https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=Selenium&logoColor=white
[selenium-url]: https://www.selenium.dev/
[pandas-badge]: https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white
[pandas-url]: https://pandas.pydata.org/
[notion-badge]: https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white
[notion-url]: https://notion.so/
[license-url]: ./LICENSE.txt
