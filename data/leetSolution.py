Sum = 0
for i in range(5):
    value = eval(input("Enter a value:\n"))
    Sum += value

average = Sum / 5
print("The average, rounded to the nearest integer is", round(average), end='.')
if average % 2 == 0:
    print("\nThe average is an even number.")
else:
    print("\nThe average is an odd number.")
