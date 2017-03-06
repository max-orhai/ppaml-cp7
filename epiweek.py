"""https://wwwn.cdc.gov/nndss/document/MMWR_Week_overview.pdf
Business rules for assigning MMWR [a.k.a. 'CDC' or 'epi'] week:
The first day of any MMWR week is Sunday. MMWR week numbering is sequential
beginning with 1 and incrementing with each week to a maximum of 52 or 53.
MMWR week #1 of an MMWR year is the first week of the year that has at least
four days in the calendar year. For example, if January 1 occurs on a Sunday,
Monday, Tuesday or Wednesday, the calendar week that includes January 1 would
be MMWR week #1. If January 1 occurs on a Thursday, Friday, or Saturday, the
calendar week that includes January 1 would be the last MMWR week of the
previous year (#52 or #53). Because of this rule, December 29, 30, and 31
could potentially fall into MMWR week #1 of the following MMWR year."""

# Algorithms adapted from
# https://en.wikipedia.org/wiki/ISO_week_date and
# http://www.staff.science.uu.nl/~gent0113/calendar/isocalendar.htm
# ...since the epi week calendar is identical to the ISO week calendar,
# except that the epi week starts on a Sunday.

from datetime import datetime, date, timedelta

# date.weekday()
# Su Mo Tu We Th Fr Sa Su
# 6  0  1  2  3  4  5  6


def epi_weeks_in_year(yyyy):
    def p(y):
        return (y + y // 4 - y // 100 + y // 400) % 7
    return 53 if p(yyyy) == 3 or p(yyyy - 1) == 2 else 52


def epiweek(d):  # consumes a datetime.date() object
    ordinal = 1 + (d - d.replace(month=1, day=1)).days
    weekday = 1 + (1 + d.weekday()) % 7
    week = (ordinal - weekday + 10) // 7
    if week < 1:
        return epi_weeks_in_year(d.year - 1), d.year - 1
    if week > epi_weeks_in_year(d.year):
        return 1, d.year + 1
    return week, d.year


# the last date (a Saturday) in given MMWR week
def last_date(wk, year):
    jan1 = date(year, 1, 1)
    wday = (1 + jan1.weekday()) % 7
    wk1d6 = jan1 + timedelta(days=6 if wday > 4 else -1)
    return wk1d6 + timedelta(days=7 * wk)


def ew(y, m, d):
    return epiweek(date(y, m, d))


# convert 'YYYY.WW' week notation to and from 'YYYY-MM-DD' dates:

def dt2ew(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d').date()
    wk, yr = epiweek(dt)
    return '{}.{:02}'.format(yr, wk)


def ew2dt(ew_str):
    yr, wk = ew_str.split('.')
    return last_date(int(wk), int(yr)).strftime('%Y-%m-%d')


def test_epiweek():
    # test cases taken from calendars at http://www.cmmcp.org/epiweek.htm
    cases = [
        # yyyy  mm  dd -> wk  yyyy
        ((2006, 12, 31), (01, 2007)),
        ((2007, 01, 01), (01, 2007)),
        ((2007, 12, 29), (52, 2007)),
        ((2007, 12, 30), (01, 2008)),
        ((2008, 01, 01), (01, 2008)),
        ((2008, 12, 27), (52, 2008)),
        ((2008, 12, 28), (53, 2008)),
        ((2009, 01, 01), (53, 2008)),
        ((2009, 01, 04), (01, 2009)),
        ((2009, 12, 31), (52, 2009)),
        ((2010, 01, 01), (52, 2009)),
        ((2010, 01, 03), (01, 2010)),
    ]
    n_bad = 0
    for given, expected in cases:
        actual = epiweek(date(*given))
        try:
            assert actual == expected
        except AssertionError:
            print('%s: expected %s but got %s' % (given, expected, actual))
            n_bad += 1
            continue
    if n_bad > 0:
        print('%s / %s failed' % (n_bad, len(cases)))

if __name__ == '__main__':
    test_epiweek()
