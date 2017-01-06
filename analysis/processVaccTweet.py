import sys
import json

from constants import dateToWeek, postalCodeToRegion


{
    "01001": {
        "Name": "Autauga County, AL",
        "No. of Tweets": {
            "01/04/2014": 6,
            "01/11/2014": 4,
            # ...,
            "12/28/2013": 2
        },
        "Population, 2013 estimate": 55136,
        "Population, 2014 estimate": 55395,
        "Persons 65 years and over, percent, 2013": 13.5,
        "Vaccination percentage %": {
            "01/04/2014": 45.57994939,
            "01/11/2014": 45.79366613,
            # ...,
            "12/28/2013": 45.40509032
        }
    },
    # ...
}



def process(filename):
    with open(filename) as fh:
        vtjson = json.load(fh)

    weekToTweets = {}
    weekToVaccPops = {}
    for (fips, data) in vtjson.iteritems():
        name = data["Name"].split(', ')
        if len(name) != 2:
            continue  # skip FIPS entries that aren't county-level
        region = postalCodeToRegion[name[-1]]
        pop13 = data["Population, 2013 estimate"]
        pop14 = data["Population, 2014 estimate"]
        mcare = data["Persons 65 years and over, percent, 2013"]
        pop = (pop13 + pop14) / 2  # easiest way to use both numbers

        if "No. of Tweets" in data:
            for (date, count) in data["No. of Tweets"].iteritems():
                week = dateToWeek(date)
                if week not in weekToTweets:
                    weekToTweets[week] = [0] * 11
                weekToTweets[week][region] += count

        if "Vaccination percentage %" in data:
            for (date, rate) in data["Vaccination percentage %"].iteritems():
                week = dateToWeek(date)
                if week not in weekToVaccPops:
                    weekToVaccPops[week] = [0] * 11
                weekToVaccPops[week][region] += (rate / 100) * (mcare / 100) * pop

    return sorted(weekToTweets.items()), sorted(weekToVaccPops.items())


if __name__ == '__main__':
    # filename = "raw/input/Flu_Vacc_Tweet_TRAIN.json"  # 2013-2014
    # filename = "raw/input/Flu_Vacc_Tweet_TEST.json"   # 2014-2015
    filename = sys.argv[1]
    wkTcs, wkVps = process(filename)
    hdr = "Year.Wk,R.01#,R.02#,R.03#,R.04#,R.05#,R.06#,R.07#,R.08#,R.09#,R.10#,US#"
    print('TWEET COUNTS:\n' + hdr)
    for (wk, tcs) in wkTcs:
        tcs.append(sum(tcs))
        print('{:05.2f}'.format(wk) + ',' + ','.join(map(str, tcs[1:])))
    print('\n\n\nVACCINATIONS:\n' + hdr)

    def fmt(num): return '{:.0f}'.format(num)

    for (wk, vps) in wkVps:
        vps.append(sum(vps))
        print('{:05.2f}'.format(wk) + ',' + ','.join(map(fmt, vps[1:])))
