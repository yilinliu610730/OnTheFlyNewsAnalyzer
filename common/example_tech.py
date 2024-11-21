# EXAMPLE_QUERY = "What are the financial trends in the technology sector in the U.S.?"

# EXAMPLE_SCHEMA = '''
# class FinancialMetric(Enum):
#     REVENUE_GROWTH = "Revenue Growth"
#     PROFIT_MARGINS = "Profit Margins"
#     STOCK_PERFORMANCE = "Stock Performance"
#     INVESTMENT_LEVELS = "Investment Levels"

# class FinancialEvent(ABC):
#     """
#     A "FinancialEvent" represents a significant occurrence or trend in the financial market, focusing on the technology sector in a specific region or country. These events can include market fluctuations, new technology trends, regulatory changes, mergers and acquisitions, or investment patterns.
#     "FinancialEvent" has the following subtypes:
#     - MarketFluctuation: Occurrences of significant changes in stock prices, market indices, or investor sentiment.
#     - RegulatoryChange: Introduction or modification of regulations affecting the technology sector.
#     - MergerAndAcquisition: Events involving the consolidation of companies or assets in the technology sector.
#     - InvestmentTrend: Patterns or shifts in investment within the technology industry, such as venture capital trends or funding rounds.
#     """
#     location: str = Field(..., description="Location or region where the financial event is observed")
#     sector: str = Field(..., description="Sector to which the financial event pertains, e.g., technology")
#     year: int = Field(2024, description="The time during which the financial event occurs, has to be 2024 otherwise ignore the event")
#     metrics: Optional[List[FinancialMetric]] = Field(None, description="List of selected financial metrics for evaluation")
#     macroeconomic_factors: List[str] = Field(..., description="List of macroeconomic factors impacting financial trends, e.g., interest rates, inflation")
#     focus_on_regulation_influence: bool = Field(..., description="Indicates interest in the influence of government policies or regulations on financial trends")
#     focus_on_technological_innovations: bool = Field(..., description="Indicates focus on the impact of recent technological innovations or disruptions on financial performance")

# class MarketFluctuation(FinancialEvent):
#     """
#     Is a type of "FinancialEvent". This event type is used to record significant changes in stock prices, market indices, or investor sentiment within the technology sector. It includes sudden spikes or drops in market value.
#     """
#     affected_party: List[str] = Field(..., description="Company name or market indices affected by the fluctuation, e.g., NVIDIA, NVDA, NASDAQ, S&P 500")
#     price_change: List[str] = Field(..., description="Change in price, in USD")
#     percentage_change: List[str] = Field(..., description="Change in percentage price")
#     reason: Optional[str] = Field(..., description="Reason for the fluctation, if known")

# class RegulatoryChange(FinancialEvent):
#     """
#     Is a type of "FinancialEvent". This event type is used when new regulations are introduced or existing regulations are modified, affecting the technology sector. These changes can impact industry practices, compliance requirements, and overall market stability.
#     """
#     regulation_details: str = Field(..., description="Details of the regulatory change and its implications")
#     regulatory_body: str = Field(..., description="The body or institution responsible for the regulatory change")

# class MergerAndAcquisition(FinancialEvent):
#     """
#     Is a type of "FinancialEvent". This event type involves activities related to the consolidation of companies or assets within the technology sector. It includes mergers, acquisitions, and significant partnerships.
#     """
#     companies_involved: List[str] = Field(..., description="List of companies involved in the merger or acquisition")
#     acquisition_value: Optional[float] = Field(..., description="Monetary value of the merger or acquisition, if disclosed")

# class InvestmentTrend(FinancialEvent):
#     """
#     Is a type of "FinancialEvent". This event type captures patterns or shifts in investment within the technology industry, such as venture capital trends, funding rounds, or new investment vehicles.
#     """
#     investment_type: str = Field(..., description="Type of investment trend observed, e.g., venture capital, IPOs")
#     notable_investments: List[str] = Field(..., description="List of notable investments or funding rounds in the technology sector")
#     investor_groups: List[str] = Field(..., description="Groups or entities leading the investment trends")
# '''

# EXAMPLE_L0_KEYWORDS = ['u.s.', 'tech', 'financ']

# EXAMPLE_L1_KEYWORDS = [
#     'financial', 'trends', 'invest', 'innovation',
#     'growth', 'market analysis', 'startups', 'venture capital', 'economic', 'stock',
#     'revenue'
# ]


EXAMPLE_QUERY = "What are the financial trends in the technology sector in the U.S.?"

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
    macroeconomic_factors: List[str] = Field(..., description="List of macroeconomic factors impacting financial trends, e.g., interest rates, inflation")
    all_company_sizes: bool = Field(True, description="Indicates focus on all company sizes from startups to large multinationals")
    focus_on_regulation_influence: bool = Field(True, description="Indicates interest in the influence of government policies or regulations on financial trends")
    focus_on_technological_innovations: bool = Field(False, description="Indicates focus on the impact of recent technological innovations or disruptions on financial performance")
    preferred_data_sources: Optional[List[str]] = Field(None, description="List of preferred data sources or reports for gathering financial information, if any")

class MarketFluctuation(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type is used to record significant changes in stock prices, market indices, or investor sentiment within the technology sector. It includes sudden spikes or drops in market value.
    """
    affected_indices: List[str] = Field(..., description="Market indices affected by the fluctuation, e.g., NASDAQ, S&P 500")
    stock_changes: List[str] = Field(..., description="List of significant stock changes in the technology sector")
    investor_sentiment: Optional[str] = Field(..., description="General investor sentiment during the fluctuation, if known")

class RegulatoryChange(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type is used when new regulations are introduced or existing regulations are modified, affecting the technology sector. These changes can impact industry practices, compliance requirements, and overall market stability.
    """
    regulation_details: str = Field(..., description="Details of the regulatory change and its implications")
    regulatory_body: str = Field(..., description="The body or institution responsible for the regulatory change")

class MergerAndAcquisition(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type involves activities related to the consolidation of companies or assets within the technology sector. It includes mergers, acquisitions, and significant partnerships.
    """
    companies_involved: List[str] = Field(..., description="List of companies involved in the merger or acquisition")
    acquisition_value: Optional[float] = Field(..., description="Monetary value of the merger or acquisition, if disclosed")

class InvestmentTrend(FinancialEvent):
    """
    Is a type of "FinancialEvent". This event type captures patterns or shifts in investment within the technology industry, such as venture capital trends, funding rounds, or new investment vehicles.
    """
    investment_type: str = Field(..., description="Type of investment trend observed, e.g., venture capital, IPOs")
    notable_investments: List[str] = Field(..., description="List of notable investments or funding rounds in the technology sector")
    investor_groups: List[str] = Field(..., description="Groups or entities leading the investment trends")
'''

EXAMPLE_L0_KEYWORDS = [
    'u.s.', 'tech'
]

EXAMPLE_L1_KEYWORDS = [
    'Financial', 'trends', 'market', 'Investment', 'Innovation',
    'Growth', 'Market analysis', 'startups', 'Venture capital', 'Economic', 'stock',
    'revenue'
]