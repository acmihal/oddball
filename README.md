# Oddball
A classic problem in recreational mathematics is to identify an
incorrectly-weighted ball in a set of N otherwise identical balls.
The challenge is to use a balance scale a maximum of W times,
where W is typically much smaller than N.
The solution must identify which ball has the incorrect weight
and whether the ball is heavier or lighter than the rest.

**Oddball** implements a solver for this problem based on Boolean Satisfiability.
The set of balls on the left and right sides of the balance scale are determined
for each of the W weighings.
The outcomes of the weighings are then looked up in a truth table that tells
which ball is wrong and whether it is light or heavy.

A simplifying assumption is made that the balls to be weighed are determined *a priori*.
That is, the choice of what to weigh next is not dependent on the outcome of the previous weighings.

## Installation

    # git clone https://github.com/acmihal/oddball.git
    # cd oddball
    # pip install -e .

## Usage

    # oddball -h
    # oddball 9 3

## Output

The Solution section gives the balls to be weighed for each of the W weighings. For example:

    # oddball 9 3
    Solving for 9 balls and 3 weighings

    Solution:
    W0: [ 0,  2,  3,  7] <=> [ 1,  4,  6,  8]
    W1: [ 0,  1,  4] <=> [ 2,  6,  8]
    W2: [ 1,  3,  6] <=> [ 4,  5,  8]

The first weighing should have balls 0, 2, 3, and 7 on the left side of the scale, and balls 1, 4, 6, and 8
on the right side of the scale. If the heavy ball is on the left or the light ball is on the right,
the outcome will be **>** (left heavier than right). If the light ball is on the left or the heavy ball
is on the right, the outcome will be **<** (right heavier than left).
If the incorrectly-weighted ball is not on the scale, the result will be **=** (both sides equal).
In this example, that would mean that the incorrectly-weighed ball must be ball 5.

The next section of the output is the Truth Table.
Look up the row in the Truth Table that matches the outcomes of the weighings to get the answer.

    Truth Table:
    ix  W0  W1  W2   Result
     0   <   <   <   8+
     1   <   <   =   0-
     2   <   <   >   6+
     3   <   =   <   3-
     4   <   =   =   7-
     5   <   =   >
     6   <   >   <   4+
     7   <   >   =   2-
     8   <   >   >   1+
     9   =   <   <
    10   =   <   =
    11   =   <   >
    12   =   =   <   5+
    13   =   =   =
    14   =   =   >   5-
    15   =   >   <
    16   =   >   =
    17   =   >   >
    18   >   <   <   1-
    19   >   <   =   2+
    20   >   <   >   4-
    21   >   =   <
    22   >   =   =   7+
    23   >   =   >   3+
    24   >   >   <   6-
    25   >   >   =   0+
    26   >   >   >   8-

Continuing with the above example, let's say that weighing 0 had outcome **>** (left side heavier),
and weighing 1 and 2 both had outcome **=** (both sides equal).
These outcomes are in row 22 of the truth table, and that row has the result **7+**.
This means the answer is that ball 7 is the incorrectly-weighted ball and it is heavier than the others.
A result with a minus sign means the incorrectly-weighted ball is lighter than the others.

Some truth table rows don't have any result. This is normal. Some combinations of weighing outcomes are impossible,
because the bad ball must have tipped the scale at some point.

In the last section of output, **Oddball** thoroughly tests the answer for you.
For every possible ball being the bad ball, and for both the heavier and lighter case,
all the weighings are simulated and the result is looked up in the truth table.
**Oddball** makes sure the truth table gives the correct answer in all cases.

For example the first test checks the case where ball 0 is light:

    Test 0-:
        W0: [ 0,  2,  3,  7] < [ 1,  4,  6,  8]
        W1: [ 0,  1,  4] < [ 2,  6,  8]
        W2: [ 1,  3,  6] = [ 4,  5,  8]
        Truth table result: ['0-'] is correct

In weighing 0, ball 0 is on the left, so the outcome is **<** (left side is lighter than the right side).
In weighing 1, ball 0 is on the left again so the outcome is again **<**.
In weighing 2, ball 0 is not on the scale, so the scale is balanced (outcome **=**).

The results **<**, **<**, and **=** correspond to row 1 in the truth table, which has the right answer **0-**.



## Examples

### 2 Balls and 1 Weighing

    # oddball 2 1
    Solving for 2 balls and 1 weighings
    No solution exists for 2 balls and 1 weighings.

If the problem cannot be solved, **Oddball** will print a message like this.

If there are only two balls, the only thing you can do is put them on opposite sides of the scale.
The scale won't balance, but you can't tell if it is because one side is heavier than it is supposed to be or lighter than it is supposed to be.

### 3 Balls and 2 Weighings
    # oddball 3 2
    Solving for 3 balls and 2 weighings
    
    Solution:
    W0: [ 0] <=> [ 1]
    W1: [ 2] <=> [ 1]
    
    Truth Table:
    ix  W0  W1   Result
     0   <   <   1+
     1   <   =   0-
     2   <   >
     3   =   <   2-
     4   =   =
     5   =   >   2+
     6   >   <
     7   >   =   0+
     8   >   >   1-
    
    Test 0-:
        W0: [ 0] < [ 1]
        W1: [ 2] = [ 1]
        Truth table result: ['0-'] is correct
    
    Test 0+:
        W0: [ 0] > [ 1]
        W1: [ 2] = [ 1]
        Truth table result: ['0+'] is correct
    
    Test 1-:
        W0: [ 0] > [ 1]
        W1: [ 2] > [ 1]
        Truth table result: ['1-'] is correct
    
    Test 1+:
        W0: [ 0] < [ 1]
        W1: [ 2] < [ 1]
        Truth table result: ['1+'] is correct
    
    Test 2-:
        W0: [ 0] = [ 1]
        W1: [ 2] < [ 1]
        Truth table result: ['2-'] is correct
    
    Test 2+:
        W0: [ 0] = [ 1]
        W1: [ 2] > [ 1]
        Truth table result: ['2+'] is correct
    
    Total correct results: 6
    Total incorrect results: 0

### 12 Balls and 3 Weighings
    # oddball 12 3
    Solving for 12 balls and 3 weighings
    
    Solution:
    W0: [ 0,  6,  7,  9] <=> [ 1,  2,  8, 10]
    W1: [ 4,  5,  6,  7] <=> [ 0,  3,  9, 10]
    W2: [ 0,  1,  3,  4] <=> [ 2,  6, 10, 11]
    
    Truth Table:
    ix  W0  W1  W2   Result
     0   <   <   <   10+
     1   <   <   =   7-
     2   <   <   >   6-
     3   <   =   <   2+
     4   <   =   =   8+
     5   <   =   >   1+
     6   <   >   <   0-
     7   <   >   =   9-
     8   <   >   >
     9   =   <   <   4-
    10   =   <   =   5-
    11   =   <   >   3+
    12   =   =   <   11+
    13   =   =   =
    14   =   =   >   11-
    15   =   >   <   3-
    16   =   >   =   5+
    17   =   >   >   4+
    18   >   <   <
    19   >   <   =   9+
    20   >   <   >   0+
    21   >   =   <   1-
    22   >   =   =   8-
    23   >   =   >   2-
    24   >   >   <   6+
    25   >   >   =   7+
    26   >   >   >   10-
    
    Test 0-:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['0-'] is correct
    
    Test 0+:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['0+'] is correct
    
    Test 1-:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['1-'] is correct
    
    Test 1+:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['1+'] is correct
    
    Test 2-:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['2-'] is correct
    
    Test 2+:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['2+'] is correct
    
    Test 3-:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['3-'] is correct
    
    Test 3+:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['3+'] is correct
    
    Test 4-:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['4-'] is correct
    
    Test 4+:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['4+'] is correct
    
    Test 5-:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['5-'] is correct
    
    Test 5+:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['5+'] is correct
    
    Test 6-:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['6-'] is correct
    
    Test 6+:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['6+'] is correct
    
    Test 7-:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['7-'] is correct
    
    Test 7+:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['7+'] is correct
    
    Test 8-:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['8-'] is correct
    
    Test 8+:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['8+'] is correct
    
    Test 9-:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['9-'] is correct
    
    Test 9+:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] = [ 2,  6, 10, 11]
        Truth table result: ['9+'] is correct
    
    Test 10-:
        W0: [ 0,  6,  7,  9] > [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] > [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['10-'] is correct
    
    Test 10+:
        W0: [ 0,  6,  7,  9] < [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] < [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['10+'] is correct
    
    Test 11-:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] > [ 2,  6, 10, 11]
        Truth table result: ['11-'] is correct
    
    Test 11+:
        W0: [ 0,  6,  7,  9] = [ 1,  2,  8, 10]
        W1: [ 4,  5,  6,  7] = [ 0,  3,  9, 10]
        W2: [ 0,  1,  3,  4] < [ 2,  6, 10, 11]
        Truth table result: ['11+'] is correct
    
    Total correct results: 24
    Total incorrect results: 0
