def twosum(numbers, targetnumber):
    for i in range(len(numbers)):
        for j in range((i + 1), len(numbers)):
            if (numbers[i] + numbers[j]) == targetnumber:
                return [i, j]
    return []
