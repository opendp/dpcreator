```python
def build_stat_specs(self):
    """
    Build a list of StatSpec subclasses for
    chain validation or running computations
    """
    self.stat_spec_list = []    # [DPMeanSpec, DPCountSpec, ...]

    # (1) Iterate through user-defined stats
    #
    for dp_stat in self.dp_statistics:    
        
        # (2) Additional info from database
        #
        dp_stat['column_index'] = self.get_col_index(dp_stat['variable'])
        dp_stat['dataset_size'] = self.dataset_size

        # (3) Build StatSpec objects
        #
        if dp_stat['statistic'] == astatic.DP_MEAN:
            # create DP Mean StatSpec
            self.add_stat_spec(DPMeanSpec(dp_stat))
            
        elif dp_stat['statistic'] == astatic.DP_COUNT:
            # create DP Count StatSpec
            self.add_stat_spec(DPCountSpec(dp_stat))
            
        # etc.
```

```python

# Validation: Iterate through StatSpec objects
#
for stat_spec in self.stat_spec_list:   # [DPMeanSpec, DPCountSpec, ...]
    # Check each stat_spec
    if not stat_spec.is_chain_valid():
        # Nope: invalid!
        self.validation_info.append(stat_spec.get_error_msg_dict())
    else:
        # (not shown: check cumulative epsilon)
        # Looks good!
        self.validation_info.append(stat_spec.get_success_msg_dict())


```


```python


# Computation: Iterate through StatSpec objects
#
col_indices = self.get_column_indices()
data_pointer = self.get_data_pointer()

# (Simplified)
for stat_spec in self.stat_spec_list:   # [DPMeanSpec, DPCountSpec, ...]

    # Run the computation chain
    stat_spec.run_chain(col_indices, data_pointer, sep_char=sep_char)
    if not stat_spec.has_error():
        # Looks good! Save the stat
        self.release_stats.append(stat_spec.get_release_dict())
    else:
        self.add_err_msg(stat_spec.get_single_err_msg())

        # Delete any previous stats
        del(self.release_stats)
        return
    
self.make_release_info()
```

```python

    def get_preprocessor(self):
        """DP Mean preprocessor for floats"""
        if self.has_error():
            return

        # Have we already already assembled it?
        if self.preprocessor is not None:
            return self.preprocessor    # Yes!

        preprocessor = (
            # Selects a column of df, Vec<str>
            make_select_column(key=self.col_index, TOA=str) >>
            # Cast the column as Vec<Optional<Float>>
            make_cast(TIA=str, TOA=float) >>
            # Impute missing values 
            make_impute_constant(self.fixed_value) >>
            # Clamp age values
            make_clamp(self.get_bounds()) >>
            make_bounded_resize(self.dataset_size, self.get_bounds(), self.fixed_value) >>
            make_sized_bounded_mean(self.dataset_size, self.get_bounds())
        )

        self.scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon), bounds=(0.0, 1000.0))
        preprocessor = preprocessor >> make_base_laplace(self.scale)

        self.preprocessor = preprocessor    # Pointer to the preprocessor to potentially re-use for .run_chain(...)

        return preprocessor
```


```json
{
    "statistic": "mean",
    "variable": "income",
    "result": {
        "value": 30978.68182667468
    },
    "epsilon": 0.6,
    "delta": 0.0,
    "bounds": {
        "min": 0.0,
        "max": 650000.0
    },
    "missing_value_handling": {
        "type": "insert_fixed",
        "fixed_value": 31000.0
    },
    "confidence_interval": 0.99,
    "confidence_interval_alpha": 0.01,
    "accuracy": {
        "value": 498.89343683324705,
        "message": "Releasing mean for the variable income. With at least probability 99.0% the output mean will differ from the true mean by at most 498.89343683324705 units. Here the units are the same units the variable has in the dataset."
    },
    "description": {
        "html": "A differentially private <b>Mean</b> for variable <b>income</b> was calculated with the result <b>30978.68182667468</b>. There is a probability of <b>99.0%</b> that the output count will differ from the true count by at most <b>498.89343683324705</b> units. Here the units are the same units the variable has in the dataset.",
        "text": "A differentially private Mean for variable \"income\" was calculated with the result30978.68182667468. There is a probability of 99.0% that the output count will differ from the true count by at most 498.89343683324705 units. Here the units are the same units the variable has in the dataset."
    }
}



```