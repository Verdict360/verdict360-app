#!/usr/bin/env python3
"""
Verdict360 MCP Server - South African Legal Analytics
Advanced analytics and insights for SA legal practice management
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import statistics
from collections import defaultdict

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verdict360-sa-legal-analytics")

@dataclass
class PracticeMetrics:
    total_matters: int
    active_matters: int
    completed_matters: int
    total_revenue: float
    average_matter_value: float
    billable_hours: float
    realization_rate: float
    client_satisfaction_score: float

@dataclass
class LegalTrend:
    trend_name: str
    category: str
    frequency: int
    growth_rate: float
    significance: str
    time_period: str
    related_areas: List[str]

@dataclass
class ComplianceMetric:
    framework: str
    compliance_score: float
    last_assessment: str
    risk_level: str
    improvement_areas: List[str]
    next_review_date: str

class SALegalAnalytics:
    """MCP Server for SA legal practice analytics and insights"""
    
    def __init__(self):
        self.server = Server("verdict360-sa-legal-analytics")
        self.analytics_cache = {}
        self.historical_data = self._initialize_historical_data()
        
        # SA Legal Market Data
        self.sa_legal_areas = {
            "corporate_law": {"market_share": 0.25, "avg_rate": 2500, "growth": 0.08},
            "litigation": {"market_share": 0.20, "avg_rate": 2200, "growth": 0.05},
            "property_law": {"market_share": 0.18, "avg_rate": 2000, "growth": 0.12},
            "family_law": {"market_share": 0.15, "avg_rate": 1600, "growth": 0.03},
            "criminal_law": {"market_share": 0.12, "avg_rate": 1800, "growth": 0.02},
            "labour_law": {"market_share": 0.10, "avg_rate": 1900, "growth": 0.15}
        }
        
        self.sa_court_hierarchy = {
            "constitutional_court": {"authority": 10, "jurisdiction": "national"},
            "supreme_court_of_appeal": {"authority": 9, "jurisdiction": "national"},
            "high_court": {"authority": 8, "jurisdiction": "provincial"},
            "magistrate_court": {"authority": 6, "jurisdiction": "local"},
            "specialized_courts": {"authority": 7, "jurisdiction": "specialized"}
        }
        
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register analytics tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available analytics tools"""
            return [
                Tool(
                    name="analyze_practice_performance",
                    description="Analyze SA legal practice performance metrics and KPIs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "time_period": {
                                "type": "string",
                                "enum": ["month", "quarter", "year", "ytd"],
                                "default": "month"
                            },
                            "practice_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific practice areas to analyze"
                            },
                            "include_benchmarks": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include SA legal market benchmarks"
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_billing_insights",
                    description="Generate billing and revenue insights for SA legal practice",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_period": {
                                "type": "string",
                                "enum": ["weekly", "monthly", "quarterly", "annually"],
                                "default": "monthly"
                            },
                            "attorney_level": {
                                "type": "string",
                                "enum": ["junior", "senior", "partner", "all"],
                                "default": "all"
                            },
                            "comparison_period": {
                                "type": "boolean",
                                "default": True,
                                "description": "Compare with previous period"
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_legal_trends",
                    description="Analyze current SA legal trends and market insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "trend_categories": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["case_law", "legislation", "regulatory", "market", "technology"]
                                },
                                "default": ["case_law", "legislation"]
                            },
                            "jurisdiction": {
                                "type": "string",
                                "enum": ["national", "provincial", "local", "all"],
                                "default": "national"
                            },
                            "time_horizon": {
                                "type": "string",
                                "enum": ["current", "6months", "1year", "2years"],
                                "default": "1year"
                            }
                        }
                    }
                ),
                Tool(
                    name="compliance_analytics",
                    description="Analyze compliance metrics and risk assessment for SA legal practice",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "compliance_frameworks": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["popia", "legal_practice_act", "attorney_fidelity_fund", "tax_compliance"]
                                },
                                "default": ["popia", "legal_practice_act"]
                            },
                            "risk_assessment": {
                                "type": "boolean",
                                "default": True
                            },
                            "include_recommendations": {
                                "type": "boolean",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="client_analytics",
                    description="Analyze client portfolio and satisfaction metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "segmentation": {
                                "type": "string",
                                "enum": ["industry", "matter_type", "revenue", "geography"],
                                "default": "matter_type"
                            },
                            "satisfaction_metrics": {
                                "type": "boolean",
                                "default": True
                            },
                            "retention_analysis": {
                                "type": "boolean",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="market_intelligence",
                    description="Generate SA legal market intelligence and competitive analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "market_segment": {
                                "type": "string",
                                "enum": ["corporate", "litigation", "property", "family", "criminal", "labour"],
                                "default": "corporate"
                            },
                            "competitive_analysis": {
                                "type": "boolean",
                                "default": True
                            },
                            "pricing_insights": {
                                "type": "boolean",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="predictive_analytics",
                    description="Generate predictive insights for SA legal practice planning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prediction_type": {
                                "type": "string",
                                "enum": ["revenue_forecast", "matter_outcome", "resource_planning", "risk_prediction"],
                                "default": "revenue_forecast"
                            },
                            "forecast_horizon": {
                                "type": "string",
                                "enum": ["3months", "6months", "1year", "2years"],
                                "default": "6months"
                            },
                            "confidence_level": {
                                "type": "number",
                                "minimum": 0.8,
                                "maximum": 0.99,
                                "default": 0.95
                            }
                        }
                    }
                ),
                Tool(
                    name="generate_executive_dashboard",
                    description="Generate executive dashboard with key SA legal practice metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "dashboard_type": {
                                "type": "string",
                                "enum": ["executive", "operational", "financial", "compliance"],
                                "default": "executive"
                            },
                            "update_frequency": {
                                "type": "string",
                                "enum": ["real_time", "daily", "weekly", "monthly"],
                                "default": "weekly"
                            },
                            "kpi_focus": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific KPIs to highlight"
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> list[TextContent]:
            """Handle analytics tool calls"""
            
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            try:
                if tool_name == "analyze_practice_performance":
                    return await self._analyze_practice_performance(arguments)
                elif tool_name == "generate_billing_insights":
                    return await self._generate_billing_insights(arguments)
                elif tool_name == "analyze_legal_trends":
                    return await self._analyze_legal_trends(arguments)
                elif tool_name == "compliance_analytics":
                    return await self._compliance_analytics(arguments)
                elif tool_name == "client_analytics":
                    return await self._client_analytics(arguments)
                elif tool_name == "market_intelligence":
                    return await self._market_intelligence(arguments)
                elif tool_name == "predictive_analytics":
                    return await self._predictive_analytics(arguments)
                elif tool_name == "generate_executive_dashboard":
                    return await self._generate_executive_dashboard(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {tool_name}")]
                    
            except Exception as e:
                logger.error(f"Analytics tool {tool_name} failed: {str(e)}")
                return [TextContent(type="text", text=f"Error in {tool_name}: {str(e)}")]
    
    def _register_resources(self):
        """Register analytics resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available analytics resources"""
            return [
                Resource(
                    uri="sa-analytics://market/benchmarks",
                    name="SA Legal Market Benchmarks",
                    description="Industry benchmarks for SA legal practice performance",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sa-analytics://trends/current",
                    name="Current SA Legal Trends",
                    description="Current trends in SA legal market and practice",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sa-analytics://compliance/frameworks",
                    name="SA Legal Compliance Frameworks",
                    description="Compliance measurement frameworks for SA legal practice",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sa-analytics://kpis/definitions",
                    name="Legal Practice KPI Definitions",
                    description="Standard KPI definitions for SA legal practice analytics",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read analytics resources"""
            
            if uri == "sa-analytics://market/benchmarks":
                return json.dumps(self._get_market_benchmarks(), indent=2)
            elif uri == "sa-analytics://trends/current":
                return json.dumps(self._get_current_trends(), indent=2)
            elif uri == "sa-analytics://compliance/frameworks":
                return json.dumps(self._get_compliance_frameworks(), indent=2)
            elif uri == "sa-analytics://kpis/definitions":
                return json.dumps(self._get_kpi_definitions(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")

    # Tool Implementation Methods
    
    async def _analyze_practice_performance(self, args: Dict) -> list[TextContent]:
        """Analyze practice performance metrics"""
        time_period = args.get("time_period", "month")
        practice_areas = args.get("practice_areas", [])
        include_benchmarks = args.get("include_benchmarks", True)
        
        # Generate performance metrics
        metrics = self._calculate_performance_metrics(time_period, practice_areas)
        
        # Add benchmarks if requested
        if include_benchmarks:
            benchmarks = self._get_market_benchmarks()
            metrics["benchmarks"] = benchmarks
        
        analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "time_period": time_period,
            "practice_areas_analyzed": practice_areas or "all",
            "performance_metrics": metrics,
            "key_insights": self._generate_performance_insights(metrics),
            "recommendations": self._generate_performance_recommendations(metrics)
        }
        
        return [TextContent(
            type="text",
            text=f"📊 Practice Performance Analysis\n\n" +
                 json.dumps(analysis, indent=2)
        )]
    
    async def _generate_billing_insights(self, args: Dict) -> list[TextContent]:
        """Generate billing and revenue insights"""
        analysis_period = args.get("analysis_period", "monthly")
        attorney_level = args.get("attorney_level", "all")
        comparison_period = args.get("comparison_period", True)
        
        billing_data = self._calculate_billing_metrics(analysis_period, attorney_level)
        
        if comparison_period:
            previous_data = self._calculate_previous_period_billing(analysis_period, attorney_level)
            billing_data["period_comparison"] = self._compare_billing_periods(billing_data, previous_data)
        
        insights = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analysis_period": analysis_period,
            "attorney_level": attorney_level,
            "billing_metrics": billing_data,
            "revenue_insights": self._generate_revenue_insights(billing_data),
            "optimization_opportunities": self._identify_billing_optimizations(billing_data)
        }
        
        return [TextContent(
            type="text",
            text=f"💰 Billing Insights Analysis\n\n" +
                 json.dumps(insights, indent=2)
        )]
    
    async def _analyze_legal_trends(self, args: Dict) -> list[TextContent]:
        """Analyze SA legal trends"""
        trend_categories = args.get("trend_categories", ["case_law", "legislation"])
        jurisdiction = args.get("jurisdiction", "national")
        time_horizon = args.get("time_horizon", "1year")
        
        trends = self._identify_legal_trends(trend_categories, jurisdiction, time_horizon)
        
        analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "trend_categories": trend_categories,
            "jurisdiction": jurisdiction,
            "time_horizon": time_horizon,
            "identified_trends": trends,
            "trend_analysis": self._analyze_trend_significance(trends),
            "impact_assessment": self._assess_trend_impact(trends),
            "strategic_implications": self._generate_strategic_implications(trends)
        }
        
        return [TextContent(
            type="text",
            text=f"📈 Legal Trends Analysis\n\n" +
                 json.dumps(analysis, indent=2)
        )]
    
    async def _compliance_analytics(self, args: Dict) -> list[TextContent]:
        """Analyze compliance metrics"""
        frameworks = args.get("compliance_frameworks", ["popia", "legal_practice_act"])
        risk_assessment = args.get("risk_assessment", True)
        include_recommendations = args.get("include_recommendations", True)
        
        compliance_data = self._calculate_compliance_metrics(frameworks)
        
        if risk_assessment:
            compliance_data["risk_assessment"] = self._perform_compliance_risk_assessment(frameworks)
        
        if include_recommendations:
            compliance_data["recommendations"] = self._generate_compliance_recommendations(compliance_data)
        
        analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "frameworks_analyzed": frameworks,
            "compliance_metrics": compliance_data,
            "overall_compliance_score": self._calculate_overall_compliance_score(compliance_data)
        }
        
        return [TextContent(
            type="text",
            text=f"🛡️ Compliance Analytics\n\n" +
                 json.dumps(analysis, indent=2)
        )]
    
    async def _client_analytics(self, args: Dict) -> list[TextContent]:
        """Analyze client portfolio"""
        segmentation = args.get("segmentation", "matter_type")
        satisfaction_metrics = args.get("satisfaction_metrics", True)
        retention_analysis = args.get("retention_analysis", True)
        
        client_data = self._analyze_client_portfolio(segmentation)
        
        if satisfaction_metrics:
            client_data["satisfaction_metrics"] = self._calculate_satisfaction_metrics()
        
        if retention_analysis:
            client_data["retention_analysis"] = self._perform_retention_analysis()
        
        analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "segmentation_type": segmentation,
            "client_analytics": client_data,
            "portfolio_insights": self._generate_portfolio_insights(client_data),
            "growth_opportunities": self._identify_growth_opportunities(client_data)
        }
        
        return [TextContent(
            type="text",
            text=f"👥 Client Analytics\n\n" +
                 json.dumps(analysis, indent=2)
        )]
    
    async def _market_intelligence(self, args: Dict) -> list[TextContent]:
        """Generate market intelligence"""
        market_segment = args.get("market_segment", "corporate")
        competitive_analysis = args.get("competitive_analysis", True)
        pricing_insights = args.get("pricing_insights", True)
        
        market_data = self._analyze_market_segment(market_segment)
        
        if competitive_analysis:
            market_data["competitive_landscape"] = self._analyze_competitive_landscape(market_segment)
        
        if pricing_insights:
            market_data["pricing_insights"] = self._generate_pricing_insights(market_segment)
        
        intelligence = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "market_segment": market_segment,
            "market_intelligence": market_data,
            "strategic_recommendations": self._generate_market_recommendations(market_data),
            "opportunity_assessment": self._assess_market_opportunities(market_segment)
        }
        
        return [TextContent(
            type="text",
            text=f"🎯 Market Intelligence\n\n" +
                 json.dumps(intelligence, indent=2)
        )]
    
    async def _predictive_analytics(self, args: Dict) -> list[TextContent]:
        """Generate predictive insights"""
        prediction_type = args.get("prediction_type", "revenue_forecast")
        forecast_horizon = args.get("forecast_horizon", "6months")
        confidence_level = args.get("confidence_level", 0.95)
        
        predictions = self._generate_predictions(prediction_type, forecast_horizon, confidence_level)
        
        analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "prediction_type": prediction_type,
            "forecast_horizon": forecast_horizon,
            "confidence_level": confidence_level,
            "predictions": predictions,
            "methodology": self._get_prediction_methodology(prediction_type),
            "key_assumptions": self._get_prediction_assumptions(prediction_type),
            "risk_factors": self._identify_prediction_risks(predictions)
        }
        
        return [TextContent(
            type="text",
            text=f"🔮 Predictive Analytics\n\n" +
                 json.dumps(analysis, indent=2)
        )]
    
    async def _generate_executive_dashboard(self, args: Dict) -> list[TextContent]:
        """Generate executive dashboard"""
        dashboard_type = args.get("dashboard_type", "executive")
        update_frequency = args.get("update_frequency", "weekly")
        kpi_focus = args.get("kpi_focus", [])
        
        dashboard_data = self._compile_dashboard_data(dashboard_type, kpi_focus)
        
        dashboard = {
            "dashboard_timestamp": datetime.utcnow().isoformat(),
            "dashboard_type": dashboard_type,
            "update_frequency": update_frequency,
            "key_metrics": dashboard_data["key_metrics"],
            "performance_indicators": dashboard_data["kpis"],
            "alerts_warnings": dashboard_data["alerts"],
            "trend_summaries": dashboard_data["trends"],
            "action_items": dashboard_data["actions"],
            "next_update": self._calculate_next_update(update_frequency)
        }
        
        return [TextContent(
            type="text",
            text=f"📋 Executive Dashboard\n\n" +
                 json.dumps(dashboard, indent=2)
        )]

    # Helper Methods and Data Generation
    
    def _initialize_historical_data(self) -> Dict:
        """Initialize historical data for analytics"""
        return {
            "practice_metrics": self._generate_historical_metrics(),
            "billing_data": self._generate_historical_billing(),
            "client_data": self._generate_historical_clients(),
            "market_data": self._generate_historical_market()
        }
    
    def _generate_historical_metrics(self) -> List[Dict]:
        """Generate historical practice metrics"""
        metrics = []
        for i in range(12):  # 12 months of data
            date = datetime.now() - timedelta(days=30*i)
            metrics.append({
                "date": date.strftime("%Y-%m"),
                "total_matters": 45 + (i * 2),
                "active_matters": 32 + i,
                "completed_matters": 13 + i,
                "revenue": 850000 + (i * 50000),
                "billable_hours": 1200 + (i * 100),
                "realization_rate": 0.85 + (0.02 * (i % 3))
            })
        return metrics[::-1]  # Reverse to chronological order
    
    def _generate_historical_billing(self) -> List[Dict]:
        """Generate historical billing data"""
        billing = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            billing.append({
                "date": date.strftime("%Y-%m"),
                "total_billed": 950000 + (i * 75000),
                "collected": 850000 + (i * 60000),
                "outstanding": 100000 + (i * 15000),
                "write_offs": 25000 + (i * 2000)
            })
        return billing[::-1]
    
    def _generate_historical_clients(self) -> List[Dict]:
        """Generate historical client data"""
        clients = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            clients.append({
                "date": date.strftime("%Y-%m"),
                "total_clients": 120 + (i * 3),
                "new_clients": 8 + (i % 4),
                "retained_clients": 112 + (i * 2),
                "satisfaction_score": 4.2 + (0.1 * (i % 3))
            })
        return clients[::-1]
    
    def _generate_historical_market(self) -> List[Dict]:
        """Generate historical market data"""
        market = []
        for area, data in self.sa_legal_areas.items():
            market.append({
                "practice_area": area,
                "market_share": data["market_share"],
                "average_rate": data["avg_rate"],
                "growth_rate": data["growth"],
                "competitiveness": "high" if data["growth"] > 0.1 else "medium"
            })
        return market
    
    def _calculate_performance_metrics(self, time_period: str, practice_areas: List[str]) -> Dict:
        """Calculate practice performance metrics"""
        # Mock calculation based on historical data
        base_metrics = {
            "total_matters": 45,
            "active_matters": 32,
            "completed_matters": 13,
            "total_revenue": 850000,
            "average_matter_value": 18888,
            "billable_hours": 1200,
            "realization_rate": 0.87,
            "utilization_rate": 0.73,
            "collection_rate": 0.89,
            "client_satisfaction": 4.3
        }
        
        # Adjust based on time period
        multiplier = {"month": 1, "quarter": 3, "year": 12, "ytd": 8}[time_period]
        
        for key in ["total_matters", "completed_matters", "total_revenue", "billable_hours"]:
            base_metrics[key] = int(base_metrics[key] * multiplier)
        
        base_metrics["average_matter_value"] = base_metrics["total_revenue"] // base_metrics["total_matters"]
        
        return base_metrics
    
    def _generate_performance_insights(self, metrics: Dict) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        if metrics["realization_rate"] < 0.85:
            insights.append("Realization rate below industry benchmark - review billing practices")
        
        if metrics["utilization_rate"] < 0.75:
            insights.append("Utilization rate indicates capacity for additional matters")
        
        if metrics["client_satisfaction"] > 4.0:
            insights.append("Strong client satisfaction supports retention and referrals")
        
        return insights
    
    def _generate_performance_recommendations(self, metrics: Dict) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if metrics["collection_rate"] < 0.90:
            recommendations.append("Implement automated follow-up for outstanding invoices")
        
        if metrics["utilization_rate"] < 0.70:
            recommendations.append("Consider marketing initiatives to increase matter volume")
        
        recommendations.append("Conduct quarterly client satisfaction surveys")
        recommendations.append("Review hourly rates against market benchmarks")
        
        return recommendations
    
    def _calculate_billing_metrics(self, period: str, attorney_level: str) -> Dict:
        """Calculate billing metrics"""
        return {
            "total_billed": 950000,
            "total_collected": 850000,
            "outstanding_amount": 100000,
            "write_offs": 25000,
            "average_hourly_rate": 2200,
            "billable_hours": 1200,
            "non_billable_hours": 300,
            "realization_rate": 0.87,
            "collection_efficiency": 0.89,
            "attorney_performance": self._get_attorney_performance(attorney_level)
        }
    
    def _get_attorney_performance(self, level: str) -> Dict:
        """Get attorney performance by level"""
        performance_data = {
            "junior": {"avg_rate": 1200, "utilization": 0.82, "realization": 0.91},
            "senior": {"avg_rate": 1800, "utilization": 0.78, "realization": 0.88},
            "partner": {"avg_rate": 2500, "utilization": 0.65, "realization": 0.85},
            "all": {"avg_rate": 2000, "utilization": 0.75, "realization": 0.88}
        }
        return performance_data.get(level, performance_data["all"])
    
    def _calculate_previous_period_billing(self, period: str, attorney_level: str) -> Dict:
        """Calculate previous period billing for comparison"""
        current = self._calculate_billing_metrics(period, attorney_level)
        # Simulate 5-10% difference for previous period
        return {
            key: value * 0.93 if isinstance(value, (int, float)) else value
            for key, value in current.items()
        }
    
    def _compare_billing_periods(self, current: Dict, previous: Dict) -> Dict:
        """Compare billing periods"""
        comparison = {}
        for key in ["total_billed", "total_collected", "outstanding_amount"]:
            if key in current and key in previous:
                change = ((current[key] - previous[key]) / previous[key]) * 100
                comparison[f"{key}_change"] = round(change, 1)
        return comparison
    
    def _generate_revenue_insights(self, billing_data: Dict) -> List[str]:
        """Generate revenue insights"""
        insights = []
        
        if billing_data["realization_rate"] > 0.85:
            insights.append("Strong realization rate indicates effective billing practices")
        
        if billing_data["outstanding_amount"] / billing_data["total_billed"] > 0.15:
            insights.append("High outstanding amounts require attention to collection processes")
        
        return insights
    
    def _identify_billing_optimizations(self, billing_data: Dict) -> List[str]:
        """Identify billing optimization opportunities"""
        optimizations = []
        
        if billing_data["non_billable_hours"] / billing_data["billable_hours"] > 0.3:
            optimizations.append("Reduce non-billable time through process improvements")
        
        if billing_data["write_offs"] / billing_data["total_billed"] > 0.05:
            optimizations.append("Review write-off procedures and client billing agreements")
        
        optimizations.append("Implement time tracking automation")
        optimizations.append("Review hourly rates quarterly")
        
        return optimizations
    
    def _identify_legal_trends(self, categories: List[str], jurisdiction: str, horizon: str) -> List[LegalTrend]:
        """Identify current legal trends"""
        trends = [
            LegalTrend(
                trend_name="POPIA Compliance Enforcement",
                category="regulatory",
                frequency=85,
                growth_rate=0.45,
                significance="high",
                time_period="2024-current",
                related_areas=["data_privacy", "corporate_governance", "compliance"]
            ),
            LegalTrend(
                trend_name="ESG Litigation Increase",
                category="case_law",
                frequency=62,
                growth_rate=0.38,
                significance="high",
                time_period="2023-current", 
                related_areas=["environmental_law", "corporate_law", "litigation"]
            ),
            LegalTrend(
                trend_name="Remote Work Legal Framework",
                category="legislation",
                frequency=73,
                growth_rate=0.28,
                significance="medium",
                time_period="2022-current",
                related_areas=["labour_law", "employment_contracts", "workplace_safety"]
            )
        ]
        
        return [t for t in trends if t.category in categories]
    
    def _analyze_trend_significance(self, trends: List[LegalTrend]) -> Dict:
        """Analyze significance of trends"""
        high_significance = [t for t in trends if t.significance == "high"]
        growing_trends = [t for t in trends if t.growth_rate > 0.3]
        
        return {
            "high_significance_count": len(high_significance),
            "rapidly_growing_trends": len(growing_trends),
            "average_growth_rate": statistics.mean([t.growth_rate for t in trends])
        }
    
    def _assess_trend_impact(self, trends: List[LegalTrend]) -> Dict:
        """Assess impact of trends on practice"""
        impact_areas = defaultdict(int)
        for trend in trends:
            for area in trend.related_areas:
                impact_areas[area] += 1
        
        return {
            "most_impacted_areas": dict(sorted(impact_areas.items(), key=lambda x: x[1], reverse=True)[:5]),
            "practice_adaptation_needed": len([t for t in trends if t.significance == "high"]) > 2
        }
    
    def _generate_strategic_implications(self, trends: List[LegalTrend]) -> List[str]:
        """Generate strategic implications"""
        implications = []
        
        popia_trends = [t for t in trends if "popia" in t.trend_name.lower()]
        if popia_trends:
            implications.append("Strengthen data privacy practice area and capabilities")
        
        esg_trends = [t for t in trends if "esg" in t.trend_name.lower()]
        if esg_trends:
            implications.append("Develop ESG advisory services and litigation capabilities")
        
        implications.append("Monitor regulatory changes for proactive client advisory")
        implications.append("Invest in legal technology for trend analysis and monitoring")
        
        return implications
    
    def _calculate_compliance_metrics(self, frameworks: List[str]) -> Dict:
        """Calculate compliance metrics"""
        metrics = {}
        
        for framework in frameworks:
            if framework == "popia":
                metrics["popia"] = ComplianceMetric(
                    framework="POPIA",
                    compliance_score=87.5,
                    last_assessment="2024-11-15",
                    risk_level="low",
                    improvement_areas=["consent management", "data breach procedures"],
                    next_review_date="2025-02-15"
                )
            elif framework == "legal_practice_act":
                metrics["legal_practice_act"] = ComplianceMetric(
                    framework="Legal Practice Act",
                    compliance_score=92.0,
                    last_assessment="2024-12-01",
                    risk_level="very_low",
                    improvement_areas=["continuing education tracking"],
                    next_review_date="2025-03-01"
                )
        
        return {k: asdict(v) for k, v in metrics.items()}
    
    def _perform_compliance_risk_assessment(self, frameworks: List[str]) -> Dict:
        """Perform compliance risk assessment"""
        return {
            "overall_risk_level": "low",
            "high_risk_areas": ["data retention policies"],
            "medium_risk_areas": ["client communication protocols"],
            "low_risk_areas": ["trust account management", "professional indemnity"],
            "risk_mitigation_priority": ["implement automated data retention", "update client privacy notices"]
        }
    
    def _generate_compliance_recommendations(self, compliance_data: Dict) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for framework, data in compliance_data.items():
            if isinstance(data, dict) and data.get("compliance_score", 100) < 90:
                recommendations.append(f"Improve {framework} compliance score through focused remediation")
        
        recommendations.extend([
            "Conduct quarterly compliance assessments",
            "Implement compliance monitoring dashboard",
            "Provide regular compliance training to staff"
        ])
        
        return recommendations
    
    def _calculate_overall_compliance_score(self, compliance_data: Dict) -> float:
        """Calculate overall compliance score"""
        scores = []
        for framework, data in compliance_data.items():
            if isinstance(data, dict) and "compliance_score" in data:
                scores.append(data["compliance_score"])
        
        return round(statistics.mean(scores) if scores else 0, 1)
    
    def _analyze_client_portfolio(self, segmentation: str) -> Dict:
        """Analyze client portfolio"""
        return {
            "total_clients": 120,
            "active_clients": 95,
            "new_clients_ytd": 28,
            "client_retention_rate": 0.87,
            "segmentation": self._perform_client_segmentation(segmentation),
            "client_value_distribution": {
                "high_value": {"count": 15, "percentage": 12.5, "revenue_contribution": 45},
                "medium_value": {"count": 35, "percentage": 29.2, "revenue_contribution": 35},
                "low_value": {"count": 70, "percentage": 58.3, "revenue_contribution": 20}
            }
        }
    
    def _perform_client_segmentation(self, segmentation_type: str) -> Dict:
        """Perform client segmentation analysis"""
        segmentations = {
            "matter_type": {
                "corporate": {"count": 35, "revenue_share": 0.40},
                "litigation": {"count": 28, "revenue_share": 0.25},
                "property": {"count": 32, "revenue_share": 0.20},
                "family": {"count": 25, "revenue_share": 0.15}
            },
            "industry": {
                "financial_services": {"count": 20, "revenue_share": 0.35},
                "manufacturing": {"count": 18, "revenue_share": 0.25},
                "technology": {"count": 15, "revenue_share": 0.20},
                "other": {"count": 67, "revenue_share": 0.20}
            },
            "revenue": {
                "high": {"count": 15, "min_annual": 100000},
                "medium": {"count": 35, "min_annual": 25000},
                "low": {"count": 70, "min_annual": 5000}
            }
        }
        
        return segmentations.get(segmentation_type, segmentations["matter_type"])
    
    def _calculate_satisfaction_metrics(self) -> Dict:
        """Calculate client satisfaction metrics"""
        return {
            "overall_satisfaction": 4.3,
            "communication_rating": 4.2,
            "expertise_rating": 4.5,
            "value_rating": 4.0,
            "responsiveness_rating": 4.1,
            "nps_score": 68,
            "survey_response_rate": 0.42
        }
    
    def _perform_retention_analysis(self) -> Dict:
        """Perform client retention analysis"""
        return {
            "overall_retention_rate": 0.87,
            "retention_by_segment": {
                "high_value": 0.95,
                "medium_value": 0.88,
                "low_value": 0.82
            },
            "churn_reasons": {
                "pricing": 0.35,
                "service_quality": 0.25,
                "communication": 0.20,
                "expertise": 0.10,
                "other": 0.10
            },
            "retention_trend": "stable"
        }
    
    def _generate_portfolio_insights(self, client_data: Dict) -> List[str]:
        """Generate client portfolio insights"""
        insights = []
        
        if client_data["client_retention_rate"] > 0.85:
            insights.append("Strong client retention indicates high satisfaction and loyalty")
        
        high_value_contribution = client_data["client_value_distribution"]["high_value"]["revenue_contribution"]
        if high_value_contribution > 40:
            insights.append("High concentration of revenue in top clients - consider diversification")
        
        return insights
    
    def _identify_growth_opportunities(self, client_data: Dict) -> List[str]:
        """Identify client growth opportunities"""
        opportunities = []
        
        opportunities.append("Cross-sell additional services to existing high-value clients")
        opportunities.append("Develop referral program for satisfied clients")
        opportunities.append("Target medium-value clients for service expansion")
        
        return opportunities
    
    def _analyze_market_segment(self, segment: str) -> Dict:
        """Analyze specific market segment"""
        segment_data = self.sa_legal_areas.get(segment, {})
        
        return {
            "segment": segment,
            "market_share": segment_data.get("market_share", 0),
            "average_rate": segment_data.get("avg_rate", 0),
            "growth_rate": segment_data.get("growth", 0),
            "market_size_estimate": "R2.5 billion",
            "key_players": ["Major Firm A", "Major Firm B", "Major Firm C"],
            "market_dynamics": self._analyze_market_dynamics(segment)
        }
    
    def _analyze_market_dynamics(self, segment: str) -> Dict:
        """Analyze market dynamics"""
        return {
            "demand_drivers": ["regulatory changes", "economic growth", "business complexity"],
            "supply_constraints": ["attorney shortage", "specialization requirements"],
            "pricing_trends": "increasing",
            "technology_adoption": "moderate",
            "competitive_intensity": "high"
        }
    
    def _analyze_competitive_landscape(self, segment: str) -> Dict:
        """Analyze competitive landscape"""
        return {
            "market_leaders": [
                {"firm": "Firm A", "market_share": 0.15, "strengths": ["brand", "resources"]},
                {"firm": "Firm B", "market_share": 0.12, "strengths": ["expertise", "client_base"]},
                {"firm": "Firm C", "market_share": 0.10, "strengths": ["innovation", "efficiency"]}
            ],
            "competitive_factors": ["expertise", "pricing", "service_quality", "brand_reputation"],
            "barriers_to_entry": ["capital_requirements", "regulatory_compliance", "talent_acquisition"],
            "your_position": "mid-tier with growth potential"
        }
    
    def _generate_pricing_insights(self, segment: str) -> Dict:
        """Generate pricing insights"""
        return {
            "market_average": self.sa_legal_areas.get(segment, {}).get("avg_rate", 2000),
            "pricing_range": {"min": 1500, "max": 3500},
            "pricing_strategies": ["value_based", "competitive", "cost_plus"],
            "optimization_opportunities": [
                "Premium pricing for specialized expertise",
                "Value-based pricing for complex matters",
                "Competitive pricing for high-volume work"
            ]
        }
    
    def _generate_market_recommendations(self, market_data: Dict) -> List[str]:
        """Generate market recommendations"""
        recommendations = []
        
        if market_data["growth_rate"] > 0.1:
            recommendations.append(f"Invest in {market_data['segment']} practice area expansion")
        
        recommendations.extend([
            "Monitor competitive pricing and adjust positioning accordingly",
            "Develop specialized expertise in high-growth areas",
            "Consider strategic partnerships for market expansion"
        ])
        
        return recommendations
    
    def _assess_market_opportunities(self, segment: str) -> Dict:
        """Assess market opportunities"""
        return {
            "opportunity_score": 7.5,  # out of 10
            "key_opportunities": [
                "Underserved mid-market clients",
                "Technology-enabled service delivery",
                "Regulatory compliance advisory"
            ],
            "investment_required": "moderate",
            "timeline": "12-18 months",
            "risk_level": "medium"
        }
    
    def _generate_predictions(self, prediction_type: str, horizon: str, confidence: float) -> Dict:
        """Generate predictive insights"""
        predictions = {
            "revenue_forecast": {
                "current": 850000,
                "predicted": 920000,
                "growth_rate": 0.08,
                "confidence_interval": {"lower": 880000, "upper": 960000}
            },
            "matter_outcome": {
                "success_probability": 0.75,
                "settlement_probability": 0.65,
                "litigation_duration_months": 18
            },
            "resource_planning": {
                "additional_attorneys_needed": 2,
                "peak_capacity_months": ["March", "September"],
                "training_investment_required": 50000
            }
        }
        
        return predictions.get(prediction_type, predictions["revenue_forecast"])
    
    def _get_prediction_methodology(self, prediction_type: str) -> str:
        """Get prediction methodology"""
        methodologies = {
            "revenue_forecast": "Time series analysis with seasonal adjustments",
            "matter_outcome": "Logistic regression with historical case data",
            "resource_planning": "Capacity planning with demand forecasting",
            "risk_prediction": "Monte Carlo simulation with risk factors"
        }
        
        return methodologies.get(prediction_type, "Statistical modeling")
    
    def _get_prediction_assumptions(self, prediction_type: str) -> List[str]:
        """Get prediction assumptions"""
        return [
            "Historical trends continue",
            "No major market disruptions",
            "Current client base remains stable",
            "Economic conditions remain similar"
        ]
    
    def _identify_prediction_risks(self, predictions: Dict) -> List[str]:
        """Identify prediction risks"""
        return [
            "Economic downturn could impact client demand",
            "Regulatory changes could affect practice areas",
            "Competitive pressure could impact pricing",
            "Technology disruption could change service delivery"
        ]
    
    def _compile_dashboard_data(self, dashboard_type: str, kpi_focus: List[str]) -> Dict:
        """Compile dashboard data"""
        return {
            "key_metrics": {
                "revenue_ytd": 8500000,
                "matters_active": 32,
                "client_satisfaction": 4.3,
                "realization_rate": 0.87
            },
            "kpis": self._get_dashboard_kpis(dashboard_type, kpi_focus),
            "alerts": [
                {"type": "warning", "message": "Outstanding invoices exceed 90 days"},
                {"type": "info", "message": "New client retention rate improving"}
            ],
            "trends": {
                "revenue_trend": "increasing",
                "client_acquisition": "stable",
                "market_position": "improving"
            },
            "actions": [
                "Review outstanding invoice collection procedures",
                "Conduct quarterly client satisfaction survey",
                "Update market rate analysis"
            ]
        }
    
    def _get_dashboard_kpis(self, dashboard_type: str, focus_areas: List[str]) -> Dict:
        """Get dashboard KPIs"""
        all_kpis = {
            "revenue_per_attorney": 425000,
            "utilization_rate": 0.73,
            "client_retention_rate": 0.87,
            "matter_success_rate": 0.91,
            "average_collection_period": 45,
            "cost_per_matter": 15600,
            "profit_margin": 0.35
        }
        
        if focus_areas:
            return {k: v for k, v in all_kpis.items() if any(focus in k for focus in focus_areas)}
        
        return all_kpis
    
    def _calculate_next_update(self, frequency: str) -> str:
        """Calculate next dashboard update"""
        intervals = {
            "real_time": timedelta(minutes=5),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30)
        }
        
        next_update = datetime.now() + intervals.get(frequency, intervals["weekly"])
        return next_update.isoformat()
    
    def _get_market_benchmarks(self) -> Dict:
        """Get SA legal market benchmarks"""
        return {
            "revenue_per_attorney": {"benchmark": 400000, "percentile_75": 450000, "percentile_25": 350000},
            "utilization_rate": {"benchmark": 0.75, "percentile_75": 0.82, "percentile_25": 0.68},
            "realization_rate": {"benchmark": 0.85, "percentile_75": 0.90, "percentile_25": 0.80},
            "collection_rate": {"benchmark": 0.90, "percentile_75": 0.95, "percentile_25": 0.85},
            "client_retention": {"benchmark": 0.85, "percentile_75": 0.92, "percentile_25": 0.78}
        }
    
    def _get_current_trends(self) -> List[Dict]:
        """Get current SA legal trends"""
        return [
            {
                "trend": "POPIA Compliance Enforcement",
                "impact": "high",
                "areas": ["data_privacy", "corporate_governance"],
                "timeline": "current"
            },
            {
                "trend": "ESG Litigation Growth", 
                "impact": "high",
                "areas": ["environmental", "corporate"],
                "timeline": "6-12 months"
            },
            {
                "trend": "Legal Technology Adoption",
                "impact": "medium",
                "areas": ["efficiency", "client_service"],
                "timeline": "ongoing"
            }
        ]
    
    def _get_compliance_frameworks(self) -> Dict:
        """Get compliance measurement frameworks"""
        return {
            "popia": {
                "metrics": ["consent_management", "data_processing", "breach_procedures"],
                "scoring": {"excellent": 90, "good": 80, "adequate": 70, "poor": 60}
            },
            "legal_practice_act": {
                "metrics": ["professional_conduct", "trust_accounting", "cpd_compliance"],
                "scoring": {"excellent": 95, "good": 85, "adequate": 75, "poor": 65}
            }
        }
    
    def _get_kpi_definitions(self) -> Dict:
        """Get KPI definitions"""
        return {
            "realization_rate": "Percentage of standard rates actually billed to clients",
            "utilization_rate": "Percentage of available time spent on billable activities",
            "collection_rate": "Percentage of billed amounts actually collected",
            "client_retention_rate": "Percentage of clients retained year-over-year",
            "matter_success_rate": "Percentage of matters with favorable outcomes",
            "revenue_per_attorney": "Annual revenue divided by number of attorneys",
            "profit_margin": "Net income as percentage of total revenue"
        }

    async def run(self):
        """Run the analytics MCP server"""
        async with self.server:
            await self.server.run()

async def main():
    """Main entry point"""
    logger.info("🚀 Starting Verdict360 SA Legal Analytics MCP Server")
    
    analytics = SALegalAnalytics()
    await analytics.run()

if __name__ == "__main__":
    asyncio.run(main())