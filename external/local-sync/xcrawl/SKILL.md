---
name: xcrawl
description: Web crawling, scraping, and search tool using XCrawl CLI. Use whenever you need to crawl websites, scrape web pages, generate site maps, or run web searches. Make sure to use this skill when the user mentions crawling, scraping, extracting content from URLs, site mapping, or web search tasks.
tools: Bash, Read, Write
---

# XCrawl Skill

XCrawl is a powerful web crawling and scraping CLI tool. This skill wraps the `xcrawl` command to enable efficient web content extraction, site mapping, and search capabilities.

## When to Use

- **Crawl websites**: Extract all accessible pages from a website
- **Scrape content**: Extract content from specific URLs in various formats (markdown, HTML, JSON, screenshot)
- **Generate sitemaps**: Discover and map all links on a website
- **Web search**: Run search queries and get AI-powered results
- **Batch processing**: Scrape multiple URLs concurrently

## Prerequisites

Ensure xcrawl is installed and authenticated:
```bash
xcrawl --version    # Check installation
xcrawl status       # Verify authentication
```

If not authenticated:
```bash
xcrawl login --browser    # Opens browser for OAuth authentication
```

## Commands

### 1. Search

Run a web search query and get results with AI summaries.

```bash
xcrawl search "<query>" [options]
```

**Options:**
- `--limit <n>`: Number of results (default: 10)
- `--country <code>`: Country code (e.g., US)
- `--language <code>`: Language code (e.g., en)
- `--json`: Output as JSON
- `--output <path>`: Save to file

**Example:**
```bash
xcrawl search "best React state management 2024"
xcrawl search "TypeScript tutorial" --limit 15 --json
```

### 2. Scrape

Extract content from one or more URLs.

```bash
xcrawl scrape <url> [url2 ...] [options]
```

**Options:**
- `--format <markdown|json|html|screenshot>`: Output format (default: markdown)
- `--output <path>`: Output path (directory for multiple URLs)
- `--wait-for <selector>`: Wait for CSS selector before scraping
- `--headers <k:v,k2:v2>`: Additional request headers
- `--cookies <cookies>`: Cookie string
- `--concurrency <n>`: Concurrent workers for batch mode (default: 3)
- `--input <path>`: Read URLs from newline-delimited file
- `--json`: Output as JSON
- `--debug`: Enable debug output

**Examples:**
```bash
xcrawl scrape https://example.com
xcrawl scrape https://example.com --format markdown
xcrawl scrape https://site.com --output ./output/
xcrawl scrape url1.txt --input url1.txt --concurrency 5
```

### 3. Map

Generate a sitemap by discovering all links on a website.

```bash
xcrawl map <url> [options]
```

**Options:**
- `--max-depth <n>`: Maximum traversal depth
- `--limit <n>`: Maximum number of links
- `--json`: Output as JSON
- `--output <path>`: Save to file

**Examples:**
```bash
xcrawl map https://example.com
xcrawl map https://example.com --max-depth 2 --limit 100
```

### 4. Crawl

Start a crawl job and monitor its status.

```bash
xcrawl crawl start <url> [options]
xcrawl crawl status <job-id>
```

**Start Options:**
- `--max-pages <n>`: Maximum pages to crawl
- `--wait`: Wait until job completes
- `--interval <ms>`: Polling interval (default: 2000)
- `--wait-timeout <ms>`: Polling timeout (default: 60000)
- `--json`: Output as JSON
- `--output <path>`: Save to file

**Examples:**
```bash
xcrawl crawl start https://example.com
xcrawl crawl start https://example.com --max-pages 50 --wait
xcrawl crawl status job-abc123
```

### 5. Status

Check account credit status.

```bash
xcrawl status
```

## Usage Patterns

### Pattern 1: Research a Topic

```
User: Help me research Next.js 15 new features
Assistant:
1. Run a web search for recent information
2. Scrape key documentation pages

[Executes:]
xcrawl search "Next.js 15 new features" --limit 10
xcrawl scrape https://nextjs.org/blog --format markdown
```

### Pattern 2: Extract Content from Multiple URLs

```
User: Get the content from these product pages
Assistant:
[Reads URL list file]
[Scrapes all URLs with markdown format]

[Executes:]
xcrawl scrape --input product_urls.txt --format markdown --concurrency 5
```

### Pattern 3: Discover Site Structure

```
User: What pages are on this documentation site?
Assistant:
[Maps the site to discover all pages]

[Executes:]
xcrawl map https://docs.example.com --max-depth 3 --limit 200 --json
```

### Pattern 4: Competitive Analysis

```
User: Compare these three competitor websites
Assistant:
[Scrape all three sites in parallel]

[Executes:]
xcrawl scrape https://competitor1.com https://competitor2.com https://competitor3.com --format markdown --concurrency 3
```

## Output Formats

| Format | Use Case |
|--------|----------|
| `markdown` | Text content, easy to process |
| `html` | Preserve HTML structure |
| `json` | Structured data, programmatic use |
| `screenshot` | Visual capture, when text extraction isn't enough |

## Tips

1. **Use `--json` for programmatic processing** - Easier to parse and extract specific fields
2. **Batch scraping** - Use `--input` file and `--concurrency` for efficient multi-URL scraping
3. **Site mapping** - Start with `--max-depth 1` to get a quick overview before going deeper
4. **Long crawls** - Use `crawl start --wait` for small sites, or just start and check status later
5. **Authentication** - Run `xcrawl login --browser` if you get auth errors

## Error Handling

- **Auth errors**: Run `xcrawl login --browser` to re-authenticate
- **Rate limits**: Reduce `--concurrency` for batch operations
- **Timeout issues**: Use `--timeout <ms>` to increase timeout for slow sites
- **Empty results**: Try with `--debug` to see what's happening

## Blocked Sites Workarounds

### ScienceDirect (验证码/CAPTCHA 阻止)

**问题**：`xcrawl scrape` 返回验证码页面或被阻止

**解决方案**：使用 Playwright 浏览器自动化通过机构授权访问

```bash
# 使用 MCP 工具 browser_navigate + browser_snapshot
# 1. 导航到页面
browser_navigate url="https://www.sciencedirect.com/science/article/pii/..."

# 2. 获取内容快照
browser_snapshot filename="/path/to/save/article.md"
```

**原理**：通过南京师范大学等机构的浏览器授权访问，绕过 ScienceDirect 的验证码检测

### PMC / PubMed Central (安全策略阻止)

**问题**：`xcrawl scrape` 返回 `[API_ERROR] Target URL is blocked by security policy`

**解决方案**：同样使用 Playwright 浏览器直接抓取

```bash
# PMC 支持开放获取，无需机构授权
browser_navigate url="https://pmc.ncbi.nlm.nih.gov/articles/PMCxxxxxxx/"
browser_snapshot filename="/path/to/save/pmc-article.md"
```

### 批量抓取模式

对于多个被阻止的链接，循环使用：

```bash
# 伪代码示例
for url in blocked_urls:
    browser_navigate url=$url
    browser_snapshot filename="output/$(basename $url).md"
```

**注意**：使用 Playwright 抓取时需要：
1. 先登录/授权浏览器（如 `xcrawl login --browser`）
2. 确保机构授权仍然有效（对于 ScienceDirect）
3. 适当控制抓取频率，避免过快
