import asyncio
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pandas as pd
from .config import DatabaseConfig
from .logging import get_logger


class DatabaseClient:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = get_logger("database_client")
        
        # 동기 엔진 (pandas용)
        self.sync_engine = self._create_sync_engine()
        
        # 비동기 엔진
        self.async_engine = self._create_async_engine()
        self.async_session = sessionmaker(
            self.async_engine, 
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    def _create_sync_engine(self):
        if self.config.type == "postgresql":
            url = f"postgresql+psycopg2://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        elif self.config.type == "mysql":
            url = f"mysql+pymysql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.config.type}")
        
        return create_engine(url)
    
    def _create_async_engine(self):
        if self.config.type == "postgresql":
            url = f"postgresql+asyncpg://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        elif self.config.type == "mysql":
            url = f"mysql+aiomysql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.config.type}")
        
        return create_async_engine(url)
    
    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        try:
            self.logger.info(f"Executing query: {query[:100]}...")
            df = pd.read_sql_query(query, self.sync_engine)
            self.logger.info(f"Query returned {len(df)} rows")
            return df
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            raise
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        try:
            async with self.async_session() as session:
                result = await session.execute(text(query))
                rows = result.fetchall()
                
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Async query failed: {e}")
            raise
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        if self.config.type == "postgresql":
            query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = :table_name
            ORDER BY ordinal_position
            """
        elif self.config.type == "mysql":
            query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = :table_name
            ORDER BY ordinal_position
            """
        else:
            raise ValueError(f"Schema query not supported for {self.config.type}")
        
        async with self.async_session() as session:
            result = await session.execute(text(query), {"table_name": table_name})
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_all_tables(self) -> List[str]:
        if self.config.type == "postgresql":
            query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        elif self.config.type == "mysql":
            query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.config.database}'"
        else:
            raise ValueError(f"Table listing not supported for {self.config.type}")
        
        result = await self.execute_query(query)
        return [row[list(row.keys())[0]] for row in result]