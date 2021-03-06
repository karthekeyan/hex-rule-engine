from flask import Flask, render_template
app = Flask(__name__,static_url_path="/static")
from flask import jsonify
import os
import os.path
import sys
import json
import sklearn
import pickle
import pandas as pd
from flask import request
import requests


@app.route("/")
def template_test():
    print("hello")
    return render_template('initial.html')


@app.route("/rest/api/")
def api_call():
    q = request.args.get('q')
    print(q)
    value = fun(q)
    #value = json.loads(value)
    return (value)

def fun(q):
    choice = q
    #choice = "ALBDULA000048805"
    print(choice)
    #choice = "ALBDULA000048805"
    ##Packages
    import pandas as pd
    import os
    import csv
    #os.chdir("E:\\PoCs\\SE2")  ## have some library
    
    #current fund value
    #Equity_NAV = 10
    #Bond_NAV = 20
    
    #Read OIPA
    OIPA_data = pd.read_csv("OIPA.csv")
    
    #Filter the required data
    test_rec = OIPA_data.loc[(OIPA_data['Client_First_Name'] == choice ) | (OIPA_data['Client_Last_Name'] == choice) | (OIPA_data['Policy_Number'] == choice)  ] 
    predictors = ["Attained_age_at_Issue", "Income_per_Annum", "Credit_Score", "Risk_Appetite_Score", "SnP_500_Index_Score", "Social_Media_Score"]
    
    X_test = test_rec[predictors]
    #ML based model
    
    import pickle
    X_test = test_rec[predictors]
    filename = "finalized_model_rf.sav"
    loaded_model = pickle.load(open(filename, 'rb'))
    prediction = loaded_model.predict(X_test)
    if prediction == 1:
        category = "Safetynet"    
    else:
        category = "Aggressive"
    
    #assign the category to the financial guidance strategy
    test_rec["Financial_Guidance_Strategy"] = category
    
    #update to OIPA database
    OIPA_data['Financial_Guidance_Strategy'] = OIPA_data['Policy_Number'].map(test_rec.set_index('Policy_Number')['Financial_Guidance_Strategy']).fillna(OIPA_data['Financial_Guidance_Strategy'])
    OIPA_data.to_csv("OIPA.csv", index = False)
    
    #Generating a results report
    test_rec.to_csv("/tmp/results.csv", index = False)
   
    # Loading the fund values
    
    #Read current fund values
    csv_file = pd.read_csv("Current_Fund_Values1.csv")
    current_fund_values = csv_file.loc[(csv_file['Client_First_Name'] == choice ) | (csv_file['Client_Second_Name'] == choice) | (csv_file['Policy_Number'] == choice)  ] 


    Current_Investment_Cashvalue_equity = round(float(current_fund_values.Current_Investment_Cashvalue_equity.values),3)
    Current_Investment_Cashvalue_MM = round(float(current_fund_values.Current_Investment_Cashvalue_MM.values),3)
    Current_Investment_units_equity = round(float(current_fund_values.Current_Investment_units_equity.values),3)        
    Current_Investment_units_MM = round(float(current_fund_values.Current_Investment_units_MM.values),3)
    #Todays_Unit_Value = float(current_fund_values.Todays_Unit_Value.values)
    Equity_NAV = float(current_fund_values.Todays_Unit_Value_Eq.values)
    Bond_NAV = float(current_fund_values.Todays_Unit_Value_Bond.values)
    Current_Total_Cash_value = round((Current_Investment_Cashvalue_equity  + Current_Investment_Cashvalue_MM),3)
    Current_Equity_Percentage = round((Current_Investment_Cashvalue_equity/Current_Total_Cash_value)*100,3)
    Current_Bond_Percentage = round((Current_Investment_Cashvalue_MM/Current_Total_Cash_value)* 100,3)

    
    ## Recommendatiion calculation
    
    #if category == "Aggressive":
    if category == "Aggressive":
        total = Current_Investment_Cashvalue_equity + Current_Investment_Cashvalue_MM
        equity_share = (Current_Investment_Cashvalue_equity / total)*100
        money_market_share = (Current_Investment_Cashvalue_MM / total)*100
        predict_equity_percent = 90.0000
        predict_mm_percent = 10.0000
        difference_equity = predict_equity_percent - equity_share
        difference_mm = predict_mm_percent - money_market_share
        Recommeneded_Equity_Investment = total * 0.9
        Recommended_MM_Investment = total * 0.1
        After_Fund_Switch_Equity_Cash_Value = round(Recommeneded_Equity_Investment,3)
        After_Fund_Switch_MM_Cash_Value = round(Recommended_MM_Investment,3)
        Total_Recommended_Value = round((Recommeneded_Equity_Investment  + Recommended_MM_Investment),3)
        Amount_to_be_switched =  round((Current_Investment_Cashvalue_MM - Recommended_MM_Investment),3)
        Switchout_percentage = round(((Amount_to_be_switched/Current_Investment_Cashvalue_MM) * 100), 3)
        Switchout_units = round((Amount_to_be_switched / Bond_NAV),3)
        Switchin_percentage = 100.0
        Switchin_Amount = Amount_to_be_switched * 1   
        After_Fund_Switch_Equity_Units = round((Recommeneded_Equity_Investment / Equity_NAV),3)
        After_Fund_Switch_MM_Units = round((Recommended_MM_Investment / Bond_NAV),3)
    
    
           
    elif category == "Safetynet":
        total = Current_Investment_Cashvalue_equity + Current_Investment_Cashvalue_MM
        equity_share = (Current_Investment_Cashvalue_equity / total)*100
        money_market_share = (Current_Investment_Cashvalue_MM / total)*100
        predict_equity_percent = 40.0000
        predict_mm_percent = 60.0000
        difference_equity = predict_equity_percent - equity_share
        difference_mm = predict_mm_percent - money_market_share
        Recommeneded_Equity_Investment = total * 0.4
        Recommended_MM_Investment = total * 0.6
        Total_Recommended_Value = round((Recommeneded_Equity_Investment  + Recommended_MM_Investment),3)
        Amount_to_be_switched =  round((Current_Investment_Cashvalue_equity - Recommeneded_Equity_Investment),3)
        Switchout_percentage = round(((Amount_to_be_switched/Current_Investment_Cashvalue_equity) * 100), 3)
        Switchout_units = round((Amount_to_be_switched / Equity_NAV),3)
        Switchin_percentage = 100.0
        Switchin_Amount = Amount_to_be_switched * 1
        After_Fund_Switch_Equity_Cash_Value = round(Recommeneded_Equity_Investment,3)
        After_Fund_Switch_Equity_Units = round((Recommeneded_Equity_Investment / Equity_NAV),3)
        After_Fund_Switch_MM_Cash_Value = round(Recommended_MM_Investment,3)
        After_Fund_Switch_MM_Units = round((Recommended_MM_Investment / Bond_NAV),3)
        
    ## output values that needs to be passed via API
    
    Client_FName = (test_rec['Client_First_Name'].values)[0]
    Client_LName = (test_rec['Client_Last_Name'].values)[0]
    Client_PolNo = (test_rec['Policy_Number'].values)[0]
    Client_Age = int((test_rec['Attained_age_at_Issue'].values)[0])
    
                           
    
    Equity_fund_name = 'Alamere Equity Income'
    MM_fund_name = 'Alamere Money Market'
    
    #Before Fund Switch
    #Before_Fund_Switch_Equity_Cash_Value = Current_Investment_Cashvalue_equity
    #Before_Fund_Switch_Equity_Outstanding_units = Current_Investment_units_equity
    #Before_Fund_Switch_Equity_Percent_Split = (equity_share)
    #Before_Fund_Switch_MM_Cash_Value = Current_Investment_Cashvalue_MM
    #Before_Fund_Switch_MM_Outstanding_units = Current_Investment_units_MM
    #Before_Fund_Switch_MM_Percent_Split = (money_market_share)
    
    #Recommended Split
    #Recommended_Equity_Split = predict_equity_percent
    #Recommended_MM_Split = predict_mm_percent
    
    
    
    #After Fund Switch
    #After_Fund_Switch_Equity_Cash_Value = Recommeneded_Equity_Investment
    #After_Fund_Switch_Equity_Units = After_Fund_Switch_Equity_Cash_Value / Equity_NAV
    #After_Fund_Switch_MM_Cash_Value = Recommended_MM_Investment
    #After_Fund_Switch_MM_Units = After_Fund_Switch_MM_Cash_Value / Bond_NAV
    

    #val = {"ClientFirstName":Client_FName, "ClientLastName":Client_LName, "ClientPolicyNo":Client_PolNo,  "ClientAge":Client_Age, "ClientCategory": category, "EquityFundName":Equity_fund_name, "BondFundName":MM_fund_name,  "BeforeCashVal":Before_Fund_Switch_Equity_Cash_Value,"BeforeOutstanding":Before_Fund_Switch_Equity_Outstanding_units,"BeforePercentSplit":Before_Fund_Switch_Equity_Percent_Split,"BeforeMMCashVal":Before_Fund_Switch_MM_Cash_Value,"BeforeMMOutstanding":Before_Fund_Switch_MM_Outstanding_units,"BeforeMMPercentSplit":Before_Fund_Switch_MM_Percent_Split,"RecommendedEquitySplit":Recommended_Equity_Split,"RecommendedMM":Recommended_MM_Split,"AfterCashValue":After_Fund_Switch_Equity_Cash_Value,"AfterEquityUnits":After_Fund_Switch_Equity_Units,"AfterMMCashValue":After_Fund_Switch_MM_Cash_Value,"AfterMMEquityUnits":After_Fund_Switch_MM_Units, "EquitySwitchin":Equity_Switchin, "EquitySwitchout":Equity_Switchout,  "MMSwitchin":mm_Switchin, "MMSwitchout":mm_Switchout, "EquityNAV": Equity_NAV, "BondNAV": Bond_NAV, "EquitySwitchAmt": Equity_switch_amount, "BondSwitchAmt": mm_switch_amount }
    val = {"ClientFirstName":Client_FName, "ClientLastName":Client_LName, "ClientPolicyNo":Client_PolNo, 
           "ClientAge":Client_Age, "ClientCategory": category, "EquityFundName":Equity_fund_name, "BondFundName":MM_fund_name, 
           "BeforeCashVal":Current_Investment_Cashvalue_equity,"BeforeOutstanding":Current_Investment_units_equity,
           "BeforePercentSplit":Current_Equity_Percentage,"BeforeMMCashVal":Current_Investment_Cashvalue_MM,
           "BeforeMMOutstanding":Current_Investment_units_MM,"BeforeMMPercentSplit":Current_Bond_Percentage,
           "CurrentTotalCashValue": Current_Total_Cash_value, "EquityNAV": Equity_NAV, "BondNAV": Bond_NAV,
           "RecommendedEquitySplit":predict_equity_percent,"RecommendedMM":predict_mm_percent,
           "AfterCashValue":After_Fund_Switch_Equity_Cash_Value, "AfterMMCashValue":After_Fund_Switch_MM_Cash_Value,
           "TotalRecommValue":Total_Recommended_Value,  "AmtBeSwitched": Amount_to_be_switched, 
           "Switchoutpercent":Switchout_percentage, "SwitchoutUnits": Switchout_units, 
           "Switchinpercent":Switchin_percentage, "SwitchinAmount": Switchin_Amount,
           "AfterEquityUnits":After_Fund_Switch_Equity_Units,
           "AfterMMEquityUnits":After_Fund_Switch_MM_Units}
    
    return (json.dumps(val))
    
if __name__ == '__main__':
    
    port = int(os.environ.get("PORT", 5000))
    #app.run(ssl_context='adhoc')
    app.run(host='0.0.0.0', port=port)
    
    
