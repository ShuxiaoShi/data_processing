import numpy as np
import pandas as pd
import argparse
import time

# head -n 100 data/baseline_date.csv > data_test/baseline_date.csv
# head -n 100 data/after_trans.csv > data_test/after_trans.csv
# head -n 100 data/after_trans_date.csv > data_test/after_trans_date.csv
# head -n 100 data/cencor_date.csv > data_test/cencor_date.csv


def load_table(fname):
    data = pd.read_csv(fname, index_col=False, dtype=str)
    return data

# def merge_two_table(tb1, tb2):
    # return pd.merge(tb1, tb2)

def step1(file1, file2):
    # ref: https://blog.csdn.net/weixin_43593330/article/details/100529293
    tb1 = load_table(file1)
    tb1 = tb1.drop(labels="icd", axis=1)
    tb2 = load_table(file2)
    tb2 = tb2.drop(labels=["icd", "n_eid"], axis=1)
    tb2.rename(columns={"disease": "disease_date"}, inplace=True)
    tb1_2 = pd.concat([tb1, tb2], axis=1)
    return tb1_2
    # print(tb1_2)

def step2(tb, ):
    # ref: https://www.yii666.com/blog/35201.html
    def clip3(v):
        return v[:3]
    tb["disease"] = tb["disease"].map(clip3)
    tb = tb.sort_values(by=["n_eid", "disease", "disease_date"], )
    # print(tb)
    tb = tb.drop_duplicates(subset=["n_eid", "disease"], keep='first')
    # tb = tb.drop_duplicates(subset=["disease"], keep='first')
    # print(tb)
    return tb

def step3(tb, file3):
    tb_bsl = pd.read_csv(file3, index_col=0, dtype=str)
    merge_tb = pd.merge(tb, tb_bsl, how="left", on="n_eid", validate="m:1")
    merge_tb["disease_date"] = pd.to_numeric(merge_tb["disease_date"])
    merge_tb["new_nutrition_date2"] = pd.to_numeric(merge_tb["new_nutrition_date2"])
    merge_tb["date_diff"] = merge_tb["disease_date"] - merge_tb["new_nutrition_date2"]
    merge_tb.drop(merge_tb[merge_tb.date_diff < 0].index, inplace=True)
    print(f"remove date_diff < 0: {tb.shape[0]} -> {merge_tb.shape[0]}")
    return merge_tb, tb_bsl

def step4(tb, tb_bsl, file4, args):
    # print(tb[~tb.isna().any(axis=1)])

    tb_censor = pd.read_csv(file4, index_col=0, dtype=str)
    tb_censor["cencer_date"] = pd.to_datetime(tb_censor["cencer_date"])

    # get sencor date and convert to sas-day value
    # ref: https://documentation.sas.com/doc/en/vdmmlcdc/8.1/ds2pg/n02zpqz4j5u3j9n1t0i95ncqep5g.htm
    # NOTE: SAS date value is from 1960-1-1, unix date is from 1970-1-1
    tb_censor["cencer_date"] = tb_censor["cencer_date"] - pd.to_datetime('1960-01-01')
    tb_censor["cencer_date"] = tb_censor["cencer_date"].map(lambda x: x.days)
    tb = pd.merge(tb, tb_censor, how="left", on="n_eid", validate="m:1")
    # get a diff time for nan
    tb_censor_fillna = pd.merge(tb_bsl, tb_censor, how="inner", on="n_eid", validate="1:1")
    tb_censor_fillna["date_diff"] = tb_censor_fillna["cencer_date"] - pd.to_numeric(tb_censor_fillna["new_nutrition_date2"])
    tb_censor_fillna.set_index("n_eid", inplace=True)

    if len(tb_bsl[tb_bsl.isna().any(axis=1)]) > 0:
        print("warning: tb_bsl have nan value", len(tb_bsl[tb_bsl.isna().any(axis=1)]))
    
    tb = tb[~tb.isna().any(axis=1)]
    tb_censor_fillna = tb_censor_fillna[~tb_censor_fillna.isna().any(axis=1)]
    if args.round2day:
        tb["date_diff"] = tb["date_diff"].round(0).astype(int)
        tb_censor_fillna["date_diff"] = tb_censor_fillna["date_diff"].round(0).astype(int)

    # get pivot table
    tb2 = tb.pivot(index='n_eid', columns='disease', values='date_diff')
    
    tb_exist = tb2.notna()
    tb_exist = tb_exist.apply(lambda x: x.astype('Int8'))
    tb_filled = tb2.apply(lambda col: col.fillna(tb_censor_fillna["date_diff"])).astype(int)

    # merge two table and reindex
    tb_all = pd.merge(tb_exist, tb_filled, on="n_eid", suffixes=("", "_len"))
    tb_all = tb_all.reindex(sorted(tb_all.columns), axis=1)

    # print(tb_all)
    return tb_all

if __name__ == "__main__":
    # s1 = pd.to_datetime('1970-01-01')
    # s2 = pd.to_datetime('1960-01-01')
    # print(s2 + pd.Timedelta(18985, unit="D"))

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--clip3', action="store_true", help="only keep 3 of desease name")
    parser.add_argument('--round2day', action="store_true", help="only keep day time")
    parser.add_argument('--out', type=str, default="out.csv")
    parser.add_argument("--input_path", type=str, default="./data/")
    args = parser.parse_args()

    dpath = args.input_path

    file1 = dpath+"after_trans.csv"
    file2 = dpath+"after_trans_date.csv"
    file3 = dpath+"baseline_date.csv"
    file4 = dpath+"cencor_date.csv"

    print("running args:", args)
    print("Step1 -----")
    tb = step1(file1, file2)
    print("Step2 -----")
    if args.clip3:
        tb = step2(tb)
    print("Step3 -----")
    tb, tb_bsl = step3(tb, file3)
    print("Step4 -----")
    tb_all = step4(tb, tb_bsl, file4, args)
    print(f"dump results to {args.out}")
    tb_all.to_csv(args.out)
    



# data = data.stack()
# data = data.reset_index(level=1)
# data.columns = ["icd", "disease"]
# # data["disease"] = data["disease"].astype(str)

        
# # print(data.rows())
# data['icd']=data["icd"].apply(modify)

# data["disease"] = data.apply(support_icd10, axis=1)
# data.to_csv("icd_ffq.csv:")