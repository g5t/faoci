
def _now():
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo  # requires Python >= 3.9
    # New puzzles are released at 00:00 UTC-5 (which is the same as New York in December, up to at least 2023)
    return datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York'))


def fetch(*, day: int, year: int):
    import requests
    from faoci import config
    
    now = _now()
    
    if not (0 < day <= 25):
        raise ValueError(f'Invalid day input [expected (0 < {day=} <= 25)')
    if not (2015 <= year <= (now.year if now.month == 12 else now.year - 1)):
        raise ValueError(f'Invalid year input; AoC started in 2015')
    if year == now.year and now.month == 12 and now.day < day:
        raise ValueError(f'Requested {day=} but it is {now} and new puzzles are released at midnight UTC-5')
    
    session_cookie = config['session']
    if not session_cookie.exists() or session_cookie.get() is None:
        raise ValueError('Provide your authentication session cookie from, e.g., '
                         '`https://adventofcode.com/2015/day/1/input`\n'
                         'as an environment variable, FAOCI_SESSION={xxx},'
                         f' or an entry `session: {{xxx}}` in {config.config_dir()}/config.yaml')

    session = requests.Session()
    request = session.get(f'https://adventofcode.com/{year}/day/{day}/input',
                          cookies={'session': session_cookie.as_str()})
    
    if not request.ok:
        raise RuntimeError('Fetching input failed with error {request.reason}')
        
    return request.text

    
    
