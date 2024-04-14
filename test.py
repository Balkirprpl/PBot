try:
    # code inside the try block which can cause an exception
    # taking the input ‘name’ from the user
        name  = input('Enter the name of the user ')
        # writing the different exception class to catch/ handle the exception
except EOFError:
        print('Hello user it is EOF exception, please enter something and run me again')
except KeyboardInterrupt:
        z = input("input:")
        print('Hello user you have pressed ctrl-c button. and input', z)
        # If both the above exception class does not match, else part will get executed
else:
        print('Hello user there is some format error')
