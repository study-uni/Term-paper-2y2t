from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        pass

    @abstractmethod
    def get_all(self) -> list[T]:
        pass

    @abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass


class SQLAlchemyBaseRepository(BaseRepository[T]):
    def __init__(self, session: Session, model_cls: type[T]):
        self.session = session
        self.model_cls = model_cls

    def get_by_id(self, id: int) -> T | None:
        return (
            self.session.query(self.model_cls).filter(self.model_cls.id == id).first()
        )

    def get_all(self) -> list[T]:
        return self.session.query(self.model_cls).all()

    def add(self, entity: T) -> None:
        self.session.add(entity)

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
