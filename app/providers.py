from typing import AsyncIterable
from dynaconf import settings
from dishka import Provider, Scope, provide
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.database import DataBaseManager, get_db_manager


class DataBaseProvider(Provider):
    
    @provide(scope=Scope.APP)
    def provide_db_mabager(self) -> DataBaseManager:
        return get_db_manager()
    
    @provide(scope=Scope.REQUEST)
    async def provide_db_session(
        self,
        db_manager: DataBaseManager) -> AsyncIterable[AsyncSession]:
        session_maker = db_manager.create_session_maker()
        async with session_maker() as session:
            yield session
    

class RedisProvider(Provider):

    @provide(scope=Scope.APP)
    async def provide_redis(self) -> redis.Redis:
        redis_client = redis.from_url(
            settings.default.redis_url,
            decode_responses=True,
        )
        yield redis_client
        await redis_client.close()

