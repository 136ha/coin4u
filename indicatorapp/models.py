from django.db import models

class Ohlcv(models.Model):
    '''
    symbol - 종목 코드
    interval - 종목 시간 단위
    timestamp - 캔들차트가 완성된 시간
    open - 시가
    high - 고가
    low - 저가
    close - 종가
    volume - 거래량
    '''
    symbol = models.CharField(max_length=12)
    interval = models.CharField(max_length=8)
    timestamp = models.DateTimeField()
    Open = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    High = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    Low = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    Close = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    Volume = models.DecimalField(max_digits=20, decimal_places=0, null=True, blank=True)

    def __str__(self):
        return f'[{self.symbol}]{self.timestamp.strftime("%Y-%m-%d")}'


class USBureauEvent(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.name


class FinancialStatement(models.Model):
    '''
    Balance sheet, income statement, cash flow
    market_cap - 시가총액
    revenue - 매출
    net_income - 순이익
    cost_and_expenses - 비용
    depreciation_and_amortization - 감가상각
    total_current_assets - 유동자산
    total_current_liabilities - 유동부채
    total_non_current_liabilities - 비유동부채
    EBITDA - 이자, 세금, 감가상각비, 무형자산상각비 차감 전 이익
    net_debt - 순차입금
    cash_flow_from_operations - 영업 현금 흐름
    cash_flow_from_investing = 투자 현금 흐름
    cash_flow_from_financing = 재무 현금 흐름
    cash_beginning_of_period - 기초 현금 자산
    cash_end_of_period - 기말 현금 자산
    gross_profit_ratio - 매출총이익률
    EBITDA_ratio - EBITDA률
    operating_income_ratio - 영업이익률
    net_income_ratio - 당기순이익률
    '''
    symbol = models.CharField(max_length=15)
    year = models.CharField(max_length=4)
    # market_cap = models.IntegerField(null=True, blank=True)
    revenue = models.IntegerField(null=True, blank=True)
    net_income = models.IntegerField(null=True, blank=True)
    net_debt = models.IntegerField(null=True, blank=True)
    EBITDA = models.IntegerField(null=True, blank=True)
    cost_and_expenses = models.IntegerField(null=True, blank=True)
    depreciation_and_amortization = models.IntegerField(null=True, blank=True)
    total_current_assets = models.IntegerField(null=True, blank=True)
    total_current_liabilities = models.IntegerField(null=True, blank=True)
    total_non_current_liabilities = models.IntegerField(null=True, blank=True)
    cash_flow_from_operations = models.IntegerField(null=True, blank=True)
    cash_flow_from_investing = models.IntegerField(null=True, blank=True)
    cash_flow_from_financing = models.IntegerField(null=True, blank=True)
    cash_beginning_of_period = models.IntegerField(null=True, blank=True)
    cash_end_of_period = models.IntegerField(null=True, blank=True)
    gross_profit_ratio = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    EBITDA_ratio = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    operating_income_ratio = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    net_income_ratio = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    # earnings_yield = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)
    # return_on_capital = models.DecimalField(max_digits=7, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f'[{self.year}]{self.symbol}'