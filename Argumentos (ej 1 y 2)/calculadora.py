import getopt, sys

def calculadora():
    operator = None
    num1 = None
    num2 = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:n:m:", ["operator","num1","num2"])
    except getopt.GetoptError as err:
        print(err)
        opts = []

    for opt, arg in opts:
        if opt in ['-o']:
            operator = arg
        elif opt in ['-n']:
            num1 = arg
        elif opt in ['-m']:
            num2 = arg

    result = eval('{} {} {}'.format(num1,operator,num2))
    print('{} {} {} = {}'.format(num1,operator,num2,result))

calculadora()