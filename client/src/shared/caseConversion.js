import {snakeCase} from "snake-case";

const camelcaseKeys = require('camelcase-keys');
const snakecaseKeys = require('snakecase-keys');


export default {
    // deep convert keys to snake case, except for contents of variableInfo
    customSnakecaseKeys(objectParam) {
        //  console.log('customizing: '+ JSON.stringify(objectParam))
        //   console.log('keys: ' +JSON.stringify(Object.keys(objectParam)))
        let convertedObject = {}
        Object.keys(objectParam).forEach((key) => {
            // If key == variableInfo, convert the key to variable_info, but don't convert the contents
            if (key == 'variableInfo') {
                convertedObject.variable_info = objectParam.variableInfo
            } else {
                if (objectParam[key] !== null && typeof objectParam[key] === 'object') {
                    console.log('calling snakecaseKeys on nested object ' + objectParam[key])
                    convertedObject[snakeCase(key)] = snakecaseKeys(objectParam[key], {deep: true})
                } else {
                    convertedObject[snakeCase(key)] = objectParam[key]
                }
            }
        })
        // console.log('returning: '+ JSON.stringify(convertedObject))
        return convertedObject
    },
    customCamelcaseKeys(object) {

    }

};
