EXPERIMENTAL_CONDITION = [
    {"DEBT": "1", "INTEREST": "2.5", "AMOUNT": "3000"},
    {"DEBT": "2", "INTEREST": "2.0", "AMOUNT": "8000"},
    {"DEBT": "3", "INTEREST": "3.5", "AMOUNT": "11000"},
    {"DEBT": "4", "INTEREST": "3.25", "AMOUNT": "13000"},
    {"DEBT": "5", "INTEREST": "3.75", "AMOUNT": "52000"},
    {"DEBT": "6", "INTEREST": "4.0", "AMOUNT": "60000"}
]
from copy import deepcopy
import sys

SAVING_INTEREST = .02
ROUNDS = [5000] * 25
ROUNDS[5] += 20000
ROUNDS[11] += 15000
ROUNDS[18] += 40000
SPECIAL_ROUNDS = [5, 11, 18]



def get_debts():
    debts = {}
    for condition in EXPERIMENTAL_CONDITION:
        debts[condition["DEBT"]] = condition["AMOUNT"]
    return debts

def get_ideal_allocation_of_money(i):
    amount = ROUNDS[i]
    ordered = sorted([deepcopy(condition) for condition in deepcopy(EXPERIMENTAL_CONDITION) if float(condition["AMOUNT"]) > 0],
                     key=lambda c: c["INTEREST"], reverse=True)
    optimum = []
    for condition in ordered:
        opt = {}
        temp = amount
        amount = amount - float(condition["AMOUNT"])
        if amount < 0:
            opt[condition["DEBT"]] = temp
            optimum.append(opt)
            break
        else:
            opt[condition["DEBT"]] = float(condition["AMOUNT"])
            optimum.append(opt)
    return optimum




def print_debts():
    print("{DEBT}{INTEREST}{AMOUNT}"
          "".format(DEBT="DEBT".ljust(15), INTEREST="INTEREST %".center(15), AMOUNT="$".rjust(15)))
    for condition in EXPERIMENTAL_CONDITION:
        if float(condition["AMOUNT"]) <= 0:
            continue
        print("{DEBT}{INTEREST}{AMOUNT}"
              "".format(DEBT=condition["DEBT"].ljust(15), INTEREST=condition["INTEREST"].center(15),
                        AMOUNT=condition["AMOUNT"].rjust(15)))


def _get_input():
    response = ""
    try:
        response = input().strip()
    except UnicodeDecodeError:
        print("Make sure that you set your keyboard to English")

    return response


def intro():
    print("Welcome to my attempt at recreating the Debt Management Game.\n"
          "Every round you will be given some money every year to try and pay off all the "
          "massive debt you have accumulated through your lavish lifestyle.\n"
          "If you decide not to use your full balance in any given year, the "
          "#remaining balance will increase by 2% and be added to the sub sequent year")
    ready = False
    while not ready:
        print("Are you ready to begin (Y/N) ??")
        r = _get_input()
        ready = True if r and r[0].upper() == "Y" else False

def update_debts():
    for debt in EXPERIMENTAL_CONDITION:
        amount = float(debt["AMOUNT"])
        if amount <= 0:
            continue
        interest_rate = float(debt["INTEREST"]) / 100
        amount = round(amount + (amount * interest_rate), 2)
        debt["AMOUNT"] = str(amount)


def update_balance_information(round_info, i):
    amount_allocated = 0
    for debt, amount in round_info.items():
        debt -= 1
        current_debt_amount = float(EXPERIMENTAL_CONDITION[debt]["AMOUNT"])
        current_debt_amount -= amount
        EXPERIMENTAL_CONDITION[debt]["AMOUNT"] = str(current_debt_amount)
        amount_allocated += amount

    remainder = ROUNDS[i] - amount_allocated
    if remainder and len(ROUNDS) < i+1:
        ROUNDS[i + 1] += (remainder + (remainder * SAVING_INTEREST))
    return


def get_special_round_message(i):
    return ""


def validate_answer(answer, i):
    parsed_answer = None

    try:
        parsed_answer = {int(val.split("=")[0]): val.split("=")[1] for val in answer.split()} or None
        alls = [all.upper() for all in parsed_answer.values()].count("ALL")
        if alls > 1:
            raise Exception
        if alls == 1:
            amount = ROUNDS[i]
            all_debt = -1
            for debt, am in parsed_answer.items():
                if am.upper() == "ALL":
                    all_debt = debt
                else:
                    amount -= float(am)
            parsed_answer[all_debt] = amount
        parsed_answer = {k: float(v) for k, v in parsed_answer.items()}
        if sum(parsed_answer.values()) > ROUNDS[i]:
            print("HEY !! That's more money than you have !! No stealing")
            parsed_answer = None
        if any([((float(EXPERIMENTAL_CONDITION[debt - 1]["AMOUNT"]) - amount) < -1) for debt, amount in parsed_answer.items()]):
            print("That's more than the debt is in total !!")
            parsed_answer = None
    except Exception as e:
        print("Hmm something's weird with your input..... try again")
        parsed_answer = None
        pass

    return parsed_answer


def double_check_answer(amount_allocated, i):
    print("So you would like to allocate your money as follows:")
    total_allocated = 0
    for debt, amount in amount_allocated.items():
        print("Debt {} -> ${}".format(debt, amount))
        total_allocated += amount
    print("Amount remaining in your account is ${}\n"
          "Is this correct (Y/N) ??".format(round(ROUNDS[i] - total_allocated), 2))
    r = _get_input()
    return True if r and r[0].upper() == "Y" else False


def get_round_input(i):
    if i in SPECIAL_ROUNDS:
        print(get_special_round_message(i))
    confirmed = False
    while not confirmed:
        print("ROUND {}".format(i + 1))
        print_debts()
        print("How would you like to allocate this years balance of ${}\n".format(round(ROUNDS[i], 2)))
        amount_allocated = None
        while not amount_allocated:
            print("Enter amount here:\t")
            amount_allocated = validate_answer(_get_input(), i)
        confirmed = double_check_answer(amount_allocated, i)
    print("Good Job ^^")
    return amount_allocated

def get_supoptimal_percentage(user_breakdown, optimal_breakdown, i):
    optimal = 0
    user_breakdown = deepcopy(user_breakdown)
    for dic_val in optimal_breakdown:
        debt, amount = list(dic_val.items())[0]
        user_spent = user_breakdown.pop(int(debt), 0)
        if user_spent:
            difference = amount - user_spent
            if difference > 0:
                optimal += user_spent
            else:
                optimal += amount

    return 100 - round((optimal / ROUNDS[i]) * 100, 3)

def validatate_args():
    _, name, with_money = sys.argv
    with_money = True if with_money and with_money[0].upper() == "F" else False
    assert len(name) > 2
    return name, with_money

def run_experiment():
    name, with_money = validatate_args()
    intro()
    sub_optimal_percentage = []
    debts = []
    for i in range(len(ROUNDS)):
        debts.append(get_debts())
        round_info = get_round_input(i)
        sub_optimal_percentage.append(get_supoptimal_percentage(round_info, get_ideal_allocation_of_money(i), i))
        update_balance_information(round_info, i)
        update_debts()
    print_debts()
    print("Sorry but you have just died in a car accident ....")
    print("You leave your remaining debt of ${} to your family".format(round(sum([float(condition["AMOUNT"]) for condition in EXPERIMENTAL_CONDITION])), 2))
    write_files(name)

def write_files():
    pass


if __name__ == "__main__":
    run_experiment()


