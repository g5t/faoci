from __future__ import annotations


def setup_database(named: str):
    from platformdirs import user_cache_path
    from sqlmodel import create_engine
    file = user_cache_path('faoci', 'g5t', ensure_exists=True).joinpath(f'{named}.db')
    return create_engine(f'sqlite:///{file.as_posix()}')

