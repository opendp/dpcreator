"""
This file is a list of dataset persistentUrls to NOT delete.
This file can be used as a model, updated as needed, etc--or, if really used, convert to optional plain text file.

Note: It doesn't matter if the url resolves. For example, this is an example JSON snippet, the "persistentUrl" will be used to identify this as the dataset to save--even if the persistentUrl doesn't work.
{
    'id': 10,
    'identifier': 'FK2/WAPEME',
    'persistentUrl': 'https://doi.org/10.5072/FK2/WAPEME',
    'protocol': 'doi',
    'authority': '10.5072',
    'publisher': 'This Dataverse is for DP Creator testing purposes only.',
    'storageIdentifier': 'file://10.5072/FK2/WAPEME',
    'metadataLanguage': 'undefined',
    'type': 'dataset'
}
"""

# Add "persistentUrl" objects to NOT delete
DATASETS_TO_KEEP = ['https://doi.org/10.5072/FK2/FAKE',
                    'https://doi:10.5072/FK2/J9BZ8P']
