"""
BuiltWith API Toolkit for Agno-AGI Marketing Automation.

Provides technology stack analysis, competitor research, and technical profiling
capabilities through the BuiltWith API.
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
class Technology:
    """Technology information from BuiltWith."""

    name: str
    category: Optional[str] = None
    version: Optional[str] = None
    first_detected: Optional[str] = None
    last_detected: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class TechProfile:
    """Complete technology profile for a domain."""

    domain: str
    technologies: List[Technology]
    categories: Dict[str, int]
    total_technologies: int
    profile_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "technologies": [tech.to_dict() for tech in self.technologies],
            "categories": self.categories,
            "total_technologies": self.total_technologies,
            "profile_date": self.profile_date,
        }


class BuiltWithToolkit(Toolkit):
    """BuiltWith API integration toolkit for technology stack analysis."""

    def __init__(self):
        super().__init__(name="builtwith_toolkit")
        self.settings = get_settings()
        self.api_key = self.settings.marketing_apis.builtwith_api_key
        self.base_url = "https://api.builtwith.com"
        self.last_request_time = 0

        if not self.api_key:
            logger.warning("BuiltWith API key not configured")

    def _rate_limit_wait(self):
        """Implement rate limiting between API calls."""
        elapsed = time.time() - self.last_request_time
        min_interval = 1.0  # 1 second between requests
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a rate-limited request to BuiltWith API."""
        if not self.api_key:
            raise ValueError("BuiltWith API key not configured")

        self._rate_limit_wait()

        url = f"{self.base_url}/{endpoint}"
        default_params = {"KEY": self.api_key}
        if params:
            default_params.update(params)

        start_time = time.time()
        try:
            response = requests.get(url, params=default_params)
            duration = time.time() - start_time
            log_api_call("builtwith", endpoint, str(response.status_code), duration)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"BuiltWith API request failed: {e}")
            raise

    @tool
    def get_domain_technologies(self, domain: str) -> Dict[str, Any]:
        """
        Get comprehensive technology stack for a domain.

        Args:
            domain: Domain to analyze (e.g., "example.com")

        Returns:
            Dictionary containing technology stack information
        """
        try:
            result = self._make_request("v20/api.json", {"LOOKUP": domain})

            if not result.get("Results"):
                return {
                    "domain": domain,
                    "technologies": [],
                    "categories": {},
                    "total_technologies": 0,
                    "error": "No data found for domain",
                }

            domain_data = result["Results"][0]
            technologies = []
            categories = {}

            # Process all technology categories
            for result_item in domain_data.get("Result", {}).get("Paths", []):
                for tech_category in result_item.get("Technologies", []):
                    category_name = tech_category.get("Name", "Unknown")
                    categories[category_name] = categories.get(category_name, 0)

                    for tech in tech_category.get("Categories", []):
                        tech_name = tech.get("Name", "Unknown")

                        technology = Technology(
                            name=tech_name,
                            category=category_name,
                            first_detected=tech.get("FirstDetected"),
                            last_detected=tech.get("LastDetected"),
                        )
                        technologies.append(technology)
                        categories[category_name] += 1

            profile = TechProfile(
                domain=domain,
                technologies=technologies,
                categories=categories,
                total_technologies=len(technologies),
                profile_date=domain_data.get("FirstIndexed"),
            )

            return profile.to_dict()

        except Exception as e:
            logger.error(f"Failed to get domain technologies: {e}")
            return {
                "domain": domain,
                "technologies": [],
                "categories": {},
                "total_technologies": 0,
                "error": str(e),
            }

    @tool
    def find_companies_using_technology(
        self, technology: str, country: Optional[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Find companies that use a specific technology.

        Args:
            technology: Technology name to search for
            country: Country to filter by (optional)
            limit: Maximum number of companies to return

        Returns:
            Dictionary containing companies using the technology
        """
        params = {"TECH": technology, "SINCE": ""}
        if country:
            params["COUNTRY"] = country

        try:
            result = self._make_request("v20/api.json", params)

            companies = []
            if result.get("Results"):
                for company in result["Results"][:limit]:
                    company_info = {
                        "domain": company.get("Domain"),
                        "country": company.get("Country"),
                        "first_detected": company.get("FirstIndexed"),
                        "last_detected": company.get("LastIndexed"),
                        "vertical": company.get("Vertical"),
                    }
                    companies.append(company_info)

            return {
                "technology": technology,
                "companies": companies,
                "total_found": len(companies),
                "country_filter": country,
            }

        except Exception as e:
            logger.error(f"Failed to find companies using technology: {e}")
            return {"technology": technology, "companies": [], "total_found": 0, "error": str(e)}

    @tool
    def get_technology_trends(self, technology: str, months: int = 12) -> Dict[str, Any]:
        """
        Get adoption trends for a specific technology.

        Args:
            technology: Technology name to analyze
            months: Number of months to look back

        Returns:
            Dictionary containing trend data
        """
        try:
            result = self._make_request(
                "trends1/api.json", {"TECH": technology, "MONTHS": str(months)}
            )

            if not result.get("Results"):
                return {"technology": technology, "trends": [], "error": "No trend data available"}

            trends = []
            for trend_item in result["Results"]:
                trend = {
                    "date": trend_item.get("Date"),
                    "count": trend_item.get("Count"),
                    "percentage": trend_item.get("Percent"),
                }
                trends.append(trend)

            return {
                "technology": technology,
                "trends": trends,
                "period_months": months,
                "latest_count": trends[-1]["count"] if trends else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get technology trends: {e}")
            return {"technology": technology, "trends": [], "error": str(e)}

    @tool
    def compare_technology_stacks(self, domains: List[str]) -> Dict[str, Any]:
        """
        Compare technology stacks across multiple domains.

        Args:
            domains: List of domains to compare

        Returns:
            Dictionary containing comparison analysis
        """
        if len(domains) > 10:
            domains = domains[:10]  # Limit to prevent excessive API calls

        try:
            profiles = {}
            all_technologies = set()

            for domain in domains:
                profile = self.get_domain_technologies(domain)
                if not profile.get("error"):
                    profiles[domain] = profile
                    for tech in profile["technologies"]:
                        all_technologies.add(tech["name"])

            # Create comparison matrix
            comparison = {
                "domains": list(profiles.keys()),
                "technology_matrix": {},
                "common_technologies": [],
                "unique_technologies": {},
                "category_comparison": {},
            }

            # Build technology matrix
            for tech in all_technologies:
                comparison["technology_matrix"][tech] = {}
                domains_with_tech = []

                for domain, profile in profiles.items():
                    has_tech = any(t["name"] == tech for t in profile["technologies"])
                    comparison["technology_matrix"][tech][domain] = has_tech
                    if has_tech:
                        domains_with_tech.append(domain)

                # Track common technologies
                if len(domains_with_tech) == len(profiles):
                    comparison["common_technologies"].append(tech)
                elif len(domains_with_tech) == 1:
                    domain = domains_with_tech[0]
                    if domain not in comparison["unique_technologies"]:
                        comparison["unique_technologies"][domain] = []
                    comparison["unique_technologies"][domain].append(tech)

            # Category comparison
            for domain, profile in profiles.items():
                comparison["category_comparison"][domain] = profile["categories"]

            return comparison

        except Exception as e:
            logger.error(f"Failed to compare technology stacks: {e}")
            return {"error": str(e)}

    @tool
    def get_market_share(self, technology: str, vertical: Optional[str] = None) -> Dict[str, Any]:
        """
        Get market share data for a technology.

        Args:
            technology: Technology to analyze
            vertical: Industry vertical to filter by (optional)

        Returns:
            Dictionary containing market share information
        """
        params = {"TECH": technology}
        if vertical:
            params["VERTICAL"] = vertical

        try:
            result = self._make_request("market1/api.json", params)

            if not result.get("Results"):
                return {
                    "technology": technology,
                    "market_share": 0,
                    "rank": None,
                    "error": "No market data available",
                }

            market_data = result["Results"][0]

            return {
                "technology": technology,
                "market_share": market_data.get("Percent", 0),
                "total_sites": market_data.get("Count", 0),
                "rank": market_data.get("Rank"),
                "vertical": vertical,
                "last_updated": market_data.get("Date"),
            }

        except Exception as e:
            logger.error(f"Failed to get market share: {e}")
            return {"technology": technology, "market_share": 0, "error": str(e)}

    @tool
    def get_competitor_technologies(self, reference_domain: str, limit: int = 5) -> Dict[str, Any]:
        """
        Find competitors and their technology stacks based on a reference domain.

        Args:
            reference_domain: Domain to use as reference
            limit: Maximum number of competitors to analyze

        Returns:
            Dictionary containing competitor technology analysis
        """
        try:
            # Get reference domain's technology stack
            ref_profile = self.get_domain_technologies(reference_domain)
            if ref_profile.get("error"):
                return {"error": f"Could not analyze reference domain: {ref_profile['error']}"}

            # Find key technologies from reference domain
            key_technologies = [
                tech["name"]
                for tech in ref_profile["technologies"]
                if tech.get("category") in ["Analytics", "CMS", "E-commerce", "Marketing"]
            ][
                :3
            ]  # Focus on top 3 key technologies

            competitors = {}

            # Find companies using similar technologies
            for tech in key_technologies:
                tech_companies = self.find_companies_using_technology(tech, limit=limit * 2)
                for company in tech_companies.get("companies", []):
                    domain = company["domain"]
                    if domain != reference_domain and domain not in competitors:
                        competitors[domain] = {"shared_technologies": [tech], "profile": None}
                    elif domain in competitors:
                        competitors[domain]["shared_technologies"].append(tech)

            # Analyze top competitors
            top_competitors = sorted(
                competitors.items(), key=lambda x: len(x[1]["shared_technologies"]), reverse=True
            )[:limit]

            competitor_analysis = []
            for domain, data in top_competitors:
                profile = self.get_domain_technologies(domain)
                if not profile.get("error"):
                    competitor_analysis.append(
                        {
                            "domain": domain,
                            "shared_technologies": data["shared_technologies"],
                            "total_technologies": profile["total_technologies"],
                            "technology_categories": profile["categories"],
                            "technologies": profile["technologies"],
                        }
                    )

            return {
                "reference_domain": reference_domain,
                "reference_technologies": len(ref_profile["technologies"]),
                "competitors": competitor_analysis,
                "analysis_based_on": key_technologies,
            }

        except Exception as e:
            logger.error(f"Failed to get competitor technologies: {e}")
            return {"error": str(e)}
