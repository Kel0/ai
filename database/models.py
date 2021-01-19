from __future__ import annotations

import json
from typing import List, Optional

from sqlalchemy import Column, String, Text
from sqlalchemy.orm.exc import NoResultFound

from .conf import base, session

db_session = session()


class Alias(base):
    origin = Column(String(length=225))
    matches = Column(Text, nullable=True)

    @classmethod
    def get(cls, **kwargs) -> Optional[Alias]:
        keys = kwargs.keys()

        try:
            _object = (
                db_session.query(cls)
                .filter(*[(getattr(cls, key) == kwargs[key]) for key in keys])
                .limit(1)
                .one()
            )
        except NoResultFound:
            return None

        _object.matches = json.loads(_object.matches)
        return _object

    @classmethod
    def filter(cls, **kwargs) -> List[Alias]:
        keys = kwargs.keys()

        objects = (
            db_session.query(cls)
            .filter(*[(getattr(cls, key) == kwargs[key]) for key in keys])
            .all()
        )
        for _object in objects:
            _object.matches = json.loads(_object.matches)

        return objects

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        db_session.add(obj)
        return db_session.commit()

    def save(self):
        if self.id is None:  # noqa
            db_session.add(self)
        return db_session.commit()

    def delete(self):
        db_session.delete(self)
        return db_session.commit()
