import Decimal from 'decimal.js';
import release from "@/api/release";

export const deltaStats = ['Histogram']
export const CL_99 = "99"
export const CL_95 = "95"
export const MAX_TOTAL_EPSILON = 1
export const MIN_EPSILON = .001

export const confLevelOptions = [
    {text: "99%", value: .99},
    {text: "95%", value: .95},
]


export default {
    statisticsUseDelta: function (statistics)
        // Only a subset of statistics use delta.
        // Return true if any statistics in the dpStatistics table
        // use delta, else return false
    {
        let useDelta = false
        statistics.forEach((item) => {
            if (deltaStats.includes(item.statistic)) {
                useDelta = true
            }
        })
        return useDelta
    },
    statisticUsesValue(valName, statistic) {
        return valName === 'epsilon' || (valName == 'delta' && deltaStats.includes(statistic))
    },
    isDeltaStat: function (statistic) {
        return deltaStats.includes(statistic)
    },
    redistributeValues(statistics, delta, epsilon, defaultDelta) {
        if (statistics && statistics.length > 0) {
            if (this.statisticsUseDelta(statistics) && delta == 0) {
                delta = defaultDelta
            }
            if (this.statisticsUseDelta(statistics)) {
                delta = 0
            }
            this.redistributeValue(epsilon, 'epsilon', statistics)
            this.redistributeValue(delta, 'delta', statistics)
        }
    },
    redistributeValue(totalValue, property, statistics,) {
        // for all statistics that use this value -
        // if locked == false, update so that the unlocked value
        // is shared equally among them.
        let lockedValue = new Decimal('0.0');
        let lockedCount = new Decimal('0');
        let unlockedCount = new Decimal('0')
        statistics.forEach((item) => {
            if (this.statisticUsesValue(property, item.statistic)) {
                if (item.locked) {
                    lockedValue = lockedValue.plus(item[property])
                    lockedCount = lockedCount.plus(1);
                } else {
                    unlockedCount = unlockedCount.plus(1)
                }
            }
        });
        const remaining = new Decimal(totalValue).minus(lockedValue)
        let valueShare = new Decimal('0')
        if (unlockedCount > 0) {
            valueShare = this.safeSplit(remaining, unlockedCount) //remaining.div(unlockedCount)
            console.log('valueShare: ' + valueShare + "," + typeof (valueShare))
        }

        // Assign value shares and convert everything back from Decimal to Number
        // before saving
        statistics.forEach((item) => {
            if (this.statisticUsesValue(property, item.statistic)) {
                if (!item.locked) {
                    item[property] = valueShare
                } else {
                    if (typeof (item[property]) == Decimal) {
                        item[property] = item[property].toNumber()
                    }
                }
            } else {
                item[property] = 0
            }
        })


    },
    safeSplit(budget, k) {
        // algorithm from Micheal Shoemate to ensure we don't exceed the total budget
        let is_x_gte_kv = (x, k, v) =>
            x >= Array(k).fill().reduce((s, _) => s + v, 0)
        let split_budget = (x, k) => {
            // preserve symmetry if possible
            if (is_x_gte_kv(x, k, x / k)) return x / k

            // try increasingly large offsets until passes
            for (let pow of Array(20).keys()) {
                // candidate value v
                let v = (x - Math.pow(10, pow - 20)) / k
                if (is_x_gte_kv(x, k, v)) return v
            }
        }
        return split_budget(budget, k)
    },

    // Returns Promise json object:
    // valid: true/false
    // data: Array of individual validation flags, accuracy, error messages for each statistic
    releaseValidation(analysisPlanId, tempStats) {
        let returnObj = {valid: true, data: null}
        return release.validate(analysisPlanId, tempStats)
            .then((resp) => {
                console.log('releaseValidation, validate response: ' + JSON.stringify(resp))
                returnObj.valid = resp.success
                returnObj.data = [{
                    "valid": returnObj.valid,
                    "message": (resp.message + ": " + JSON.stringify(resp.errors))
                }]

                return returnObj
            })
            .catch((error) => {
                returnObj.valid = false
                returnObj.data = [{"valid": false, "message": error}]
                return returnObj
            })
    }

}
