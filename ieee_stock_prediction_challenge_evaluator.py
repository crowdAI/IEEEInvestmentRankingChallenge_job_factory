import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import scipy.stats as stat

def calc_metrics(time_period, pred_df, actuals_df):
    
    #subset values for one time_chunk
    pred = pred_df.loc[pred_df['time_period'] == time_period,:]
    
    # rerank predictions from 1 to n for this time period to break ties
    # tied ranks are ranked in the order of observation (i.e [1,2,2,2,3] -> [1,2,3,4,5])
    # this ensures that the DCG is calculated consistently for all submissions
    pred['Rank_F6M'] = stat.rankdata(pred['Rank_F6M'],method= 'ordinal')
    
    #change column name before merging
    pred = pred.rename(columns={'Rank_F6M': 'Rank_F6M_pred'})
    
    #subset values for one time_period
    actuals = actuals_df.loc[actuals_df['time_period'] == time_period,:]
    
    # left join predictions onto actuals by index
    combined = actuals.merge(pred.loc[:,['index','Rank_F6M_pred']], on = 'index', how = 'left')
    
    #calculate spearman correlation
    spearman = stat.spearmanr(combined['Rank_F6M'],combined['Rank_F6M_pred'])[0]
    
    #calculate NDCG = DCG of Top 20% / Ideal DCG of Top 20%
    # subset top 20% predictions
    t20 = combined.loc[combined['Rank_F6M_pred'] <= np.nanpercentile(combined['Rank_F6M_pred'],20),:]
    t20['discount'] = np.amax(combined['Rank_F6M_pred'])/(np.amax(combined['Rank_F6M_pred'])-combined['Rank_F6M_pred'])
    t20['gain'] = t20['Norm_Ret_F6M']*t20['discount']
    DCG = np.sum(t20['gain'])
    
    #subset top 20% actuals
    i20 = combined.loc[combined['Rank_F6M'] <= np.nanpercentile(combined['Rank_F6M'],20),:]
    i20['discount'] = np.amax(combined['Rank_F6M'])/(np.amax(combined['Rank_F6M'])-combined['Rank_F6M'])
    i20['gain'] = i20['Norm_Ret_F6M']*i20['discount']
    IDCG = np.sum(i20['gain'])
    
    NDCG = DCG/IDCG
    
    # return time_period, spearman correlation, NDCG
    return(pd.DataFrame([(time_period,spearman,NDCG)],columns = ['time_period','spearman','NDCG']))


class IEEEStockPredictionChallengeEvaluator:
    def __init__(self, answer_file_path):
        self.answer_file_path = answer_file_path
        
    def _evaluate(self, submission_file_path):
        submission = pd.read_csv(submission_file_path)
        
        # read in actuals .csv --- Is this the right way to reference?
        actuals = pd.read_csv(self.answer_file_path)

        # unique time periods to use in the for loop
        time_periods = np.unique(actuals['time_period'])
        time_periods = np.setdiff1d(time_periods,['2016_2','2017_1'])

        # apply the calc_metrics function to each time period and store the results in a data frame
        results = pd.DataFrame(columns=['time_period','spearman','NDCG'])
        for time_period in time_periods:
            results = results.append(calc_metrics(time_period, submission, actuals))

        # rename the columns and reduce the number of decimal places shown
        results.iloc[:,1:2] = np.round(results.iloc[:,1:2],decimals=5)

        _result_object = {
            "score": np.mean(results['spearman']),
            "score_secondary" : np.mean(results['NDCG'])
        }
        return _result_object

if __name__ == "__main__":
    evaluator = IEEEStockPredictionChallengeEvaluator("data/ground_truth_corrected.csv")
    print(evaluator._evaluate("data/sample_submission.csv"))
