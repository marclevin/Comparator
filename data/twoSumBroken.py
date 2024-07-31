def twosum(numbers, target):
    for i in numbers:
        for j in numbers - i:
            if (numbers[i] + numbers[j]) == target:
                return [i, j]
    return []
