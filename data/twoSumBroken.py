def twosum(numbers, target):
    for i in range(len(numbers)):
        for j in range(i, len(numbers)):
            if (numbers[i] + numbers[j]) == target:
                return [i, j + 1]
    return [1]
