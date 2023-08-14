from importlib import import_module


class TushareAPI(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.instances = {}
        self.config = config
        pass

    def __getattr__(self, name):
        if not self.instances.get(name):
            self.instances[name] = self.instance_from_name(name, self.config)
        return self.instances.get(name)

    def all_apis(self):
        apis = [
            'adj_factor', 'stock_company', 'daily', 'moneyflow', 'bak_daily', 'namechange', 'fund_basic', 'monthly',
            'moneyflow_hsgt', 'stock_mx', 'stk_rewards', 'stock_vx', 'hs_const', 'bak_basic', 'suspend_d', 'weekly',
            'stock_basic', 'new_share', 'stk_managers', 'daily_basic', 'ggt_daily', 'ggt_top10', 'hsgt_top10',
            'ggt_monthly', 'income_vip', 'balancesheet_vip', 'cashflow_vip', 'forecast_vip', 'express_vip', 'dividend',
            'fina_indicator_vip', 'ths_daily', 'ths_member', 'anns', 'trade_cal', 'stock_vx', 'stock_mx', 'fund_adj',
            'fund_company', 'fund_div', 'fund_manager', 'fund_nav', 'fund_portfolio', 'fund_sales_ratio',
            'fund_sales_vol', 'fund_share', 'fund_daily', 'index_basic', 'index_daily', 'index_dailybasic',
            'index_classify', 'index_member', 'ths_index', 'index_global', 'index_weekly', 'index_monthly',
            'index_weight', 'daily_info', 'sz_daily_info', 'ths_daily', 'ths_member', 'cn_cpi', 'cn_gdp', 'cn_m',
            'cn_ppi', 'sf_month', 'us_tbr', 'us_tltr', 'us_trltr', 'us_trycr'
        ]
        apis.extend(['daily_full'])
        return apis

    def _instance_from_name(self, name, config):
        if name == 'daily_full':
            adj_factor_module = import_module("tutake.api.ts.daily_full")
            clazz = getattr(adj_factor_module, "DailyFull")
            return clazz(config)

    def instance_from_name(self, name, config):

        if name == 'adj_factor':
            adj_factor_module = import_module("tutake.api.ts.adj_factor")
            clazz = getattr(adj_factor_module, "AdjFactor")
            return clazz(config)
        if name == 'stock_company':
            stock_company_module = import_module("tutake.api.ts.stock_company")
            clazz = getattr(stock_company_module, "StockCompany")
            return clazz(config)
        if name == 'daily':
            daily_module = import_module("tutake.api.ts.daily")
            clazz = getattr(daily_module, "Daily")
            return clazz(config)
        if name == 'moneyflow':
            moneyflow_module = import_module("tutake.api.ts.moneyflow")
            clazz = getattr(moneyflow_module, "Moneyflow")
            return clazz(config)
        if name == 'bak_daily':
            bak_daily_module = import_module("tutake.api.ts.bak_daily")
            clazz = getattr(bak_daily_module, "BakDaily")
            return clazz(config)
        if name == 'namechange':
            namechange_module = import_module("tutake.api.ts.namechange")
            clazz = getattr(namechange_module, "Namechange")
            return clazz(config)
        if name == 'fund_basic':
            fund_basic_module = import_module("tutake.api.ts.fund_basic")
            clazz = getattr(fund_basic_module, "FundBasic")
            return clazz(config)
        if name == 'monthly':
            monthly_module = import_module("tutake.api.ts.monthly")
            clazz = getattr(monthly_module, "Monthly")
            return clazz(config)
        if name == 'moneyflow_hsgt':
            moneyflow_hsgt_module = import_module("tutake.api.ts.moneyflow_hsgt")
            clazz = getattr(moneyflow_hsgt_module, "MoneyflowHsgt")
            return clazz(config)
        if name == 'stock_mx':
            stock_mx_module = import_module("tutake.api.ts.stock_mx")
            clazz = getattr(stock_mx_module, "StockMx")
            return clazz(config)
        if name == 'stk_rewards':
            stk_rewards_module = import_module("tutake.api.ts.stk_rewards")
            clazz = getattr(stk_rewards_module, "StkRewards")
            return clazz(config)
        if name == 'stock_vx':
            stock_vx_module = import_module("tutake.api.ts.stock_vx")
            clazz = getattr(stock_vx_module, "StockVx")
            return clazz(config)
        if name == 'hs_const':
            hs_const_module = import_module("tutake.api.ts.hs_const")
            clazz = getattr(hs_const_module, "HsConst")
            return clazz(config)
        if name == 'bak_basic':
            bak_basic_module = import_module("tutake.api.ts.bak_basic")
            clazz = getattr(bak_basic_module, "BakBasic")
            return clazz(config)
        if name == 'suspend_d':
            suspend_d_module = import_module("tutake.api.ts.suspend_d")
            clazz = getattr(suspend_d_module, "SuspendD")
            return clazz(config)
        if name == 'weekly':
            weekly_module = import_module("tutake.api.ts.weekly")
            clazz = getattr(weekly_module, "Weekly")
            return clazz(config)
        if name == 'stock_basic':
            stock_basic_module = import_module("tutake.api.ts.stock_basic")
            clazz = getattr(stock_basic_module, "StockBasic")
            return clazz(config)
        if name == 'new_share':
            new_share_module = import_module("tutake.api.ts.new_share")
            clazz = getattr(new_share_module, "NewShare")
            return clazz(config)
        if name == 'stk_managers':
            stk_managers_module = import_module("tutake.api.ts.stk_managers")
            clazz = getattr(stk_managers_module, "StkManagers")
            return clazz(config)
        if name == 'daily_basic':
            daily_basic_module = import_module("tutake.api.ts.daily_basic")
            clazz = getattr(daily_basic_module, "DailyBasic")
            return clazz(config)
        if name == 'ggt_daily':
            ggt_daily_module = import_module("tutake.api.ts.ggt_daily")
            clazz = getattr(ggt_daily_module, "GgtDaily")
            return clazz(config)
        if name == 'ggt_top10':
            ggt_top10_module = import_module("tutake.api.ts.ggt_top10")
            clazz = getattr(ggt_top10_module, "GgtTop10")
            return clazz(config)
        if name == 'hsgt_top10':
            hsgt_top10_module = import_module("tutake.api.ts.hsgt_top10")
            clazz = getattr(hsgt_top10_module, "HsgtTop10")
            return clazz(config)
        if name == 'ggt_monthly':
            ggt_monthly_module = import_module("tutake.api.ts.ggt_monthly")
            clazz = getattr(ggt_monthly_module, "GgtMonthly")
            return clazz(config)
        if name == 'income_vip':
            income_vip_module = import_module("tutake.api.ts.income_vip")
            clazz = getattr(income_vip_module, "IncomeVip")
            return clazz(config)
        if name == 'balancesheet_vip':
            balancesheet_vip_module = import_module("tutake.api.ts.balancesheet_vip")
            clazz = getattr(balancesheet_vip_module, "BalancesheetVip")
            return clazz(config)
        if name == 'cashflow_vip':
            cashflow_vip_module = import_module("tutake.api.ts.cashflow_vip")
            clazz = getattr(cashflow_vip_module, "CashflowVip")
            return clazz(config)
        if name == 'forecast_vip':
            forecast_vip_module = import_module("tutake.api.ts.forecast_vip")
            clazz = getattr(forecast_vip_module, "ForecastVip")
            return clazz(config)
        if name == 'express_vip':
            express_vip_module = import_module("tutake.api.ts.express_vip")
            clazz = getattr(express_vip_module, "ExpressVip")
            return clazz(config)
        if name == 'dividend':
            dividend_module = import_module("tutake.api.ts.dividend")
            clazz = getattr(dividend_module, "Dividend")
            return clazz(config)
        if name == 'fina_indicator_vip':
            fina_indicator_vip_module = import_module("tutake.api.ts.fina_indicator_vip")
            clazz = getattr(fina_indicator_vip_module, "FinaIndicatorVip")
            return clazz(config)
        if name == 'ths_daily':
            ths_daily_module = import_module("tutake.api.ts.ths_daily")
            clazz = getattr(ths_daily_module, "ThsDaily")
            return clazz(config)
        if name == 'ths_member':
            ths_member_module = import_module("tutake.api.ts.ths_member")
            clazz = getattr(ths_member_module, "ThsMember")
            return clazz(config)
        if name == 'anns':
            anns_module = import_module("tutake.api.ts.anns")
            clazz = getattr(anns_module, "Anns")
            return clazz(config)
        if name == 'trade_cal':
            trade_cal_module = import_module("tutake.api.ts.trade_cal")
            clazz = getattr(trade_cal_module, "TradeCal")
            return clazz(config)
        if name == 'stock_vx':
            stock_vx_module = import_module("tutake.api.ts.stock_vx")
            clazz = getattr(stock_vx_module, "StockVx")
            return clazz(config)
        if name == 'stock_mx':
            stock_mx_module = import_module("tutake.api.ts.stock_mx")
            clazz = getattr(stock_mx_module, "StockMx")
            return clazz(config)
        if name == 'fund_adj':
            fund_adj_module = import_module("tutake.api.ts.fund_adj")
            clazz = getattr(fund_adj_module, "FundAdj")
            return clazz(config)
        if name == 'fund_company':
            fund_company_module = import_module("tutake.api.ts.fund_company")
            clazz = getattr(fund_company_module, "FundCompany")
            return clazz(config)
        if name == 'fund_div':
            fund_div_module = import_module("tutake.api.ts.fund_div")
            clazz = getattr(fund_div_module, "FundDiv")
            return clazz(config)
        if name == 'fund_manager':
            fund_manager_module = import_module("tutake.api.ts.fund_manager")
            clazz = getattr(fund_manager_module, "FundManager")
            return clazz(config)
        if name == 'fund_nav':
            fund_nav_module = import_module("tutake.api.ts.fund_nav")
            clazz = getattr(fund_nav_module, "FundNav")
            return clazz(config)
        if name == 'fund_portfolio':
            fund_portfolio_module = import_module("tutake.api.ts.fund_portfolio")
            clazz = getattr(fund_portfolio_module, "FundPortfolio")
            return clazz(config)
        if name == 'fund_sales_ratio':
            fund_sales_ratio_module = import_module("tutake.api.ts.fund_sales_ratio")
            clazz = getattr(fund_sales_ratio_module, "FundSalesRatio")
            return clazz(config)
        if name == 'fund_sales_vol':
            fund_sales_vol_module = import_module("tutake.api.ts.fund_sales_vol")
            clazz = getattr(fund_sales_vol_module, "FundSalesVol")
            return clazz(config)
        if name == 'fund_share':
            fund_share_module = import_module("tutake.api.ts.fund_share")
            clazz = getattr(fund_share_module, "FundShare")
            return clazz(config)
        if name == 'fund_daily':
            fund_daily_module = import_module("tutake.api.ts.fund_daily")
            clazz = getattr(fund_daily_module, "FundDaily")
            return clazz(config)
        if name == 'index_basic':
            index_basic_module = import_module("tutake.api.ts.index_basic")
            clazz = getattr(index_basic_module, "IndexBasic")
            return clazz(config)
        if name == 'index_daily':
            index_daily_module = import_module("tutake.api.ts.index_daily")
            clazz = getattr(index_daily_module, "IndexDaily")
            return clazz(config)
        if name == 'index_dailybasic':
            index_dailybasic_module = import_module("tutake.api.ts.index_dailybasic")
            clazz = getattr(index_dailybasic_module, "IndexDailybasic")
            return clazz(config)
        if name == 'index_classify':
            index_classify_module = import_module("tutake.api.ts.index_classify")
            clazz = getattr(index_classify_module, "IndexClassify")
            return clazz(config)
        if name == 'index_member':
            index_member_module = import_module("tutake.api.ts.index_member")
            clazz = getattr(index_member_module, "IndexMember")
            return clazz(config)
        if name == 'ths_index':
            ths_index_module = import_module("tutake.api.ts.ths_index")
            clazz = getattr(ths_index_module, "ThsIndex")
            return clazz(config)
        if name == 'index_global':
            index_global_module = import_module("tutake.api.ts.index_global")
            clazz = getattr(index_global_module, "IndexGlobal")
            return clazz(config)
        if name == 'index_weekly':
            index_weekly_module = import_module("tutake.api.ts.index_weekly")
            clazz = getattr(index_weekly_module, "IndexWeekly")
            return clazz(config)
        if name == 'index_monthly':
            index_monthly_module = import_module("tutake.api.ts.index_monthly")
            clazz = getattr(index_monthly_module, "IndexMonthly")
            return clazz(config)
        if name == 'index_weight':
            index_weight_module = import_module("tutake.api.ts.index_weight")
            clazz = getattr(index_weight_module, "IndexWeight")
            return clazz(config)
        if name == 'daily_info':
            daily_info_module = import_module("tutake.api.ts.daily_info")
            clazz = getattr(daily_info_module, "DailyInfo")
            return clazz(config)
        if name == 'sz_daily_info':
            sz_daily_info_module = import_module("tutake.api.ts.sz_daily_info")
            clazz = getattr(sz_daily_info_module, "SzDailyInfo")
            return clazz(config)
        if name == 'ths_daily':
            ths_daily_module = import_module("tutake.api.ts.ths_daily")
            clazz = getattr(ths_daily_module, "ThsDaily")
            return clazz(config)
        if name == 'ths_member':
            ths_member_module = import_module("tutake.api.ts.ths_member")
            clazz = getattr(ths_member_module, "ThsMember")
            return clazz(config)
        if name == 'cn_cpi':
            cn_cpi_module = import_module("tutake.api.ts.cn_cpi")
            clazz = getattr(cn_cpi_module, "CnCpi")
            return clazz(config)
        if name == 'cn_gdp':
            cn_gdp_module = import_module("tutake.api.ts.cn_gdp")
            clazz = getattr(cn_gdp_module, "CnGdp")
            return clazz(config)
        if name == 'cn_m':
            cn_m_module = import_module("tutake.api.ts.cn_m")
            clazz = getattr(cn_m_module, "CnM")
            return clazz(config)
        if name == 'cn_ppi':
            cn_ppi_module = import_module("tutake.api.ts.cn_ppi")
            clazz = getattr(cn_ppi_module, "CnPpi")
            return clazz(config)
        if name == 'sf_month':
            sf_month_module = import_module("tutake.api.ts.sf_month")
            clazz = getattr(sf_month_module, "SfMonth")
            return clazz(config)
        if name == 'us_tbr':
            us_tbr_module = import_module("tutake.api.ts.us_tbr")
            clazz = getattr(us_tbr_module, "UsTbr")
            return clazz(config)
        if name == 'us_tltr':
            us_tltr_module = import_module("tutake.api.ts.us_tltr")
            clazz = getattr(us_tltr_module, "UsTltr")
            return clazz(config)
        if name == 'us_trltr':
            us_trltr_module = import_module("tutake.api.ts.us_trltr")
            clazz = getattr(us_trltr_module, "UsTrltr")
            return clazz(config)
        if name == 'us_trycr':
            us_trycr_module = import_module("tutake.api.ts.us_trycr")
            clazz = getattr(us_trycr_module, "UsTrycr")
            return clazz(config)
        else:
            instance = self._instance_from_name(name, config)
            if instance:
                return instance
            else:
                return None
