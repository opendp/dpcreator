Papa = require('papaparse');
const fs = require('fs');

fs.readFile('./build_locale/DPCreatorText.csv', 'utf8', function (err, csvString) {
    if (err) throw err;
    Papa.parse(csvString, {
        complete: function (results) {
            let pageDict = {};
            for (let row in results.data) {
                if (row > 0) {
                    let pageName = results.data[row][0]
                    if (!pageDict[pageName])
                        pageDict[pageName] = {}
                    pageDict[pageName][results.data[row][1]] = results.data[row][2]
                }
            }
            console.log("Finished:", JSON.stringify(pageDict, null, 4));
            let json = JSON.stringify(pageDict, null, 4)
            // Write data in 'Output.txt' .
            fs.writeFile('Outputjson.txt', json, (err) => {
                // In case of a error throw err.
                if (err) throw err;
            })
        }
    });
});
