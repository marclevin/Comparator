def twosum(numbers, targetnumber):
    for i in range(len(numbers)):
        for j in range((i + 1), len(numbers)):
            if helper_check(numbers[i], numbers[j], targetnumber):
                return [i, j]
    return []


def helper_check(num1, num2, target):
    return num1 + num2 == (target)
