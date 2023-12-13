from __future__ import annotations
from sqlmodel import Field, SQLModel, Session, select
from datetime import datetime, timedelta
from .cache import setup_database
from .fetch import _now


class Input(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    year: int = Field(index=True)
    day: int = Field(index=True)
    content: str


class Time(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    microsecond: int
    timezone: str | None

    @classmethod
    def from_datetime(cls, d):
        return Time(year=d.year, month=d.month, day=d.day, hour=d.hour, minute=d.second, microsecond=d.microsecond,
                    timezone=d.tzinfo.key if d.tzinfo is not None and hasattr(d.tzinfo, 'key') else None)

    def to_datetime(self) -> datetime:
        from zoneinfo import ZoneInfo
        return datetime(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute,
                        second=self.second, microsecond=self.microsecond,
                        tzinfo=ZoneInfo(self.timezone) if self.timezone is not None else ZoneInfo('America/New_York'))


ENGINE = setup_database('database')


def once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.ran:
            return func(*args, **kwargs)

    wrapper.ran = False
    return wrapper


@once
def create_database_and_tables():
    SQLModel.metadata.create_all(ENGINE)


def get_database_timestamp():
    with Session(ENGINE) as session:
        time = session.get(Time, 1)
        if time is None:
            n = _now()
            is_jan = n.month == 1
            n.replace(year=n.year - 1 if is_jan else n.year, month=12 if is_jan else n.month - 1, day=1)
            session.add(Time.from_datetime(n))
            session.commit()
            return n
        else:
            return time.to_datetime()


def set_database_timestamp(t: datetime):
    with Session(ENGINE) as session:
        if session.get(Time, 1) is None:
            session.add(Time.from_datetime(t))
        else:
            time = Time.from_datetime(t)
            time.id = 1
            session.add(time)
            session.commit()


def get_database_content(year: int, day: int) -> str | None:
    with Session(ENGINE) as session:
        content = session.exec(select(Input).where(Input.year == year, Input.day == day)).first()
    return None if content is None else content.content


def add_database_content(year: int, day: int, content: str):
    to_save = Input(year=year, day=day, content=content)
    with Session(ENGINE) as session:
        session.add(to_save)
        session.commit()


def retrieve_content(year: int, day: int):
    """Get the file content from the database, or populate the database if it is not present"""
    from time import sleep
    from .fetch import fetch
    if content := get_database_content(year, day):
        return content
    #  ensure we respect rate limiting:
    last_request = get_database_timestamp()
    while (_now() - last_request) < timedelta(seconds=1):
        sleep(0.1)
    #
    content = fetch(day=day, year=year)
    add_database_content(year, day, content)
    set_database_timestamp(_now())
    return content
