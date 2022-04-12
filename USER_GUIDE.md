# The DP Creator User Guide

This document should ultimately serve as a user guide for end users who need to know specifics about using DP Creator, 
but are not concerned with the details in the README, such as Docker files and other configurations. 

This should highlight:

1. Which statistics are available
2. Adding data to a Dataverse installation
3. Allowing the data to be accessible by DP Creator
4. Walking through the DP Creator workflow, through to the release page

 
## Supported Statistics

|           | Boolean | Categorical | Float | Integer | Return Type   |
|-----------|---------|-------------|-------|---------|---------------|
| Count     | X       | X           | X     | X       | Integer       |
| Mean      |         |             | X     | X       | Float         |
| Histogram |         | X           |       | X       | List[Integer] |
| Variance  |         |             | X     | X       | Float         |