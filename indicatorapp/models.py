from django.db import models


class Item(models.Model):
    '''
    symbol - 종목 코드
    name - 종목 이름
    country - 종목이 상장되어 있는 나라
    market - 종목이 상장된 시장
    sectorName - 섹터명
    sectorSymbol - 섹터 코드
    '''
    symbol = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=20)
    country = models.CharField(max_length=20, null=True, blank=True)
    market = models.CharField(max_length=20, null=True, blank=True)
    sectorName = models.CharField(max_length=25)
    sectorSymbol = models.CharField(max_length=12)

    def __str__(self):
        return f'{self.name}[{self.symbol}]'


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
