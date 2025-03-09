from fastapi import APIRouter, HTTPException
from elasticsearch import Elasticsearch
from src.config.config import settings
from utils.logging import logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create the router
router = APIRouter(prefix="/elastic", tags=["Elasticsearch"])


# Create Elasticsearch client
def get_elasticsearch_client():
    try:
        es_client = Elasticsearch(
            hosts=[f"{settings.ES.ELASTIC_HOST}:{settings.ES.ELASTIC_PORT}"],
            api_key=settings.ES.ELASTIC_API_KEY,
            verify_certs=False  # Note: For production, set to True and provide proper certificates
        )
        return es_client
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to connect to Elasticsearch")


@router.get("/info", status_code=200)
async def get_cluster_info():
    """
    Get Elasticsearch cluster information including:
    - Cluster name
    - Cluster status (green, yellow, red)
    - Number of nodes
    - Version information
    """
    try:
        es_client = get_elasticsearch_client()

        # Get cluster info
        cluster_info = es_client.info()
        cluster_health = es_client.cluster.health()

        return {
            "cluster_name": cluster_health["cluster_name"],
            "status": cluster_health["status"],
            "number_of_nodes": cluster_health["number_of_nodes"],
            "active_shards": cluster_health["active_shards"],
            "elasticsearch_version": cluster_info["version"]["number"],
            "lucene_version": cluster_info["version"]["lucene_version"]
        }
    except Exception as e:
        logger.error(f"Error getting cluster info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve Elasticsearch cluster info: {str(e)}")


@router.get("/indices", status_code=200)
async def get_indices_info():
    """
    Get information about all indices in the Elasticsearch cluster.
    """
    try:
        es_client = get_elasticsearch_client()
        indices = es_client.cat.indices(format="json")
        return indices
    except Exception as e:
        logger.error(f"Error getting indices info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve indices info: {str(e)}")


@router.get("/index/{index_name}", status_code=200)
async def get_index_details(index_name: str):
    """
    Get detailed information about a specific index.
    """
    try:
        es_client = get_elasticsearch_client()
        index_exists = es_client.indices.exists(index=index_name)

        if not index_exists:
            raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

        index_stats = es_client.indices.stats(index=index_name)
        index_settings = es_client.indices.get_settings(index=index_name)
        index_mapping = es_client.indices.get_mapping(index=index_name)

        return {
            "name": index_name,
            "stats": index_stats,
            "settings": index_settings,
            "mapping": index_mapping
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting index details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve index details: {str(e)}")