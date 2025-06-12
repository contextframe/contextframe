---
url: "https://docs.litellm.ai/docs/data_security"
title: "Data Privacy and Security | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/data_security#__docusaurus_skipToContent_fallback)

On this page

# Data Privacy and Security

At LiteLLM, **safeguarding your data privacy and security** is our top priority. We recognize the critical importance of the data you share with us and handle it with the highest level of diligence.

With LiteLLM Cloud, we handle:

- Deployment

- Scaling

- Upgrades and security patches

- Ensuring high availability

[All services are online](https://status.litellm.ai/)


## Security Measures [​](https://docs.litellm.ai/docs/data_security\#security-measures "Direct link to Security Measures")

### LiteLLM Cloud [​](https://docs.litellm.ai/docs/data_security\#litellm-cloud "Direct link to LiteLLM Cloud")

- We encrypt all data stored using your `LITELLM_MASTER_KEY` and in transit using TLS.
- Our database and application run on GCP, AWS infrastructure, partly managed by NeonDB.
  - US data region: Northern California (AWS/GCP `us-west-1`) & Virginia (AWS `us-east-1`)
  - EU data region Germany/Frankfurt (AWS/GCP `eu-central-1`)
- All users have access to SSO (Single Sign-On) through OAuth 2.0 with Google, Okta, Microsoft, KeyCloak.
- Audit Logs with retention policy
- Control Allowed IP Addresses that can access your Cloud LiteLLM Instance

### Self-hosted Instances LiteLLM [​](https://docs.litellm.ai/docs/data_security\#self-hosted-instances-litellm "Direct link to Self-hosted Instances LiteLLM")

- **No data or telemetry is stored on LiteLLM Servers when you self-host**
- For installation and configuration, see: [Self-hosting guide](https://docs.litellm.ai/docs/proxy/deploy)
- **Telemetry**: We run no telemetry when you self-host LiteLLM

For security inquiries, please contact us at [support@berri.ai](mailto:support@berri.ai)

## **Security Certifications** [​](https://docs.litellm.ai/docs/data_security\#security-certifications "Direct link to security-certifications")

| **Certification** | **Status** |
| --- | --- |
| SOC 2 Type I | Certified. Report available upon request on Enterprise plan. |
| SOC 2 Type II | Certified. Report available upon request on Enterprise plan. |
| ISO 27001 | Certified. Report available upon request on Enterprise |

## Supported Data Regions for LiteLLM Cloud [​](https://docs.litellm.ai/docs/data_security\#supported-data-regions-for-litellm-cloud "Direct link to Supported Data Regions for LiteLLM Cloud")

LiteLLM supports the following data regions:

- US, Northern California (AWS/GCP `us-west-1`)
- Europe, Frankfurt, Germany (AWS/GCP `eu-central-1`)

All data, user accounts, and infrastructure are completely separated between these two regions

## Collection of Personal Data [​](https://docs.litellm.ai/docs/data_security\#collection-of-personal-data "Direct link to Collection of Personal Data")

### For Self-hosted LiteLLM Users: [​](https://docs.litellm.ai/docs/data_security\#for-self-hosted-litellm-users "Direct link to For Self-hosted LiteLLM Users:")

- No personal data is collected or transmitted to LiteLLM servers when you self-host our software.
- Any data generated or processed remains entirely within your own infrastructure.

### For LiteLLM Cloud Users: [​](https://docs.litellm.ai/docs/data_security\#for-litellm-cloud-users "Direct link to For LiteLLM Cloud Users:")

- LiteLLM Cloud tracks LLM usage data - We do not access or store the message / response content of your API requests or responses. You can see the [fields tracked here](https://github.com/BerriAI/litellm/blob/main/schema.prisma#L174)

**How to Use and Share the Personal Data**

- Only proxy admins can view their usage data, and they can only see the usage data of their organization.
- Proxy admins have the ability to invite other users / admins to their server to view their own usage data
- LiteLLM Cloud does not sell or share any usage data with any third parties.

## Cookies Information, Security, and Privacy [​](https://docs.litellm.ai/docs/data_security\#cookies-information-security-and-privacy "Direct link to Cookies Information, Security, and Privacy")

### For Self-hosted LiteLLM Users: [​](https://docs.litellm.ai/docs/data_security\#for-self-hosted-litellm-users-1 "Direct link to For Self-hosted LiteLLM Users:")

- Cookie data remains within your own infrastructure.
- LiteLLM uses minimal cookies, solely for the purpose of allowing Proxy users to access the LiteLLM Admin UI.
- These cookies are stored in your web browser after you log in.
- We do not use cookies for advertising, tracking, or any purpose beyond maintaining your login session.
- The only cookies used are essential for maintaining user authentication and session management for the app UI.
- Session cookies expire when you close your browser, logout or after 24 hours.
- LiteLLM does not use any third-party cookies.
- The Admin UI accesses the cookie to authenticate your login session.
- The cookie is stored as JWT and is not accessible to any other part of the system.
- We (LiteLLM) do not access or share this cookie data for any other purpose.

### For LiteLLM Cloud Users: [​](https://docs.litellm.ai/docs/data_security\#for-litellm-cloud-users-1 "Direct link to For LiteLLM Cloud Users:")

- LiteLLM uses minimal cookies, solely for the purpose of allowing Proxy users to access the LiteLLM Admin UI.
- These cookies are stored in your web browser after you log in.
- We do not use cookies for advertising, tracking, or any purpose beyond maintaining your login session.
- The only cookies used are essential for maintaining user authentication and session management for the app UI.
- Session cookies expire when you close your browser, logout or after 24 hours.
- LiteLLM does not use any third-party cookies.
- The Admin UI accesses the cookie to authenticate your login session.
- The cookie is stored as JWT and is not accessible to any other part of the system.
- We (LiteLLM) do not access or share this cookie data for any other purpose.

## Security Vulnerability Reporting Guidelines [​](https://docs.litellm.ai/docs/data_security\#security-vulnerability-reporting-guidelines "Direct link to Security Vulnerability Reporting Guidelines")

We value the security community's role in protecting our systems and users. To report a security vulnerability:

- Email [support@berri.ai](mailto:support@berri.ai) with details
- Include steps to reproduce the issue
- Provide any relevant additional information

We'll review all reports promptly. Note that we don't currently offer a bug bounty program.

## Vulnerability Scanning [​](https://docs.litellm.ai/docs/data_security\#vulnerability-scanning "Direct link to Vulnerability Scanning")

- LiteLLM runs [`grype`](https://github.com/anchore/grype) security scans on all built Docker images.
  - See [`grype litellm` check on ci/cd](https://github.com/BerriAI/litellm/blob/main/.circleci/config.yml#L1099).
  - Current Status: ✅ Passing. 0 High/Critical severity vulnerabilities found.

## Legal/Compliance FAQs [​](https://docs.litellm.ai/docs/data_security\#legalcompliance-faqs "Direct link to Legal/Compliance FAQs")

### Procurement Options [​](https://docs.litellm.ai/docs/data_security\#procurement-options "Direct link to Procurement Options")

1. Invoicing
2. AWS Marketplace
3. Azure Marketplace

### Vendor Information [​](https://docs.litellm.ai/docs/data_security\#vendor-information "Direct link to Vendor Information")

Legal Entity Name: Berrie AI Incorporated

Company Phone Number: 7708783106

Point of contact email address for security incidents: [krrish@berri.ai](mailto:krrish@berri.ai)

Point of contact email address for general security-related questions: [krrish@berri.ai](mailto:krrish@berri.ai)

Has the Vendor been audited / certified?

- SOC 2 Type I. Certified. Report available upon request on Enterprise plan.
- SOC 2 Type II. In progress. Certificate available by April 15th, 2025.
- ISO 27001. Certified. Report available upon request on Enterprise plan.

Has an information security management system been implemented?

- Yes - [CodeQL](https://codeql.github.com/) and a comprehensive ISMS covering multiple security domains.

Is logging of key events - auth, creation, update changes occurring?

- Yes - we have [audit logs](https://docs.litellm.ai/docs/proxy/multiple_admins#1-switch-on-audit-logs)

Does the Vendor have an established Cybersecurity incident management program?

- Yes, Incident Response Policy available upon request.

Does the vendor have a vulnerability disclosure policy in place? [Yes](https://github.com/BerriAI/litellm?tab=security-ov-file#security-vulnerability-reporting-guidelines)

Does the vendor perform vulnerability scans?

- Yes, regular vulnerability scans are conducted as detailed in the [Vulnerability Scanning](https://docs.litellm.ai/docs/data_security#vulnerability-scanning) section.

Signer Name: Krish Amit Dholakia

Signer Email: [krrish@berri.ai](mailto:krrish@berri.ai)

- [Security Measures](https://docs.litellm.ai/docs/data_security#security-measures)
  - [LiteLLM Cloud](https://docs.litellm.ai/docs/data_security#litellm-cloud)
  - [Self-hosted Instances LiteLLM](https://docs.litellm.ai/docs/data_security#self-hosted-instances-litellm)
- [**Security Certifications**](https://docs.litellm.ai/docs/data_security#security-certifications)
- [Supported Data Regions for LiteLLM Cloud](https://docs.litellm.ai/docs/data_security#supported-data-regions-for-litellm-cloud)
- [Collection of Personal Data](https://docs.litellm.ai/docs/data_security#collection-of-personal-data)
  - [For Self-hosted LiteLLM Users:](https://docs.litellm.ai/docs/data_security#for-self-hosted-litellm-users)
  - [For LiteLLM Cloud Users:](https://docs.litellm.ai/docs/data_security#for-litellm-cloud-users)
- [Cookies Information, Security, and Privacy](https://docs.litellm.ai/docs/data_security#cookies-information-security-and-privacy)
  - [For Self-hosted LiteLLM Users:](https://docs.litellm.ai/docs/data_security#for-self-hosted-litellm-users-1)
  - [For LiteLLM Cloud Users:](https://docs.litellm.ai/docs/data_security#for-litellm-cloud-users-1)
- [Security Vulnerability Reporting Guidelines](https://docs.litellm.ai/docs/data_security#security-vulnerability-reporting-guidelines)
- [Vulnerability Scanning](https://docs.litellm.ai/docs/data_security#vulnerability-scanning)
- [Legal/Compliance FAQs](https://docs.litellm.ai/docs/data_security#legalcompliance-faqs)
  - [Procurement Options](https://docs.litellm.ai/docs/data_security#procurement-options)
  - [Vendor Information](https://docs.litellm.ai/docs/data_security#vendor-information)