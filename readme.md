# AST-Hints: Comparator and Hint Generator



## Comparator

The comparator is a tool that compares the ASTs of two files and returns the differences between them.

## TODO:
1. Retrieve the correct solution AST from the database. (Chris)
2. Retrieve the next-best solution AST from the database. (Chris)
3. Compute edit vectors between the current solution and the next best solution.
4. Generate a power set of all edit vectors.
5. Construct intermediate ASTs by applying subsets of the edit vectors to the current solution AST.
6. Score each intermediate AST using the desirability metric.
7. Return the intermediate AST with the highest score along with the edit vectors.
8. 