def twoSum(list, target):
    length = len(list)
    for i in range(1, length):  # Start from 1 instead of 0
        for j in range(i):  # Go up to, but not including, i
            if list[i] + list[j] == target:
                new_list = i, j
                return list(new_list)
    return -1
