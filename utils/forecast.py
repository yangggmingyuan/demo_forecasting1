"""需求预测工具函数模块"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime


def get_customer_history(df: pd.DataFrame, customer_id: str) -> pd.DataFrame:
    """
    获取指定客户的历史数据
    
    Args:
        df: 完整的数据DataFrame
        customer_id: 客户ID
        
    Returns:
        该客户的历史数据DataFrame
    """
    # 检测客户标识字段
    customer_field = None
    possible_fields = ['Customer_ID', 'Customer_Name', 'CustomerCode', 'Customer']
    for field in possible_fields:
        if field in df.columns:
            customer_field = field
            break
    
    if customer_field is None:
        if 'Customer_Type' in df.columns:
            customer_field = 'Customer_Type'
        else:
            return pd.DataFrame()
    
    customer_data = df[df[customer_field] == customer_id].copy()
    
    # 确保Date列是datetime类型
    if 'Date' in customer_data.columns:
        if not pd.api.types.is_datetime64_any_dtype(customer_data['Date']):
            customer_data['Date'] = pd.to_datetime(customer_data['Date'], errors='coerce')
    
    return customer_data


def calculate_bias_rate(customer_data: pd.DataFrame) -> Dict[str, float]:
    """
    计算客户的历史偏差率统计
    
    Args:
        customer_data: 客户历史数据
        
    Returns:
        包含偏差率统计信息的字典
    """
    if len(customer_data) == 0:
        return {
            'avg_bias_rate': 0.0,
            'mape': 0.0,
            'mae': 0.0,
            'std_error': 0.0,
            'record_count': 0
        }
    
    # 计算预测误差
    customer_data = customer_data.copy()
    customer_data['Forecast_Error'] = customer_data['Forecast_Qty'] - customer_data['Actual_Qty']
    
    # 计算偏差率（避免除零）
    customer_data['Bias_Rate'] = np.where(
        customer_data['Actual_Qty'] != 0,
        (customer_data['Forecast_Error'] / customer_data['Actual_Qty']),
        0
    )
    
    # 计算MAPE（平均绝对百分比误差）
    customer_data['Abs_Error_Pct'] = np.where(
        customer_data['Actual_Qty'] != 0,
        np.abs(customer_data['Forecast_Error'] / customer_data['Actual_Qty'] * 100),
        np.nan
    )
    
    # 统计指标
    avg_bias_rate = customer_data['Bias_Rate'].mean()
    mape = customer_data['Abs_Error_Pct'].mean()
    mae = customer_data['Forecast_Error'].abs().mean()
    std_error = customer_data['Bias_Rate'].std()
    
    return {
        'avg_bias_rate': avg_bias_rate if not pd.isna(avg_bias_rate) else 0.0,
        'mape': mape if not pd.isna(mape) else 0.0,
        'mae': mae if not pd.isna(mae) else 0.0,
        'std_error': std_error if not pd.isna(std_error) else 0.0,
        'record_count': len(customer_data)
    }


def calculate_seasonal_factor(customer_data: pd.DataFrame, target_month: int) -> Optional[float]:
    """
    计算季节性因子（基于目标月份的历史数据）
    
    Args:
        customer_data: 客户历史数据
        target_month: 目标月份（1-12）
        
    Returns:
        季节性因子，如果没有该月份的历史数据则返回None
    """
    if len(customer_data) == 0 or 'Date' not in customer_data.columns:
        return None
    
    # 筛选目标月份的历史数据
    target_month_data = customer_data[customer_data['Date'].dt.month == target_month]
    
    if len(target_month_data) == 0:
        return None
    
    # 计算该月份的平均偏差率
    target_month_data = target_month_data.copy()
    target_month_data['Bias_Rate'] = np.where(
        target_month_data['Actual_Qty'] != 0,
        (target_month_data['Forecast_Qty'] - target_month_data['Actual_Qty']) / target_month_data['Actual_Qty'],
        0
    )
    
    seasonal_bias_rate = target_month_data['Bias_Rate'].mean()
    
    # 计算整体平均偏差率
    all_data = customer_data.copy()
    all_data['Bias_Rate'] = np.where(
        all_data['Actual_Qty'] != 0,
        (all_data['Forecast_Qty'] - all_data['Actual_Qty']) / all_data['Actual_Qty'],
        0
    )
    overall_bias_rate = all_data['Bias_Rate'].mean()
    
    # 季节性因子 = 该月份偏差率 / 整体偏差率
    if overall_bias_rate != 0:
        seasonal_factor = seasonal_bias_rate / overall_bias_rate
        return seasonal_factor if not pd.isna(seasonal_factor) else None
    
    return None


def calculate_confidence_interval(predicted_value: float, std_error: float, confidence_level: float = 0.95) -> Tuple[float, float]:
    """
    计算预测值的置信区间
    
    Args:
        predicted_value: 预测值
        std_error: 标准误差
        confidence_level: 置信水平（默认0.95，即95%置信区间）
        
    Returns:
        (下限, 上限) 元组
    """
    # Z-score for 95% confidence interval
    z_score = 1.96 if confidence_level == 0.95 else 2.58 if confidence_level == 0.99 else 1.645
    
    margin = predicted_value * std_error * z_score
    lower_bound = max(0, predicted_value - margin)  # 确保不为负数
    upper_bound = predicted_value + margin
    
    return (lower_bound, upper_bound)


def predict_actual_demand(
    df: pd.DataFrame,
    customer_id: str,
    target_month: int,
    user_forecast: float,
    use_seasonal: bool = True
) -> Dict:
    """
    预测客户的实际提货量
    
    Args:
        df: 完整的数据DataFrame
        customer_id: 客户ID
        target_month: 目标月份（1-12）
        user_forecast: 用户输入的预测需求
        use_seasonal: 是否使用季节性调整
        
    Returns:
        包含预测结果的字典
    """
    # 1. 获取客户历史数据
    customer_data = get_customer_history(df, customer_id)
    
    if len(customer_data) == 0:
        return {
            'predicted_actual': user_forecast,
            'confidence_interval': (user_forecast * 0.8, user_forecast * 1.2),
            'bias_rate': 0.0,
            'mape': 0.0,
            'mae': 0.0,
            'historical_records': 0,
            'seasonal_factor': None,
            'warning': '该客户没有历史数据，预测结果仅供参考',
            'reliability': '低'
        }
    
    # 2. 计算历史偏差率统计
    stats = calculate_bias_rate(customer_data)
    
    # 3. 确定使用的偏差率
    bias_rate = stats['avg_bias_rate']
    seasonal_factor = None
    
    if use_seasonal:
        seasonal_factor = calculate_seasonal_factor(customer_data, target_month)
        if seasonal_factor is not None:
            # 如果找到季节性因子，使用该月份的偏差率
            target_month_data = customer_data[customer_data['Date'].dt.month == target_month]
            if len(target_month_data) > 0:
                target_month_data = target_month_data.copy()
                target_month_data['Bias_Rate'] = np.where(
                    target_month_data['Actual_Qty'] != 0,
                    (target_month_data['Forecast_Qty'] - target_month_data['Actual_Qty']) / target_month_data['Actual_Qty'],
                    0
                )
                bias_rate = target_month_data['Bias_Rate'].mean()
                if pd.isna(bias_rate):
                    bias_rate = stats['avg_bias_rate']
    
    # 4. 预测实际提货量
    # 公式：预测实际 = 用户预测 × (1 - 偏差率)
    predicted_actual = user_forecast * (1 - bias_rate)
    
    # 确保预测值不为负数
    predicted_actual = max(0, predicted_actual)
    
    # 5. 计算置信区间
    confidence_interval = calculate_confidence_interval(predicted_actual, stats['std_error'])
    
    # 6. 评估可靠性
    reliability = '高' if stats['record_count'] >= 10 else '中' if stats['record_count'] >= 5 else '低'
    
    return {
        'predicted_actual': predicted_actual,
        'confidence_interval': confidence_interval,
        'bias_rate': bias_rate,
        'mape': stats['mape'],
        'mae': stats['mae'],
        'historical_records': stats['record_count'],
        'seasonal_factor': seasonal_factor,
        'warning': None,
        'reliability': reliability
    }

