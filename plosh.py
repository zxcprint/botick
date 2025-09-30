print("quick test: What orientation r u?")
name = input("Your name? ")

print("your sex? ")
sex = input("female/male: ").lower()
if sex == "female":
    print("do you love girls?")
else:
    print("че нахуй?")
love = input ("yes/no: ").lower()
if love == "yes":
    print("WOW! congratuations, " + name + "! you are lesbian!")
elif love == "no":
    print("oh no! you are hetero:(")
