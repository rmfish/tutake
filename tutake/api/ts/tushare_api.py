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
            'stock_company', 'hk_hold', 'stk_rewards', 'hs_const', 'report_rc', 'stk_managers', 'moneyflow_hsgt',
            'fx_obasic', 'namechange', 'shibor_lpr', 'ccass_hold', 'stock_vx', 'bak_daily', 'fx_daily', 'suspend_d',
            'daily', 'weekly', 'libor', 'stock_mx', 'ci_daily', 'wz_index', 'bak_basic', 'stock_basic', 'shibor',
            'ccass_hold_detail', 'gz_index', 'fund_basic', 'limit_list_d', 'new_share', 'monthly', 'us_tycr',
            'moneyflow', 'adj_factor', 'hibor', 'daily_basic', 'ggt_daily', 'ggt_top10', 'hsgt_top10', 'ggt_monthly',
            'income_vip', 'balancesheet_vip', 'cashflow_vip', 'forecast_vip', 'express_vip', 'dividend',
            'fina_indicator_vip', 'ths_daily', 'ths_member', 'anns', 'trade_cal', 'stk_limit', 'fina_audit',
            'fina_mainbz_vip', 'margin', 'margin_detail', 'margin_target', 'top10_holders', 'top10_floatholders',
            'top_list', 'top_inst', 'fund_adj', 'fund_company', 'fund_div', 'fund_manager', 'fund_nav',
            'fund_portfolio', 'fund_sales_ratio', 'fund_sales_vol', 'fund_share', 'fund_daily', 'index_basic',
            'index_daily', 'index_dailybasic', 'index_classify', 'index_member', 'ths_index', 'index_global',
            'index_weekly', 'index_monthly', 'index_weight', 'daily_info', 'sz_daily_info', 'cn_cpi', 'cn_gdp', 'cn_m',
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

        if name == 'stock_company':
            stock_company_module = import_module("tutake.api.ts.stock_company")
            clazz = getattr(stock_company_module, "StockCompany")
            return clazz(config)
        if name == 'hk_hold':
            hk_hold_module = import_module("tutake.api.ts.hk_hold")
            clazz = getattr(hk_hold_module, "HkHold")
            return clazz(config)
        if name == 'stk_rewards':
            stk_rewards_module = import_module("tutake.api.ts.stk_rewards")
            clazz = getattr(stk_rewards_module, "StkRewards")
            return clazz(config)
        if name == 'hs_const':
            hs_const_module = import_module("tutake.api.ts.hs_const")
            clazz = getattr(hs_const_module, "HsConst")
            return clazz(config)
        if name == 'report_rc':
            report_rc_module = import_module("tutake.api.ts.report_rc")
            clazz = getattr(report_rc_module, "ReportRc")
            return clazz(config)
        if name == 'stk_managers':
            stk_managers_module = import_module("tutake.api.ts.stk_managers")
            clazz = getattr(stk_managers_module, "StkManagers")
            return clazz(config)
        if name == 'moneyflow_hsgt':
            moneyflow_hsgt_module = import_module("tutake.api.ts.moneyflow_hsgt")
            clazz = getattr(moneyflow_hsgt_module, "MoneyflowHsgt")
            return clazz(config)
        if name == 'fx_obasic':
            fx_obasic_module = import_module("tutake.api.ts.fx_obasic")
            clazz = getattr(fx_obasic_module, "FxObasic")
            return clazz(config)
        if name == 'namechange':
            namechange_module = import_module("tutake.api.ts.namechange")
            clazz = getattr(namechange_module, "Namechange")
            return clazz(config)
        if name == 'shibor_lpr':
            shibor_lpr_module = import_module("tutake.api.ts.shibor_lpr")
            clazz = getattr(shibor_lpr_module, "ShiborLpr")
            return clazz(config)
        if name == 'ccass_hold':
            ccass_hold_module = import_module("tutake.api.ts.ccass_hold")
            clazz = getattr(ccass_hold_module, "CcassHold")
            return clazz(config)
        if name == 'stock_vx':
            stock_vx_module = import_module("tutake.api.ts.stock_vx")
            clazz = getattr(stock_vx_module, "StockVx")
            return clazz(config)
        if name == 'bak_daily':
            bak_daily_module = import_module("tutake.api.ts.bak_daily")
            clazz = getattr(bak_daily_module, "BakDaily")
            return clazz(config)
        if name == 'fx_daily':
            fx_daily_module = import_module("tutake.api.ts.fx_daily")
            clazz = getattr(fx_daily_module, "FxDaily")
            return clazz(config)
        if name == 'suspend_d':
            suspend_d_module = import_module("tutake.api.ts.suspend_d")
            clazz = getattr(suspend_d_module, "SuspendD")
            return clazz(config)
        if name == 'daily':
            daily_module = import_module("tutake.api.ts.daily")
            clazz = getattr(daily_module, "Daily")
            return clazz(config)
        if name == 'weekly':
            weekly_module = import_module("tutake.api.ts.weekly")
            clazz = getattr(weekly_module, "Weekly")
            return clazz(config)
        if name == 'libor':
            libor_module = import_module("tutake.api.ts.libor")
            clazz = getattr(libor_module, "Libor")
            return clazz(config)
        if name == 'stock_mx':
            stock_mx_module = import_module("tutake.api.ts.stock_mx")
            clazz = getattr(stock_mx_module, "StockMx")
            return clazz(config)
        if name == 'ci_daily':
            ci_daily_module = import_module("tutake.api.ts.ci_daily")
            clazz = getattr(ci_daily_module, "CiDaily")
            return clazz(config)
        if name == 'wz_index':
            wz_index_module = import_module("tutake.api.ts.wz_index")
            clazz = getattr(wz_index_module, "WzIndex")
            return clazz(config)
        if name == 'bak_basic':
            bak_basic_module = import_module("tutake.api.ts.bak_basic")
            clazz = getattr(bak_basic_module, "BakBasic")
            return clazz(config)
        if name == 'stock_basic':
            stock_basic_module = import_module("tutake.api.ts.stock_basic")
            clazz = getattr(stock_basic_module, "StockBasic")
            return clazz(config)
        if name == 'shibor':
            shibor_module = import_module("tutake.api.ts.shibor")
            clazz = getattr(shibor_module, "Shibor")
            return clazz(config)
        if name == 'ccass_hold_detail':
            ccass_hold_detail_module = import_module("tutake.api.ts.ccass_hold_detail")
            clazz = getattr(ccass_hold_detail_module, "CcassHoldDetail")
            return clazz(config)
        if name == 'gz_index':
            gz_index_module = import_module("tutake.api.ts.gz_index")
            clazz = getattr(gz_index_module, "GzIndex")
            return clazz(config)
        if name == 'fund_basic':
            fund_basic_module = import_module("tutake.api.ts.fund_basic")
            clazz = getattr(fund_basic_module, "FundBasic")
            return clazz(config)
        if name == 'limit_list_d':
            limit_list_d_module = import_module("tutake.api.ts.limit_list_d")
            clazz = getattr(limit_list_d_module, "LimitListD")
            return clazz(config)
        if name == 'new_share':
            new_share_module = import_module("tutake.api.ts.new_share")
            clazz = getattr(new_share_module, "NewShare")
            return clazz(config)
        if name == 'monthly':
            monthly_module = import_module("tutake.api.ts.monthly")
            clazz = getattr(monthly_module, "Monthly")
            return clazz(config)
        if name == 'us_tycr':
            us_tycr_module = import_module("tutake.api.ts.us_tycr")
            clazz = getattr(us_tycr_module, "UsTycr")
            return clazz(config)
        if name == 'moneyflow':
            moneyflow_module = import_module("tutake.api.ts.moneyflow")
            clazz = getattr(moneyflow_module, "Moneyflow")
            return clazz(config)
        if name == 'adj_factor':
            adj_factor_module = import_module("tutake.api.ts.adj_factor")
            clazz = getattr(adj_factor_module, "AdjFactor")
            return clazz(config)
        if name == 'hibor':
            hibor_module = import_module("tutake.api.ts.hibor")
            clazz = getattr(hibor_module, "Hibor")
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
        if name == 'stk_limit':
            stk_limit_module = import_module("tutake.api.ts.stk_limit")
            clazz = getattr(stk_limit_module, "StkLimit")
            return clazz(config)
        if name == 'fina_audit':
            fina_audit_module = import_module("tutake.api.ts.fina_audit")
            clazz = getattr(fina_audit_module, "FinaAudit")
            return clazz(config)
        if name == 'fina_mainbz_vip':
            fina_mainbz_vip_module = import_module("tutake.api.ts.fina_mainbz_vip")
            clazz = getattr(fina_mainbz_vip_module, "FinaMainbzVip")
            return clazz(config)
        if name == 'margin':
            margin_module = import_module("tutake.api.ts.margin")
            clazz = getattr(margin_module, "Margin")
            return clazz(config)
        if name == 'margin_detail':
            margin_detail_module = import_module("tutake.api.ts.margin_detail")
            clazz = getattr(margin_detail_module, "MarginDetail")
            return clazz(config)
        if name == 'margin_target':
            margin_target_module = import_module("tutake.api.ts.margin_target")
            clazz = getattr(margin_target_module, "MarginTarget")
            return clazz(config)
        if name == 'top10_holders':
            top10_holders_module = import_module("tutake.api.ts.top10_holders")
            clazz = getattr(top10_holders_module, "Top10Holders")
            return clazz(config)
        if name == 'top10_floatholders':
            top10_floatholders_module = import_module("tutake.api.ts.top10_floatholders")
            clazz = getattr(top10_floatholders_module, "Top10Floatholders")
            return clazz(config)
        if name == 'top_list':
            top_list_module = import_module("tutake.api.ts.top_list")
            clazz = getattr(top_list_module, "TopList")
            return clazz(config)
        if name == 'top_inst':
            top_inst_module = import_module("tutake.api.ts.top_inst")
            clazz = getattr(top_inst_module, "TopInst")
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
