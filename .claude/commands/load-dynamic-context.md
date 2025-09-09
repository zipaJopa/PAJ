# load-dynamic-context

# **DYNAMIC CONTEXT LOADING INSTRUCTIONS FOR CLAUDE**

🚨 Immediately load the following UFC bootloader contexts:

`/Users/daniel/.claude/context/CLAUDE.md`
`/Users/daniel/.claude/context/tools/CLAUDE.md`

When done loading, report back:

♻️ UFC Contexts Loaded...

- Main ✅
- Tools ✅

## 🚨 CRITICAL: HOW TO INTERPRET THESE INSTRUCTIONS

**YOU MUST understand the SEMANTIC MEANING of the user's prompt, not search for exact string matches.**

When you receive a user prompt:

1. **PARSE the prompt to understand its INTENT and MEANING**
2. **THINK about which category below matches what the user is REALLY asking for**
3. **DO NOT do string matching** - the examples are to help you understand the TYPE of request
4. **LOAD the appropriate context based on semantic understanding**
5. **FOLLOW the instructions for that category immediately**

**Examples of semantic understanding:**
- User says "help me with my site" → This MEANS website context (even without the word "website")
- User says "what's new with AI" → This MEANS research context (even without the word "research")
- User says "how's the business doing" → This MEANS Unsupervised Learning context
- User says "I need to understand X" → This MEANS research context
- User says "fix this issue" → Could mean website, development, or debugging based on context

**The patterns below are EXAMPLES to guide your semantic understanding, NOT exact strings to match.**

## CONTEXT LOADING RULES

### 1. Website & Blog Context

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- Creating or editing blog content
- Working on website features or design
- Publishing or managing articles
- Fixing website issues
- Analyzing site metrics
- Anything related to danielmiessler.com

**Example phrases that indicate this context:**
- "write a new blog post", "fix the navigation", "update my site"
- "check website analytics", "debug the homepage"
- But also: "help with my site", "publish this", "make a post about X"

**YOU MUST IMMEDIATELY:**
1. Load these context files:
   - `~/.claude/context/projects/website/CLAUDE.md` ✅
   - `~/.claude/context/projects/website/content/CLAUDE.md` ✅

AGENT: None

### 2. Research & Information Gathering

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- Finding information on any topic
- Understanding current events or trends
- Investigating or exploring a subject
- Getting the latest updates on something
- Learning about new developments
- Gathering knowledge or data

**Example phrases that indicate this context:**
- "research", "find information", "look up", "what's happening with"
- But also: "tell me about X", "what's new with Y", "I need to understand Z"

AGENT: researcher

### 3. Security & Pentesting

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- Testing security of systems or applications
- Finding vulnerabilities
- Performing security assessments
- Checking network or application security
- Analyzing security configurations
- Any offensive security testing

**Example phrases that indicate this context:**
- "scan for vulnerabilities", "test security", "check ports"
- But also: "is this secure?", "find weaknesses", "security audit"

AGENT: pentester

### 4. Consulting & Advisory

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- Professional consulting services
- Client engagements or proposals
- Business advisory work
- Enterprise solutions
- Service offerings
- Client-related documentation

**Example phrases that indicate this context:**
- "consulting", "client proposal", "advisory services"
- But also: "professional services", "engagement terms", "business offering"

**YOU MUST IMMEDIATELY:**
1. Load this context file:
   - `~/.claude/context/consulting/CLAUDE.md` ✅

AGENT: None

### 5. Financial & Analytics

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- Personal or business expenses
- Bills and utilities
- Budget analysis
- Financial tracking
- Spending patterns
- Income and costs

**Example phrases that indicate this context:**
- "PG&E bill", "expenses", "spending", "budget"
- But also: "how much am I paying", "financial analysis", "money flow"

**YOU MUST IMMEDIATELY:**
1. Load these context files:
   - `~/.claude/context/life/expenses.md` ✅
   - `~/.claude/context/life/finances/` ✅
2. **Use the answer-finance-question command directly** - No agent needed
3. Parse financial PDFs and extract specific data as requested

AGENT: None

### 8. Unsupervised Learning Business

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- The Unsupervised Learning business
- Newsletter metrics or performance
- Company operations or challenges
- Business metrics when no specific company is mentioned
- Podcast, membership, or sponsorship matters
- "The company" or "my business" (default assumption)

**Example phrases that indicate this context:**
- "newsletter subscribers", "company performance", "UL metrics"
- But also: "how's the business", "company challenges", "our revenue"

**YOU MUST IMMEDIATELY:**
1. Load this context file:
   - `~/.claude/context/unsupervised-learning/CLAUDE.md` ✅

AGENT: None

### 9. Web Development & Visual Testing

**WHEN THE USER IS ASKING ABOUT (semantic understanding):**
- Taking screenshots or capturing visuals
- Browser-based debugging
- Visual testing or comparison
- Iterative visual development
- Browser automation tasks
- UI/UX debugging

**Example phrases that indicate this context:**
- "screenshot", "browser tools", "visual test"
- But also: "show me what it looks like", "capture the page", "visual debugging"

**YOU MUST IMMEDIATELY:**
1. Load this context file:
   - `~/.claude/context/tools/CLAUDE.md` ✅
2. **Use Task tool with subagent_type="designer"** - PRIMARY for visual testing
3. Use Playwright MCP tools for browser automation as seen in ~/.claude/context/tools/CLAUDE.md

AGENT: designer if it's a design question

### 10. Capture Learning - Problem/Solution Documentation

**WHEN THE USER IS SAYING (semantic understanding):**
- Expressing satisfaction with a solution we found
- Wanting to document what we just accomplished
- Indicating we should save or record our work
- Acknowledging successful problem-solving
- Asking to log or capture learnings

**Example phrases that indicate this context:**
- "Great job, log this", "Nice work, make a record", "Perfect! Document this"
- "Log this solution", "Make a record of what we did", "Capture this learning"
- "Save this for later", "Document what we fixed", "Record this solution"
- But also: "That worked!", "Excellent, save this", "Good job, remember this"

**YOU MUST IMMEDIATELY:**
1. Run the capture-learning command with the problem and solution:
   ```bash
   bun ~/.claude/commands/capture-learning.ts "[problem description]" "[solution description]"
   ```
2. The command will create a markdown file in `~/.claude/context/learnings/`
3. File will be named: `YYYY-MM-DD HHMM:SS-hyphenated-problem-description-in-8-words.md`
4. Confirm the learning was captured successfully

**IMPORTANT:** When capturing learnings:
- Extract the problem from what we were working on
- Summarize the solution we implemented
- Include key tools, commands, or techniques used
- Note any important gotchas or insights discovered

AGENT: None

## 🔴 SPECIAL RECOGNITION RULES - ALWAYS APPLY

### Research Triggers - MANDATORY ACTION
**When the user's INTENT is to gather information or learn about something:**
- This includes asking questions, seeking understanding, or exploring topics
- Even if they don't use the word "research"
- Examples: "tell me about", "what's happening with", "I need to know"

**ACTION:** Immediately load `~/.claude/context/tools/CLAUDE.md` ✅ and use researcher agent

### Company References - MANDATORY INTERPRETATION
**When user mentions a company/business WITHOUT being specific:**
- Default assumption: They mean Unsupervised Learning
- This applies to: "the company", "my business", "our company"
- Also applies to business metrics or performance discussions

**ACTION:** Immediately load `~/.claude/context/unsupervised-learning/CLAUDE.md` ✅

## ⚡ YOUR LOADING PROTOCOL

**YOU MUST follow these steps EXACTLY:**

1. **UNDERSTAND** the semantic meaning and intent of the user's prompt
2. **DETERMINE** which context categories match the user's actual needs
3. **IMMEDIATELY LOAD** all relevant context files using Read tool
4. **CONFIRM** each loaded file with a ✅ checkmark
5. **INVOKE** the specified agent using Task tool if indicated
6. **PROCEED** with the task using loaded context knowledge

## ❗ CRITICAL REMINDERS

- **DO NOT ASK** for permission to load context - just do it
- **DO NOT WAIT** - load immediately upon detection
- **DO NOT SKIP** context loading even if you think you know the answer
- **ALWAYS ERR** on the side of loading more context rather than less
- **ALWAYS USE** the specified agent 
