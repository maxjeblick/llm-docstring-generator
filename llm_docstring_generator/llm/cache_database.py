"""
Code adapted from https://github.com/optuna/optuna/blob/master/optuna/storages/_rdb/storage.py
Allows for potential extensions, i.e. accessing the database from multiple processes using a suitable
SQLAlchemy engine such as mysql or postgresql.
"""
import hashlib
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import sqlalchemy
import sqlalchemy.exc as sqlalchemy_exc
import sqlalchemy.orm as sqlalchemy_orm
from loguru import logger
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CacheEntry(Base):  # type: ignore
    __tablename__ = "llm_cache"

    key = Column(String, primary_key=True)
    prompt = Column(Text)
    prompt_truncated = Column(Text)
    answer = Column(Text)
    system_prompt = Column(Text)
    model = Column(Text)


@contextmanager
def _create_scoped_session(
    scoped_session: sqlalchemy_orm.scoped_session,
    ignore_integrity_error: bool = False,
) -> Generator[sqlalchemy_orm.Session, None, None]:
    session = scoped_session()
    try:
        yield session
        session.commit()
    except sqlalchemy_exc.IntegrityError as e:
        session.rollback()
        if ignore_integrity_error:
            logger.debug(
                "Ignoring {}. This happens due to a timing issue among threads/processes/nodes. "
                "Another one might have committed a record with the same key(s).".format(
                    repr(e)
                )
            )
        else:
            raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        session.rollback()
        raise e
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class LLMCache:
    def __init__(
        self,
        db_name: str,
        engine_kwargs: Optional[Dict[str, Any]] = None,
        *,
        skip_table_creation: bool = False,
    ) -> None:
        self.engine = sqlalchemy.engine.create_engine(
            db_name, **(engine_kwargs or dict())
        )
        self.scoped_session = sqlalchemy_orm.scoped_session(
            sqlalchemy_orm.sessionmaker(bind=self.engine)
        )
        if not skip_table_creation:
            Base.metadata.create_all(self.engine)

    def get_llm_answer(
        self,
        prompt: str,
        prompt_truncated: str,
        system_prompt: str,
        model: str,
    ) -> Optional[str]:
        with _create_scoped_session(
            self.scoped_session, ignore_integrity_error=False
        ) as session:
            hash_input = prompt + prompt_truncated + system_prompt + model
            md5_hash = hashlib.md5(hash_input.encode()).hexdigest()
            cache_entry = session.query(CacheEntry).get(md5_hash)
            if cache_entry:
                logger.debug("Using cached result")
                return cache_entry.answer
        return None

    def save_llm_answer(
        self,
        prompt: str,
        prompt_truncated: str,
        answer: str,
        system_prompt: str,
        model: str,
    ) -> None:
        hash_input = prompt + prompt_truncated + system_prompt + model
        md5_hash = hashlib.md5(hash_input.encode()).hexdigest()
        with _create_scoped_session(
            self.scoped_session, ignore_integrity_error=False
        ) as session:
            cache_entry = CacheEntry(
                key=md5_hash,
                prompt=prompt,
                prompt_truncated=prompt_truncated,
                answer=answer,
                system_prompt=system_prompt,
                model=model,
            )
            session.add(cache_entry)


def create_default_llm_cache(config) -> Optional[LLMCache]:
    if config.db_root_path is None:
        logger.warning("No cache database path provided. Caching disabled.")
        return None
    else:
        db_path = Path(config.db_root_path) / f"llm_cache_{config.model}"
        db_path.mkdir(exist_ok=True, parents=True)
        db_name = str(db_path / "llm_cache.db").lstrip("/")
        return LLMCache(
            db_name=f"sqlite:////{db_name}",
            engine_kwargs=dict(pool_size=50, max_overflow=0),
        )
