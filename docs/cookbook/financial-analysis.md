# Financial Report Analysis

Build an intelligent financial analysis system that processes earnings reports, financial statements, and market data to provide insights and track company performance over time.

## Problem Statement

Financial analysts need to process vast amounts of financial documents, extract key metrics, identify trends, and generate insights from quarterly reports, annual statements, and market data. Manual analysis is time-consuming and may miss important patterns.

## Solution Overview

We'll build a financial analysis system that:
1. Ingests financial reports from multiple sources (PDFs, XBRL, APIs)
2. Extracts structured financial data and metrics
3. Tracks performance trends over time
4. Identifies significant changes and anomalies
5. Generates comparative analysis and insights

## Complete Code

```python
import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from pathlib import Path
import yfinance as yf
import requests
import fitz  # PyMuPDF
from lxml import etree
import plotly.graph_objects as go

from contextframe import (
    FrameDataset,
    FrameRecord,
    create_metadata,
    create_relationship,
    add_relationship_to_metadata,
    generate_uuid
)

class FinancialReportAnalyzer:
    """Comprehensive financial report analysis system."""
    
    def __init__(self, dataset_path: str = "financial_reports.lance"):
        """Initialize financial analyzer."""
        self.dataset = FrameDataset.create(dataset_path) if not FrameDataset.exists(dataset_path) else FrameDataset(dataset_path)
        
        # Key financial metrics to extract
        self.key_metrics = {
            'revenue': ['revenue', 'sales', 'total revenue', 'net revenue'],
            'earnings': ['net income', 'earnings', 'profit', 'net profit'],
            'eps': ['earnings per share', 'eps', 'diluted eps'],
            'assets': ['total assets', 'assets'],
            'liabilities': ['total liabilities', 'liabilities'],
            'equity': ['shareholders equity', 'stockholders equity', 'equity'],
            'cash': ['cash and cash equivalents', 'cash'],
            'debt': ['total debt', 'long term debt', 'short term debt']
        }
        
        # Financial ratios
        self.ratios = {
            'pe_ratio': 'Price to Earnings',
            'debt_to_equity': 'Debt to Equity',
            'current_ratio': 'Current Ratio',
            'roa': 'Return on Assets',
            'roe': 'Return on Equity',
            'profit_margin': 'Profit Margin',
            'revenue_growth': 'Revenue Growth YoY'
        }
        
    def ingest_earnings_report(self, 
                             company_ticker: str,
                             report_path: str,
                             report_type: str = "10-Q",
                             fiscal_period: str = None) -> FrameRecord:
        """Ingest and analyze earnings report."""
        print(f"Ingesting {report_type} for {company_ticker}")
        
        # Extract text from PDF
        if report_path.endswith('.pdf'):
            content = self._extract_pdf_content(report_path)
        elif report_path.endswith('.xml'):
            content = self._extract_xbrl_content(report_path)
        else:
            with open(report_path, 'r') as f:
                content = f.read()
        
        # Extract financial data
        financial_data = self._extract_financial_metrics(content)
        
        # Get market data
        market_data = self._get_market_data(company_ticker)
        
        # Calculate ratios
        ratios = self._calculate_ratios(financial_data, market_data)
        
        # Analyze trends
        trend_analysis = self._analyze_trends(company_ticker, financial_data)
        
        # Create comprehensive report record
        metadata = create_metadata(
            title=f"{company_ticker} {report_type} - {fiscal_period or datetime.now().strftime('%Y Q%q')}",
            source="financial_report",
            company_ticker=company_ticker,
            report_type=report_type,
            fiscal_period=fiscal_period,
            filing_date=datetime.now().isoformat(),
            
            # Financial metrics
            revenue=financial_data.get('revenue'),
            earnings=financial_data.get('earnings'),
            eps=financial_data.get('eps'),
            total_assets=financial_data.get('assets'),
            total_liabilities=financial_data.get('liabilities'),
            shareholders_equity=financial_data.get('equity'),
            cash=financial_data.get('cash'),
            total_debt=financial_data.get('debt'),
            
            # Ratios
            pe_ratio=ratios.get('pe_ratio'),
            debt_to_equity=ratios.get('debt_to_equity'),
            current_ratio=ratios.get('current_ratio'),
            roa=ratios.get('roa'),
            roe=ratios.get('roe'),
            profit_margin=ratios.get('profit_margin'),
            
            # Trends
            revenue_growth_yoy=trend_analysis.get('revenue_growth'),
            earnings_growth_yoy=trend_analysis.get('earnings_growth'),
            trend_signals=trend_analysis.get('signals', []),
            
            # Market data
            stock_price=market_data.get('price'),
            market_cap=market_data.get('market_cap'),
            volume=market_data.get('volume')
        )
        
        # Create summary content
        summary = self._generate_financial_summary(
            company_ticker, financial_data, ratios, trend_analysis
        )
        
        record = FrameRecord(
            text_content=f"{summary}\\n\\n{content[:5000]}...",  # Include summary + excerpt
            metadata=metadata,
            unique_id=generate_uuid(),
            record_type="document"
        )
        
        self.dataset.add(record, generate_embedding=True)
        
        # Create relationships to previous reports
        self._link_to_previous_reports(record, company_ticker)
        
        return record
    
    def _extract_pdf_content(self, pdf_path: str) -> str:
        """Extract text content from PDF."""
        doc = fitz.open(pdf_path)
        text = ""
        
        for page in doc:
            text += page.get_text()
            
            # Also extract tables
            tables = page.find_tables()
            for table in tables:
                for row in table.extract():
                    text += " | ".join(str(cell) if cell else "" for cell in row) + "\\n"
        
        doc.close()
        return text
    
    def _extract_xbrl_content(self, xbrl_path: str) -> str:
        """Extract content from XBRL filing."""
        tree = etree.parse(xbrl_path)
        
        # Extract all fact values
        facts = []
        for element in tree.xpath("//*[@contextRef]"):
            if element.text:
                facts.append(f"{element.tag.split('}')[-1]}: {element.text}")
        
        return "\\n".join(facts)
    
    def _extract_financial_metrics(self, content: str) -> Dict[str, float]:
        """Extract key financial metrics from content."""
        metrics = {}
        content_lower = content.lower()
        
        for metric_key, search_terms in self.key_metrics.items():
            for term in search_terms:
                # Look for patterns like "Revenue: $1,234.5 million"
                patterns = [
                    rf"{term}[:\s]+\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?",
                    rf"{term}.*?\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?",
                    rf"\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?\s*{term}"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content_lower, re.IGNORECASE)
                    if match:
                        value = match.group(1).replace(',', '')
                        multiplier = {
                            'thousand': 1000,
                            'million': 1000000,
                            'billion': 1000000000
                        }.get(match.group(2), 1) if match.lastindex > 1 else 1
                        
                        try:
                            metrics[metric_key] = float(value) * multiplier
                            break
                        except ValueError:
                            continue
                
                if metric_key in metrics:
                    break
        
        return metrics
    
    def _get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get current market data for company."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'price': info.get('currentPrice', info.get('regularMarketPrice')),
                'market_cap': info.get('marketCap'),
                'volume': info.get('volume', info.get('regularMarketVolume')),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'beta': info.get('beta')
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}
    
    def _calculate_ratios(self, financial_data: Dict[str, float], 
                         market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate financial ratios."""
        ratios = {}
        
        # P/E Ratio
        if market_data.get('price') and financial_data.get('eps'):
            ratios['pe_ratio'] = market_data['price'] / financial_data['eps']
        
        # Debt to Equity
        if financial_data.get('debt') and financial_data.get('equity'):
            ratios['debt_to_equity'] = financial_data['debt'] / financial_data['equity']
        
        # Return on Assets
        if financial_data.get('earnings') and financial_data.get('assets'):
            ratios['roa'] = (financial_data['earnings'] / financial_data['assets']) * 100
        
        # Return on Equity
        if financial_data.get('earnings') and financial_data.get('equity'):
            ratios['roe'] = (financial_data['earnings'] / financial_data['equity']) * 100
        
        # Profit Margin
        if financial_data.get('earnings') and financial_data.get('revenue'):
            ratios['profit_margin'] = (financial_data['earnings'] / financial_data['revenue']) * 100
        
        return ratios
    
    def _analyze_trends(self, ticker: str, current_data: Dict[str, float]) -> Dict[str, Any]:
        """Analyze trends compared to previous periods."""
        # Get previous reports
        previous_reports = self.dataset.filter({
            'metadata.company_ticker': ticker,
            'metadata.report_type': {'in': ['10-Q', '10-K']}
        })
        
        if not previous_reports:
            return {'signals': ['First report - no historical data']}
        
        # Sort by date
        previous_reports.sort(key=lambda x: x.metadata.custom_metadata.get('filing_date', ''))
        
        # Get same period last year
        last_year = None
        for report in previous_reports:
            report_date = datetime.fromisoformat(
                report.metadata.custom_metadata.get('filing_date', '')
            )
            if (datetime.now() - report_date).days > 350:
                last_year = report
                break
        
        if not last_year:
            return {'signals': ['Insufficient historical data']}
        
        # Calculate growth rates
        analysis = {'signals': []}
        
        # Revenue growth
        if current_data.get('revenue') and last_year.metadata.custom_metadata.get('revenue'):
            growth = ((current_data['revenue'] - last_year.metadata.custom_metadata['revenue']) / 
                     last_year.metadata.custom_metadata['revenue']) * 100
            analysis['revenue_growth'] = growth
            
            if growth > 20:
                analysis['signals'].append(f"Strong revenue growth: {growth:.1f}% YoY")
            elif growth < -10:
                analysis['signals'].append(f"Revenue decline: {growth:.1f}% YoY")
        
        # Earnings growth
        if current_data.get('earnings') and last_year.metadata.custom_metadata.get('earnings'):
            growth = ((current_data['earnings'] - last_year.metadata.custom_metadata['earnings']) / 
                     abs(last_year.metadata.custom_metadata['earnings'])) * 100
            analysis['earnings_growth'] = growth
            
            if growth > 25:
                analysis['signals'].append(f"Exceptional earnings growth: {growth:.1f}% YoY")
            elif growth < -20:
                analysis['signals'].append(f"Earnings decline: {growth:.1f}% YoY")
        
        # Debt changes
        if current_data.get('debt') and last_year.metadata.custom_metadata.get('debt'):
            debt_change = ((current_data['debt'] - last_year.metadata.custom_metadata['debt']) / 
                          last_year.metadata.custom_metadata['debt']) * 100
            
            if debt_change > 50:
                analysis['signals'].append(f"Significant debt increase: {debt_change:.1f}%")
            elif debt_change < -30:
                analysis['signals'].append(f"Debt reduction: {abs(debt_change):.1f}%")
        
        return analysis
    
    def _generate_financial_summary(self, ticker: str, 
                                  financial_data: Dict[str, float],
                                  ratios: Dict[str, float],
                                  trends: Dict[str, Any]) -> str:
        """Generate executive summary of financial report."""
        summary_parts = [f"# {ticker} Financial Report Summary\\n"]
        
        # Key metrics
        summary_parts.append("## Key Financial Metrics")
        if financial_data.get('revenue'):
            summary_parts.append(f"- Revenue: ${financial_data['revenue']:,.0f}")
        if financial_data.get('earnings'):
            summary_parts.append(f"- Net Income: ${financial_data['earnings']:,.0f}")
        if financial_data.get('eps'):
            summary_parts.append(f"- EPS: ${financial_data['eps']:.2f}")
        
        # Ratios
        if ratios:
            summary_parts.append("\\n## Financial Ratios")
            if ratios.get('pe_ratio'):
                summary_parts.append(f"- P/E Ratio: {ratios['pe_ratio']:.2f}")
            if ratios.get('profit_margin'):
                summary_parts.append(f"- Profit Margin: {ratios['profit_margin']:.1f}%")
            if ratios.get('roe'):
                summary_parts.append(f"- ROE: {ratios['roe']:.1f}%")
        
        # Trends
        if trends.get('signals'):
            summary_parts.append("\\n## Key Insights")
            for signal in trends['signals']:
                summary_parts.append(f"- {signal}")
        
        return "\\n".join(summary_parts)
    
    def _link_to_previous_reports(self, current_report: FrameRecord, ticker: str):
        """Create relationships to previous reports."""
        # Get previous reports
        previous = self.dataset.filter({
            'metadata.company_ticker': ticker,
            'metadata.report_type': {'in': ['10-Q', '10-K']}
        })
        
        if previous:
            # Link to most recent previous report
            previous.sort(key=lambda x: x.metadata.custom_metadata.get('filing_date', ''), 
                        reverse=True)
            
            if previous[0].unique_id != current_report.unique_id:
                current_report.metadata = add_relationship_to_metadata(
                    current_report.metadata,
                    create_relationship(
                        source_id=current_report.unique_id,
                        target_id=previous[0].unique_id,
                        relationship_type="reference",
                        properties={'reference_type': 'previous_report'}
                    )
                )
    
    def compare_companies(self, tickers: List[str], 
                         metrics: List[str] = None) -> pd.DataFrame:
        """Compare financial metrics across companies."""
        if not metrics:
            metrics = ['revenue', 'earnings', 'profit_margin', 'roe', 'debt_to_equity']
        
        comparison_data = []
        
        for ticker in tickers:
            # Get most recent report
            reports = self.dataset.filter({
                'metadata.company_ticker': ticker
            })
            
            if reports:
                latest = max(reports, 
                           key=lambda x: x.metadata.custom_metadata.get('filing_date', ''))
                
                row = {'ticker': ticker}
                for metric in metrics:
                    row[metric] = latest.metadata.custom_metadata.get(metric, None)
                
                comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def generate_performance_chart(self, ticker: str, 
                                 metric: str = 'revenue') -> go.Figure:
        """Generate performance chart over time."""
        # Get all reports for company
        reports = self.dataset.filter({
            'metadata.company_ticker': ticker
        })
        
        if not reports:
            return None
        
        # Sort by date
        reports.sort(key=lambda x: x.metadata.custom_metadata.get('filing_date', ''))
        
        # Extract data
        dates = []
        values = []
        
        for report in reports:
            date = report.metadata.custom_metadata.get('filing_date')
            value = report.metadata.custom_metadata.get(metric)
            
            if date and value:
                dates.append(datetime.fromisoformat(date))
                values.append(value)
        
        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=metric.replace('_', ' ').title(),
            line=dict(width=3)
        ))
        
        fig.update_layout(
            title=f"{ticker} - {metric.replace('_', ' ').title()} Over Time",
            xaxis_title="Date",
            yaxis_title=metric.replace('_', ' ').title(),
            hovermode='x unified'
        )
        
        return fig
    
    def identify_investment_opportunities(self, 
                                        min_revenue_growth: float = 15,
                                        max_pe_ratio: float = 25,
                                        min_profit_margin: float = 10) -> List[Dict[str, Any]]:
        """Identify companies meeting investment criteria."""
        # Get all latest reports
        all_companies = {}
        all_reports = self.dataset.filter({
            'metadata.report_type': {'in': ['10-Q', '10-K']}
        })
        
        # Group by company
        for report in all_reports:
            ticker = report.metadata.custom_metadata.get('company_ticker')
            if ticker:
                if ticker not in all_companies:
                    all_companies[ticker] = []
                all_companies[ticker].append(report)
        
        # Analyze each company
        opportunities = []
        
        for ticker, reports in all_companies.items():
            # Get latest report
            latest = max(reports, 
                       key=lambda x: x.metadata.custom_metadata.get('filing_date', ''))
            
            # Check criteria
            revenue_growth = latest.metadata.custom_metadata.get('revenue_growth_yoy', 0)
            pe_ratio = latest.metadata.custom_metadata.get('pe_ratio', float('inf'))
            profit_margin = latest.metadata.custom_metadata.get('profit_margin', 0)
            
            if (revenue_growth >= min_revenue_growth and 
                pe_ratio <= max_pe_ratio and 
                profit_margin >= min_profit_margin):
                
                opportunities.append({
                    'ticker': ticker,
                    'revenue_growth': revenue_growth,
                    'pe_ratio': pe_ratio,
                    'profit_margin': profit_margin,
                    'market_cap': latest.metadata.custom_metadata.get('market_cap'),
                    'signals': latest.metadata.custom_metadata.get('trend_signals', [])
                })
        
        # Sort by revenue growth
        return sorted(opportunities, key=lambda x: x['revenue_growth'], reverse=True)

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = FinancialReportAnalyzer()
    
    # Ingest earnings reports
    companies = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    
    for ticker in companies:
        # In practice, you'd download actual reports
        report_path = f"reports/{ticker}_10Q_2024Q3.pdf"
        
        if os.path.exists(report_path):
            analyzer.ingest_earnings_report(
                company_ticker=ticker,
                report_path=report_path,
                report_type="10-Q",
                fiscal_period="2024 Q3"
            )
    
    # Compare companies
    comparison = analyzer.compare_companies(
        tickers=companies,
        metrics=['revenue', 'profit_margin', 'roe', 'pe_ratio']
    )
    
    print("\\nCompany Comparison:")
    print(comparison.to_string())
    
    # Find investment opportunities
    opportunities = analyzer.identify_investment_opportunities(
        min_revenue_growth=20,
        max_pe_ratio=30,
        min_profit_margin=15
    )
    
    print("\\nInvestment Opportunities:")
    for opp in opportunities:
        print(f"\\n{opp['ticker']}:")
        print(f"  Revenue Growth: {opp['revenue_growth']:.1f}%")
        print(f"  P/E Ratio: {opp['pe_ratio']:.2f}")
        print(f"  Profit Margin: {opp['profit_margin']:.1f}%")
    
    # Generate performance chart
    fig = analyzer.generate_performance_chart('AAPL', 'revenue')
    if fig:
        fig.show()
```

## Key Concepts

### Multi-Format Support

The system handles various financial document formats:
- **PDF Reports**: Extracts text and tables from scanned documents
- **XBRL Filings**: Parses structured financial data
- **API Data**: Integrates with market data providers
- **Excel/CSV**: Processes tabular financial data

### Metric Extraction

Intelligent extraction of financial metrics:
- Pattern matching for monetary values
- Context-aware metric identification
- Handling of different units (millions, billions)
- Validation against expected ranges

### Trend Analysis

Comprehensive trend tracking:
- Year-over-year comparisons
- Quarter-over-quarter growth
- Moving averages and volatility
- Anomaly detection

## Extensions

### Advanced Analytics

1. **Predictive Modeling**
   - Forecast future performance
   - Risk assessment models
   - Valuation models (DCF, comparables)
   - Scenario analysis

2. **Peer Analysis**
   - Industry benchmarking
   - Competitive positioning
   - Market share analysis
   - Relative valuation

3. **Sentiment Analysis**
   - Management commentary tone
   - Analyst sentiment tracking
   - News sentiment correlation
   - Social media sentiment

4. **Alternative Data**
   - Web scraping for foot traffic
   - Satellite imagery analysis
   - Job posting trends
   - Patent filings

### Integration Options

1. **Data Sources**
   - SEC EDGAR API
   - Bloomberg Terminal
   - Reuters Eikon
   - Alpha Vantage

2. **Visualization**
   - Interactive dashboards
   - Real-time monitoring
   - Custom reports
   - Mobile alerts

3. **Workflow Automation**
   - Automatic report ingestion
   - Alert on significant changes
   - Report generation
   - Compliance checking

## Best Practices

1. **Data Quality**
   - Validate extracted metrics
   - Cross-reference multiple sources
   - Handle missing data gracefully
   - Document assumptions

2. **Compliance**
   - Respect data licenses
   - Implement access controls
   - Audit trail maintenance
   - Regulatory compliance

3. **Performance**
   - Cache market data
   - Batch process reports
   - Optimize PDF extraction
   - Use incremental updates

4. **Analysis Accuracy**
   - Adjust for one-time items
   - Consider seasonality
   - Account for currency effects
   - Normalize for comparability

This financial analysis system provides a foundation for sophisticated investment research and financial monitoring capabilities.