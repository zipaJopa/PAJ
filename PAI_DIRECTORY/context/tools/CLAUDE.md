# 🛠️ TOOLS DOCUMENTATION - YOUR PRIMARY PROBLEM-SOLVING METHOD

## 🚨 CRITICAL RULE: TOOLS FIRST, ALWAYS 🚨

**STOP AND READ THIS CAREFULLY:**

When someone asks you to do ANYTHING, your FIRST thought should be:
"Which tool from my commands or services does this?"

**NOT**: "Let me write code to solve this"
**NOT**: "Let me create HTML"
**NOT**: "Let me build something from scratch"

**INSTEAD**: "Let me use the appropriate tool that already exists"

## Web searches

Don't use fetch to research things, use `${PAI_DIR}/commands/web-research.md` instead.

## 🚨🚨🚨 CHROME DEVTOOLS MCP - FOR ALL WEB BROWSING & TESTING 🚨🚨🚨

**THESE ARE YOUR EYES, Kai!**

**USE THIS FOR EVERYTHING WEB-BASED:**
- Opening web pages
- Testing web apps
- Troubleshooting web pages
- Browser automation
- Taking screenshots
- Clicking buttons and links
- Filling out forms
- Scrolling pages
- Visual debugging
- Checking console errors

**THE CHROME DEVTOOLS MCP TOOLS ARE NAMED:**
- `mcp__chrome-devtools__navigate_page` - Open a URL
- `mcp__chrome-devtools__take_screenshot` - Capture screenshot
- `mcp__chrome-devtools__click` - Click elements
- `mcp__chrome-devtools__fill` - Fill form fields
- `mcp__chrome-devtools__list_console_messages` - Check errors
- `mcp__chrome-devtools__evaluate_script` - Run JavaScript
- And more...

**CRITICAL RULES:**
- ✅ ALWAYS use Chrome DevTools MCP for web browsing
- ✅ NEVER use curl, fetch, or wget for web debugging
- ✅ Take screenshots to SEE what's happening
- ✅ The tools are prefixed with `mcp__chrome-devtools__`

NEVER USE curl or Playwright for this. Only Chrome DevTools MCP.

**Official Documentation:** https://github.com/ChromeDevTools/chrome-devtools-mcp

## 📁 AVAILABLE COMMANDS (${PAI_DIR}/commands/)

**🚨 CHECK THESE FIRST - They solve specific problems completely!**

`read ${PAI_DIR}/commands/`

Read the descriptions in each of those to understand what they're used for and when you should invoke them.

### 💰 FINANCIAL QUESTIONS - ALWAYS USE ANSWER-FINANCE-QUESTION COMMAND

**CRITICAL:** When the user asks about financial information:
1. **ALWAYS use the `answer-finance-question` command** - It parses financial PDFs and extracts specific data
2. **Include the command in your response** - Show the user what financial data was found
3. **Financial questions include**:
   - Utility bills (PG&E, water, electricity)
   - Vendor payments and amounts
   - Monthly expense patterns
   - Bill amounts from bank statements

Examples that should trigger the command:
- "What is my PG&E bill?"
- "How much do I spend on utilities?"
- "What's my typical water bill?"
- "Show me restaurant spending"
- "What utilities am I paying for?"

## 🔌 MCP SERVERS - Model Context Protocol Services

## Your full list of MCP servers is in `read ${PAI_DIR}/.mcp.json`.

Read the descriptions in each of those to understand what they're used for and when you should invoke them.

## 🚨 SPECIALIZED SCRAPING OF DIFFICULT CONTENT ONLINE (Apify MCP)

Some web content is extremely difficult to browse, scrape, or crawl with other tools, such as from LinkedIn or Facebook or Instagram or X/Twitter. For systems like that, you want to use the Apify MCP server.

**CRITICAL**: When Daniel asks about:
- **LinkedIn scraping** or getting content from LinkedIn profiles/posts
- **X (Twitter) scraping** or getting content from X profiles/posts  
- **Social media content extraction** that's traditionally difficult to crawl
- **Protected/bot-detection content** from major platforms

**YOU MUST USE THE APIFY MCP SERVER** - We have this specifically installed for handling these challenging scraping tasks that regular tools cannot access due to bot detection, authentication requirements, and anti-scraping measures.

Use `mcp__apify__search-actors` to find appropriate scrapers, then use the relevant Apify actors for the task.

## 📚 Ref MCP Server - Documentation Search For Up-to-date Development (Ref MCP)

This MCP server is for always having the most up-to-date documentation and best practices for writing code using specific technologies. So when you start a project, you should always hit this MCP server for the technologies that you are building with to make sure you are using the best practices. 

Any engineer or developer agents should always use this as well.

### Available Ref MCP Tools:

1. **ref_search_documentation** - Primary documentation search
   - Searches technical documentation for APIs, services, libraries, frameworks
   - Returns relevant sections from documentation pages
   - Token-efficient (returns only most relevant ~5k tokens)
   - Smart session tracking to avoid duplicate results
   - Use for: Finding specific API methods, configuration options, best practices

2. **ref_read_url** - Direct documentation reading  
   - Fetches content from a URL and converts to markdown
   - Intelligently filters out irrelevant sections based on search context
   - Optimized for documentation pages (loads all code tabs, etc.)
   - Returns deep links to specific sections for verification
   - Use for: Following documentation links, reading specific pages

3. **ref_search_web** - Fallback web search
   - General web search when documentation search doesn't find results
   - Finds relevant pages on the web
   - Can be combined with ref_read_url to read found pages
   - Use for: Finding documentation not in Ref's index, blog posts, tutorials

### Key Features:
- **Token Efficiency**: Smart chunking to return only relevant tokens (e.g., 200 tokens from an 80k token API doc)
- **Session Intelligence**: Tracks search trajectory to minimize context and avoid repeated results
- **Documentation-Optimized**: Tuned specifically for technical documentation crawling
- **Fast Performance**: Quick lookups without deep research overhead
- **Context Preservation**: Maintains search context to filter irrelevant sections

### When to Use Ref MCP:
- Starting any new coding project (check latest framework docs)
- Looking up API parameters or methods
- Finding configuration options or best practices
- Checking current library versions and features
- Getting code examples from official documentation
- Verifying implementation details before coding

### Usage Examples:
- "Check React 19 documentation for new features"
- "Find Stripe API webhook configuration"
- "Look up Python asyncio best practices"
- "Get Next.js 15 app router documentation"
- "Search for AWS Lambda environment variables"

## 💳 Stripe MCP Server - Payment Management

The Stripe MCP server lets us manage our production Stripe account, including creating new products, getting payment information, etc.

We primarily use it to complete the end-to-end building of new applications and hook it up to a real Stripe page where people can buy and use the product

**When to use**:
- Processing charges and refunds
- Creating and managing subscriptions
- Viewing payment history and invoices
- Managing products and pricing

**Security Considerations**:
- Always confirm amounts and customer IDs before operations
- Never expose customer payment details in responses

**Common Operations** (always verify before executing):
- Create/update customers
- Process payments
- Issue refunds (DOUBLE CHECK AMOUNTS)
- Manage subscriptions
- Generate invoices
- View transaction history

**Before ANY Stripe operation**:
1. Confirm the exact operation with the user
2. Verify customer/payment IDs
3. Double-check amounts (especially for charges/refunds)
4. Consider if test mode would be more appropriate
