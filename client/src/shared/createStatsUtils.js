import Decimal from 'decimal.js';
import release from "@/api/release";

export const deltaStats = ['Histogram']
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
    validateRelease: function (analysisPlanId, tempStats) {
        release.validate(analysisPlanId, tempStats)
            .then((resp) => {
                let accuracyList = []
                let returnObj = {}
                console.log('validate response: ' + JSON.stringify(resp))
                let valid = true
                resp.data.forEach((item, index) => {
                    accuracyList.push(item.accuracy)

                    if (item.valid !== true) {
                        item.stat = tempStats[index]
                        valid = false;
                    }
                })
                if (valid) {

                    returnObj = {valid: valid, accuracyList: accuracyList}
                } else {
                    returnObj = {valid: false, validationErrorMsg: resp.data}
                }

                return returnObj
            })
            .catch((error) => {
                this.validationErrorMsg = [{"valid": false, "message": error}]
                return {valid: false, accuracyList: acc}
            })
    },
    statisticUsesValue(valName, statistic) {
        return valName === 'epsilon' || (valName == 'delta' && deltaStats.includes(statistic))
    },
    isDeltaStat: function (statistic) {
        return deltaStats.includes(statistic)
    },
    redistributeValues(statistics, delta, epsilon, defaultDelta) {
        if (statistics) {
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
        if (unlockedCount > 0) {
            const valueShare = remaining.div(unlockedCount)
            // Assign value shares and convert everything back from Decimal to Number
            // before saving
            statistics.forEach((item) => {
                if (this.statisticUsesValue(property, item.statistic)) {
                    if (!item.locked) {
                        item[property] = valueShare.toNumber()
                    } else {
                        if (typeof (item[property]) == Decimal) {
                            item[property] = item[property].toNumber()
                        }
                    }

                } else {
                    item[property] = 0
                }
            })

        }

    },

    // Returns Promise json object:
    // valid: true/false
    // data: Array of individual validation flags, accuracy, error messages for each statistic
    releaseValidation(analysisPlanId, tempStats) {
        let returnObj = {valid: true, data: null}
        return release.validate(analysisPlanId, tempStats)
            .then((resp) => {
                console.log('releaseValidation, validate response: ' + JSON.stringify(resp))
                returnObj.data = resp.data
                resp.data.forEach((item, index) => {
                    if (item.valid !== true) {
                        returnObj.valid = false;
                    }
                })
                return returnObj
            })
            .catch((error) => {
                returnObj.valid = false
                returnObj.data = [{"valid": false, "message": error}]
                return returnObj
            })
    }

}