import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dataset_names = []
dataset_data = []
folder_path = 'dataset'
size = 0

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if os.path.isfile(os.path.join(folder_path, file)):
            if file.endswith('NS.csv'):

                #file = "dataset/" + file
                #print(file)
                df = pd.read_csv('dataset/'+file)
                file = file[0:-7]
                dataset_names.append(file)
                dataset_data.append(df)
                size = size+1
else:
    print("the folder ", folder_path, " does not exist")

dataset_dict = {}
for name, value in zip(dataset_names, dataset_data):
    dataset_dict[name] = [[value]]
# print(dataset_dict)

# HISTORICAL PRICE PERFORMANCE ##############################################################
# print(dataset_dict)
for i in range(0, size):
    final_acp = dataset_data[i]['Adj Close'].iloc[-1]
    initial_acp = dataset_data[i]['Adj Close'].iloc[0]
    annual_return = '{:.3f}'.format(((final_acp - initial_acp)/initial_acp)*100)
    # dataset_dict[dataset_names[i]][0](annual_return)
    (dataset_dict[dataset_names[i]]).append(annual_return)
#
# for i in range(0, size):
# print((dataset_dict[dataset_names[i]])[1])
# for i in range(0, size):
#     print(dataset_dict[dataset_names[i]])
# print(dataset_dict)
# print(dataset_names)

# test = dataset_names[:]
#
# for i in range(0, size):
#     swapped = False
#     for j in range(0, size- i - 1):
#         if (dataset_dict[dataset_names[i]])[1] > (dataset_dict[dataset_names[i+1]])[1]:
#             test[j], test[j+1] = test[j+1], test[j]
#             swapped = True
#         if not swapped:
#             break
# # print(test)
# for i in range(0, size):
#     print(test[i])

# MOVING AVERAGES (SMA & EMA)###################################################

def SMA_EMA(df_A_name, df_B_name):

    df_A = pd.read_csv('dataset/' + df_A_name + '.NS.csv')
    df_B = pd.read_csv('dataset/' + df_B_name + '.NS.csv')

    # Define moving average window sizes
    short_window = 50  # Short-term window
    long_window = 200  # Long-term window

    # Calculate SMA and EMA for Stock A
    df_A['SMA_A'] = df_A['Adj Close'].rolling(window=short_window).mean()
    df_A['EMA_A'] = df_A['Adj Close'].ewm(span=short_window, adjust=False).mean()

    # Calculate SMA and EMA for Stock B
    df_B['SMA_B'] = df_B['Adj Close'].rolling(window=short_window).mean()
    df_B['EMA_B'] = df_B['Adj Close'].ewm(span=short_window, adjust=False).mean()

    # Calculate the MACD & Signal for Stock A
    df_A['MACD_A'] = df_A['EMA_A'] - df_A['EMA_A'].rolling(window=long_window).mean()
    df_A['Signal_A'] = df_A['MACD_A'].ewm(span=9, adjust=False).mean()

    # Calculate the MACD & Signal for Stock B
    df_B['MACD_B'] = df_B['EMA_B'] - df_B['EMA_B'].rolling(window=long_window).mean()
    df_B['Signal_B'] = df_B['MACD_B'].ewm(span=9, adjust=False).mean()

    # Calculate Golden Crosses and Death Crosses for Stock A
    df_A['Golden_Cross_A'] = (df_A['SMA_A'] > df_A['SMA_A'].shift(1)) & (df_B['SMA_B'] < df_B['SMA_B'].shift(1))
    df_A['Death_Cross_A'] = (df_A['SMA_A'] < df_A['SMA_A'].shift(1)) & (df_B['SMA_B'] > df_B['SMA_B'].shift(1))

    # Calculate Golden Crosses and Death Crosses for Stock B
    df_B['Golden_Cross_B'] = (df_B['SMA_B'] > df_B['SMA_B'].shift(1)) & (df_A['SMA_A'] < df_A['SMA_A'].shift(1))
    df_B['Death_Cross_B'] = (df_B['SMA_B'] < df_B['SMA_B'].shift(1)) & (df_A['SMA_A'] > df_A['SMA_A'].shift(1))

    stock_A_metrics = {
        'Golden_Crosses': df_A['Golden_Cross_A'].sum(),
        'Death_Crosses': df_A['Death_Cross_A'].sum(),
        'Last_MACD': df_A['MACD_A'].iloc[-1],
        'Last_Signal': df_A['Signal_A'].iloc[-1],
    }

    stock_B_metrics = {
        'Golden_Crosses': df_B['Golden_Cross_B'].sum(),
        'Death_Crosses': df_B['Death_Cross_B'].sum(),
        'Last_MACD': df_B['MACD_B'].iloc[-1],
        'Last_Signal': df_B['Signal_B'].iloc[-1],
    }

    def four_inner_factors(stock_A, stock_B):
        golden_cross_bin = 0
        death_cross_bin = 0
        last_MACD_bin = 0
        last_signal_bin = 0

        if stock_A['Golden_Crosses'] > stock_B['Golden_Crosses']:
            golden_cross_bin = 1
        if stock_A['Death_Crosses'] < stock_B['Death_Crosses']:
            death_cross_bin = 1
        if stock_A['Last_MACD'] > stock_B['Last_MACD']:
            last_MACD_bin = 1
        if stock_A['Last_Signal'] > stock_B['Last_Signal']:
            last_signal_bin = 1

        stock_valuation = ((golden_cross_bin * 0.2 * (stock_A['Golden_Crosses'] - stock_B['Golden_Crosses']))
                           + (death_cross_bin * 0.2 * (1 / (stock_A['Death_Crosses'] - stock_B['Death_Crosses'])))
                           + (last_MACD_bin * 0.3 * (stock_A['Last_MACD'] - stock_B['Last_MACD']))
                           + (last_signal_bin * 0.3 * (stock_A['Last_Signal'] - stock_B['Last_Signal'])))

        # print(golden_cross_bin, death_cross_bin, last_MACD_bin, last_signal_bin)
        return stock_valuation

    stock_A_valuation = four_inner_factors(stock_A_metrics, stock_B_metrics)
    stock_B_valuation = four_inner_factors(stock_B_metrics, stock_A_metrics)

    # print("A = ", stock_A_valuation)
    # print("B = ", stock_B_valuation)
    if (stock_A_valuation > stock_B_valuation):
        return True
    else:
        return False

SMA_EMA_order = dataset_names[:]
for i in range(0, size):
    swapped = False
    for j in range(0, size - i - 1):
        df_A_name = SMA_EMA_order[j]
        df_B_name = SMA_EMA_order[j+1]

        if SMA_EMA(df_A_name, df_B_name):
            SMA_EMA_order[j], SMA_EMA_order[j+1] = SMA_EMA_order[j+1], SMA_EMA_order[j]
            swapped = True
        if not swapped:
            break

for i in SMA_EMA_order:
    (dataset_dict[i]).append(SMA_EMA_order.index(i))

# print(dataset_dict)

#TRADING VOLUMES ##############################################################

def OBV(A_file, B_file):
    df_test_1 = pd.read_csv('dataset/' + A_file +'.NS.csv')
    df_test_2 = pd.read_csv('dataset/' + B_file +'.NS.csv')

    df_test_1['Daily_OBV_1'] = 0
    df_test_2['Daily_OBV_2'] = 0

    df_test_1.loc[df_test_1['Adj Close'] > df_test_1['Adj Close'].shift(1), 'Daily_OBV_1'] = df_test_1['Volume']
    df_test_1.loc[df_test_1['Adj Close'] < df_test_1['Adj Close'].shift(1), 'Daily_OBV_1'] = -df_test_1['Volume']
    df_test_1['OBV_1'] = df_test_1['Daily_OBV_1'].cumsum()

    df_test_2.loc[df_test_2['Adj Close'] > df_test_2['Adj Close'].shift(1), 'Daily_OBV_2'] = df_test_2['Volume']
    df_test_2.loc[df_test_2['Adj Close'] < df_test_2['Adj Close'].shift(1), 'Daily_OBV_2'] = -df_test_2['Volume']
    df_test_2['OBV_2'] = df_test_2['Daily_OBV_2'].cumsum()

    cumulative_obv_1 = df_test_1['OBV_1'].iloc[-1]
    cumulative_obv_2 = df_test_2['OBV_2'].iloc[-1]

    if cumulative_obv_1 > cumulative_obv_2:
        return True
    else:
        return False

volume_order = dataset_names[:]
for i in range(0, size):
    swapped = False
    for j in range(0, size - i - 1):
        A_name = volume_order[j]
        B_name = volume_order[j + 1]
        if OBV(A_name, B_name):
            volume_order[j], volume_order[j + 1] = volume_order[j + 1], volume_order[j]
            swapped = True
        if not swapped:
            break
# for i in range(0, size):
#     print(volume_order[i])
for i in volume_order:
    (dataset_dict[i]).append(volume_order.index(i))


##STOCHIASTIC OSCILLATOR ##################################



def stochastic_oscillator(A_file, B_file):

    df_test_1 = pd.read_csv('dataset/' + A_file +'.NS.csv')
    df_test_2 = pd.read_csv('dataset/' + B_file +'.NS.csv')

    period = 14

    df_test_1['Lowest_Low_1'] = df_test_1['Low'].rolling(window = period).min()
    df_test_1['Highest_High_1'] = df_test_1['High'].rolling(window = period).max()
    df_test_1['%K_stock_1'] = ((df_test_1['Adj Close']))

    df_test_2['Lowest_Low_2'] = df_test_2['Low'].rolling(window=period).min()
    df_test_2['Highest_High_2'] = df_test_2['High'].rolling(window=period).max()
    df_test_2['%K_stock_2'] = ((df_test_2['Adj Close']))

    # plt.figure(figsize = (12, 6))
    # plt.plot(df_test_1['Date'], df_test_1['%K_stock_1'], color = 'blue')
    # plt.plot(df_test_2['Date'], df_test_2['%K_stock_2'], color = 'green')
    # plt.xlabel('Date')
    # plt.ylabel('%K Value')
    # plt.title('test')
    # plt.show()

    average_k_1 = df_test_1['%K_stock_1'].mean()
    average_k_2 = df_test_2['%K_stock_2'].mean()

    if average_k_1 > average_k_2:
        return True
    else:
        return False

stochastic_order = dataset_names[:]
for i in range(0, size):
    for j in range(0, size - i - 1):
        A_name = stochastic_order[j]
        B_name = stochastic_order[j+1]
        if stochastic_oscillator(A_name, B_name):
            stochastic_order[j], stochastic_order[j+1] = stochastic_order[j+1], stochastic_order[j]
            swapped = True
        if not swapped:
            break

# for i in range(0, size):
#     print(stochastic_order[i])
for i in volume_order:
    (dataset_dict[i]).append(stochastic_order.index(i))


print(dataset_dict)



