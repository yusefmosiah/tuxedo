Choir: OpenHands Fork for Citation Economics
Strategic Goal: Adapt OpenHands for research and writing with verifiable citation economics

Timeline: 4-6 weeks for initial adaptation

Core Insight: When citation verification works for text, it works for all content as a consequence.

Executive Summary
Fork OpenHands to create a research and writing platform focused on citation economics. The user sees a clean writing interface (Ghostwriter workflow), while the agent uses code tools behind the scenes to manipulate data, verify citations, and structure knowledge.

Key Architectural Principle:

User-facing: Writing/research interface only (no code UI)
Agent-facing: Full access to code tools for data manipulation
Purpose: Agent is "smart" by running algorithms, parsing data, verifying citations
Why Fork OpenHands
Infrastructure We Get:

Event streaming (show research progress)
Multi-agent coordination (hypothesis former + researchers + verifiers)
Browser tool (visual web research + citation verification)
Workspace (store research artifacts)
Terminal + code tools (agent uses internally)
What We Hide from Users:

Code editor UI
Git interface
Debugger panels
Test runner UI
What We Show to Users:

Research progress ("Forming hypotheses...")
Citation verification status
Evidence gathering visualization
Final research reports
Publishing options (domain + NFT)
What Agent Uses Internally:

# User sees: "Verifying citations..."

# Agent does:

terminal.run("python verify_citations.py evidence_1.md")
file_editor.parse_html(source_url)
code_tool.build_citation_graph(citations)
terminal.run("node extract_metadata.js pdf_file.pdf")
Citation Economics Focus
From Choir Whitepaper: The platform enables value attribution through verifiable citations. When we solve this for text (research reports), we solve it for all content types.

Result: Research platform where agent manipulates data intelligently, users see polished research flow

Core Mental Model: Agent Controls Computer
The key insight: User interacts with an agent that controls a computer.

User's View:
├── Chat panel (talk to agent)
├── Browser panel (agent's rendered output + web access)
└── Workspace files (agent's filesystem)
Agent's Computer:
├── Filesystem (markdown files, JSON data, HTML output)
├── Terminal (Python/Node scripts for data processing)
├── Browser (fetch sources, render documents)
└── Data feeds (global web + private APIs)
├── Public: Web scraping, APIs
└── Private: Somnia, user's wallet, custom feeds
Browser as Primary UI (Key Affordance)
Instead of building custom report viewer:

# Agent writes markdown

file_editor.write("04_draft/report.md", content)

# Convert to styled HTML

terminal.run("pandoc report.md -o report.html --css=choir-style.css")

# Display in browser

browser.navigate("file:///workspace/04_draft/report.html")
User sees: Beautiful rendered report in browser pane, updating live as agent writes.

Benefits:

✅ No custom UI needed (browser already handles CSS, images, links)
✅ Live preview as agent writes
✅ Citations are hyperlinks (click to verify)
✅ Export-ready (HTML already exists)
✅ Browser serves dual purpose: render docs + fetch sources
Mental model reinforced: Agent uses same browser to fetch sources AND display output.

Phase 1: Fork & UI Transformation (Week 1)
Objectives
Create fork with clean git history
Keep ALL backend tools (git, code editor, terminal, etc.) - agent uses these
Hide code UI from users - show only research/writing interface
Replace frontend with Ghostwriter research flow
Verify agent can still use code tools internally
1.1 Initial Fork

# Clone OpenHands

git clone https://github.com/All-Hands-AI/OpenHands.git choir-platform
cd choir-platform

# Create our fork

git remote rename origin upstream
git remote add origin https://github.com/choir-harmonies/choir-platform.git

# Create development branch

git checkout -b choir/main
1.2 Architecture: User UI vs Agent Tools
Backend Tools (Keep All - Agent Uses):

Tool Path Agent Uses For
Terminal /openhands/tools/terminal/ Run Python scripts, parse data
File editor /openhands/tools/file/ Manipulate JSON, parse HTML
Git /openhands/tools/git/ Version workspace, track changes
Browser /openhands/tools/browser/ Fetch sources, verify citations
Code tools /openhands/tools/code/ Data processing algorithms
Frontend (Replace with Research UI):

Remove from UI Replace With
Code editor panel Research report viewer
Git UI Citation graph visualization
Debugger panel Hypothesis status dashboard
Terminal UI Research progress indicator
Test runner UI Citation verification panel
Key Principle:

User sees: "Verifying 47 citations..." ✍️
Agent does: terminal.run("python verify.py") (hidden)
1.3 Frontend Simplification: Browser-First
Core UI Components (Keep):

Chat panel (user ↔ agent conversation)
Browser panel (dual purpose: render reports + fetch sources)
Workspace file tree (show agent's filesystem)
Remove/Hide:

Code editor UI
Git panels
Debugger UI
Terminal UI (agent uses terminal, user doesn't see it)
Result: Clean 3-panel interface

┌─────────────┬──────────────────────┐
│ Chat │ Browser │
│ (convo) │ (rendered docs) │
│ │ │
├─────────────┤ │
│ Workspace │ │
│ Files │ │
│ │ │
└─────────────┴──────────────────────┘
Agent workflow for displaying documents:

# 1. Write markdown

file_editor.write("report.md", """

# DeFi Lending Research

## Hypothesis 1: Capital Efficiency

[Evidence shows...](sources/evidence_1.md)

## Citation Graph

See interactive visualization below...
""")

# 2. Convert to HTML with styling

terminal.run("""
pandoc report.md -o report.html \
 --css=choir-theme.css \
 --metadata title="Research Report" \
 --standalone
""")

# 3. Browser displays it

browser.navigate("file:///workspace/04_draft/report.html")

# User sees: Beautiful rendered report with live citations

For citation verification:

# User clicks citation link in rendered report

# Browser navigates to source (agent fetched earlier)

browser.navigate("https://source-url.com/paper.pdf")

# Or to local evidence file

browser.navigate("file:///workspace/02_evidence/evidence_1.html")
1.4 Agent Prompt: Use Code Tools Internally
System Prompt for Research Agent:

# openhands/prompts/research_agent.txt

You are a research agent with access to coding tools for data manipulation.
TOOLS AVAILABLE:

- terminal: Run Python/Node scripts to parse data
- file_editor: Manipulate JSON, parse HTML, structure citations
- browser: Fetch web sources, verify links
- git: Version control workspace
  USER SEES: Research progress ("Forming hypotheses", "Verifying citations")
  YOU DO: Use code tools to manipulate data intelligently
  Example workflow:

1. User: "Research DeFi lending"
2. You (internally):
   - terminal.run("python scrape_sources.py 'DeFi lending'")
   - file_editor.parse_html(sources)
   - file_editor.structure_json(citations)
3. User sees: "Found 47 sources, verifying citations..."
4. You (internally):
   - terminal.run("python verify_citations.py citations.json")
5. User sees: "✓ 43/47 citations verified"
   NEVER show code to user. They see research progress only.
   1.5 Verification: Agent Uses Tools, User Sees Research
   Test Script:

# test_hidden_tools.py

async def test_agent_uses_code_tools_internally():
"""Agent can use code tools while user sees research UI.""" # Start research
response = await agent.research("Test topic") # Assert: Agent used terminal internally
assert "terminal.run" in agent.internal_log # Assert: User only saw research messages
user_messages = [m for m in response if m["type"] == "user_visible"]
assert all("python" not in m["content"] for m in user_messages)
assert any("Forming hypotheses" in m["content"] for m in user_messages)
Phase 2: Ghostwriter Tool Integration (Week 2-3)
Objectives
Replace coding tools with Ghostwriter research tools
Integrate our existing tool nodes
Test multi-agent research workflow
Verify browser tool works for web research
2.1 Tool Migration Strategy
Our Tool Nodes → OpenHands Tool Format:

# backend/agent/ghostwriter/tools/hypothesis_former.py (our current)

class FormHypothesesTool(GhostwriterToolBase):
async def run(self, topic: str, session_id: str) -> ToolResult: # Our implementation
pass

# Adapt to OpenHands format:

# openhands/tools/ghostwriter/hypothesis_former.py

from openhands.tools import BaseTool
class FormHypothesesTool(BaseTool):
"""OpenHands-compatible wrapper."""
name = "form_hypotheses"
description = "Generate research hypotheses with certitude scores"
async def execute(self, **kwargs) -> dict: # Call our existing implementation
from backend.agent.ghostwriter.tools.hypothesis_former import FormHypothesesTool as OurTool
tool = OurTool()
result = await tool.run(**kwargs) # Convert to OpenHands format
return {
"success": result.success,
"output": result.output,
"metadata": result.metadata
}
Tool Registration:

# openhands/tools/ghostwriter/**init**.py

from .hypothesis_former import FormHypothesesTool
from .hypothesis_revisor import RevisitHypothesesTool
from .web_researcher import ExecuteWebResearchTool

# ... other tools

GHOSTWRITER_TOOLS = [
FormHypothesesTool,
RevisitHypothesesTool,
ExecuteWebResearchTool,
# ... all 10 tools
]

# openhands/tools/**init**.py

from .ghostwriter import GHOSTWRITER_TOOLS
from .browser import BrowserTool
from .file import FileEditorTool
from .terminal import TerminalTool

# Remove coding tools

# from .git import GitTool # REMOVED

# from .debugger import DebuggerTool # REMOVED

ALL_TOOLS = GHOSTWRITER_TOOLS + [BrowserTool, FileEditorTool, TerminalTool]
2.2 Browser Tool Enhancement (🔥 Killer Feature)
Current Browser Tool:

Navigate to URLs
Take screenshots
Extract text
Click elements
Enhance for Research Animation:

# openhands/tools/browser/research_browser.py

class ResearchBrowserTool(BrowserTool):
"""Enhanced browser for visual web research."""
async def execute*search(self, query: str, max_results: int = 20):
"""
Execute search and visually show process.
UI shows: - Browser navigating to Google - Search query typing animation - Results loading - Agent clicking relevant links - Text highlighting as it extracts citations
""" # Navigate to search engine
await self.navigate("https://google.com")
await self.emit_screenshot("search_page_loaded") # Type query (with animation events)
await self.type_text("#search-input", query, animated=True)
await self.emit_screenshot("query_entered") # Submit search
await self.click("#search-button")
await self.wait_for_load()
await self.emit_screenshot("results_loaded") # Extract and show results
results = await self.extract_search_results() # Visit each result
for i, result in enumerate(results[:max_results]):
await self.emit_event({
"type": "visiting_result",
"index": i,
"url": result.url,
"title": result.title
})
await self.navigate(result.url)
await self.emit_screenshot(f"result*{i}") # Extract and highlight citations
citations = await self.extract*citations()
await self.highlight_elements(citations)
await self.emit_screenshot(f"citations*{i}")
return results
Frontend Visualization:

// frontend/components/ResearchBrowser.tsx
export function ResearchBrowserView({ events }) {
return (
<div className="research-browser">
{/_ Live browser viewport _/}
<div className="browser-viewport">
<img src={latestScreenshot} alt="Browser" />
{/_ Highlight citations _/}
{highlightedElements.map(el => (
<div className="highlight" style={el.bounds} />
))}
</div>
{/_ Research progress _/}
<div className="research-progress">
<h3>Web Research Progress</h3>
<p>Visiting result {currentResult}/{totalResults}</p>
<p>Found {citationCount} citations</p>
</div>
{/_ Citation list _/}
<div className="citations">
{citations.map(citation => (
<CitationCard citation={citation} />
))}
</div>
</div>
)
}
Users watch the AI research in real-time. This is engaging and builds trust.

2.3 Multi-Agent Orchestration
Adapt OpenHands Swarm Pattern:

# openhands/agent/ghostwriter_orchestrator.py

from openhands.agent import Agent, DelegatorAgent
class GhostwriterOrchestrator(DelegatorAgent):
"""
Research orchestrator using OpenHands swarm pattern.
"""
def **init**(self):
super().**init**(
name="research*orchestrator",
tools=GHOSTWRITER_TOOLS
)
async def run(self, topic: str): # Stage 1: Form hypotheses (Sonnet)
hypothesis_agent = Agent(
llm=Sonnet,
tools=[FormHypothesesTool]
)
hypotheses = await self.delegate(
hypothesis_agent,
task=f"Form hypotheses about: {topic}"
) # Stage 2: Design experiments (Sonnet)
designer_agent = Agent(
llm=Sonnet,
tools=[DesignExperimentsTool]
)
experiments = await self.delegate(
designer_agent,
task="Design searches to test hypotheses",
context=hypotheses
) # Stage 3: Parallel research (Haiku swarm)
researcher_agents = [
Agent(llm=Haiku, tools=[ExecuteWebResearchTool, ResearchBrowserTool])
for * in range(5)
] # Parallel execution (OpenHands handles this)
evidence = await self.delegate_parallel(
researcher_agents,
tasks=experiments.searches
) # Continue through remaining stages...
Phase 3: UI Customization & Rebrand (Week 3-4)
Objectives
Replace GitHub OAuth with Passkey auth
Rebrand visual identity (OpenHands → Tuxedo)
Move navigation bar (left → right)
Replace code editor with report previewer
Apply our design system
3.1 Auth System Migration
Remove GitHub OAuth:

# Remove GitHub auth components

rm -rf frontend/src/auth/GitHubAuth.tsx
rm -rf frontend/src/auth/github-config.ts
Integrate Our Passkey Auth:

// frontend/src/auth/PasskeyAuth.tsx
// Copy from: tuxedo/src/components/PasskeyAuth.tsx
import { usePasskey } from '../hooks/usePasskey'
export function PasskeyAuth() {
const { login, register, isAuthenticated, user } = usePasskey()
// Same implementation we already have
return (
<div className="auth-container">
<h2>Sign in to Tuxedo</h2>
<button onClick={register}>Create Passkey</button>
<button onClick={login}>Sign In</button>
</div>
)
}
Update Backend:

# openhands/server/auth.py

# Remove GitHub OAuth

# from openhands.auth.github import GitHubAuth

# Add Passkey auth

from backend.auth.passkey_manager import PasskeyManager
class AuthManager:
def **init**(self):
self.passkey = PasskeyManager()
async def authenticate(self, credential: dict) -> User: # Verify passkey credential
user_id = await self.passkey.verify_credential(credential)
return User(id=user_id)
3.2 Visual Rebranding
Color Scheme (Stellar-inspired):

/_ frontend/src/styles/theme.css _/
:root {
/_ Primary - Stellar Purple/Blue _/
--color-primary: #7B61FF;
--color-primary-dark: #5B42D9;
--color-primary-light: #9B81FF;
/_ Accent - Cyan (blockchain) _/
--color-accent: #00D9FF;
/_ Background _/
--color-bg: #0A0E27;
--color-surface: #1A1E3F;
/_ Text _/
--color-text-primary: #FFFFFF;
--color-text-secondary: #A0AABF;
}
Logo Replacement:

# Replace logo files

cp tuxedo/public/logo.svg frontend/public/logo.svg
cp tuxedo/public/favicon.ico frontend/public/favicon.ico
#Update references
find frontend/src -name "_.tsx" -exec sed -i '' 's/OpenHands/Tuxedo/g' {} \;
find frontend/src -name "_.tsx" -exec sed -i '' 's/All-Hands AI/Tuxedo Research AI/g' {} \;
3.3 Layout Changes (Nav Bar: Left → Right)
Current Layout:

// OpenHands: Left sidebar navigation

<div className="app-layout">
  <Sidebar position="left">  {/* ← Navigation */}
    <NavLinks />
  </Sidebar>
  <MainContent />
</div>
Tuxedo Layout:

// Tuxedo: Right sidebar navigation

<div className="app-layout tuxedo-layout">
  <MainContent />  {/* ← Takes prominence */}
  <Sidebar position="right">  {/* ← Navigation moved */}
    <NavLinks />
  </Sidebar>
</div>
CSS Updates:

/_ frontend/src/styles/layout.css _/
.tuxedo-layout {
display: flex;
flex-direction: row-reverse; /_ Flip _/
}
.sidebar-right {
border-left: 1px solid var(--color-surface); /_ Was border-right _/
order: 2; /_ Ensure it's on right _/
}
.main-content {
order: 1;
flex: 1;
}
3.4 Replace Code Editor with Report Previewer
Remove:

rm -rf frontend/src/components/CodeEditor
rm -rf frontend/src/components/Theia
Add:

// frontend/src/components/ReportPreviewer.tsx
import ReactMarkdown from 'react-markdown'
export function ReportPreviewer({ workspace }) {
const [reportPath, setReportPath] = useState('07_final/final_report.md')
const [content, setContent] = useState('')
// Load report from workspace
useEffect(() => {
const loadReport = async () => {
const file = await workspace.readFile(reportPath)
setContent(file)
}
loadReport()
}, [reportPath])
return (
<div className="report-previewer">
<div className="toolbar">
<select value={reportPath} onChange={(e) => setReportPath(e.target.value)}>
<option value="00_hypotheses/initial_hypotheses.json">Hypotheses</option>
<option value="02_evidence/evidence_hypothesis_1.md">Evidence</option>
<option value="04_draft/thesis_driven_draft.md">Draft</option>
<option value="07_final/final_report.md">Final Report</option>
</select>
<button onClick={() => downloadReport()}>Download</button>
<button onClick={() => publishReport()}>Publish</button>
</div>
<div className="preview">
<ReactMarkdown>{content}</ReactMarkdown>
</div>
</div>
)
}
Phase 4: Advanced Features (Week 4-6)
Objectives
"Publish to your domain" functionality
NFT minting on Stellar/Somnia
Research templates
(Optional) Non-blocking interaction mode
4.1 "Publish to Your Domain"
Feature: Deploy research report to user's custom domain

# openhands/publishing/domain_publisher.py

class DomainPublisher:
"""
Publish research reports to user's domain.
Uses static site generation.
"""
async def publish_to_domain(
self,
workspace_dir: Path,
user_domain: str, # e.g., "research.alice.com"
deployment_target: str = "vercel" # or "netlify", "cloudflare pages"
): # 1. Generate static site from report
site_dir = await self.generate_static_site(workspace_dir) # 2. Deploy via API
if deployment_target == "vercel":
deployment_url = await self.deploy_to_vercel(
site_dir,
domain=user_domain
)
return deployment_url
async def generate_static_site(self, workspace_dir: Path) -> Path:
"""Convert research workspace to static website.""" # Create site structure
site_dir = workspace_dir / "\_site"
site_dir.mkdir(exist_ok=True) # Generate index.html from final report
report_md = (workspace_dir / "07_final/final_report.md").read_text()
html = markdown_to_html(report_md, template="research_report")
(site_dir / "index.html").write_text(html) # Copy evidence/hypotheses as subpages
(site_dir / "hypotheses.html").write_text(
generate_hypotheses_page(workspace_dir)
)
(site_dir / "evidence.html").write_text(
generate_evidence_page(workspace_dir)
)
return site_dir
Frontend:

// frontend/src/components/PublishModal.tsx
export function PublishModal({ workspace }) {
const [domain, setDomain] = useState('')
const [deploying, setDeploying] = useState(false)
const handlePublish = async () => {
setDeploying(true)
const result = await publishToDomain(workspace.id, domain)
alert(`Published to: ${result.url}`)
}
return (
<Modal>
<h2>Publish Research Report</h2>
<input
placeholder="your-domain.com"
value={domain}
onChange={(e) => setDomain(e.target.value)}
/>
<button onClick={handlePublish}>
{deploying ? 'Publishing...' : 'Publish to Domain'}
</button>
</Modal>
)
}
4.2 Multi-Chain EVM Publishing
Feature: Publish content/code to any EVM chain (Arbitrum, Base, Optimism, Avalanche, Monad)

# openhands/tools/blockchain/evm/nft_publisher.py

from web3 import Web3
from eth_account import Account
class EVMPublisher:
"""Publish content as NFTs across EVM chains."""
CHAINS = {
"arbitrum": {"rpc": "https://arb1.arbitrum.io/rpc", "chain_id": 42161},
"base": {"rpc": "https://mainnet.base.org", "chain_id": 8453},
"optimism": {"rpc": "https://mainnet.optimism.io", "chain_id": 10},
"avalanche": {"rpc": "https://api.avax.network/ext/bc/C/rpc", "chain_id": 43114},
"monad": {"rpc": "https://rpc.monad.xyz", "chain_id": 41454}, # Placeholder
}
async def mint_content_nft(
self,
workspace_dir: Path,
user_wallet: str,
chain: str = "base", # Default to Base (Coinbase L2)
nft_standard: str = "ERC721" # or "ERC1155"
): # 1. Upload to IPFS/Arweave
content_uri = await self.upload_to_decentralized_storage(workspace_dir) # 2. Connect to chain
w3 = Web3(Web3.HTTPProvider(self.CHAINS[chain]["rpc"])) # 3. Deploy or use existing NFT contract
nft_contract = await self.get_or_deploy_nft_contract(w3, chain, nft_standard) # 4. Mint NFT
tx_hash = await nft_contract.functions.mint(
to=user_wallet,
tokenURI=content_uri
).transact()
return {
"tx_hash": tx_hash.hex(),
"chain": chain,
"content_uri": content_uri,
"explorer_url": self.get_explorer_url(tx_hash, chain),
"opensea_url": self.get_opensea_url(nft_contract.address, chain)
}
async def deploy_custom_contract(
self,
workspace_dir: Path,
chain: str,
contract_name: str
):
"""
Deploy custom smart contract from workspace.
Supports EVM chains for code publishing.
""" # Read compiled contract from workspace
contract_json = (workspace_dir / "contracts" / f"{contract_name}.json").read_text() # Deploy to selected chain
w3 = Web3(Web3.HTTPProvider(self.CHAINS[chain]["rpc"])) # ... deployment logic
Multi-Chain UI:

// frontend/src/components/EVMPublishModal.tsx
export function EVMPublishModal({ workspace, contentType }) {
const [chain, setChain] = useState('base')
const chains = [
{ id: 'arbitrum', name: 'Arbitrum', icon: '🔷' },
{ id: 'base', name: 'Base', icon: '🔵' },
{ id: 'optimism', name: 'Optimism', icon: '🔴' },
{ id: 'avalanche', name: 'Avalaunch', icon: '🔺' },
{ id: 'monad', name: 'Monad', icon: '🟣' },
]
return (
<Modal title="Publish to EVM">
<h3>Select Chain</h3>
<div className="chain-selector">
{chains.map(c => (
<button
key={c.id}
className={chain === c.id ? 'active' : ''}
onClick={() => setChain(c.id)} >
{c.icon} {c.name}
</button>
))}
</div>
<button onClick={() => publishToChain(workspace, chain)}>
Publish {contentType} to {chains.find(c => c.id === chain)?.name}
</button>
</Modal>
)
}
4.3 Research Templates
Feature: Pre-configured research workflows for common tasks

# openhands/templates/research_templates.py

TEMPLATES = {
"defi_protocol_analysis": {
"name": "DeFi Protocol Analysis",
"hypotheses_template": [
{"hypothesis": "Protocol X has better capital efficiency than competitors"},
{"hypothesis": "Protocol X's security model is auditable"},
{"hypothesis": "Protocol X has sustainable tokenomics"}
],
"search_strategy": "focus_on_whitepapers_and_audits",
"style": "defi_report"
},
"market_research": {
"name": "Market Research Report",
"hypotheses_template": [
{"hypothesis": "Market size is growing at X% CAGR"},
{"hypothesis": "Key competitors are A, B, C"},
{"hypothesis": "Market is dominated by incumbents"}
],
"search_strategy": "broad_market_coverage",
"style": "business_report"
}
}
4.4 Non-Blocking Interaction (Optional)
If we want to add it later:

# openhands/agent/interruptible_agent.py

class InterruptibleAgent(Agent):
"""Agent that can be interrupted mid-task."""
async def run_interruptible(self, task: str):
while not self.is_complete(): # Check for user interventions
if self.has_pending_messages():
msg = self.get_next_message() # Decide: pause and respond, or queue for later?
if self.should_pause_for(msg): # Pause main task
response = await self.handle_intervention(msg)
await self.emit_message(response) # Ask if should continue
should_continue = await self.ask_user("Continue research?")
if not should_continue:
return self.get_current_state()
else: # Queue for later
self.queue_message(msg) # Continue main task
await self.execute_next_action()
Deployment
Phala CVM Deployment
Docker Compose for Phala:

# docker-compose.phala.yaml

version: '3.8'
services:
tuxedo-backend:
build:
context: .
dockerfile: Dockerfile
volumes: - phala-data:/app/data # Persistent, encrypted
environment: - PHALA_DEPLOYMENT=true - BASE_URL=https://tuxedo.phala.network
ports: - "8000:8000"
volumes:
phala-data:
driver: local # Phala provides encrypted volumes
Maintenance Strategy
Syncing with Upstream

# Periodically pull OpenHands updates

git fetch upstream

# Review changes

git log tuxedo/main..upstream/main

# Selectively merge useful updates

git cherry-pick <commit-hash>

# Or merge entire release

git merge upstream/v2.0.0
What to Sync:

✅ Core bug fixes (event stream, WebSocket)
✅ Performance improvements
✅ Security patches
❌ New coding tools (we don't need)
❌ UI changes that conflict with our design
Success Metrics
Phase 1 Complete (UI Transformation)
✅ Fork created, all backend tools preserved
✅ Code UI hidden from users
✅ Research interface implemented
✅ Agent can use code tools internally
✅ Users see research flow only
Phase 2 Complete (Ghostwriter Tools)
✅ All 10 research tools integrated
✅ Citation verification working
✅ Multi-agent research coordination
✅ Browser shows citation verification visually
Phase 3 Complete (Citation Economics)
✅ Citation graph visualization
✅ Value attribution working
✅ On-chain citation verification
✅ Passkey auth integrated
Phase 4 Complete (Publishing & Economics)
✅ Publish to custom domain
✅ EVM multi-chain publishing (Base, Arbitrum, Optimism)
✅ NFT minting with embedded citations
✅ Citation economics working (pay for verified citations)
✅ Content attribution graph on-chain
Risk Mitigation
Risk Mitigation
Upstream breaking changes Pin to stable release, selective merge
Too much code to maintain Focus on core, delete aggressively
Performance issues Profiling, optimize event stream
User confusion (different from OpenHands) Clear onboarding, documentation
Next Steps
Review this plan with team
Create fork (Week 1, Day 1)
Run cleanup script (Week 1, Day 1)
Verify core tests (Week 1, Day 2)
Start Ghostwriter tool integration (Week 2)
Estimated Time to MVP: 4-6 weeks (vs 3-6 months from scratch)

ROI: 5-10x faster time to market by leveraging mature infrastructure
