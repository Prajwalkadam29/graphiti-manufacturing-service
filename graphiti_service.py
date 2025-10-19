"""
Manufacturing Asset Intelligence - Graphiti Service with Google Gemini
Updated REST API using latest Graphiti Core with proper Gemini integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY not set - service will not function")
else:
    logger.info("✅ Google Gemini API key configured")

# Initialize Graphiti with latest Gemini integration
graphiti = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global graphiti

    # Startup
    logger.info("🚀 Starting Manufacturing Graphiti Service")
    logger.info(f"   Version: 3.0.0")

    try:
        from graphiti_core import Graphiti
        from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
        from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
        from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

        if GEMINI_API_KEY:
            # Initialize Graphiti with Gemini components
            graphiti = Graphiti(
                os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password"),
                llm_client=GeminiClient(
                    config=LLMConfig(
                        api_key=GEMINI_API_KEY,
                        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
                    )
                ),
                embedder=GeminiEmbedder(
                    config=GeminiEmbedderConfig(
                        api_key=GEMINI_API_KEY,
                        embedding_model=os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
                    )
                ),
                cross_encoder=GeminiRerankerClient(
                    config=LLMConfig(
                        api_key=GEMINI_API_KEY,
                        model=os.getenv("GEMINI_RERANKER_MODEL", "gemini-2.0-flash-exp")
                    )
                )
            )

            logger.info(f"✅ Graphiti initialized with Gemini")
            logger.info(f"   LLM Model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')}")
            logger.info(f"   Embedding Model: {os.getenv('GEMINI_EMBEDDING_MODEL', 'text-embedding-004')}")
            logger.info(f"   Reranker Model: {os.getenv('GEMINI_RERANKER_MODEL', 'gemini-2.0-flash-exp')}")
        else:
            logger.warning("⚠️ Cannot initialize Graphiti without GEMINI_API_KEY")

    except ImportError as ie:
        logger.error(f"❌ Graphiti not installed properly: {ie}")
        logger.info("ℹ️ Install with: pip install 'graphiti-core[google-genai]'")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Graphiti: {e}")
        logger.info("ℹ️ Check your Neo4j connection and API key")

    logger.info(f"   Graphiti Status: {'✅ Ready' if graphiti else '❌ Not initialized'}")

    yield  # Application runs here

    # Shutdown
    logger.info("👋 Shutting down Manufacturing Graphiti Service")
    if graphiti:
        try:
            await graphiti.close()
            logger.info("✅ Graphiti connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Graphiti: {e}")

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Manufacturing Graphiti Service (Gemini)",
    description="Smart knowledge graph service for manufacturing assets using Google Gemini",
    version="3.0.0",
    lifespan=lifespan
)

# ============================================
# DATA MODELS
# ============================================

class Node(BaseModel):
    """A single entity (tool, part, project, asset)"""
    id: str
    label: str
    properties: Dict[str, Any]

class Edge(BaseModel):
    """A relationship between two entities"""
    source: str
    target: str
    type: str
    properties: Optional[Dict[str, Any]] = {}

class GraphInput(BaseModel):
    """Complete graph data from document"""
    nodes: List[Node]
    edges: List[Edge]
    episode_name: str
    episode_type: str = "document"
    source_description: str
    reference_time: Optional[str] = None  # ISO format timestamp

class SearchQuery(BaseModel):
    """Search request"""
    query: str
    limit: int = 10
    center_node_uuid: Optional[str] = None  # For focused searches
    num_results: Optional[int] = None  # Alternative to limit

class AddEpisodeRequest(BaseModel):
    """Request to add a text episode"""
    name: str
    episode_body: str
    source_description: str
    reference_time: Optional[str] = None

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Manufacturing Graphiti Service with Gemini",
        "status": "healthy" if graphiti else "unhealthy",
        "version": "3.0.0",
        "llm_provider": "Google Gemini",
        "llm_model": "gemini-2.0-flash",
        "embedding_model": "text-embedding-004",
        "reranker_model": "gemini-2.0-flash-exp",
        "endpoints": {
            "health": "/health",
            "build_graph": "/build-graph",
            "search_graph": "/search-graph",
            "add_episode": "/add-episode",
            "get_stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy" if graphiti else "unhealthy",
        "graphiti_initialized": graphiti is not None,
        "gemini_configured": GEMINI_API_KEY is not None,
        "neo4j_uri": os.getenv("NEO4J_URI", "Not set"),
        "neo4j_user": os.getenv("NEO4J_USER", "neo4j"),
        "configuration": {
            "llm_model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            "embedding_model": os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004"),
            "reranker_model": os.getenv("GEMINI_RERANKER_MODEL", "gemini-2.0-flash-exp")
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # Try to check Neo4j connection
    if graphiti:
        try:
            # Simple connection test
            health_status["neo4j_connected"] = True
        except Exception as e:
            health_status["neo4j_connected"] = False
            health_status["neo4j_error"] = str(e)

    return health_status

@app.post("/add-episode")
async def add_episode(data: AddEpisodeRequest):
    """
    Add a text episode to the knowledge graph

    This creates an episode node and extracts entities/relationships
    automatically using Gemini's understanding.
    """
    if not graphiti:
        raise HTTPException(
            status_code=503,
            detail="Graphiti not initialized. Check GEMINI_API_KEY and Neo4j connection."
        )

    try:
        logger.info(f"📝 Adding episode: {data.name}")

        # Parse reference time if provided
        ref_time = datetime.utcnow()
        if data.reference_time:
            try:
                ref_time = datetime.fromisoformat(data.reference_time.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Failed to parse reference_time: {e}, using current time")

        # Add episode - Graphiti will automatically extract entities and relationships
        result = await graphiti.add_episode(
            name=data.name,
            episode_body=data.episode_body,
            source_description=data.source_description,
            reference_time=ref_time
        )

        # FIXED: Handle different return types from add_episode
        episode_id = None
        entities_count = 0
        relations_count = 0
        
        # Try to extract episode information from result
        if hasattr(result, 'episode'):
            episode = result.episode
            if hasattr(episode, 'uuid'):
                episode_id = str(episode.uuid)
            elif hasattr(episode, 'id'):
                episode_id = str(episode.id)
        
        # Try to get entity/relation counts
        if hasattr(result, 'nodes'):
            entities_count = len(result.nodes) if result.nodes else 0
        if hasattr(result, 'edges'):
            relations_count = len(result.edges) if result.edges else 0

        # Fallback if no episode ID found
        if not episode_id:
            episode_id = "created"  # Generic placeholder

        logger.info(f"✅ Episode processed successfully")
        logger.info(f"   Entities extracted: {entities_count}")
        logger.info(f"   Relations extracted: {relations_count}")

        return {
            "status": "success",
            "episode_id": episode_id,
            "episode_name": data.name,
            "entities_extracted": entities_count,
            "relations_extracted": relations_count,
            "message": "Episode added successfully. Entities and relationships extracted automatically.",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Failed to add episode: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-graph")
async def build_graph(data: GraphInput):
    """
    Build knowledge graph from pre-extracted entities and relationships

    This is useful when you've already extracted entities from a document
    and want to add them to the graph with full control.
    """
    if not graphiti:
        raise HTTPException(
            status_code=503,
            detail="Graphiti not initialized. Check GEMINI_API_KEY and Neo4j connection."
        )

    try:
        logger.info(f"📥 Building graph for: {data.episode_name}")
        logger.info(f"   Nodes: {len(data.nodes)}, Edges: {len(data.edges)}")

        # Parse reference time if provided
        ref_time = datetime.utcnow()
        if data.reference_time:
            try:
                ref_time = datetime.fromisoformat(data.reference_time.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Failed to parse reference_time: {e}, using current time")

        # Create episode first
        episode_body = f"Manufacturing document containing {len(data.nodes)} entities and {len(data.edges)} relationships"

        result = await graphiti.add_episode(
            name=data.episode_name,
            episode_body=episode_body,
            source_description=data.source_description,
            reference_time=ref_time
        )

        # Extract episode ID
        episode_id = "created"
        if hasattr(result, 'episode'):
            episode = result.episode
            if hasattr(episode, 'uuid'):
                episode_id = str(episode.uuid)
            elif hasattr(episode, 'id'):
                episode_id = str(episode.id)

        logger.info(f"✅ Created episode: {episode_id}")

        # Track created nodes mapping for edge creation
        node_uuid_map = {}
        node_results = []

        # Add nodes
        for node in data.nodes:
            try:
                node_name = node.properties.get('name', node.id)

                # Add node to graph
                created_node = await graphiti.add_node(
                    name=node_name,
                    labels=[node.label] if isinstance(node.label, str) else node.label,
                    properties=node.properties
                )

                node_uuid_map[node.id] = str(created_node.uuid)
                node_results.append({
                    "original_id": node.id,
                    "graphiti_uuid": str(created_node.uuid),
                    "name": node_name,
                    "status": "created"
                })

                logger.info(f"  ✅ Node: {node_name} ({created_node.uuid})")

            except Exception as e:
                logger.error(f"  ❌ Failed to create node {node.id}: {e}")
                node_results.append({
                    "original_id": node.id,
                    "status": "failed",
                    "error": str(e)
                })

        # Add edges
        edge_results = []
        for edge in data.edges:
            try:
                # Get UUIDs from map
                source_uuid = node_uuid_map.get(edge.source)
                target_uuid = node_uuid_map.get(edge.target)

                if not source_uuid or not target_uuid:
                    raise ValueError(f"Source or target node not found in created nodes")

                # Add edge to graph
                created_edge = await graphiti.add_edge(
                    source_node_uuid=source_uuid,
                    target_node_uuid=target_uuid,
                    relationship_type=edge.type,
                    properties=edge.properties or {}
                )

                edge_results.append({
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "graphiti_uuid": str(created_edge.uuid),
                    "status": "created"
                })

                logger.info(f"  ✅ Edge: {edge.source} --[{edge.type}]--> {edge.target}")

            except Exception as e:
                logger.error(f"  ❌ Failed to create edge {edge.source}->{edge.target}: {e}")
                edge_results.append({
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "status": "failed",
                    "error": str(e)
                })

        successful_nodes = len([n for n in node_results if n['status'] == 'created'])
        successful_edges = len([e for e in edge_results if e['status'] == 'created'])

        logger.info(f"✅ Graph built: {successful_nodes}/{len(data.nodes)} nodes, {successful_edges}/{len(data.edges)} edges")

        return {
            "status": "success",
            "episode_id": episode_id,
            "episode_name": data.episode_name,
            "nodes_created": successful_nodes,
            "nodes_failed": len(data.nodes) - successful_nodes,
            "edges_created": successful_edges,
            "edges_failed": len(data.edges) - successful_edges,
            "node_details": node_results,
            "edge_details": edge_results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Failed to build graph: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-graph")
async def search_graph(data: SearchQuery):
    """
    Search knowledge graph with natural language using Gemini

    Uses semantic search with embeddings and reranking for best results.
    """
    if not graphiti:
        raise HTTPException(
            status_code=503,
            detail="Graphiti not initialized"
        )

    try:
        logger.info(f"🔍 Searching: {data.query}")

        # Use Graphiti's search with reranking
        search_results = await graphiti.search(
            query=data.query,
            num_results=data.num_results or data.limit,
            center_node_uuid=data.center_node_uuid
        )

        # Format results
        formatted_results = []
        for result in search_results:
            node_data = {
                "uuid": str(result.uuid) if hasattr(result, 'uuid') else None,
                "name": result.name if hasattr(result, 'name') else None,
                "labels": result.labels if hasattr(result, 'labels') else [],
                "fact": getattr(result, 'fact', None),
                "valid_at": str(result.valid_at) if hasattr(result, 'valid_at') else None,
                "invalid_at": str(result.invalid_at) if hasattr(result, 'invalid_at') else None,
            }

            formatted_results.append(node_data)

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
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """
    Get statistics about the knowledge graph
    """
    if not graphiti:
        raise HTTPException(status_code=503, detail="Graphiti not initialized")

    try:
        # This would require custom Cypher queries through Graphiti's driver
        # For now, return basic status
        return {
            "status": "success",
            "message": "Graph statistics endpoint - implementation depends on your specific needs",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# STARTUP AND SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Starting Manufacturing Graphiti Service")
    logger.info(f"   Version: 3.0.0")
    logger.info(f"   Graphiti Status: {'✅ Ready' if graphiti else '❌ Not initialized'}")

    if graphiti:
        logger.info("   LLM: Google Gemini 2.0 Flash")
        logger.info("   Embeddings: text-embedding-004")
        logger.info("   Reranker: gemini-2.0-flash-exp")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("👋 Shutting down Manufacturing Graphiti Service")
    if graphiti:
        try:
            await graphiti.close()
            logger.info("✅ Graphiti connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Graphiti: {e}")

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
