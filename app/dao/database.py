from dynaconf import settings
from pydantic import NonNegativeFloat
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession,  create_async_engine, async_sessionmaker

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
                engine
            )
        return self.session

