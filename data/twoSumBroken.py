def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range((i + 1), len(nums)):
            if helper_check(nums[i], nums[j], target):
                return [i, j]
    return []


def helper_check(num1, num2, other):
    return num1 + num2 == other
