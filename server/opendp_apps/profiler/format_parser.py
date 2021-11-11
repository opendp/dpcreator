from dateutil import parser
from dateutil import relativedelta, tz
from calendar import monthrange
from six import text_type, binary_type, integer_types

import datetime
import string
import collections
import time


'''Modified _ymd object that support format detection'''
class _format_ymd(list):
    def __init__(self, tzstr, *args, **kwargs):
        super(_format_ymd, self).__init__(*args, **kwargs)
        self.century_specified = False
        self.tzstr = tzstr
        self.format_list = list()

    @staticmethod
    def token_could_be_year(token, year):
        try:
            return int(token) == year
        except ValueError:
            return False

    @staticmethod
    def find_potential_year_tokens(year, tokens):
        return [token for token in tokens if _format_ymd.token_could_be_year(token, year)]

    def find_probablie_year_index(self, tokens):
        for index, token in enumerate(self):
            potential_year_tokens = _format_ymd.find_potential_year_tokens(token[0], tokens)
            if len(potential_year_tokens) == 1 and len(potential_year_tokens[0]) > 2:
                return index

    # def append(self, val):
    #     # TODO: Modify val, should be a 3-tuple (val, val_repr, token_idx)
    #     if hasattr(val, '__len__'):
    #         if val.isdigit() and len(val) > 2:
    #             self.century_specified = True
    #     elif val > 100:
    #         self.century_specified = True
    #
    #     super(self.__class__, self).append(int(val))

    def append(self, val_tuple):
        assert isinstance(val_tuple, list) and len(val_tuple) == 3  # (val, val_repr, token_idx)
        val = val_tuple[0]

        if hasattr(val, '__len__'):
            if val.isdigit() and len(val) > 2:
                self.century_specified = True
        elif val > 100:
            self.century_specified = True

        val_tuple[0] = int(val)
        super(self.__class__, self).append(val_tuple)

    def resolve_ymd(self, mstridx, yearfirst, dayfirst):
        # print(self)
        len_ymd = len(self)
        year, month, day = (None, None, None)

        if len_ymd > 3:
            raise ValueError("More than three YMD values")
        elif len_ymd == 1 or (mstridx != -1 and len_ymd == 2):
            # One member, or two member with a month string
            if mstridx != -1:
                month = self[mstridx]
                del self[mstridx]

            if len_ymd > 1 or mstridx == -1:
                if self[0][0] > 31:
                    year = self[0]
                else:
                    day = self[0]

        elif len_ymd == 2:
            if self[0][0] > 32:
                year, month = self
            elif self[1][0] > 31:
                month, year = self
            elif dayfirst and self[1][0] <= 12:
                day, month = self
            else:
                month, day = self
        elif len_ymd == 3:
            # Three members
            if mstridx == 0:
                month, day, year = self
            elif mstridx == 1:
                if self[0][0] > 31 or (yearfirst and self[2][0] <= 31):
                    year, month, day = self
                else:
                    day, month, year = self

            elif mstridx == 2:
                if self[1][0] > 31:
                    day, year, month = self
                else:
                    year, day, month = self

            else:
                if self[0][0] > 31 or self.find_probablie_year_index(parser._timelex.split(self.tzstr)) == 0 or \
                        (yearfirst and self[1][0] <= 12 and self[2][0] <= 31):
                    if dayfirst and self[2][0] <= 12:
                        year, day, month = self
                    else:
                        year, month, day = self
                elif self[0][0] > 12 or (dayfirst and self[1][0] <= 12):
                    day, month, year = self
                else:
                    month, day, year = self

        return year, month, day

    @staticmethod
    def get_tuple_format(str_tuple, role):
        _, val_repr, idx = str_tuple
        if idx is None:
            # Pre-defined date format, should not be changed
            return None

        if 'year' == role:
            if len(val_repr) == 4:
                return '%Y'
            elif len(val_repr) == 2:
                return '%y'
            else:
                return '?'
        elif 'month' == role:
            if len(val_repr) == 2 or len(val_repr) == 1:
                return '%m'
            elif len(val_repr) == 3:
                return '%b'
            else:
                return '%B'
        elif 'day' == role:
            return '%d'
        else:
            raise ValueError('Unsupported role value {}'.format(role))



class format_parserinfo(parser.parserinfo):
    # Remove AM/PM support for fuzzy parsing, should not be supported
    new_AMPM = [('am', 'am'), ('pm', 'pm')]

    def __init__(self, dayfirst=False, yearfirst=False):
        super(format_parserinfo, self).__init__(dayfirst, yearfirst)
        self._ampm = self._convert(self.new_AMPM)


class parser_with_format(parser.parser):
    def __init__(self, info=None):
        super(parser_with_format, self).__init__(info=info)
        if info:
            assert isinstance(info, format_parserinfo)

        self.info = info or format_parserinfo()

    def parse(self, timestr, default=None, ignoretz=False, tzinfos=None, **kwargs):
        # Follow the same routine of dateuilt.parser.parse(), adding an auxiliary list to support format detection

        if default is None:
            default = datetime.datetime.now().replace(year=1900, month=1, day=1,
                                                      hour=0, minute=0, second=0, microsecond=0)

        res, date_format = self._parse(timestr, **kwargs)

        if not date_format or '?' in date_format:
            # Date Format that cannot be supported
            date_format = '?'

        if res is None:
            raise ValueError('Unknown string format')

        if len(res) == 0:
            raise ValueError('String does not contain a date.')

        repl = dict()
        for attr in ('year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond'):
            value = getattr(res, attr)
            if value is not None:
                repl[attr] = value

        if 'day' not in repl:
            cyear = default.year if res.year is None else res.year
            cmonth = default.month if res.month is None else res.month
            cday = default.day if res.day is None else res.day

            if cday > monthrange(cyear, cmonth)[1]:
                repl['day'] = monthrange(cyear, cmonth)[1]

        ret = default.replace(**repl)

        if res.weekday is not None and not res.day:
            ret = ret + relativedelta.relativedelta(weekday=res.weekday)

        if not ignoretz:
            if isinstance(tzinfos, collections.Callable) or tzinfos and res.tzname in tzinfos:
                if isinstance(tzinfos, collections.Callable):
                    tzdata = tzinfos(res.tzname, res.tzoffset)
                else:
                    tzdata = tzinfos.get(res.tzname)

                if isinstance(tzdata, datetime.tzinfo):
                    tzinfo = tzdata
                elif isinstance(tzdata, text_type):
                    tzinfo = tz.tzstr(tzdata)
                elif isinstance(tzdata, integer_types):
                    tzinfo = tz.tzoffset(res.tzname, tzdata)
                else:
                    raise ValueError('Offset must be tzinfo subclass, tz string, or int offset')

                ret = ret.replace(tzinfo=tzinfo)

            elif res.tzname and res.tzname in time.tzname:
                ret = ret.replace(tzinfo=tz.tzlocal())
            elif res.tzoffset == 0:
                ret = ret.replace(tzinfo=tz.tzutc())
            elif res.tzoffset:
                ret = ret.replace(tzinfo=tz.tzoffset(res.tzname, res.tzoffset))

        return ret, date_format

    def _parse(self, timestr, dayfirst=None, yearfirst=None, fuzzy=False, fuzzy_with_tokens=False):
        if fuzzy_with_tokens:
            fuzzy = True

        info = self.info

        if dayfirst is None:
            dayfirst = info.dayfirst

        if yearfirst is None:
            yearfirst = info.yearfirst

        res = self._result()
        l = parser._timelex.split(timestr)
        # Auxiliary dict for date format
        format = [token for token in l]

        # Keep up with the last token skipped so we can recombine
        # Consecutively skipped tokens (-2 for when i begins at 0)
        last_skipped_token_i = -2
        skipped_tokens = list()

        try:
            # Modified year/month/day list
            ymd = _format_ymd(timestr)

            # Index of the month string in ymd
            mstridx = -1

            len_l = len(l)
            i = 0
            while i < len_l:
                # Go through each token

                # Check if it's a number:
                try:
                    value_repr = l[i]
                    value = float(value_repr)
                except ValueError:
                    value = None

                if value is not None:
                    # Token is a number
                    len_li = len(l[i])
                    i += 1

                    if (len(ymd) == 3 and len_li in (2, 4) and res.hour is None and
                            (i >= len_l or (l[i] != ':' and info.hms(l[i]) is None))):
                        # 19990101T23[59]
                        s = l[i-1]
                        res.hour = int(s[:2])
                        format[i-1] = '%H'

                        if len_li == 4:
                            res.minute = int(s[2:])
                            format[i-1] += '%M'

                    elif len_li == 6 or (len_li > 6 and l[i-1].find('.') == 6):
                        # YYMMDD or HHMMSS[.ss]
                        s = l[i-1]

                        if not ymd and l[i-1].find('.') == -1:
                            # Pre-defined YMD, format should not be changed during ymd_resolve
                            ymd.append([s[:2], None, None])
                            ymd.append([s[2:4], None, None])
                            ymd.append([s[4:], None, None])
                            format[i-1] = '%y%m%d'
                        else:
                            res.hour = int(s[:2])
                            res.minute = int(s[2:4])
                            res.second, res.microsecond, tmp = _format_parsems(s[4:])
                            format[i-1] = '%H%M' + tmp

                    elif len_li in (8, 12, 14):
                        # YYYYMMDD
                        s = l[i-1]
                        # Pre-defined YMD, format should not be changed during ymd_resolve
                        ymd.append([s[:4], None, None])
                        ymd.append([s[4:6], None, None])
                        ymd.append([s[6:8], None, None])
                        format[i-1] = '%Y%m%d'

                        if len_li > 8:
                            res.hour = int(s[8:10])
                            res.minute = int(s[10:12])
                            format[i-1] += '%H%M'

                            if len_li > 12:
                                res.second = int(s[12:])
                                format[i-1] += '%S'
                    elif ((i < len_l and info.hms(l[i]) is not None)
                          or (i+1 < len_l and l[i] == ' ' and info.hms(l[i+1]) is not None)):

                        # HH[]h or MM[] m or SS[.ss][] s
                        v_idx = i - 1
                        if l[i] == ' ':
                            i += 1
                        n_idx = i

                        idx = info.hms(l[i])

                        while True:
                            if idx == 0:
                                res.hour = int(value)
                                format[v_idx] = '%H'
                                format[n_idx] = l[n_idx]

                                if value % 1:
                                    format[v_idx] = '?'
                                    res.minute = int(60 * (value % 1))

                            elif idx == 1:
                                res.minute = int(value)
                                format[v_idx] = '%M'
                                format[n_idx] = l[n_idx]

                                if value % 1:
                                    format[v_idx] = '?'
                                    res.second = int(60 * (value % 1))

                            elif idx == 2:
                                res.second, res.microsecond, tmp = _format_parsems(value_repr)
                                format[v_idx] = tmp

                            i += 1

                            if i >= len_l or idx == 2:
                                break

                            # 12h00
                            try:
                                value_repr = l[i]
                                value = float(value_repr)
                            except ValueError:
                                break

                            else:
                                # Further parse is possible, continue this loop
                                v_idx = i
                                i += 1
                                n_idx = i
                                idx += 1

                                if i < len_l:
                                    new_idx = info.hms(l[i])

                                    if new_idx is not None:
                                        idx = new_idx

                    elif i == len_l and l[i-2] == ' ' and info.hms(l[i-3]) is not None:
                        # X h MM or X m SS
                        idx = info.hms(l[i-3])

                        if idx == 0:
                            res.minute = int(value)
                            format[i-1] = '%M'
                            sec_remainder = value % 1

                            if sec_remainder:
                                format[i-1] = '?'
                                res.second = int(60 * sec_remainder)
                        elif idx == 1:
                            res.second, res.microsecond, tmp = _format_parsems(value_repr)
                            format[i-1] = tmp

                        #  We don't need to advance the tokens here because the i == len_l call indicates that
                        #  we're looking at all the tokens already
                    elif i+1 < len_l and l[i] == ':':
                        # HH:MM[:SS[.ss]]
                        res.hour = int(value)
                        format[i-1] = '%H'
                        i += 1

                        value = float(l[i])
                        res.minute = int(value)
                        format[i] = '%M'

                        if value % 1:
                            format[i] = '?'
                            res.second = int(60 * (value % 1))

                        i += 1

                        if i < len_l and l[i] == ':':
                            res.second, res.microsecond, tmp = _format_parsems(l[i+1])
                            format[i+1] = tmp
                            i += 2
                    elif i < len_l and l[i] in ('-', '/', '.'):
                        sep = l[i]
                        # ymd.append(value_repr)
                        ymd.append([value_repr, value_repr, i-1])
                        i += 1

                        if i < len_l and not info.jump(l[i]):
                            # l[i] is not a jump string
                            try:
                                # Failed Condition, l[i] cannot be convert to int
                                # ymd.append(l[i])
                                ymd.append([l[i], l[i], i])
                            except ValueError:
                                value = info.month(l[i])

                                if value is not None:
                                    # format[i] = '%b' if len(l[i]) == 3 else '%B'
                                    # ymd.append(value)
                                    ymd.append([value, l[i], i])
                                    assert mstridx == -1
                                    mstridx = len(ymd) - 1
                                else:
                                    return None, None

                            i += 1

                            if i < len_l and l[i] == sep:
                                # We have three members
                                i += 1
                                value = info.month(l[i])

                                if value is not None:
                                    # format[i] = '%b' if len(l[i]) == 3 else '%B'
                                    # ymd.append(value)
                                    ymd.append([value, l[i], i])
                                    mstridx = len(ymd) - 1
                                    assert mstridx == -1
                                else:
                                    # ymd.append(l[i])
                                    ymd.append([l[i], l[i], i])

                                i += 1

                    elif i >= len_l or info.jump(l[i]):
                        if i+1 < len_l and info.ampm(l[i+1]) is not None:
                            # 12 am
                            res.hour = int(value)

                            if res.hour < 12 and info.ampm(l[i+1]) == 1:
                                res.hour += 12
                            elif res.hour == 12 and info.ampm(l[i+1]) == 0:
                                res.hour = 0

                            format[i-1] = '%I'
                            format[i+1] = '%p'
                            i += 1
                        else:
                            # ymd.append(value)
                            tmp_collection = value_repr.split('.')

                            if len(tmp_collection) > 1:
                                # YYYY.MM ?
                                ymd.append([tmp_collection[0], None, None])
                                ymd.append([tmp_collection[1], None, None])
                                format[i-1] = '%Y.%m'
                            else:
                                ymd.append([value, value_repr, i-1])
                        i += 1
                    elif info.ampm(l[i]) is not None:
                        # 12am
                        res.hour = int(value)
                        if res.hour < 12 and info.ampm(l[i]) == 1:
                            res.hour += 12
                        elif res.hour == 12 and info.ampm(l[i]) == 0:
                            res.hour = 0
                        format[i-1] = '%I'
                        format[i] = '%p'

                        i += 1
                    elif info.month(l[i]) is not None:
                        # 12Sep[1999]
                        assert mstridx == -1
                        ymd.append([value, value_repr, i-1])
                        ymd.append([info.month(l[i]), l[i], i])
                        mstridx = len(ymd) - 1

                        # Go to next token
                        i += 1

                        if i < len_l:
                            pass
                        else:
                            # Assume l[i] is year
                            try:
                                ymd.append([l[i], l[i], i])
                            except:
                                # Wrong guess, fall back
                                pass

                    elif not fuzzy:
                        return None, None
                    else:
                        i += 1
                    continue

                # Check weekday
                value = info.weekday((l[i]))
                if value is not None:
                    format[i] = '%a' if len(l[i]) == 3 else '%A'
                    res.weekday = value
                    i += 1
                    continue

                # Check month name
                value = info.month(l[i])
                if value is not None:
                    # ymd.append(value)
                    ymd.append([value, l[i], i])
                    assert mstridx == -1
                    mstridx = len(ymd)-1

                    i += 1
                    if i < len_l:
                        if l[i] in ('-', '/'):
                            # Jan-01[-99]
                            sep = l[i]
                            i += 1
                            # ymd.append(l[i])
                            ymd.append([l[i], l[i], i])
                            i += 1

                            if i < len_l and l[i] == sep:
                                # Jan-01-99
                                i += 1
                                # ymd.append(l[i])
                                ymd.append([l[i], l[i], i])
                                i += 1

                        elif i+3 < len_l and l[i] == l[i+1] == ' ' and info.pertain(l[i+1]):
                            # Jan of 01
                            # In this case, 01 is clearly year
                            try:
                                value = int(l[i+3])
                            except ValueError:
                                # Wrong Guess
                                pass
                            else:
                                # ymd.append(str(info.convertyear(value)))
                                ymd.append([str(info.convertyear(value)), value, i-1])
                            i += 4
                    continue

                # Check am/pm
                value = info.ampm(l[i])
                if value is not None:
                    # 'a' or 'am' may erroneously trigger the AM/PM flag, should be avoid in this parser
                    val_is_ampm = True
                    if fuzzy:
                        raise ValueError('fuzzy should never be true for this parser')

                    if res.hour is None:
                        raise ValueError('No hour specified with AM or PM flag.')

                    elif not 0 <= res.hour <= 12:
                        raise  ValueError('Invalid hour specified for 12-hour check')

                    if val_is_ampm:
                        if value == 1 and res.hour < 12:
                            res.hour += 12
                        elif value == 0 and res.hour == 12:
                            res.hour = 0
                        res.ampm = value
                        format[i] = '%p'
                    i += 1
                    continue

                # Check for a timezone name
                if (res.hour is not None and len(l[i]) <= 5 and res.tzname is None and res.tzoffset is None and
                        not [x for x in l[i] if x not in string.ascii_uppercase]):
                    res.tzname = l[i]
                    res.tzoffset = info.tzoffset(res.tzname)
                    format[i] = '%Z'

                    i += 1

                    # Check for something like GMT+3, or BRST+3. -- keep the original code, but the format is invalid
                    if i < len_l and l[i] in ('+', '-'):
                        format[i-1] = '?'
                        l[i] = ('+', '-')[l[i] == '+']
                        res.tzoffset = None
                        if info.utczone(res.tzname):
                            res.tzname = None

                    continue

                # Check for a numbered timezone -- This has no support for the format
                if res.hour is not None and l[i] in ('+', '-'):
                    format[i] = '%Z'
                    signal = (-1, 1)[l[i] == '+']
                    i += 1
                    len_li = len(l[i])

                    if len_li == 4:
                        res.tzoffset = int(l[i][:2]) * 3600 + int(l[i][2:]) * 60
                        format[i] = ''
                    elif i+1 < len_l and l[i+1] == ':':
                        res.tzoffset = int(l[i]) * 3600 + int(l[i+2]) * 60
                        format[i], format[i+1], format[i+2] = '', '', ''
                        i += 2
                    elif len_li <= 2:
                        res.tzoffset = int(l[i][:2]) * 3600
                        format[i] = ''
                    else:
                        return None, None
                    i += 1

                    res.tzoffset *= signal

                    # Look for a timezone name between parenthesis
                    if (i+3 < len_l and info.jump(l[i]) and l[i+1] == '(' and l[i+3] == ')' and 3 <= len(l[i+2]) <= 5
                            and not [x for x in l[i+2] if x not in string.ascii_uppercase]):
                        res.tzname = l[i+2]
                        i += 4
                    continue

                # Check jumps
                if not (info.jump(l[i])):
                    return None, None

                # Check unsupported string
                if l[i] in ['st', 'nd', 'rd', 'th']:
                    format[i] = '?'

                i += 1

            # Process year/month/day
            year, month, day = ymd.resolve_ymd(mstridx, yearfirst, dayfirst)
            if year is not None:
                year[1] = _format_ymd.get_tuple_format(year, 'year')
                res.year = year[0]
                res.century_specified = ymd.century_specified
                if year[1]:
                    format[year[2]] = year[1]

            if month is not None:
                month[1] = _format_ymd.get_tuple_format(month, 'month')
                res.month = month[0]
                if month[1]:
                    format[month[2]] = month[1]

            if day is not None:
                day[1] = _format_ymd.get_tuple_format(day, 'day')
                res.day = day[0]
                if day[1]:
                    format[day[2]] = day[1]

        except (IndexError, ValueError, AssertionError):
            return None, None

        if not info.validate(res):
            return None, None

        # print(format)
        return res, "".join(format)


def _format_parsems(value):
    """Parse a I[.F] seconds value into (seconds, microseconds)."""
    # TODO: %f seems not fully correct
    if "." not in value:
        return int(value), 0, "%S"
    else:
        i, f = value.split(".")
        return int(i), int(f.ljust(6, "0")[:6]), "%S.%f"


DEFAULTPARSER = parser_with_format()


def parse(timestr, parserinfo=None, **kwargs):
    if parserinfo:
        return parser_with_format(parserinfo).parse(timestr, **kwargs)
    else:
        return DEFAULTPARSER.parse(timestr, **kwargs)


if __name__ == '__main__':
    # test_parser = parser_with_format()
    test_str = '2006-12-31'
    res, res_format = parse(test_str)
    print('Parsered Time {}'.format(res))
    print('Parsered Time Format {}'.format(res_format))
    new_res = datetime.datetime.strptime(test_str, res_format)
    print('Parsered Time via standard parser {}'.format(new_res))