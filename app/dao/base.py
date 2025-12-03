from abc import ABC
from pydantic import BaseModel
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, Select

from app.dao.models import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    "Base class for all other DAOs"

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, object_in: CreateSchemaType) -> ModelType:
        object_data = object_in.model_dump()
        db_object = self.model(**object_data)
        self.session.add(db_object)
        await self.session.flush()
        await self.session.refresh(db_object)
        
        return db_object
    
    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id))

        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        offset: int = 0, 
        limit: int = 100,
        **filters) -> List[ModelType]:

        query = select(self.model)
        query = self.__filter_query(query, filters=filters)
        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def update(
        self, 
        id: int, 
        object_in: UpdateSchemaType) -> Optional[ModelType]:
        
        object_data = object_in.model_dump()
        if not object_data:
            return await self.get(id)

        await update(self.model).where(
            self.model.id == id).values(**object_data)
        await self.session.flush()

        return await self.get(id)

    async def delete(self, id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()

        return result.rowcount > 0
    
    async def count(self, **filters) -> int:
        from sqlalchemy import func

        query = select(func.count(self.model.id))
        query = self.__filter_query(query, filters=filters)
        result = await self.session.execute(query)

        return result.scalar() or 0 

    async def exists(self, **filters) -> bool:
        query = select(self.model.id)
        query = self.__filter_query(query, filters=filters)
        query = query.limit(1)
        result = await self.session.execute(query)

        return result.scalar() is not None

    def __filter_query(self, query: Select, **filters) -> Select:
        for k, v in filters.items():
            if hasattr(self.model, k) and v is not None:
                query = query.where(getattr(self.model, k) == v)
        return query