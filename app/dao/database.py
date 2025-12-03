from typing import Optional 
from dynaconf import settings
from pydantic import NonNegativeFloat
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession,  create_async_engine, async_sessionmaker

from app.dao.models import Base

class DataBaseManager:
    def __init__(self):
        self.adsn: str = settings.db.db_async_url
        self.engine: AsyncEngine = None
        self.session: AsyncSession = None
    
    def create_engine(self) -> AsyncEngine:
        if self.engine is None:
            self.engine = create_async_engine(
                self.adsn,
                echo=False,
                future=True,
            )
    
    def create_session_maker(self) -> async_sessionmaker[AsyncSession]:
        engine = self.create_engine()
        if self.session is None:
            self.session = async_sessionmaker(
                engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        return self.session
    
    async def create_tables(self):
        engine = self.create_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        engine = self.create_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self):
        if self.engine:
            await self.engine.dispose()


db_manager: Optional[DataBaseManager] = None

def get_db_manager(settings):
    global db_manager
    if db_manager is None:
        db_manager = DataBaseManager(settings)
    return db_manager


