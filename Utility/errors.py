#------------------------------------------ ERROR MANAGER ------------------------------------------

def manage_error(e):
    err = "generic error"
    if e == 0:
        print("---SUCCESS---")
    else:
        if e == 1:
            err = "invalid user"
        if e == 2:
            err = "invalid sign"
        if e == 3:
            err = "invalid session"
        if e == 4:
            err = "expired opt"
        if e == 5:
            err = "invalid encrypt"
        if e == 6:
            err = "old data"
        print("ERROR: ", e, ":\t", err)
