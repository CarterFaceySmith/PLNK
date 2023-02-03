# import src.rebalance as rebalance, src.backtest as bktest, src.config as config

def main():
    print("Welcome back, Sir.")
    mode = input("Select your trading mode:\n1. Backtest\n2. Rebalance\n3. Liquidate portfolio\n4. Check stats\n5. Add ticker\n6. Switch portfolio preset\n7. Exit\n> ")
    match mode:
        case "1":
            #Backtest
            pass
        case '2':
            #Rebalance
            pass
        case '3':
            #Liquidate
            pass
        case '4':
            #Check stats
            pass
        case '5':
            #Add ticker
            pass
        case '6':
            #Switch portfolio preset
            pass
        case '7':
            #Default exit
            exit(0)
        case _:
            #Error catch exit
            exit(1)

if __name__ == '__main__':
    main()