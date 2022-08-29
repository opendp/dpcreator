from copy import copy

KEY_CATEGORIES = 'categories'

def format_variable_info(variable_info: dict) -> dict:
    """
    Format the categories within variable_info before it is saved to the database.

    Typical variable_info structure is:
    { "variable_name":{
            "categories": [may or may not exist but if they're strings, trim the spaces]
        }
    }

    Example: {
          "session":{
              "name":"Session",
              "type":"Boolean",
              "label":"",
              "sortOrder":2,
              "categories":[]  # Nothing to do
           },
           "subject":{
              "name":"Subject",
              "type":"Categorical",
              "label":"Subject",
              "selected":true,
              "sortOrder":0,
              "categories":["ac"," kj"," ys", "zz"," bh1"]  # strip the spaces!
           }
    }

    @param variable_info:
    @return:
    """
    if not variable_info:  # empty, None, etc, just return it
        return variable_info

    variable_info2 = copy(variable_info)

    updated_info = {}
    for var_name, var_info in variable_info2.items():
        # Format the categories
        if not KEY_CATEGORIES in var_info:
            updated_info[var_name] = var_info
            continue
        else:
            orig_categories = var_info.get(KEY_CATEGORIES, [])
            updated_categories = []

            if not isinstance(orig_categories, list):
                # Not a list, set the updated 'categories' to [] (via 'updated_categories)
                pass
            else:
                for orig_cat in orig_categories:
                    if isinstance(orig_cat, str):
                        orig_cat = orig_cat.strip()
                    else:
                        # If there's a non-string in a list of category strings, leave it to be checked elsewhere
                        pass

                    if orig_cat:  # (if it turns out to be None or an empty string, ignore it)
                        updated_categories.append(orig_cat)

            # Add the info to the updated dict
            var_info[KEY_CATEGORIES] = updated_categories
            updated_info[var_name] = var_info

    return updated_info


