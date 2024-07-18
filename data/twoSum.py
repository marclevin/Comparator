def twoSum(list, target):
    length = len(list)
    for i in range(length - 1):
        for j in range(i + 1, length):
            if list[i] + list[j] == target:
                new_list = i, j
                return list(new_list)
    return -1