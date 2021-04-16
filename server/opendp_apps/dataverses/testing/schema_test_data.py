
schema_info_01_file_id = 4164587
schema_info_01_file_pid = 'no-pid-in-schema'

schema_info_01 = {
   "@id":"https://doi.org/10.7910/DVN/PUXVDH",
   "name":"Replication Data for: Eye-typing experiment",
   "@type":"Dataset",
   "author":[
      {
         "name":"Bafna, Tanya",
         "affiliation":"Danmarks Tekniske Universitet"
      }
   ],
   "creator":[
      {
         "name":"Bafna, Tanya",
         "affiliation":"Danmarks Tekniske Universitet"
      }
   ],
   "license":{
      "url":"https://creativecommons.org/publicdomain/zero/1.0/",
      "text":"CC0",
      "@type":"Dataset"
   },
   "version":"1",
   "@context":"http://schema.org",
   "keywords":[
      "Engineering",
      "Medicine, Health and Life Sciences",
      "eye-tracking, eye-typing, mental fatigue"
   ],
   "provider":{
      "name":"Harvard Dataverse",
      "@type":"Organization"
   },
   "publisher":{
      "name":"Harvard Dataverse",
      "@type":"Organization"
   },
   "identifier":"https://doi.org/10.7910/DVN/PUXVDH",
   "description":[
      "The data consists of performance and eye-tracking features obtained during an eye-typing experiment conducted over 4 days, 2 sessions on each day, with 18 participants."
   ],
   "dateModified":"2020-11-04",
   "distribution":[
      {
         "name":"Fatigue_data.tab",
         "@type":"DataDownload",
         "contentUrl":"https://dataverse.harvard.edu/api/access/datafile/4164587",
         "fileFormat":"text/tab-separated-values",
         "contentSize":36399,
         "description":"Fatigue level (taken from trials 1,5 and 10 on each day) and eye-tracking and performance data from trials that correlate to the corresponding fatigue level. (For all sessions where the correlation between left and right pupil size was greater or equal to 0.75)"
      },
      {
         "name":"Fatigue_difference_consecutive_subjScore.tab",
         "@type":"DataDownload",
         "contentUrl":"https://dataverse.harvard.edu/api/access/datafile/4164586",
         "fileFormat":"text/tab-separated-values",
         "contentSize":2795,
         "description":"Difference between intermediate fatigue level (obtained after session 1) and initial fatigue level (obtained before experiment) and between  terminal fatigue level (obtained after session 2) and intermediate fatigue level (obtained after session 1) "
      },
      {
         "name":"Fatigue_difference_terminal_initial_subjScore.tab",
         "@type":"DataDownload",
         "contentUrl":"https://dataverse.harvard.edu/api/access/datafile/4164589",
         "fileFormat":"text/tab-separated-values",
         "contentSize":2712,
         "description":"Difference between  terminal fatigue level (obtained after session 2) and initial fatigue level (obtained before experiment)"
      },
      {
         "name":"PerceivedEffort_data.tab",
         "@type":"DataDownload",
         "contentUrl":"https://dataverse.harvard.edu/api/access/datafile/4164588",
         "fileFormat":"text/tab-separated-values",
         "contentSize":123290,
         "description":"Eye-tracking and performance data for every trial, and the perceived effort for every trial (For all sessions where the correlation between left and right pupil size was greater or equal to 0.75)"
      },
      {
         "name":"PerceivedEffort_subjScore.tab",
         "@type":"DataDownload",
         "contentUrl":"https://dataverse.harvard.edu/api/access/datafile/4164590",
         "fileFormat":"text/tab-separated-values",
         "contentSize":17053,
         "description":"Perceived effort for every trial "
      }
   ],
   "datePublished":"2020-11-04",
   "includedInDataCatalog":{
      "url":"https://dataverse.harvard.edu",
      "name":"Harvard Dataverse",
      "@type":"DataCatalog"
   }
}