print("quick pregnancy test:")
input("your sex: ")
input("Day of your last menstruation cycle: ")
sex = input("Do you have sex partner: ").lower()
if sex == "yes":
        gender = input("it's woman or man: ").lower()
        if gender == "woman":
            print("Congrats! You can't have childrens!")
else:
    print("suka tvar")