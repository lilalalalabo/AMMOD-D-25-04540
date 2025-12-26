import numpy as np
import pandas as pd

# ============ 数据输入 ============
advance_dist = np.array([
    [10, 7, 5, 3, 3],      # 计划第1年购买 [不提前, 提前1年, 提前2年, 提前3年, 无穷提前]
    [15, 2, 6, 1, 1],      # 计划第2年购买
    [14, 5, 2, 4, 2],      # 计划第3年购买
    [9, 3, 3, 1, 4],       # 计划第4年购买
    [17, 6, 2, 8, 5]       # 计划第5年购买
])

delay_dist = np.array([
    [12, 5, 5, 3, 3],      # 计划第1年购买
    [11, 5, 4, 1, 4],      # 计划第2年购买
    [12, 8, 5, 1, 1],      # 计划第3年购买
    [9, 3, 3, 1, 4],       # 计划第4年购买
    [11, 8, 2, 5, 12]      # 计划第5年购买
])

# 倾向比例和观望比例
preference_ratios = np.array([1.0, 0.777777778, 0.7, 0.4, 0.352941176])
neutral_ratios = np.array([0.0, 0.222222222, 0.3, 0.6, 0.647058824])

# 每年计划购买的总人数
planned_total = np.sum(advance_dist, axis=1)

print("基础信息:")
print(f"每年计划购买总人数: {list(planned_total)}")
print("\n购买比例:")
for i in range(5):
    print(f"第{i+1}年: 倾向型={preference_ratios[i]:.4f}, 观望型={neutral_ratios[i]:.4f}")

# ============ 辅助函数 ============
def round_purchases(purchases_array):
    """四舍五入取整"""
    return np.round(purchases_array).astype(int)

# ============ 情景模拟 ============
years = 5
initial_ownership = 60
all_scenarios_results = []

# 1. 中性事件情景
print("\n" + "="*70)
print("1. 中性事件情景（基线）")
print("="*70)

for event_year in range(1, years+1):
    new_purchases = np.zeros(years, dtype=float)
    
    # 所有年份都按正常比例购买：倾向型100% + 观望型50%
    for plan_year in range(1, years+1):
        plan_idx = plan_year - 1
        total = planned_total[plan_idx]
        pref_ratio = preference_ratios[plan_idx]
        neu_ratio = neutral_ratios[plan_idx]
        purchasers = total * (pref_ratio + neu_ratio * 0.5)
        new_purchases[plan_year-1] += purchasers
    
    new_purchases = round_purchases(new_purchases)
    
    # 计算累计保有量
    cumulative = initial_ownership
    cumulative_ownership = []
    for i in range(years):
        cumulative += new_purchases[i]
        cumulative_ownership.append(cumulative)
    
    scenario_name = f"Neutral_Year{event_year}"
    all_scenarios_results.append({
        'scenario': scenario_name,
        'event_type': 'Neutral',
        'event_year': event_year,
        'new_purchases': new_purchases.copy(),
        'cumulative': np.array(cumulative_ownership)
    })
    
    if event_year == 1:
        print(f"中性事件基准:")
        print(f"  新增购买: {new_purchases}")
        print(f"  累计保有: {cumulative_ownership}")

# 2. 积极事件情景 - 修正无穷提前逻辑
print("\n" + "="*70)
print("2. 积极事件情景（修正无穷提前）")
print("="*70)

for event_year in range(1, years+1):
    new_purchases = np.zeros(years, dtype=float)
    
    # 处理所有计划购买年份
    for plan_year in range(1, years+1):
        plan_idx = plan_year - 1
        total = planned_total[plan_idx]
        pref_ratio = preference_ratios[plan_idx]
        neu_ratio = neutral_ratios[plan_idx]
        
        if plan_year < event_year:
            # 事件发生前的年份：按正常比例购买
            purchasers = total * (pref_ratio + neu_ratio * 0.5)
            new_purchases[plan_year-1] += purchasers
            
        elif plan_year == event_year:
            # 事件发生年份：所有计划这一年购买的人都购买（100%）
            new_purchases[event_year-1] += total
            
        else:  # plan_year > event_year
            # 事件发生后的年份：
            # 1. 处理提前购买（包括无穷提前）
            # 2. 剩余的人在原计划年份按新比例购买（中立系数从0.5变为1）
            
            # 初始化剩余人数
            remaining_people = total
            
            # 处理所有提前购买情况
            for t in range(5):  # t=0,1,2,3,4
                num_people = advance_dist[plan_idx, t]
                
                if t == 0:  # 不提前
                    # 在原计划年份购买
                    pass
                    
                elif t == 4:  # 无穷提前
                    # 关键修正：一旦出现积极事件，无穷提前的人立即购买
                    new_purchases[event_year-1] += num_people  # 在事件年购买
                    remaining_people -= num_people
                    
                else:  # t=1,2,3年提前
                    if event_year >= plan_year - t:
                        # 满足提前条件，在事件年购买
                        new_purchases[event_year-1] += num_people
                        remaining_people -= num_people
            
            # 剩余的人（不提前的人）在原计划年份购买
            # 注意：积极事件发生后，中立系数从0.5变为1
            purchasers = remaining_people * (pref_ratio + neu_ratio * 1.0)
            new_purchases[plan_year-1] += purchasers
    
    new_purchases = round_purchases(new_purchases)
    
    # 计算累计保有量
    cumulative = initial_ownership
    cumulative_ownership = []
    for i in range(years):
        cumulative += new_purchases[i]
        cumulative_ownership.append(cumulative)
    
    scenario_name = f"Positive_Year{event_year}"
    all_scenarios_results.append({
        'scenario': scenario_name,
        'event_type': 'Positive',
        'event_year': event_year,
        'new_purchases': new_purchases.copy(),
        'cumulative': np.array(cumulative_ownership)
    })
    
    print(f"\nPositive_Year{event_year}:")
    print(f"  新增购买: {new_purchases}")
    print(f"  累计保有: {cumulative_ownership}")
    
    # 验证积极事件第1年
    if event_year == 1:
        print(f"  验证第1年购买量: {new_purchases[0]}")
        # 手动计算验证
        manual_total = 0
        # 第1年本身
        manual_total += planned_total[0]
        # 第2-5年提前到第1年的人
        for plan_year in [2, 3, 4, 5]:
            plan_idx = plan_year - 1
            for t in range(5):
                if t == 0:
                    continue  # 不提前
                elif t == 4:  # 无穷提前
                    manual_total += advance_dist[plan_idx, t]
                else:  # t=1,2,3
                    if 1 >= plan_year - t:
                        manual_total += advance_dist[plan_idx, t]
        print(f"  手动计算验证: {manual_total}")

# 3. 消极事件情景
print("\n" + "="*70)
print("3. 消极事件情景")
print("="*70)

for event_year in range(1, years+1):
    new_purchases = np.zeros(years, dtype=float)
    
    for plan_year in range(1, years+1):
        plan_idx = plan_year - 1
        total = planned_total[plan_idx]
        pref_ratio = preference_ratios[plan_idx]
        neu_ratio = neutral_ratios[plan_idx]
        
        if plan_year < event_year:
            # 事件发生前的年份：按正常比例购买
            purchasers = total * (pref_ratio + neu_ratio * 0.5)
            new_purchases[plan_year-1] += purchasers
            
        elif plan_year == event_year:
            # 事件发生年份：按推迟分布处理
            
            # 处理不推迟的人（t=0）
            num_no_delay = delay_dist[plan_idx, 0]
            # 只有倾向型购买
            purchasers = num_no_delay * pref_ratio
            new_purchases[event_year-1] += purchasers
            
            # 处理推迟的人（t=1,2,3）
            for t in range(1, 4):
                num_delay = delay_dist[plan_idx, t]
                if num_delay > 0:
                    delay_year = event_year + t
                    if delay_year <= years:
                        # 只有倾向型会推迟购买
                        new_purchases[delay_year-1] += num_delay * pref_ratio
            
            # 无穷推迟的人（t=4）取消购买 - 不处理
        
        else:  # plan_year > event_year
            # 事件发生后的年份：只有倾向型购买（中立系数从0.5变为0）
            purchasers = total * pref_ratio
            new_purchases[plan_year-1] += purchasers
    
    new_purchases = round_purchases(new_purchases)
    
    # 计算累计保有量
    cumulative = initial_ownership
    cumulative_ownership = []
    for i in range(years):
        cumulative += new_purchases[i]
        cumulative_ownership.append(cumulative)
    
    scenario_name = f"Negative_Year{event_year}"
    all_scenarios_results.append({
        'scenario': scenario_name,
        'event_type': 'Negative',
        'event_year': event_year,
        'new_purchases': new_purchases.copy(),
        'cumulative': np.array(cumulative_ownership)
    })
    
    print(f"\nNegative_Year{event_year}:")
    print(f"  新增购买: {new_purchases}")
    print(f"  累计保有: {cumulative_ownership}")

# ============ 汇总结果 ============
print("\n" + "="*70)
print("15种情景汇总")
print("="*70)

results_table = []
for scenario in all_scenarios_results:
    row = [scenario['scenario']]
    row.extend(scenario['cumulative'])
    results_table.append(row)

df_results = pd.DataFrame(results_table, 
                          columns=['Scenario', 'Year1', 'Year2', 'Year3', 'Year4', 'Year5'])

# 排序
df_results['EventType'] = df_results['Scenario'].apply(lambda x: x.split('_')[0])
df_results['EventYear'] = df_results['Scenario'].apply(lambda x: int(x.split('_')[1].replace('Year', '')))
df_results = df_results.sort_values(['EventType', 'EventYear'])

print(df_results[['Scenario', 'Year1', 'Year2', 'Year3', 'Year4', 'Year5']].to_string(index=False))

# ============ 计算统计量 ============
print("\n" + "="*70)
print("统计量汇总")
print("="*70)

stats_data = []
for year_idx in range(years):
    year_col = f'Year{year_idx+1}'
    values = df_results[year_col].values
    
    stats_data.append({
        'Year': year_idx+1,
        'Mean': np.mean(values),
        'Min': np.min(values),
        'Max': np.max(values),
        'Std': np.std(values)
    })

df_stats = pd.DataFrame(stats_data)
print(df_stats.to_string(index=False))

# ============ 输出模糊集参数 ============
print("\n" + "="*70)
print("模糊集参数（μ, v̲, v̄, σ）")
print("="*70)
for idx, row in df_stats.iterrows():
    print(f"Year {int(row['Year'])}: μ={row['Mean']:.2f}, v̲={row['Min']:.2f}, v̄={row['Max']:.2f}, σ={row['Std']:.2f}")

# ============ 保存结果 ============
df_results.to_csv('ev_ownership_scenarios_final_corrected_v2.csv', index=False)
df_stats.to_csv('ev_ownership_statistics_final_corrected_v2.csv', index=False)
print("\n结果已保存至文件。")