
- snippet for: `more information`,`epsilon text`

## snippet

```html
<p>If you are not familiar with differential privacy, one analogy for privacy budgeting is going clothes shopping with a fixed budget. With a fixed budget you can only purchase so many items and have to prioritize which pieces are most important for your wardrobe.</p>
<p>Within differential privacy, the privacy budget is known as epsilon, denoted by the Greek letter <b>&epsilon;</b>.</p>
<p>As an example, let's say your epsilon, or privacy budget, is 1.0. When you are at the stage of selecting DP statistics to calculate, you can decide how much epsilon to "spend." For example, suppose your data file contains the variable "Age" and you want to "buy", or calculate, the DP mean of "Age." You could start by "spending," or budgeting, 0.5 epsilon for that statistic.</p>
<ul>
<li><b>Statistic:</b> DP Mean of Age</li>
<li><b>Budget/Epsilon &epsilon;:</b> 0.5 </li>
</ul>
<p>At this point, <i>before</i> running an actual calculation or touching the source data file, DP Creator can determine an error measure for the calculation. In the example below, with a Confidence Level set to 95%, the error is 0.479:</p>
<ul>
<li><b>Statistic:</b> DP Mean of Age</li>
<li><b>Budget/Epsilon &epsilon;:</b> 0.5 </li>
<li><b>Error:</b> 0.479</li>
<li><b>What it means:</b><br />
There is 95% confidence that the DP Mean will be within 0.479 years of the actual mean age.</p></li>
</li>
</ul>
<p>As may be seen above, with an &epsilon; of <b>0.5</b>, the error is <b>0.479</b>. Now, what if you used less &epsilon;, say 0.25?</p>
<ul>
<li><b>Statistic:</b> DP Mean of Age</li>
<li><b>Budget/Epsilon &epsilon;:</b> 0.25 </li>
<li><b>Error:</b> 0.959 </li>
<li><b>What it means:</b><br />
There is 95% confidence that the DP Mean will be within 0.959 years of the actual mean age.</p></li>
</li>
</ul>
<p>In this case, using less &epsilon; <i>increases</i> the error, giving stronger privacy protection but less accuracy.</p>
<p>In contrast, what happens when more &epsilon; is allocated for the same statistic? Say 0.75:</p>
<ul>
<li><b>Statistic:</b> DP Mean of Age</li>
<li><b>Budget/Epsilon &epsilon;:</b> 0.75 </li>
<li><b>Error:</b> 0.320 </li>
<li><b>What it means:</b><br />
There is 95% confidence that the DP Mean will be within 0.320 years of the actual mean age.</p></li>
</li>
</ul>
<p>Looking through this example, using more &epsilon; <i>decreases</i> the error, giving less privacy protection but more accuracy.</p>
<p>These examples show how increasing or decreasing the epsilon, or privacy budget, changes the error, impacting the privacy/accuracy of the statistic. </p>
<table>
<tr>
<th>epsilon</th>
<th>accuracy</th>
</tr>
<tr>
<td>0.25</td>
<td>0.959</td>
</tr>
<tr>
<td>0.50</td>
<td>0.479</td>
</tr>
<td>0.75</td>
<td>0.320</td>
</tr>
</table>
<p>The relationship between epsilon and accuracy/error may be described as:</p> 
<ul>
<li>Lower <b>&epsilon;</b> value --> higher error --> stronger privacy, less accuracy</li>
<li>Higher <b>&epsilon;</b> value --> lower error --> weaker privacy, more accuracy</li>
</ul>
<p>Again, this accuracy/error measure may be determined <i>before</i> running the actual calculation. This allows you to experiment with different statistics and epsilon allocations before calculating the DP statistics. It is simillar to adding/removing/editing items in an online shopping cart before committing to a purchase.</p>
<p>As a rule of thumb, <b>&epsilon;</b> should be thought of as a small number, between approximately 1/100 and 1.</p>
<p><i>(Note: This information has been excerpted from the book chapter <a href=""https://admindatahandbook.mit.edu/book/v1.0/diffpriv.html"" target=""_blank"">Designing Access with Differential Privacy</a>, which also contains illustrative examples.)</i></p>
```