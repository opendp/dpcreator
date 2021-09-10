// TODO: replace this with real list statistics that use delta
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
    }
}