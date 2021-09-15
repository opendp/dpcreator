import Decimal from 'decimal.js';

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

                }
            })

        }

    },
}