# Weighting problem solver using Constaint Logic Programming

## Problem statement
Imagine we have asked 1000 people from Poland about something 
f.e. how much money do they earn. We also ask them about their gender and
age. After that, we would like to know sum of incomes among women
in Poland. 

Problem: in our survey we have only 1000 people, and in Poland there are abot
40.000.000 people. 

Solution: multiply answer of each person by 40.000

Problem: In out survey, we have 60% women and 40% men, but in reality 
in Poland it is 55% women and 45% men

Solution: Give men slightly bigger and women slightly lower weight,
so sum of weight still will be 40.000.000, but sum of weights of
women will be 55% of 40.000.000 instead of 60%.

Problem: But we also have age, and we wold like to keep 
age structure of Poland as well.

Solution: If we know how many women of all age groups we have in Poland
(such joint of demographic features is called 'cross'), we can also
distribute weights like in the previous examples.

Problem: But we do not know population of crosses...

Solution: Let's use CLP!

## Input

Population file:
```json
{
  "age": {
    "15-20": 10
  },
  "sex": {
    "m": 6,
    "k": 4
  },
  "total": 10
}
```

Panelists file:
```json
{
  "1": {
    "demo": {
      "age": "15-20",
      "sex": "m"
    },
    "metric": 100
  },
  "2": {
    "demo": {
      "age": "15-20",
      "sex": "k"
    },
    "metric": 150
  }
}
```

##Output

Weights of each panelist:
```json
{
    "1": 6,
    "2": 4
}
```

##Solution description

We have to guess population od cross knowing only sums of
crosses. If conditions are not conflicting, then there exist
multiple solutions to that problem. We wold like to choose
one that modifies input crosses structure (percentage of whole population) 
as little as possible. To 
achieve that we define function for out CLP program
to minimize
```text
input_percent = |panelists_in_cross| / |all panelists|
output_percent = cross_size / |sum of all cross_sizes| 
error_function = sum of abs(input_percent - output_percent) for all crosses
```

Weight of panelists are calculated easily: each panelist
from cross gets weight `cross_size / |panelists_in_cross|`. Of course
we can distribute weights over panelists in cross in many
different ways, in this simple solution there was no point to 
distinguish panelists from same cross, so there is no reason for
panelists to have different weights.

## Weighting efficiency
Solution aims to maximize weighting efficiency defined as
```text
     (sum_of_weights) ** 2
     ---------------------
          panel_size  
we = --------------------- * 100
     sum of (weights ** 2)
```
Unfortunately, it cannot optimize this function directly because
it is quadratic function, and since we use eclipse-clp with
OSI solver, we are limited to linear programming.

## How is it done in practice?
[RIM Weighting](http://www.mrdcsoftware.com/blog/what-is-rim-weighting-with-free-excel-working-model)