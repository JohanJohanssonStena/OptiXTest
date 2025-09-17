#functions
def func(h = 'no input', n = 1):
    h = h.upper()
    if n < 10:
        for i in  range(0, n):
            print(h)
    else:
        print('you are too loud')
    print('done')
n = 7
a = 'hey'
func(a, n)