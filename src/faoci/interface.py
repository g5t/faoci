from .fetch import _now
from .database import create_database_and_tables, get_database_content


def fetch(*, year: int, day: int) -> str:
    # Ensure the database exists, and that we have connection to it:
    create_database_and_tables()
    # Grab the file contents from the database, or populate the contents and return them
    content = get_database_content(year=year, day=day)  # content = fetch(args.day, args.year)
    return content


def fetch_lines(*, year: int, day: int) -> list[str]:
    return fetch(year=year, day=day).splitlines()


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
    content = fetch(day=args.day, year=args.year)
    with open(output, 'w') as file:
        file.write(content)

    if not args.quiet:
        import sys
        print('\n'.join(content.split('\n')[:10]), file=sys.stderr)



