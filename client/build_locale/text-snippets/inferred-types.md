
- snippet for: `more information,inferred-types text`

## snippet

```html
<p>When DP Creator first reads a data file, it attempts to infer each variable type, distinguishing between: Boolean, Categorical, Float, and Integer.</p>
<p>However, this inference may not be correct and needs to be double-checked by the user! Without checking, a privacy violation may occur.</p>
<p>For example, a dataset variable may be inferred to be <b>Boolean</b> because only two values for that variable appear in the data file. However, there may be more possible values that are not present in the data. The <i>absence</i> of those values may result in a privacy violation.</p>
<p>For example:</p>
<ul>
<li>Pretend all people can one have one of three possible shape biomarkers: circle, square, and trapezoid--and trapezoid is associated with a fatal disease.</li>
<li>A dataset on people living in Sunrise Beach, Los Angeles is loaded into DP Creator and the ShapeBiomarker variable includes the values circle and trapezoid (the fatal shape) but not square.
    <br />&nbsp; &nbsp;<b>All possible values:</b> circle, square, and trapezoid
    <br />&nbsp; &nbsp;<b>Values in the dataset</b>: circle, trapezoid
    <br />&nbsp; &nbsp;<b>Incorrect Type inference</b>: Boolean
    <br />&nbsp; &nbsp;<b>Actual Type</b>: Categorical
</li>
<li>Finding only two values in the dataset, DP Creator infers it to be type <b>Boolean</b></li>
<li>If the type is not corrected to <b>Categorical</b> and a histogram is run on the ShapeBiomarker variable, someone with knowledge of shape biomarkers will be able to learn that no one in Sunrise Beach has the ShapeBiomarker ""square.""</li>
<li>Depending on the histogram values, the size of Sunrise Beach, and available adjacent data someone may be able to identify people who have the fatal trapezoid biomarker.</li>
<li>A serious privacy violation has occurred!</li>
</ul>    
<p><i>Remember to check that the Variable Type is correct!</i></p>
```