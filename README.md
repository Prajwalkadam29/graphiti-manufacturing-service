# graphiti-manufacturing-service
Graphiti service for manufacturing assets.


# Manufacturing Asset Intelligence - Graphiti Service

A smart knowledge graph service for manufacturing assets powered by Google Gemini AI and Neo4j. Automatically extracts entities, relationships, and insights from unstructured manufacturing data.

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🎯 Features

- **🤖 AI-Powered Extraction**: Automatically extracts entities and relationships using Google Gemini
- **🔍 Semantic Search**: Natural language search across your knowledge graph
- **🔗 Knowledge Graph**: Neo4j-powered graph database for complex relationships
- **🛡️ Duplicate Prevention**: Automatic detection and prevention of duplicate episodes
- **📊 Statistics & Monitoring**: Real-time insights into your knowledge graph
- **⚡ REST API**: Easy-to-use FastAPI endpoints
- **🔄 Episode Management**: Add, list, search, and delete episodes

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Neo4j Aura](#setup-neo4j-aura)
3. [Setup Indexes (Critical)](#setup-indexes-critical)
4. [Get Google Gemini API Key](#get-google-gemini-api-key)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Running Locally](#running-locally)
8. [Deploying to Render](#deploying-to-render)
9. [API Endpoints](#api-endpoints)
10. [Example Requests](#example-requests)
11. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

- Python 3.10 or higher
- Neo4j Aura account (free tier available)
- Google Gemini API key (free tier available)
- Git (for deployment)

---

## 🗄️ Setup Neo4j Aura

### Step 1: Create Neo4j Aura Account

1. Go to [Neo4j Aura](https://console.neo4j.io/)
2. Sign up for a free account
3. Click **"Create Database"** → Select **"Free"** tier
4. Choose a name for your database (e.g., "manufacturing-graph")
5. **Important**: Save the password shown - you won't see it again!

### Step 2: Get Connection Details

After creating the database:

1. Click on your database in the console
2. Note down these details:
   - **URI**: `neo4j+s://xxxxxxxx.databases.neo4j.io`
   - **Username**: `neo4j`
   - **Password**: (the one you saved in Step 1)

### Step 3: Open Neo4j Browser

1. In Neo4j Aura console, click **"Open"** next to your database
2. Or click **"Query"** button
3. Login with username `neo4j` and your password

---

## 🔍 Setup Indexes (Critical)

**⚠️ IMPORTANT**: These indexes are **required** for Graphiti to work. Run these in Neo4j Browser before using the service.

### Step 1: Create Node Fulltext Index

Open Neo4j Browser and run:

```cypher
CREATE FULLTEXT INDEX node_name_and_summary IF NOT EXISTS
FOR (n:Entity)
ON EACH [n.name, n.summary]
```

**What this does**: Creates a fulltext search index on Entity nodes for the `name` and `summary` properties.

### Step 2: Create Edge Fulltext Index

```cypher
CREATE FULLTEXT INDEX edge_name_and_fact IF NOT EXISTS
FOR ()-[r:RELATES_TO]-()
ON EACH [r.name, r.fact]
```

**What this does**: Creates a fulltext search index on relationships for the `name` and `fact` properties.

### Step 3: Create Additional Indexes (Recommended)

```cypher
CREATE INDEX entity_uuid IF NOT EXISTS FOR (n:Entity) ON (n.uuid);
CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name);
CREATE INDEX episode_uuid IF NOT EXISTS FOR (n:Episode) ON (n.uuid);
```

**What this does**: Creates regular indexes for better query performance.

### Step 4: Verify Indexes

Run this query to check all indexes were created:

```cypher
SHOW INDEXES
```

You should see these indexes:
- ✅ `node_name_and_summary` (FULLTEXT)
- ✅ `edge_name_and_fact` (FULLTEXT)
- ✅ `entity_uuid` (RANGE)
- ✅ `entity_name` (RANGE)
- ✅ `episode_uuid` (RANGE)

---

## 🔑 Get Google Gemini API Key

### Step 1: Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key (starts with `AIza...`)

### Step 2: Save API Key

Keep this key safe - you'll need it for configuration.

---

## 💾 Installation

### Step 1: Clone or Download Project

```bash
# If using Git
git clone <your-repo-url>
cd manufacturing-graphiti-service

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Create `.env` File

Create a `.env` file in the project root with your credentials:

```env
# ===========================================
# Manufacturing Graphiti Service Configuration
# ===========================================

# Google Gemini API Configuration
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GEMINI_MODEL=gemini-2.0-flash
GEMINI_EMBEDDING_MODEL=text-embedding-004
GEMINI_RERANKER_MODEL=gemini-2.0-flash-exp

# Graphiti Configuration
GRAPHITI_PROVIDER=google-genai

# Neo4j Database Configuration
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password-here

# Server Configuration
PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=development

# Optional: Disable telemetry
GRAPHITI_TELEMETRY_ENABLED=false
```

**Replace**:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `NEO4J_URI`: Your Neo4j Aura connection URI
- `NEO4J_PASSWORD`: Your Neo4j password

---

## 🚀 Running Locally

### Start the Service

```bash
# Make sure virtual environment is activated
python graphiti_service.py
```

**Expected Output**:
```
🚀 Starting Manufacturing Graphiti Service
   Version: 3.0.0
✅ Google Gemini API key configured
✅ Graphiti initialized with Gemini
   LLM Model: gemini-2.0-flash
   Embedding Model: text-embedding-004
   Reranker Model: gemini-2.0-flash-exp
   Graphiti Status: ✅ Ready
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test the Service

Open your browser and go to:
```
http://localhost:8000
```

You should see:
```json
{
  "service": "Manufacturing Graphiti Service with Gemini",
  "status": "healthy",
  "version": "3.0.0"
}
```

---

## 📡 API Endpoints

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info and status |
| GET | `/health` | Detailed health check |
| GET | `/stats` | Knowledge graph statistics |
| GET | `/episodes?limit=10` | List all episodes |

### Knowledge Graph Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/add-episode` | Add text episode (auto-extraction) |
| POST | `/build-graph` | Add pre-extracted entities/relations |
| POST | `/search-graph` | Search with natural language |
| DELETE | `/episode/{uuid}` | Delete an episode |

---

## 🧪 Example Requests

### 1. Check Service Health

```bash
curl https://your-service.onrender.com/health
```
*Note:* Instead of `https://your-service.onrender.com`, you can hit request on `http://localhost:8000`.

**Response**:
```json
{
  "status": "healthy",
  "graphiti_initialized": true,
  "gemini_configured": true,
  "neo4j_connected": true
}
```

---

### 2. Add Manufacturing Data (Simple)

```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Installation - Jan 2024",
    "episode_body": "CNC Machine XYZ-100 was installed in Assembly Line 5 on 2024-01-15. It processes aluminum parts and has a capacity of 500 parts per day. Manufactured by ACME Corp.",
    "source_description": "Installation log from maintenance department"
  }'
```

**Response**:
```json
{
  "status": "success",
  "episode_id": "6e6e6f20-79dc-4dae-952d-d1b1217f81d8",
  "episode_name": "Machine Installation - Jan 2024",
  "entities_extracted": 4,
  "relations_extracted": 3,
  "message": "Episode added successfully. Entities and relationships extracted automatically.",
  "timestamp": "2025-10-19T04:39:16.438884"
}
```

---

### 3. Add Complex Manufacturing Scenario

```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Equipment Report - Week 42",
    "episode_body": "Production summary for week 42:\n\nRobotic Arm RA-500 in Cell B completed 1,250 welds with 99.8% accuracy. Operated by technician John Smith.\n\nLathe L-100 in Workshop D processed 500 aluminum parts. Requires maintenance check due soon.\n\nCNC Machine M-2000 in Cell A ran for 40 hours with 99.5% uptime. Handled orders for Project Phoenix.\n\nQuality inspection found 3 defective parts from Machine M-2000, traced to calibration issue.",
    "source_description": "Weekly maintenance and production report"
  }'
```

**Response**:
```json
{
  "status": "success",
  "episode_id": "abc-123-def-456",
  "entities_extracted": 8,
  "relations_extracted": 12
}
```

---

### 4. Search the Knowledge Graph

**Simple Search**:
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What machines are in Assembly Line 5?",
    "limit": 10
  }'
```

**Response**:
```json
{
  "status": "success",
  "query": "What machines are in Assembly Line 5?",
  "results": [
    {
      "uuid": "a53d5fae-c25c-4752-8f8c-4e022447c72b",
      "name": "INSTALLED_IN",
      "fact": "Machine XYZ-100 was installed in Assembly Line 5.",
      "valid_at": "2024-01-15 00:00:00+00:00"
    }
  ],
  "count": 1
}
```

**Complex Search**:
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which robotic arms had quality issues and who operates them?",
    "limit": 5
  }'
```

---

### 5. Prevent Duplicate Episodes

**First Attempt (Success)**:
```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maintenance Check - March 2024",
    "episode_body": "Routine maintenance performed on Machine XYZ-100.",
    "source_description": "Maintenance log"
  }'
```

**Second Attempt (Blocked)**:
```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maintenance Check - March 2024",
    "episode_body": "Different content",
    "source_description": "Maintenance log"
  }'
```

**Response**:
```json
{
  "status": "duplicate",
  "episode_id": "existing-uuid",
  "message": "Episode with this name already exists. Set 'skip_duplicate_check': true to force add."
}
```

**Force Add Duplicate**:
```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maintenance Check - March 2024",
    "episode_body": "Different content",
    "source_description": "Maintenance log",
    "skip_duplicate_check": true
  }'
```

---

### 6. Build Custom Graph (Pre-Extracted Data)

```bash
curl -X POST https://your-service.onrender.com/build-graph \
  -H "Content-Type: application/json" \
  -d '{
    "episode_name": "Custom Equipment Network",
    "source_description": "Pre-extracted from inventory system",
    "nodes": [
      {
        "id": "machine1",
        "label": "Machine",
        "properties": {
          "name": "CNC Mill MC-500",
          "type": "CNC Machine",
          "location": "Building A"
        }
      },
      {
        "id": "line1",
        "label": "ProductionLine",
        "properties": {
          "name": "Assembly Line 7",
          "capacity": 1000
        }
      }
    ],
    "edges": [
      {
        "source": "machine1",
        "target": "line1",
        "type": "LOCATED_IN",
        "properties": {
          "since": "2024-01-01"
        }
      }
    ]
  }'
```

---

### 7. Get Statistics

```bash
curl https://your-service.onrender.com/stats
```

**Response**:
```json
{
  "status": "success",
  "episodes_count": 15,
  "entities_count": 87,
  "relationships_count": 134,
  "timestamp": "2025-10-19T05:00:00"
}
```

---

### 8. List All Episodes

```bash
curl https://your-service.onrender.com/episodes?limit=10
```

**Response**:
```json
{
  "status": "success",
  "episodes": [
    {
      "uuid": "abc-123",
      "name": "Machine Installation - Jan 2024",
      "created_at": "2024-01-15T10:30:00",
      "source": "Installation log"
    }
  ],
  "count": 10
}
```

---

### 9. Delete an Episode

```bash
curl -X DELETE https://your-service.onrender.com/episode/abc-123-def-456
```

**Response**:
```json
{
  "status": "success",
  "message": "Episode abc-123-def-456 deleted successfully"
}
```

---

## 🎓 Usage Patterns

### Pattern 1: Daily Equipment Logs

Add daily logs as episodes:

```bash
# Monday
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Equipment Log - 2024-01-15",
    "episode_body": "Machine XYZ operated 8 hours, produced 400 parts...",
    "source_description": "Daily operations log"
  }'

# Tuesday
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Equipment Log - 2024-01-16",
    "episode_body": "Machine XYZ operated 6 hours, maintenance performed...",
    "source_description": "Daily operations log"
  }'
```

Then search across all logs:
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many hours did Machine XYZ operate last week?"
  }'
```

---

### Pattern 2: Incident Reports

Track equipment issues:

```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Incident Report - INC-2024-001",
    "episode_body": "Machine XYZ-100 experienced overheating at 14:30. Temperature reached 85°C. Emergency shutdown performed by operator Jane Doe. Root cause: cooling system failure. Vendor ABC Parts contacted for replacement parts.",
    "source_description": "Safety incident report"
  }'
```

Later, find related incidents:
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What cooling system failures have we had?"
  }'
```

---

### Pattern 3: Maintenance Tracking

```bash
curl -X POST https://your-service.onrender.com/add-episode \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maintenance - Machine XYZ-100 - 2024-Q1",
    "episode_body": "Quarterly maintenance performed:\n- Oil change completed\n- Bearings inspected, no wear detected\n- Calibration checked and adjusted\n- Software updated to v2.3.1\n- Next service due: April 2024\nTechnician: Mike Johnson\nParts used: Oil Filter OF-123, Lubricant LUB-456",
    "source_description": "Quarterly maintenance schedule"
  }'
```

---

## 🔍 Advanced Search Examples

### Temporal Queries
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What happened to Machine XYZ-100 in January 2024?"
  }'
```

### Relationship Queries
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which machines are operated by John Smith?"
  }'
```

### Quality & Performance Queries
```bash
curl -X POST https://your-service.onrender.com/search-graph \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me machines with quality issues or low uptime"
  }'
```

---

## 🛠️ Troubleshooting

### Issue: "Graphiti not initialized"

**Symptoms**: Service returns 503 errors

**Solutions**:
1. Check your `.env` file has correct credentials
2. Verify `GEMINI_API_KEY` is set and valid
3. Check Neo4j connection details
4. Restart the service

### Issue: "There is no such fulltext schema index"

**Symptoms**: Errors mentioning `node_name_and_summary` or `edge_name_and_fact`

**Solution**: You forgot to create the indexes! Go back to [Setup Indexes](#setup-indexes-critical) section.

### Issue: Duplicate entities created

**Symptoms**: Search returns multiple similar entities

**Explanation**: This is normal. Graphiti uses AI to merge entities, but it's not 100% perfect. Very similar but slightly different entities might be kept separate.

**Solution**: Use more consistent naming in your episode bodies.

### Issue: Search returns no results

**Solutions**:
1. Wait 3-5 seconds after adding episode for indexing
2. Try different search queries
3. Check if data was actually added: `curl https://your-service.onrender.com/stats`
4. Verify indexes are created: Run `SHOW INDEXES` in Neo4j Browser

### Issue: Slow response times

**Solutions**:
1. Reduce `limit` parameter in searches
2. Check Neo4j Aura instance status
3. Monitor Gemini API quota
4. Consider upgrading Neo4j tier for production

---

## 📊 Monitoring

### Check Service Health
```bash
# Quick check
curl https://your-service.onrender.com/

# Detailed health
curl https://your-service.onrender.com/health
```

### Monitor Graph Growth
```bash
# Get statistics
curl https://your-service.onrender.com/stats

# Count episodes
curl https://your-service.onrender.com/episodes?limit=1
```

### View Logs

**Local**:
- Check terminal output

**Render**:
- Go to Render dashboard → Your service → Logs tab

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** to Git
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables** in production (Render handles this)

3. **Rotate API keys** periodically

4. **Use Neo4j Aura** for secure managed database

5. **Enable HTTPS** (Render provides this automatically)

---

## 📚 Project Structure

```
manufacturing-graphiti-service/
├── graphiti_service.py      # Main FastAPI application
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (DO NOT COMMIT)
├── .gitignore              # Git ignore file
├── render.yaml             # Render deployment config
└── README.md               # This file
```

---

## 🤝 Support

### Documentation
- [Graphiti Core Docs](https://docs.graphiti.ai/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Built with ❤️ for manufacturing intelligence**
