EXAMPLE_QUERY = "What are the financial trends in the technology sector in the U.S.?"
EXAMPLE_SCHEMA_OLD = '''
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

EXAMPLE_SCHEMA = '''
class FinancialMetric(Enum):
    REVENUE_GROWTH = "Revenue Growth"
    PROFIT_MARGINS = "Profit Margins"
    STOCK_PERFORMANCE = "Stock Performance"
    INVESTMENT_LEVELS = "Investment Levels"

class FinancialEvent(ABC):
    """
    A "FinancialEvent" represents a significant occurrence or trend in the financial market, focusing on the technology sector in a specific region or country. These events can include market fluctuations, new technology trends, regulatory changes, mergers and acquisitions, or investment patterns.
    "FinancialEvent" has the following subtypes:
    - MarketFluctuation: Occurrences of significant changes in stock prices, market indices, or investor sentiment.
    - RegulatoryChange: Introduction or modification of regulations affecting the technology sector.
    - MergerAndAcquisition: Events involving the consolidation of companies or assets in the technology sector.
    - InvestmentTrend: Patterns or shifts in investment within the technology industry, such as venture capital trends or funding rounds.
    """
    location: str = Field(..., description="Location or region where the financial event is observed")
    sector: str = Field(..., description="Sector to which the financial event pertains, e.g., technology")
    date: datetime = Field(..., description="The time during which the financial event occurs")
    is_software: bool = Field(True, description="Indicates focus on software segment")
    metrics: Optional[List[FinancialMetric]] = Field(None, description="List of selected financial metrics for evaluation")
    is_national: bool = Field(True, description="Indicates focus on national-level trends within the U.S.")
    macroeconomic_factors: List[str] = Field(
        ..., description="List of macroeconomic factors impacting financial trends, e.g., interest rates, inflation"
    )
    all_company_sizes: bool = Field(True, description="Indicates focus on all company sizes from startups to large multinationals")
    focus_on_regulation_influence: bool = Field(True, description="Indicates interest in the influence of government policies or regulations on financial trends")
    focus_on_technological_innovations: bool = Field(False, description="Indicates focus on the impact of recent technological innovations or disruptions on financial performance")
    preferred_data_sources: Optional[List[str]] = Field(
        None, description="List of preferred data sources or reports for gathering financial information, if any"
    )

class MarketFluctuation(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type is used to record significant changes in stock prices, market indices, or investor sentiment within the technology sector. It includes sudden spikes or drops in market value.
    """
    affected_indices: List[str] = Field(
        ..., description="Market indices affected by the fluctuation, e.g., NASDAQ, S&P 500"
    )
    stock_changes: List[str] = Field(
        ..., description="List of significant stock changes in the technology sector"
    )
    investor_sentiment: Optional[str] = Field(
        ..., description="General investor sentiment during the fluctuation, if known"
    )

class RegulatoryChange(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type is used when new regulations are introduced or existing regulations are modified, affecting the technology sector. These changes can impact industry practices, compliance requirements, and overall market stability.
    """
    regulation_details: str = Field(
        ..., description="Details of the regulatory change and its implications"
    )
    regulatory_body: str = Field(
        ..., description="The body or institution responsible for the regulatory change"
    )

class MergerAndAcquisition(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type involves activities related to the consolidation of companies or assets within the technology sector. It includes mergers, acquisitions, and significant partnerships.
    """
    companies_involved: List[str] = Field(
        ..., description="List of companies involved in the merger or acquisition"
    )
    acquisition_value: Optional[float] = Field(
        ..., description="Monetary value of the merger or acquisition, if disclosed"
    )

class InvestmentTrend(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type captures patterns or shifts in investment within the technology industry, such as venture capital trends, funding rounds, or new investment vehicles.
    """
    investment_type: str = Field(
        ..., description="Type of investment trend observed, e.g., venture capital, IPOs"
    )
    notable_investments: List[str] = Field(
        ..., description="List of notable investments or funding rounds in the technology sector"
    )
    investor_groups: List[str] = Field(
        ..., description="Groups or entities leading the investment trends"
    )
'''

EXAMPLE_L0_KEYWORDS = [
    'u.s.', 'tech'
]

EXAMPLE_L1_KEYWORDS = [
    'Financial', 'trends', 'market', 'Investment', 'Innovation',
    'Growth', 'Market analysis', 'startups', 'Venture capital', 'Economic', 'stock',
    'revenue'
]