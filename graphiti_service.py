"""
Manufacturing Asset Intelligence - Graphiti Service
Simple REST API that connects Graphiti with Neo4j
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Manufacturing Graphiti Service",
    description="Smart knowledge graph service for manufacturing assets",
    version="1.0.0"
)

# Import Graphiti (will be installed via requirements.txt)
try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    
    # Initialize Graphiti with Neo4j connection
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password")
    )
    logger.info("✅ Graphiti initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Graphiti: {e}")
    graphiti = None

# ============================================
# DATA MODELS (Define what data looks like)
# ============================================

class Node(BaseModel):
    """A single entity (tool, part, project, asset)"""
    id: str
    label: str  # 'Tool', 'Part', 'Project', 'Asset'
    properties: Dict[str, Any]

class Edge(BaseModel):
    """A relationship between two entities"""
    source: str  # ID of source entity
    target: str  # ID of target entity
    type: str   # 'USES', 'COMPATIBLE_WITH', etc.
    properties: Optional[Dict[str, Any]] = {}

class GraphInput(BaseModel):
    """Complete graph data from document"""
    nodes: List[Node]
    edges: List[Edge]
    episode_name: str
    episode_type: str = "document"
    source_description: str

class SearchQuery(BaseModel):
    """Search request"""
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = {}

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Manufacturing Graphiti Service",
        "status": "healthy" if graphiti else "unhealthy",
        "version": "1.0.0",
        "endpoints": ["/health", "/build-graph", "/search-graph"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy" if graphiti else "unhealthy",
        "graphiti_connected": graphiti is not None,
        "neo4j_uri": os.getenv("NEO4J_URI", "Not set"),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/build-graph")
async def build_graph(data: GraphInput):
    """
    Build knowledge graph from extracted entities and relationships
    
    This is called when a document is uploaded and processed.
    """
    
    if not graphiti:
        raise HTTPException(
            status_code=503, 
            detail="Graphiti service not initialized. Check Neo4j connection."
        )
    
    try:
        logger.info(f"📥 Building graph for: {data.episode_name}")
        
        # Step 1: Create Episode (like a chapter in a book)
        # This groups all data from one document together
        episode = await graphiti.add_episode(
            name=data.episode_name,
            episode_body=f"Manufacturing document with {len(data.nodes)} entities and {len(data.edges)} relationships",
            source_description=data.source_description,
            episode_type=EpisodeType.text,
            reference_time=datetime.utcnow()
        )
        
        logger.info(f"✅ Created episode: {episode.uuid}")
        
        # Step 2: Add Nodes (entities like tools, parts)
        node_results = []
        for node in data.nodes:
            try:
                result = await graphiti.add_node(
                    name=node.properties.get('name', node.id),
                    labels=[node.label],
                    properties=node.properties,
                    episode_id=episode.uuid
                )
                node_results.append({
                    "id": node.id,
                    "graphiti_id": str(result.uuid),
                    "status": "created"
                })
                logger.info(f"  ✅ Created node: {node.properties.get('name')}")
            except Exception as e:
                logger.error(f"  ❌ Failed to create node {node.id}: {e}")
                node_results.append({
                    "id": node.id,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Step 3: Add Edges (relationships)
        edge_results = []
        for edge in data.edges:
            try:
                result = await graphiti.add_edge(
                    source_node_id=edge.source,
                    target_node_id=edge.target,
                    edge_type=edge.type,
                    properties=edge.properties,
                    episode_id=episode.uuid
                )
                edge_results.append({
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "status": "created"
                })
                logger.info(f"  ✅ Created edge: {edge.source} -> {edge.target}")
            except Exception as e:
                logger.error(f"  ❌ Failed to create edge: {e}")
                edge_results.append({
                    "source": edge.source,
                    "target": edge.target,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Return summary
        return {
            "status": "success",
            "episode_id": str(episode.uuid),
            "episode_name": data.episode_name,
            "nodes_created": len([n for n in node_results if n['status'] == 'created']),
            "edges_created": len([e for e in edge_results if e['status'] == 'created']),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to build graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-graph")
async def search_graph(data: SearchQuery):
    """
    Search knowledge graph with natural language
    
    This is called when user asks a question.
    """
    
    if not graphiti:
        raise HTTPException(status_code=503, detail="Graphiti not initialized")
    
    try:
        logger.info(f"🔍 Searching for: {data.query}")
        
        # Use Graphiti's smart search
        results = await graphiti.search(
            query=data.query,
            limit=data.limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "name": result.node.name,
                "labels": result.node.labels,
                "properties": result.node.properties,
                "relevance_score": result.score,
                "context": getattr(result, 'context', None)
            })
        
        logger.info(f"✅ Found {len(formatted_results)} results")
        
        return {
            "status": "success",
            "query": data.query,
            "results": formatted_results,
            "count": len(formatted_results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
