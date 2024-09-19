su = 0
for i in range(5):
    a = int(input("Enter a value:\n"))
    su = su + a

    average = su // 5
print("The average, rounded to the nearest integer is", average, end='')
print(".")
if average % 2 == 0:
    print("The average is an even number.")
else:
    print("The average is an odd number.")
