print("calculate")
try:    
    num1 = float(input("select first number: "))
    num2 = float(input("select second number: "))
except ValueError:
    print("oshipka")
    exit()
operation = input("chto sdelat (+, -, *, /): ")
if operation == "+":
    result = num1 + num2
elif operation == "-":
    result = num1 - num2
elif operation == "*":
    result = num1 * num2
elif operation == "/":
    if num2 == 0:
        print("na nol ne delat")
        exit()
    result = num1 / num2
else:
    print("oh no...")
    exit()
print("your number: ", result)