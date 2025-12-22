"""库存策略页面模块"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.navigation import navigate_to
from utils.forecast import predict_actual_demand
from utils.inventory import calculate_monthly_strategy
from ui.components import render_kpi_card

def page_inventory_strategy():
    """库存策略页面：库存优化与补货策略仿真"""
    
    # Initialize View Mode
    if 'inv_view_mode' not in st.session_state:
        st.session_state['inv_view_mode'] = 'dashboard'

    # Retrieve Data
    df = st.session_state.get('df_data')

    if df is None:
        st.warning("⚠️ 请先在 '数据分析' 页面上传数据文件以启用库存策略功能。")
        if st.button("前往数据分析页面"):
            st.session_state['current_page'] = "Data Analysis"
            st.rerun()
        return

    # Determine Customer Field
    customer_field = None
    possible_fields = ['Customer_ID', 'Customer_Name', 'CustomerCode', 'Customer', 'Product_ID', 'SKU']
    for field in possible_fields:
        if field in df.columns:
            customer_field = field
            break
    
    if customer_field is None:
        if 'Customer_Type' in df.columns:
            customer_field = 'Customer_Type'
        else:
            st.error("❌ 数据中未找到客户或商品标识字段")
            return

    # Dispatcher
    if st.session_state['inv_view_mode'] == 'dashboard':
        render_dashboard(df, customer_field)
    else:
        render_prediction_page(df, customer_field)

def render_dashboard(df, customer_field):
    """渲染总库存策略仪表盘 (增强版)"""
    
    # 1. Header Area
    if st.button("← 返回主页"):
        st.session_state['current_page'] = 'Home'
        st.rerun()
        
    col_header, col_btn = st.columns([3, 1])
    with col_header:
        st.markdown('<h1 class="page-title">📦 库存策略总控台</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">监控全网库存健康状况，实时调整优化策略</p>', unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔮 进入需求预测工作台", type="primary", use_container_width=True):
            st.session_state['inv_view_mode'] = 'prediction'
            st.rerun()

    st.markdown("---")

    # 2. Intelligent Alerts (智能预警)
    # Mocking some alert data derived from df stats (e.g. low transaction items as proxy for risk)
    top_items = df[customer_field].value_counts()
    low_stock_count = int(len(top_items) * 0.15) # Mock 15% items low stock
    reorder_count = int(len(top_items) * 0.25)
    
    col_alert1, col_alert2 = st.columns(2)
    with col_alert1:
        st.error(f"⚠️ **紧急缺货预警**: {low_stock_count} 个商品低于安全库存水位")
    with col_alert2:
        st.warning(f"📦 **补货建议**: {reorder_count} 个商品已达到再订货点 (ROP)")

    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    item_count = df[customer_field].nunique()
    
    with k1:
        st.markdown(render_kpi_card("监控 SKU 总数", f"{item_count}", "活跃商品"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi_card("当前平均服务水平", "94.2%", "同比 -0.8%"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi_card("库存周转天数", "24 天", "目标 <30 天"), unsafe_allow_html=True)
    with k4:
        st.markdown(render_kpi_card("潜在断货损失", "¥12,400", "近30天预测"), unsafe_allow_html=True)

    st.markdown("---")

    # 3. Interactive Policy Sandbox (策略沙箱) & Visualization
    st.subheader("🛠️ 策略沙箱推演 (Policy Sandbox)")
    
    col_sand_ctrl, col_sand_viz = st.columns([1, 2])
    
    with col_sand_ctrl:
        st.caption("调整参数以模拟影响:")
        sim_service_level = st.slider("目标服务水平 (Service Level)", 0.80, 0.99, 0.95, 0.01)
        sim_lead_time = st.slider("平均补货提前期 (Lead Time Days)", 1, 60, 15, 1)
        sim_unit_cost = st.number_input("平均单件持有成本 (¥)", value=10.0, step=0.5)
        
        # Simple Simulation Logic (Mock calculation)
        # Higher service level -> Higher Z score -> Higher Safety Stock
        # Higher lead time -> Higher Pipeline Stock
        import scipy.stats as stats
        z_score = stats.norm.ppf(sim_service_level)
        base_demand = 5000 
        std_dev = 1000
        
        # Formulas
        safety_stock = z_score * std_dev * np.sqrt(sim_lead_time/30) # Simplified
        cycle_stock = (base_demand / 2) # Rough avg
        total_stock = safety_stock + cycle_stock
        holding_cost = total_stock * sim_unit_cost
        stockout_prob = (1 - sim_service_level) * 100
        
        st.info(
            f"📊 **推演结果**:\n\n"
            f"• 建议安全库存: **{int(safety_stock):,}** 件\n"
            f"• 预计总持有成本: **¥{int(holding_cost):,}**\n"
            f"• 缺货风险概率: **{stockout_prob:.1f}%**"
        )
        
    with col_sand_viz:
        # Dynamic Chart: Trade-off Curve
        # Generate points for curve
        sl_range = np.linspace(0.80, 0.99, 20)
        costs = []
        risks = []
        
        for sl in sl_range:
            z = stats.norm.ppf(sl)
            ss = z * std_dev * np.sqrt(sim_lead_time/30)
            t_stock = ss + cycle_stock
            costs.append(t_stock * sim_unit_cost)
            risks.append((1-sl)*100)
            
        fig_sim = go.Figure()
        
        # Cost Line (Left Y)
        fig_sim.add_trace(go.Scatter(
            x=sl_range*100, y=costs, 
            name='库存持有成本 (Cost)',
            line=dict(color='#e74a3b', width=3)
        ))
        
        # Risk Line (Right Y) - Using bar potentially or just dual axis line
        # Let's keep it simple: Just cost vs Service Level curve, and mark the current selection
        
        # Mark current selection
        fig_sim.add_trace(go.Scatter(
            x=[sim_service_level*100], y=[holding_cost],
            mode='markers', name='当前设定',
            marker=dict(size=14, color='black', symbol='x')
        ))

        fig_sim.update_layout(
            title="服务水平 vs 库存成本 权衡曲线",
            xaxis_title="服务水平 (%)",
            yaxis_title="预计持有成本 (¥)",
            hovermode="x unified",
            plot_bgcolor='white',
            height=400
        )
        fig_sim.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
        fig_sim.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig_sim, use_container_width=True)

    # 4. Actionable Stock Status Table
    st.subheader("📋 重点关注商品概览 (Top Aggregated Items)")
    
    # Create sample "Actionable" Data
    agg_df = df[customer_field].value_counts().head(8).reset_index()
    agg_df.columns = ['Product/Customer', 'Avg_Monthly_Demand']
    # Add mock columns
    agg_df['Current_Stock'] = np.random.randint(50, 500, size=len(agg_df))
    agg_df['Suggested_ROP'] = agg_df['Current_Stock'] + np.random.randint(-50, 50, size=len(agg_df)) # Some below, some above
    
    def get_status(row):
        if row['Current_Stock'] < row['Suggested_ROP'] * 0.8:
            return "🔴 严重缺货"
        elif row['Current_Stock'] < row['Suggested_ROP']:
            return "🟡 需补货"
        else:
            return "🟢 正常"
            
    agg_df['Status'] = agg_df.apply(get_status, axis=1)
    
    # Reorder columns
    display_df = agg_df[['Product/Customer', 'Status', 'Current_Stock', 'Suggested_ROP', 'Avg_Monthly_Demand']]
    
    # Styled dataframe
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Product/Customer": st.column_config.TextColumn("商品/客户"),
            "Status": st.column_config.TextColumn("状态", help="基于当前库存与ROP对比"),
            "Current_Stock": st.column_config.ProgressColumn("当前库存", format="%d", min_value=0, max_value=600),
            "Suggested_ROP": st.column_config.NumberColumn("建议再订货点 (ROP)"),
            "Avg_Monthly_Demand": st.column_config.NumberColumn("月均需求 (Hist)")
        }
    )


def render_prediction_page(df, customer_field):
    """渲染预测与详情分析页面"""
    
    # Navigation Header
    col_nav, _ = st.columns([1, 5])
    with col_nav:
        if st.button("← 返回总看板"):
            st.session_state['inv_view_mode'] = 'dashboard'
            st.rerun()

    st.markdown('<h2 class="page-title">🔮 客户需求预测与策略生成</h2>', unsafe_allow_html=True)
    st.markdown("---")

    # Determine Product Field (Force SKU_ID if available as per user request for "supply_chain_data")
    product_field = None
    # Priority: SKU_ID (Spec specific), then various fallbacks
    possible_prod_fields = ['SKU_ID', 'Product_ID', 'SKU', 'Item_Code', 'Product', 'Product Name']
    for field in possible_prod_fields:
        if field in df.columns:
            product_field = field
            break
            
    if not product_field:
        product_field = "Product_Generic"

    # ==========================================
    # 1. Prediction Inputs (Table Based)
    # ==========================================
    st.subheader("1. 市场需求预测输入")
    st.caption("请在下方表格填入：年份、月份、客户、商品以及您的预测值。可直接在表格中下拉选择。")

    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Prepare Options
    unique_customers = sorted(df[customer_field].dropna().unique().astype(str))
    unique_products = sorted(df[product_field].dropna().unique().astype(str))
    
    # Defaults
    default_cust = unique_customers[0] if len(unique_customers) > 0 else "Unknown"
    default_prod = unique_products[0] if len(unique_products) > 0 else "Unknown"

    # Initialize Data Editor State
    if 'forecast_input_df' not in st.session_state:
         init_forecast_table(current_year, current_month, default_cust, default_prod)
    elif 'Customer_ID' not in st.session_state['forecast_input_df'].columns:
         # Reset if schema mismatch from previous version
         init_forecast_table(current_year, current_month, default_cust, default_prod)

    # Utility Toolbar & Filters
    col_tools, _ = st.columns([2, 5])
    with col_tools:
        if st.button("重置/清空表格"):
            init_forecast_table(current_year, current_month, default_cust, default_prod)
            st.rerun()

    # Filter Container
    with st.expander("🔎 数据筛选 (点击展开)", expanded=False):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        full_df = st.session_state['forecast_input_df']
        
        # Get unique values for filters
        avail_years = sorted(full_df['Year'].unique()) if not full_df.empty else []
        avail_months = sorted(full_df['Month'].unique()) if not full_df.empty else []
        avail_custs = sorted(full_df['Customer_ID'].astype(str).unique()) if not full_df.empty else []
        avail_prods = sorted(full_df['Product_ID'].astype(str).unique()) if not full_df.empty else []

        with f_col1:
            sel_years = st.multiselect("年份", avail_years)
        with f_col2:
            sel_months = st.multiselect("月份", avail_months)
        with f_col3:
            sel_custs = st.multiselect("客户", avail_custs)
        with f_col4:
            sel_prods = st.multiselect("商品", avail_prods)
            
    # Apply filters
    filtered_df = full_df.copy()
    if sel_years:
        filtered_df = filtered_df[filtered_df['Year'].isin(sel_years)]
    if sel_months:
        filtered_df = filtered_df[filtered_df['Month'].isin(sel_months)]
    if sel_custs:
        filtered_df = filtered_df[filtered_df['Customer_ID'].astype(str).isin(sel_custs)]
    if sel_prods:
        filtered_df = filtered_df[filtered_df['Product_ID'].astype(str).isin(sel_prods)]

    # Data Editor
    # Note: Changes made here must be reflected back to the main session_state dataframe
    edited_subset = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True, # We hide index visually, but we rely on internal alignment for updates if rows are modified
        column_config={
            "Year": st.column_config.NumberColumn("年份", format="%d", min_value=2020, max_value=2030),
            "Month": st.column_config.NumberColumn("月份", format="%d", min_value=1, max_value=12),
            "Customer_ID": st.column_config.SelectboxColumn(
                "客户 (Customer)", 
                help="选择所属客户",
                width="medium",
                options=unique_customers, 
                required=True
            ),
            "Product_ID": st.column_config.SelectboxColumn(
                f"商品 ({product_field})", 
                help="选择商品SKU/种类",
                width="medium",
                options=unique_products, 
                required=True
            ),
            "User_Forecast": st.column_config.NumberColumn(
                "预测需求 (Qty)", 
                min_value=0, 
                format="%.0f", 
                required=True
            ),
        },
        key="editor_demand"
    )

    # Sync changes back to main dataframe
    # 1. Update existing rows (intersection of index)
    # We use .update() which updates in place based on index
    if not edited_subset.equals(filtered_df):
        # We need to be careful: data_editor returns a new DF with potentially new rows (new index) or deleted rows
        # If rows were added, they have new range index usually? Or if filtered, it's tricky.
        # Simplification: If filters are ACTIVE, disable adding/deleting rows to prevent index confusion, OR complex merge logic.
        # The safest approach for a "Filtered View" is update-only. Adding rows in a filtered view is ambiguous (what are the hidden values?)
        
        # However, for simple use cases, st.data_editor with num_rows="dynamic" on a filtered subset often resets/reindexes.
        # Let's try explicit update for common index.
        
        st.session_state['forecast_input_df'].update(edited_subset)
        
        # Handle added rows (if any, though 'dynamic' on filtered view is risky)
        # Handle deleted rows (if any)
        # Identify indices present in 'filtered_df' but missing in 'edited_subset' -> Delete them from main
        missing_indices = filtered_df.index.difference(edited_subset.index)
        if not missing_indices.empty:
             st.session_state['forecast_input_df'] = st.session_state['forecast_input_df'].drop(missing_indices)
        
        # Identify new indices in 'edited_subset' -> Append them
        new_indices = edited_subset.index.difference(filtered_df.index)
        # This part is tricky because Streamlit might re-index new rows starting from 0 or max+1 of the SUBSET.
        # If we really need Robust Adding, we should disable filters.
        # For now, let's assume update works fine for edits.
        if not new_indices.empty:
             new_rows = edited_subset.loc[new_indices]
             st.session_state['forecast_input_df'] = pd.concat([st.session_state['forecast_input_df'], new_rows])

    # Button Row
    st.markdown("<br>", unsafe_allow_html=True)
    start_simulation = st.button("🚀 开始预测分析", type="primary", use_container_width=True)

    # ==========================================
    # Logic & Results
    # ==========================================
    if start_simulation:
        if st.session_state['forecast_input_df'].empty:
            st.warning("⚠️ 请先在表格中添加预测数据。")
        else:
            with st.spinner("正在逐行进行多因子预测分析..."):
                run_simulation_bulk(df, st.session_state['forecast_input_df'], customer_field, product_field)
    
    # Display Results if available
    if 'simulation_results' in st.session_state:
        render_simulation_results()

def init_forecast_table(current_year, current_month, default_cust, default_prod):
    """初始化预测输入表 (多行结构)"""
    future_months_data = []
    temp_date = datetime(current_year, current_month, 1)
    
    if temp_date.month == 12:
        temp_date = datetime(temp_date.year + 1, 1, 1)
    else:
        temp_date = datetime(temp_date.year, temp_date.month + 1, 1)

    for i in range(3):
        future_months_data.append({
            "Year": temp_date.year,
            "Month": temp_date.month,
            "Customer_ID": default_cust,
            "Product_ID": default_prod,
            "User_Forecast": 1000.0
        })
        if temp_date.month == 12:
            temp_date = datetime(temp_date.year + 1, 1, 1)
        else:
            temp_date = datetime(temp_date.year, temp_date.month + 1, 1)
    
    st.session_state['forecast_input_df'] = pd.DataFrame(future_months_data)

def run_simulation_bulk(df, edited_df, customer_field, product_field="Product_ID"):
    """运行批量仿真逻辑"""
    results = []
    total_predicted_demand = 0
    lead_time = 15     # Default
    service_level = 0.95 # Default

    for index, row in edited_df.iterrows():
        try:
            target_year = int(row['Year'])
            target_month = int(row['Month'])
            cust_id = str(row['Customer_ID'])
            prod_id = str(row['Product_ID'])
            user_forecast = float(row['User_Forecast'])
            
            # Predict
            pred_result = predict_actual_demand(
                df=df,
                customer_id=cust_id,
                target_month=target_month,
                user_forecast=user_forecast,
                use_seasonal=True
            )
            
            predicted_actual = pred_result['predicted_actual']
            mae = pred_result['mae']
            bias_rate = pred_result['bias_rate']
            
            # Inventory Strategy
            if mae == 0 and predicted_actual > 0:
                mae_for_strategy = predicted_actual * 0.2
            else:
                mae_for_strategy = mae
                
            inventory_strategy = calculate_monthly_strategy(
                monthly_demand=predicted_actual,
                metrics_mae=mae_for_strategy,
                lead_time_days=lead_time,
                service_level=service_level
            )
            
            total_predicted_demand += predicted_actual
            
            results.append({
                "Year": target_year,
                "Month": target_month,
                "Customer_ID": cust_id,
                "Product_ID": prod_id,
                "User_Forecast": user_forecast,
                "Predicted_Actual": round(predicted_actual, 2),
                "Correction": f"{bias_rate*100:+.1f}%",
                "Safety_Stock": inventory_strategy['safety_stock'],
                "ROP": inventory_strategy['reorder_point'],
                "Max_Stock": inventory_strategy['target_stock_level']
            })
        except Exception as e:
            st.error(f"Error processing row {index}: {e}")
    
    results_df = pd.DataFrame(results)
    st.session_state['simulation_results'] = results_df
    st.session_state['total_predicted_demand'] = total_predicted_demand

def render_simulation_results():
    """展示仿真结果详情 (包括商品维度)"""
    results_df = st.session_state['simulation_results']
    
    st.success("✅ 预测分析完成！")
    st.markdown("---")
    
    # Visualization Section
    st.subheader("📊 预测结果可视化")
    
    results_df['Date_Str'] = results_df.apply(lambda x: f"{int(x['Year'])}-{int(x['Month']):02d}", axis=1)
    
    col_vis1, col_vis2 = st.columns(2)
    
    with col_vis1:
        st.markdown("##### 🥧 各商品实际需求占比 (Pie Chart)")
        
        # Date Selector for Pie Chart
        available_dates = sorted(results_df['Date_Str'].unique())
        selected_date_for_pie = st.selectbox("选择月份 (Select Month)", available_dates, key="pie_date_sel")
        
        # Filter Data
        pie_data = results_df[results_df['Date_Str'] == selected_date_for_pie]
        
        if not pie_data.empty:
            fig_pie = px.pie(
                pie_data, 
                values='Predicted_Actual', 
                names='Product_ID', 
                title=f'{selected_date_for_pie} 各商品需求占比',
                hole=0.4
            )
            # Show Value, Percentage and Label
            fig_pie.update_traces(textposition='inside', textinfo='label+percent+value')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("该月份无数据")

    with col_vis2:
        st.markdown("##### 📊 多周期需求趋势 (Grouped Bar Chart)")
        # Multi-line Bar Chart (Grouped Bar)
        # X: Date, Y: Demand, Color: Product
        fig_bar_group = px.bar(
            results_df, 
            x='Date_Str', 
            y='Predicted_Actual',
            color='Product_ID',
            barmode='group',
            text='Predicted_Actual', # Show values
            title='各月多商品需求趋势对比',
            labels={'Predicted_Actual': '预测实际需求 (Qty)', 'Date_Str': '时间周期', 'Product_ID': '商品'}
        )
        
        # Configure text labels on bars
        fig_bar_group.update_traces(
            texttemplate='%{text:.0f}', 
            textposition='outside'
        )
        
        fig_bar_group.update_layout(
            plot_bgcolor='white', 
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            uniformtext_minsize=8, 
            uniformtext_mode='hide',
            margin=dict(t=50, l=25, r=25, b=25) # Add margin for outside text
        )
        fig_bar_group.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
        fig_bar_group.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        st.plotly_chart(fig_bar_group, use_container_width=True)

    st.markdown("---")
    st.subheader("🏭 客户商品需求分布 (Customer-Product Demand)")
    
    # Selector for this specific chart
    cp_date = st.selectbox("选择月份进行分析 (Select Month)", sorted(results_df['Date_Str'].unique()), key="cp_bar_date")
    
    # Filter
    cp_data = results_df[results_df['Date_Str'] == cp_date]
    
    if not cp_data.empty:
        # Grouped Bar: X=Customer, Color=Product, Y=Demand
        fig_cp = px.bar(
            cp_data,
            x='Customer_ID',
            y='Predicted_Actual',
            color='Product_ID',
            barmode='group',
            text='Predicted_Actual',
            title=f"{cp_date} 客户-商品 需求分布",
            labels={'Customer_ID': '客户 (Customer)', 'Predicted_Actual': '需求量 (Qty)', 'Product_ID': '商品 (Product)'}
        )
        
        fig_cp.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_cp.update_layout(
            plot_bgcolor='white',
            hovermode='closest',
            margin=dict(t=50, l=25, r=25, b=25),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_cp.update_yaxes(showgrid=True, gridcolor='#f0f0f0')
        
        st.plotly_chart(fig_cp, use_container_width=True)
    else:
        st.info("该月份无数据")

    # 3. Data Table
    st.subheader("📝 详细策略数据列表")
    
    display_df = results_df.copy()
    display_df = display_df[['Year', 'Month', 'Customer_ID', 'Product_ID', 'User_Forecast', 'Predicted_Actual', 'Correction', 'Safety_Stock', 'ROP', 'Max_Stock']]
    display_df.columns = ['年份', '月份', '客户', '商品', '用户预测', 'AI预测实际', '修正率', '建议安全库存', '再订货点', '目标最大库存']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
