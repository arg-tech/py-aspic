

def check_preference(set1, set2, element_preferences):

    if len(set1) == 0:
        return False

    if len(set2) == 0:
        return True

    if element_preferences == []:
        return True

    for x in set1:
        x = str(x)
        for y in set2:
            y = str(y)

            if (x,y) in element_preferences:
                return True

    return False
