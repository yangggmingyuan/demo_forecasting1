"""库存策略计算工具模块"""
import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Dict, Union

def calculate_inventory_policy(
    daily_demand: float,
    daily_std_dev: float,
    lead_time_days: int,
    service_level: float = 0.95,
    review_period_days: int = 30
) -> Dict[str, float]:
    """
    计算库存策略参数 (SS, ROP, Max Stock)
    """
    # 计算Z值 (正态分布分位数)
    z_score = norm.ppf(service_level)
    
    # 1. 安全库存 (Safety Stock)
    # 公式: SS = Z * daily_std_dev * sqrt(lead_time_days)
    # 严谨起见，考虑检查周期: sqrt(lead_time + review_period)
    safety_stock = z_score * daily_std_dev * np.sqrt(lead_time_days)
    
    # 2. 再订货点 (Reorder Point)
    lead_time_demand = daily_demand * lead_time_days
    reorder_point = lead_time_demand + safety_stock
    
    # 3. 目标最大库存
    target_stock_level = daily_demand * (lead_time_days + review_period_days) + safety_stock
    
    return {
        "safety_stock": max(0, round(safety_stock, 2)),
        "reorder_point": max(0, round(reorder_point, 2)),
        "target_stock_level": max(0, round(target_stock_level, 2)),
        "lead_time_demand": max(0, round(lead_time_demand, 2)),
        "z_score": round(z_score, 2)
    }

def calculate_monthly_strategy(
    monthly_demand: float,
    metrics_mae: float,
    lead_time_days: int,
    service_level: float,
    days_in_month: int = 30
) -> Dict[str, float]:
    """
    基于月度预测计算库存策略
    """
    daily_demand = monthly_demand / days_in_month
    
    # 估算日需求标准差 (假设月度波动主要由MAE反映)
    monthly_std_dev = metrics_mae * 1.25
    daily_std_dev = monthly_std_dev / np.sqrt(days_in_month)
    
    return calculate_inventory_policy(
        daily_demand=daily_demand,
        daily_std_dev=daily_std_dev,
        lead_time_days=lead_time_days,
        service_level=service_level,
        review_period_days=days_in_month
    )
