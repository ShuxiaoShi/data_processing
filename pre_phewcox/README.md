## 任务描述：
1. 先合并after_trans.csv和after_trans_date.csv，date文件里的diseases变量就是时间，直接合并就行，顺序是一致的
2. 把after_trans里疾病的编码改成三位，比如上面的N201，变成N20，字母也算一位，然后相同的id去重，留下对应的date最早的那个。
3. 再合并baseline_date.csv，用里面的变量new_nutrition_date2，然后用之前疾病的date减去new_nutrition_date2，负数都删掉 
4. 然后就可以转置成上面那一行例子，得这个病就是1，没得就是0，1的lenth就是after_trans_date-new_nutrition_date2，0的lenth就是用，cencore_date.csv里面的cencor_date-new_nutrition_date2
