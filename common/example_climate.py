EXAMPLE_QUERY = "How did the U.S. reacted to climate change in the past year?"

EXAMPLE_SCHEMA = '''
class GovernmentLevel(Enum):
    FEDERAL = "Federal Government"
    STATE = "State Government"
    BOTH = "Both Federal and State Governments"

class GovernmentActionType(Enum):
    LEGISLATIVE = "Legislative Measures"
    EXECUTIVE = "Executive Actions"
    JUDICIAL = "Judicial Decisions"

class ClimateResponse(ABC):
    """
    A "ClimateResponse" event is a structured representation of actions, policies, or events related to climate change. These events encompass a wide range of activities undertaken by governments, organizations, and individuals to address, mitigate, or adapt to climate change impacts.
    
    "ClimateResponse" event type has the following subtypes:
    - PolicyImplementation: Introduction or enactment of policies aimed at mitigating climate change effects.
    - PublicAwarenessCampaign: Efforts to educate and raise awareness among the public about climate change.
    - TechnologicalInnovation: Development and deployment of new technologies to combat climate change.
    """
    location: str = Field(..., description="Location where the climate response takes place")
    date: str = Field(..., description="Date when the event occurred")
    description: str = Field(..., description="Brief description of the climate response event")

class PolicyImplementation(ClimateResponse):
    """
    Is a type of "ClimateResponse" event. This event type involves the introduction or enactment of policies aimed at mitigating climate change effects. It includes governmental policies, regulations, and international agreements.
    """
    policies_enacted: List[str] = Field(
        ...,
        description="List of policies or regulations enacted to address climate change"
    )
    responsible_agency: str = Field(
        ..., 
        description="Government agency or organization responsible for the policy implementation"
    )
    government_level: GovernmentLevel = Field(
        GovernmentLevel.BOTH,
        description="Level of government involved in the policy implementation"
    )
    action_type: GovernmentActionType = Field(
        GovernmentActionType.LEGISLATIVE,
        description="Type of government action related to climate change"
    )

class PublicAwarenessCampaign(ClimateResponse):
    """
    Is a type of "ClimateResponse" event. This event type involves efforts to educate and raise awareness among the public about climate change. It includes campaigns, educational programs, and media outreach.
    """
    campaign_name: str = Field(
        ..., 
        description="Name of the public awareness campaign"
    )
    target_audience: List[str] = Field(
        ..., 
        description="Target audience groups for the campaign"
    )
    mediums_used: List[str] = Field(
        ..., 
        description="Mediums used for disseminating the campaign message (e.g., social media, TV, flyers)"
    )

class TechnologicalInnovation(ClimateResponse):
    """
    Is a type of "ClimateResponse" event. This event type involves the development and deployment of new technologies to combat climate change. It includes innovations in renewable energy, carbon capture, and sustainable practices.
    """
    technology_name: str = Field(
        ..., 
        description="Name of the technology or innovation"
    )
    sector: str = Field(
        ..., 
        description="Sector in which the technology is applied (e.g., energy, transportation, agriculture)"
    )
    impact: str = Field(
        ..., 
        description="Expected or observed impact of the technology on climate change mitigation"
    )
'''

EXAMPLE_L0_KEYWORDS = [
    'u.s.', 'climate'
]

EXAMPLE_L1_KEYWORDS = ['United States', 'climate change', 'federal government', 'legislative measures', 'state governments']