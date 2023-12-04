
def _now():
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo  # requires Python >= 3.9
    # New puzzles are released at 00:00 UTC-5 (which is the same as New York in December, up to at least 2023)
    return datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York'))


def fetch(day: int, year: int):
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
                         'as an evironment variable, FAOCI_SESSION={xxx},'
                         ' or an entry `session: {xxx}` in {config.config_dir()}/config.yaml')

    session = requests.Session()
    request = session.get(f'https://adventofcode.com/{year}/day/{day}/input',
                          cookies={'session': session_cookie.as_str()})
    
    if not request.ok:
        raise RuntimeError('Fetching input failed with error {request.reason}')
        
    return request.text
    

def entrypoint():
    from argparse import ArgumentParser
    now = _now()
    
    parser = ArgumentParser(description='Grab an input file from Advent of Code')
    parser.add_argument('-y', '--year', type=int, help='the year to fetch from', default=now.year)
    parser.add_argument('-d', '--day', type=int, help='the day of advent to fetch', default=now.day)
    parser.add_argument('-o', '--output', type=str, help='the output filename', default=None)
    parser.add_argument('-q', '--quiet', action='store_true', help='quiet operation')
    
    args = parser.parse_args()
    
    output = f'Day{args.day:02d}.txt' if args.output is None else args.output
    content = fetch(args.day, args.year)
    with open(output, 'w') as file:
        file.write(output)
        
    if not args.quiet:
        import sys
        print('\n'.join(content.split('\n')[:10]), file=sys.stderr)
        
    
    
    
    
    
