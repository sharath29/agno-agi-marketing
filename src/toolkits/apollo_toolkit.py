"""
Apollo.io API Toolkit for Agno-AGI Marketing Automation.

Provides comprehensive lead enrichment, contact search, and company data retrieval
capabilities through the Apollo.io API.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from agno.tools import Toolkit, tool
from loguru import logger

from config.logging import log_api_call
from config.settings import get_settings


@dataclass
class Contact:
    """Contact data structure from Apollo."""

    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Company:
    """Company data structure from Apollo."""

    id: Optional[str] = None
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    revenue: Optional[str] = None
    technologies: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ApolloToolkit(Toolkit):
    """Apollo.io API integration toolkit for lead generation and enrichment."""

    def __init__(self):
        super().__init__(name="apollo_toolkit")
        self.settings = get_settings()
        self.api_key = self.settings.marketing_apis.apollo_api_key
        self.base_url = "https://api.apollo.io/v1"
        self.rate_limit = self.settings.marketing_apis.apollo_rate_limit
        self.last_request_time = 0

        if not self.api_key:
            logger.warning("Apollo API key not configured")

    def _rate_limit_wait(self):
        """Implement rate limiting between API calls."""
        elapsed = time.time() - self.last_request_time
        min_interval = 60 / self.rate_limit  # requests per minute to seconds per request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make a rate-limited request to Apollo API."""
        if not self.api_key:
            raise ValueError("Apollo API key not configured")

        self._rate_limit_wait()

        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            else:
                response = requests.post(url, headers=headers, json=data)

            duration = time.time() - start_time
            log_api_call("apollo", endpoint, str(response.status_code), duration)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Apollo API request failed: {e}")
            raise

    @tool
    def search_people(
        self,
        query: Optional[str] = None,
        company_names: Optional[List[str]] = None,
        titles: Optional[List[str]] = None,
        industries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        seniority_levels: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Dict[str, Any]:
        """
        Search for contacts using Apollo's people search API.

        Args:
            query: General search query
            company_names: List of company names to filter by
            titles: List of job titles to filter by
            industries: List of industries to filter by
            locations: List of locations to filter by
            seniority_levels: List of seniority levels (e.g., "executive", "director")
            page: Page number for pagination
            per_page: Number of results per page

        Returns:
            Dictionary containing contacts and pagination info
        """
        data = {"page": page, "per_page": min(per_page, 100)}  # Apollo max is 100

        if query:
            data["q"] = query
        if company_names:
            data["organization_names"] = company_names
        if titles:
            data["person_titles"] = titles
        if industries:
            data["organization_industry_tag_ids"] = industries
        if locations:
            data["person_locations"] = locations
        if seniority_levels:
            data["person_seniority"] = seniority_levels

        try:
            result = self._make_request("mixed_people/search", "POST", data)

            contacts = []
            for person in result.get("people", []):
                contact = Contact(
                    id=person.get("id"),
                    first_name=person.get("first_name"),
                    last_name=person.get("last_name"),
                    name=person.get("name"),
                    email=person.get("email"),
                    title=person.get("title"),
                    company_name=person.get("organization", {}).get("name"),
                    linkedin_url=person.get("linkedin_url"),
                    phone=person.get("phone"),
                )
                contacts.append(contact.to_dict())

            return {
                "contacts": contacts,
                "total_entries": result.get("total_entries", 0),
                "page": result.get("page", page),
                "per_page": result.get("per_page", per_page),
                "num_pages": result.get("num_pages", 0),
            }

        except Exception as e:
            logger.error(f"Failed to search people: {e}")
            return {"contacts": [], "error": str(e)}

    @tool
    def search_organizations(
        self,
        query: Optional[str] = None,
        industries: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        size_ranges: Optional[List[str]] = None,
        revenue_ranges: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 25,
    ) -> Dict[str, Any]:
        """
        Search for companies using Apollo's organization search API.

        Args:
            query: General search query
            industries: List of industries to filter by
            locations: List of locations to filter by
            size_ranges: List of company size ranges (e.g., "1-10", "11-50")
            revenue_ranges: List of revenue ranges
            technologies: List of technologies used by the company
            page: Page number for pagination
            per_page: Number of results per page

        Returns:
            Dictionary containing companies and pagination info
        """
        data = {"page": page, "per_page": min(per_page, 100)}

        if query:
            data["q"] = query
        if industries:
            data["organization_industry_tag_ids"] = industries
        if locations:
            data["organization_locations"] = locations
        if size_ranges:
            data["organization_num_employees_ranges"] = size_ranges
        if revenue_ranges:
            data["organization_revenue_ranges"] = revenue_ranges
        if technologies:
            data["technology_names"] = technologies

        try:
            result = self._make_request("mixed_companies/search", "POST", data)

            companies = []
            for org in result.get("organizations", []):
                company = Company(
                    id=org.get("id"),
                    name=org.get("name"),
                    domain=org.get("primary_domain"),
                    industry=(
                        org.get("primary_industry", {}).get("industry")
                        if org.get("primary_industry")
                        else None
                    ),
                    size=org.get("employee_count"),
                    location=(
                        org.get("primary_phone", {}).get("source")
                        if org.get("primary_phone")
                        else None
                    ),
                    revenue=org.get("estimated_num_employees"),
                    technologies=[tech.get("name") for tech in org.get("technologies", [])],
                )
                companies.append(company.to_dict())

            return {
                "companies": companies,
                "total_entries": result.get("total_entries", 0),
                "page": result.get("page", page),
                "per_page": result.get("per_page", per_page),
                "num_pages": result.get("num_pages", 0),
            }

        except Exception as e:
            logger.error(f"Failed to search organizations: {e}")
            return {"companies": [], "error": str(e)}

    @tool
    def enrich_contact(self, email: str) -> Dict[str, Any]:
        """
        Enrich a contact's information using their email address.

        Args:
            email: Email address to enrich

        Returns:
            Dictionary containing enriched contact information
        """
        data = {"email": email}

        try:
            result = self._make_request("people/match", "POST", data)

            if result.get("person"):
                person = result["person"]
                contact = Contact(
                    id=person.get("id"),
                    first_name=person.get("first_name"),
                    last_name=person.get("last_name"),
                    name=person.get("name"),
                    email=person.get("email"),
                    title=person.get("title"),
                    company_name=person.get("organization", {}).get("name"),
                    linkedin_url=person.get("linkedin_url"),
                    phone=person.get("phone"),
                )
                return {"contact": contact.to_dict(), "enriched": True}
            else:
                return {"contact": None, "enriched": False, "message": "Contact not found"}

        except Exception as e:
            logger.error(f"Failed to enrich contact: {e}")
            return {"contact": None, "enriched": False, "error": str(e)}

    @tool
    def enrich_company(self, domain: str) -> Dict[str, Any]:
        """
        Enrich a company's information using their domain.

        Args:
            domain: Company domain to enrich

        Returns:
            Dictionary containing enriched company information
        """
        data = {"domain": domain}

        try:
            result = self._make_request("organizations/enrich", "POST", data)

            if result.get("organization"):
                org = result["organization"]
                company = Company(
                    id=org.get("id"),
                    name=org.get("name"),
                    domain=org.get("primary_domain"),
                    industry=(
                        org.get("primary_industry", {}).get("industry")
                        if org.get("primary_industry")
                        else None
                    ),
                    size=org.get("employee_count"),
                    location=(
                        org.get("primary_phone", {}).get("source")
                        if org.get("primary_phone")
                        else None
                    ),
                    revenue=org.get("estimated_num_employees"),
                    technologies=[tech.get("name") for tech in org.get("technologies", [])],
                )
                return {"company": company.to_dict(), "enriched": True}
            else:
                return {"company": None, "enriched": False, "message": "Company not found"}

        except Exception as e:
            logger.error(f"Failed to enrich company: {e}")
            return {"company": None, "enriched": False, "error": str(e)}

    @tool
    def get_contact_details(self, contact_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific contact.

        Args:
            contact_id: Apollo contact ID

        Returns:
            Dictionary containing detailed contact information
        """
        try:
            result = self._make_request(f"people/{contact_id}")

            if result.get("person"):
                person = result["person"]
                contact = Contact(
                    id=person.get("id"),
                    first_name=person.get("first_name"),
                    last_name=person.get("last_name"),
                    name=person.get("name"),
                    email=person.get("email"),
                    title=person.get("title"),
                    company_name=person.get("organization", {}).get("name"),
                    linkedin_url=person.get("linkedin_url"),
                    phone=person.get("phone"),
                )
                return {"contact": contact.to_dict(), "found": True}
            else:
                return {"contact": None, "found": False, "message": "Contact not found"}

        except Exception as e:
            logger.error(f"Failed to get contact details: {e}")
            return {"contact": None, "found": False, "error": str(e)}

    @tool
    def find_similar_companies(self, company_domain: str, limit: int = 10) -> Dict[str, Any]:
        """
        Find companies similar to the specified company.

        Args:
            company_domain: Domain of the reference company
            limit: Maximum number of similar companies to return

        Returns:
            Dictionary containing similar companies
        """
        try:
            # First get the company details
            company_data = self.enrich_company(company_domain)
            if not company_data.get("enriched"):
                return {"companies": [], "error": "Reference company not found"}

            ref_company = company_data["company"]

            # Search for companies with similar characteristics
            search_params = {"per_page": limit}

            if ref_company.get("industry"):
                search_params["industries"] = [ref_company["industry"]]
            if ref_company.get("size"):
                search_params["size_ranges"] = [ref_company["size"]]
            if ref_company.get("technologies"):
                search_params["technologies"] = ref_company["technologies"][:3]  # Limit to first 3

            result = self.search_organizations(**search_params)

            # Filter out the reference company
            similar_companies = [
                company
                for company in result.get("companies", [])
                if company.get("domain") != company_domain
            ]

            return {
                "companies": similar_companies[:limit],
                "reference_company": ref_company,
                "total_found": len(similar_companies),
            }

        except Exception as e:
            logger.error(f"Failed to find similar companies: {e}")
            return {"companies": [], "error": str(e)}
