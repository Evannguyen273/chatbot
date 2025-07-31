"""
BigQuery Client for H&M Data Assistant
Updated to use new environment configuration
"""
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError, BadRequest
import pandas as pd
from config.env_config import get_config

class BigQueryClient:
    def __init__(self, project_id: str = None, service_account_info: dict = None):
        """Initialize BigQuery client with flexible configuration"""
        if not project_id or not service_account_info:
            # Load from environment config
            config = get_config()
            credentials_info = config.get_bigquery_credentials()
            project_id = credentials_info["project_id"]
            service_account_info = credentials_info["service_account_info"]
        
        if not service_account_info:
            raise ValueError("BigQuery service account information not found")
        
        # Create client with service account
        self.client = bigquery.Client.from_service_account_info(
            service_account_info, 
            project=project_id
        )
        self.project_id = project_id

    def execute_query(self, sql: str) -> pd.DataFrame:
        """Execute SQL and return DataFrame. Handles common errors."""
        try:
            query_job = self.client.query(sql)
            return query_job.to_dataframe()
        except BadRequest as e:
            raise ValueError(f"Invalid SQL: {str(e)}")
        except GoogleAPICallError as e:
            raise ConnectionError(f"BigQuery API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")

    def get_schema(self, dataset: str, table: str) -> str:
        """Get schema for a table."""
        try:
            table_ref = self.client.dataset(dataset).table(table)
            table = self.client.get_table(table_ref)
            return "\n".join([f"{field.name}: {field.field_type}" for field in table.schema])
        except Exception as e:
            raise RuntimeError(f"Error getting schema for {dataset}.{table}: {str(e)}")

    def test_connection(self) -> bool:
        """Test BigQuery connection"""
        try:
            # Simple test query
            query = "SELECT 1 as test"
            result = self.client.query(query).result()
            return True
        except Exception as e:
            print(f"BigQuery connection test failed: {e}")
            return False

def create_bigquery_client() -> BigQueryClient:
    """Factory function to create BigQuery client"""
    return BigQueryClient()

# Legacy support - can be removed later
def get_bigquery_client() -> BigQueryClient:
    """Get or create BigQuery client instance"""
    return create_bigquery_client()