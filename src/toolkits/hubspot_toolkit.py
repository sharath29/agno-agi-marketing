"""
HubSpot API Toolkit for Agno-AGI Marketing Automation.

Provides comprehensive CRM operations, contact management, deal tracking,
and marketing automation capabilities through the HubSpot API.
"""

import time
from typing import Dict, List, Optional, Any, Union
import requests
from dataclasses import dataclass, field
from agno import Toolkit, tool
from loguru import logger

from ..config.settings import get_settings
from ..config.logging import log_api_call


@dataclass
class HubSpotContact:
    """HubSpot contact data structure."""
    id: Optional[str] = None
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    company: Optional[str] = None
    jobtitle: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    lifecyclestage: Optional[str] = None
    lead_status: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = {k: v for k, v in self.__dict__.items() if v is not None and k != 'properties'}
        base_dict.update(self.properties)
        return base_dict


@dataclass
class HubSpotDeal:
    """HubSpot deal data structure."""
    id: Optional[str] = None
    dealname: Optional[str] = None
    amount: Optional[float] = None
    dealstage: Optional[str] = None
    pipeline: Optional[str] = None
    closedate: Optional[str] = None
    hubspot_owner_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = {k: v for k, v in self.__dict__.items() if v is not None and k != 'properties'}
        base_dict.update(self.properties)
        return base_dict


@dataclass
class HubSpotCompany:
    """HubSpot company data structure."""
    id: Optional[str] = None
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    numberofemployees: Optional[int] = None
    annualrevenue: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = {k: v for k, v in self.__dict__.items() if v is not None and k != 'properties'}
        base_dict.update(self.properties)
        return base_dict


class HubSpotToolkit(Toolkit):
    """HubSpot API integration toolkit for CRM operations and marketing automation."""
    
    def __init__(self):
        super().__init__(name="hubspot_toolkit")
        self.settings = get_settings()
        self.api_key = self.settings.marketing_apis.hubspot_api_key
        self.base_url = "https://api.hubapi.com"
        self.rate_limit = self.settings.marketing_apis.hubspot_rate_limit
        self.last_request_time = 0
        
        if not self.api_key:
            logger.warning("HubSpot API key not configured")
    
    def _rate_limit_wait(self):
        """Implement rate limiting between API calls."""
        elapsed = time.time() - self.last_request_time
        min_interval = 60 / self.rate_limit  # requests per minute to seconds per request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None, params: Dict = None) -> Dict:
        """Make a rate-limited request to HubSpot API."""
        if not self.api_key:
            raise ValueError("HubSpot API key not configured")
        
        self._rate_limit_wait()
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            duration = time.time() - start_time
            log_api_call("hubspot", endpoint, str(response.status_code), duration)
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HubSpot API request failed: {e}")
            raise

    @tool
    def search_contacts(
        self,
        query: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for contacts in HubSpot CRM.
        
        Args:
            query: General search query
            email: Email address to search for
            company: Company name to filter by
            limit: Maximum number of contacts to return
            
        Returns:
            Dictionary containing matching contacts
        """
        search_data = {
            "limit": min(limit, 100),
            "properties": [
                "email", "firstname", "lastname", "company", "jobtitle",
                "phone", "website", "lifecyclestage", "lead_status"
            ]
        }
        
        filters = []
        if email:
            filters.append({
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            })
        if company:
            filters.append({
                "propertyName": "company",
                "operator": "CONTAINS_TOKEN",
                "value": company
            })
        if query:
            filters.append({
                "propertyName": "email",
                "operator": "CONTAINS_TOKEN",
                "value": query
            })
        
        if filters:
            search_data["filterGroups"] = [{"filters": filters}]
        
        try:
            result = self._make_request("crm/v3/objects/contacts/search", "POST", search_data)
            
            contacts = []
            for contact_data in result.get("results", []):
                props = contact_data.get("properties", {})
                contact = HubSpotContact(
                    id=contact_data.get("id"),
                    email=props.get("email"),
                    firstname=props.get("firstname"),
                    lastname=props.get("lastname"),
                    company=props.get("company"),
                    jobtitle=props.get("jobtitle"),
                    phone=props.get("phone"),
                    website=props.get("website"),
                    lifecyclestage=props.get("lifecyclestage"),
                    lead_status=props.get("lead_status")
                )
                contacts.append(contact.to_dict())
            
            return {
                "contacts": contacts,
                "total": result.get("total", 0),
                "query": query or email or company
            }
            
        except Exception as e:
            logger.error(f"Failed to search contacts: {e}")
            return {"contacts": [], "total": 0, "error": str(e)}

    @tool
    def create_contact(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        company: Optional[str] = None,
        jobtitle: Optional[str] = None,
        phone: Optional[str] = None,
        additional_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new contact in HubSpot CRM.
        
        Args:
            email: Contact email (required)
            firstname: First name
            lastname: Last name
            company: Company name
            jobtitle: Job title
            phone: Phone number
            additional_properties: Additional custom properties
            
        Returns:
            Dictionary containing created contact information
        """
        properties = {"email": email}
        
        if firstname:
            properties["firstname"] = firstname
        if lastname:
            properties["lastname"] = lastname
        if company:
            properties["company"] = company
        if jobtitle:
            properties["jobtitle"] = jobtitle
        if phone:
            properties["phone"] = phone
        if additional_properties:
            properties.update(additional_properties)
        
        contact_data = {"properties": properties}
        
        try:
            result = self._make_request("crm/v3/objects/contacts", "POST", contact_data)
            
            props = result.get("properties", {})
            contact = HubSpotContact(
                id=result.get("id"),
                email=props.get("email"),
                firstname=props.get("firstname"),
                lastname=props.get("lastname"),
                company=props.get("company"),
                jobtitle=props.get("jobtitle"),
                phone=props.get("phone")
            )
            
            return {
                "contact": contact.to_dict(),
                "created": True,
                "id": result.get("id")
            }
            
        except Exception as e:
            logger.error(f"Failed to create contact: {e}")
            return {"contact": None, "created": False, "error": str(e)}

    @tool
    def update_contact(
        self,
        contact_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing contact in HubSpot CRM.
        
        Args:
            contact_id: HubSpot contact ID
            properties: Properties to update
            
        Returns:
            Dictionary containing updated contact information
        """
        update_data = {"properties": properties}
        
        try:
            result = self._make_request(f"crm/v3/objects/contacts/{contact_id}", "PATCH", update_data)
            
            props = result.get("properties", {})
            contact = HubSpotContact(
                id=result.get("id"),
                email=props.get("email"),
                firstname=props.get("firstname"),
                lastname=props.get("lastname"),
                company=props.get("company"),
                jobtitle=props.get("jobtitle"),
                phone=props.get("phone")
            )
            
            return {
                "contact": contact.to_dict(),
                "updated": True
            }
            
        except Exception as e:
            logger.error(f"Failed to update contact: {e}")
            return {"contact": None, "updated": False, "error": str(e)}

    @tool
    def create_deal(
        self,
        dealname: str,
        amount: float,
        dealstage: str,
        contact_id: Optional[str] = None,
        company_id: Optional[str] = None,
        closedate: Optional[str] = None,
        additional_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new deal in HubSpot CRM.
        
        Args:
            dealname: Deal name
            amount: Deal amount
            dealstage: Deal stage
            contact_id: Associated contact ID
            company_id: Associated company ID
            closedate: Expected close date (YYYY-MM-DD)
            additional_properties: Additional custom properties
            
        Returns:
            Dictionary containing created deal information
        """
        properties = {
            "dealname": dealname,
            "amount": str(amount),
            "dealstage": dealstage
        }
        
        if closedate:
            properties["closedate"] = closedate
        if additional_properties:
            properties.update(additional_properties)
        
        deal_data = {"properties": properties}
        
        # Add associations if provided
        if contact_id or company_id:
            associations = []
            if contact_id:
                associations.append({
                    "to": {"id": contact_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}]
                })
            if company_id:
                associations.append({
                    "to": {"id": company_id},
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}]
                })
            deal_data["associations"] = associations
        
        try:
            result = self._make_request("crm/v3/objects/deals", "POST", deal_data)
            
            props = result.get("properties", {})
            deal = HubSpotDeal(
                id=result.get("id"),
                dealname=props.get("dealname"),
                amount=float(props.get("amount", 0)) if props.get("amount") else None,
                dealstage=props.get("dealstage"),
                closedate=props.get("closedate")
            )
            
            return {
                "deal": deal.to_dict(),
                "created": True,
                "id": result.get("id")
            }
            
        except Exception as e:
            logger.error(f"Failed to create deal: {e}")
            return {"deal": None, "created": False, "error": str(e)}

    @tool
    def get_deal_pipeline(self) -> Dict[str, Any]:
        """
        Get deal pipeline stages and information.
        
        Returns:
            Dictionary containing pipeline information
        """
        try:
            result = self._make_request("crm/v3/pipelines/deals")
            
            pipelines = []
            for pipeline in result.get("results", []):
                pipeline_info = {
                    "id": pipeline.get("id"),
                    "label": pipeline.get("label"),
                    "stages": []
                }
                
                for stage in pipeline.get("stages", []):
                    stage_info = {
                        "id": stage.get("id"),
                        "label": stage.get("label"),
                        "displayOrder": stage.get("displayOrder"),
                        "probability": stage.get("metadata", {}).get("probability")
                    }
                    pipeline_info["stages"].append(stage_info)
                
                pipelines.append(pipeline_info)
            
            return {"pipelines": pipelines}
            
        except Exception as e:
            logger.error(f"Failed to get deal pipeline: {e}")
            return {"pipelines": [], "error": str(e)}

    @tool
    def search_companies(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for companies in HubSpot CRM.
        
        Args:
            query: General search query
            domain: Company domain to search for
            industry: Industry to filter by
            limit: Maximum number of companies to return
            
        Returns:
            Dictionary containing matching companies
        """
        search_data = {
            "limit": min(limit, 100),
            "properties": [
                "name", "domain", "industry", "city", "state", "country",
                "numberofemployees", "annualrevenue"
            ]
        }
        
        filters = []
        if domain:
            filters.append({
                "propertyName": "domain",
                "operator": "EQ",
                "value": domain
            })
        if industry:
            filters.append({
                "propertyName": "industry",
                "operator": "CONTAINS_TOKEN",
                "value": industry
            })
        if query:
            filters.append({
                "propertyName": "name",
                "operator": "CONTAINS_TOKEN",
                "value": query
            })
        
        if filters:
            search_data["filterGroups"] = [{"filters": filters}]
        
        try:
            result = self._make_request("crm/v3/objects/companies/search", "POST", search_data)
            
            companies = []
            for company_data in result.get("results", []):
                props = company_data.get("properties", {})
                company = HubSpotCompany(
                    id=company_data.get("id"),
                    name=props.get("name"),
                    domain=props.get("domain"),
                    industry=props.get("industry"),
                    city=props.get("city"),
                    state=props.get("state"),
                    country=props.get("country"),
                    numberofemployees=int(props.get("numberofemployees", 0)) if props.get("numberofemployees") else None,
                    annualrevenue=float(props.get("annualrevenue", 0)) if props.get("annualrevenue") else None
                )
                companies.append(company.to_dict())
            
            return {
                "companies": companies,
                "total": result.get("total", 0),
                "query": query or domain or industry
            }
            
        except Exception as e:
            logger.error(f"Failed to search companies: {e}")
            return {"companies": [], "total": 0, "error": str(e)}

    @tool
    def get_contact_analytics(
        self,
        date_range: int = 30
    ) -> Dict[str, Any]:
        """
        Get contact analytics and metrics.
        
        Args:
            date_range: Number of days to look back
            
        Returns:
            Dictionary containing contact analytics
        """
        try:
            # Get recent contacts
            search_data = {
                "limit": 100,
                "properties": ["email", "lifecyclestage", "lead_status", "createdate"],
                "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}]
            }
            
            result = self._make_request("crm/v3/objects/contacts/search", "POST", search_data)
            
            # Analyze the data
            contacts = result.get("results", [])
            analytics = {
                "total_contacts": len(contacts),
                "lifecycle_stages": {},
                "lead_statuses": {},
                "recent_contacts": len(contacts)
            }
            
            for contact in contacts:
                props = contact.get("properties", {})
                
                # Count lifecycle stages
                stage = props.get("lifecyclestage", "Unknown")
                analytics["lifecycle_stages"][stage] = analytics["lifecycle_stages"].get(stage, 0) + 1
                
                # Count lead statuses
                status = props.get("lead_status", "Unknown")
                analytics["lead_statuses"][status] = analytics["lead_statuses"].get(status, 0) + 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get contact analytics: {e}")
            return {"error": str(e)}