
EXAMPLE_SCHEMA = '''
class FinancialTrend(ACLEDEvent, ABC):
    """
    A "Financial Trend" event describes the patterns and tendencies in financial metrics observed over time within a specific sector. For the technology sector, these trends can represent changes in stock prices, market capitalization, revenue growth, investment rates, or other economic indicators relevant to tech companies in the U.S. This event type captures both positive and negative financial developments and can highlight periods of growth, decline, or stability.
    - InvestmentIncrease: Represents a significant rise in investments within the technology sector, including venture capital, private equity, and public market investments.
    - MarketCapGrowth: Reflects an increase in the overall market capitalization of tech companies, indicating a general market valuation increase.
    - RevenueGrowth: Tracks the revenue increases across tech companies, which may result from new products, expansion into new markets, or overall industry growth.
    - StockPriceFluctuation: Captures the variations in stock prices of tech companies, which could be influenced by market trends, company performance, or external economic factors.
    """
    sector: str = Field(..., description="The specific sector under analysis, here being 'technology'.")
    country: str = Field(..., description="The country of interest, here the 'U.S.'.") 
    period: str = Field(..., description="The time frame over which the financial trends are observed.")

class InvestmentReceived(FinancialTrend):
    """
    This subtype of "Financial Trend" is used when there is a significant rise in the level of investments within the technology sector. This can include increases in venture capital funding, growth in private equity stakes, or enhancements in other forms of financial injections into tech companies.
    """
    investment_type: List[str] = Field(..., description="Types of investments observed to increase such as venture capital, private equity, etc.")
    amount: float = Field(..., description="The monetary value of the investment increase.")
    unit: str = Field(..., description="The currency and unit in which the investment increase is measured. Such as Million USD, Billion USD, etc.")
    companies_involved: Optional[List[str]] = Field(None, description="List of key companies that received these investments. Such as technology startups, established tech firms, etc.")

class InvestmentMade(FinancialTrend):
    """
    This subtype of "Financial Trend" is used when there is a significant rise in the level of investments within the technology sector. This can include increases in venture capital funding, growth in private equity stakes, or enhancements in other forms of financial injections into tech companies.
    """
    investment_type: List[str] = Field(..., description="Types of investments observed to increase such as venture capital, private equity, etc.")
    amount: float = Field(..., description="The monetary value of the investment increase.")
    unit: str = Field(..., description="The currency and unit in which the investment increase is measured. Such as Million USD, Billion USD, etc.")
    companies_involved: Optional[List[str]] = Field(None, description="List of key companies that made these investments. Such as venture capital firms, private equity funds, etc.")

class MarketCapGrowth(FinancialTrend):
    """
    This subtype of "Financial Trend" reflects an increase in the overall market capitalization of companies within the technology sector, suggesting a rise in market valuation.
    """
    average_increase_percentage: float = Field(..., description="The average percentage increase in market capitalization.")
    leading_companies: List[str] = Field(..., description="Companies leading in market cap growth.")

class RevenueGrowth(FinancialTrend):
    """
    Represents growth in revenue across technology sector companies, which could be due to factors like market expansion, product launches, or increased consumer demand.
    """
    average_growth_rate: float = Field(..., description="The average revenue growth rate observed.")
    key_contributors: List[str] = Field(..., description="Major companies contributing to this revenue growth.")

class StockPriceFluctuation(FinancialTrend):
    """
    Captures the fluctuations in stock prices of technology sector companies, which can be influenced by various internal and external economic factors.
    """
    volatility_index: float = Field(..., description="A measure of the price volatility observed among tech stocks.")
    impacted_companies: List[str] = Field(..., description="Companies whose stock prices have shown significant fluctuations.")
'''

EXAMPLE_L0_KEYWORDS = [
    'u.s.', 'tech'
]

EXAMPLE_L1_KEYWORDS = [
    'Financial', 'trends', 'Technology sector', 'market', 'Investment', 'Innovation',
    'Growth', 'Market analysis', 'startups', 'Venture capital', 'Economic', 'stock',
    'revenue'
]