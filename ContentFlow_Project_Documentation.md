# ContentFlow - Project Documentation (MVP v0.1 Focus)

## 1. Introduction & Vision (Derived from PRD)

### 1.1. Vision
To create the leading mobile-first marketplace that seamlessly connects brands with talented content "clippers" (editors & distributors). ContentFlow will revolutionize how short-form video content is created, distributed, and rewarded through an intuitive, AI-powered platform.

### 1.2. Problem Statement
*   **For Brands:** Difficulty finding reliable and skilled clippers, managing multiple creators, tracking content performance across platforms, and ensuring fair payment for results.
*   **For Clippers:** Difficulty finding consistent, quality projects, getting fair compensation based on content performance, and managing payments efficiently.

### 1.3. Proposed Solution
ContentFlow will be a mobile-first marketplace connecting brands and clippers, delivered as a Progressive Web App (PWA) for broad accessibility. It will feature OTP-verified registration for security and direct social media account integration (e.g., TikTok) for streamlined content distribution and performance verification. The platform will offer a comprehensive campaign management system, allowing brands to post projects and track their status (e.g., `"In Progress"`, `"Finished"`, `"Discarded"`), and clippers to explore, apply, and submit content. It will include user profiles, role-specific dashboards, basic in-app messaging, and will facilitate performance-based payouts, initially managed with significant admin/manual support for view verification and payment processing.
> **Note:** This solution is now aligned with the Payper application model, emphasizing direct social media integration and comprehensive campaign management.

### 1.4. Project Goals (MVP)
*   Successfully launch a functional mobile app (iOS & Android preferred) implementing the Payper-inspired core user flows.
    > **Key Focus:** Delivering a working application that embodies the core Payper-like interactions.
*   Validate the "One-Click-Solution" philosophy through seamless user onboarding (`Email+OTP`, Social Connect) and core task completion.
    > **Key Focus:** Ensuring ease of use for critical user journeys.
*   Onboard an initial cohort of brands and clippers to test the end-to-end campaign lifecycle: Brand posts campaign -> Clipper applies & submits content -> Clipper posts to social media -> Views tracked (MVP: `manual/link-based`) -> Clipper status/earnings updated.
    > **Key Focus:** Proving the fundamental value proposition and operational flow.
*   Successfully integrate with at least one major social media platform (e.g., TikTok) for clipper account connection and content link submission.
    > **Key Focus:** Technical validation of a key third-party integration.
*   Gather user feedback on usability, particularly for campaign management, content submission, and dashboard clarity.
    > **Key Focus:** Informing future iterations based on real user experience.

## 2. Target Audience (Derived from PRD)

| User Group         | Description / Key Characteristics                                                                                                                               |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Brands/Businesses** | Small to medium-sized businesses (SMBs), startups, entrepreneurs, marketing agencies managing multiple clients, influencers, and personal brands looking to scale content output. |
| **Clippers/Creators** | Freelance video editors specializing in short-form content (Reels, TikToks, Shorts), social media managers offering content creation/distribution, and aspiring content creators.    |

## 3. Prioritized MVP Features (Payper-centric Model)

This section outlines the core MVP features for ContentFlow, aligned with the Payper application flow analysis and detailed in `ContentFlow_User_Flows.md` and `ContentFlow_UI_Screen_Descriptions.md`.

### 3.1. User Onboarding & Authentication
*   **Description:** Secure and streamlined user registration and login.
*   **Details:**
    *   **Email Registration:** Users sign up using their email address.
    *   **OTP Verification:** Email addresses are verified using a One-Time Password (OTP) sent to the user.
    *   **Password Setup:** Secure password creation and confirmation.
    *   **Role Selection:** Users designate themselves as either "Brand" or "Clipper".
    *   **Social Media Account Connection (Clipper Focus):** Clippers connect their primary social media account (e.g., TikTok) to facilitate content distribution, identity verification, and (future) view tracking.
        > **Note:** The initial MVP will focus on TikTok integration, mirroring the Payper flow.
    *   **Login:** Secure login for returning users with email and password.
    *   **Forgot Password:** Basic flow for password reset.

### 3.2. Brand User Features
*   **Description:** Functionality enabling brands to manage their content campaigns and interactions.
*   **Details:**
    *   **Brand Profile Setup:** Basic profile information (e.g., company name).
    *   **Campaign Creation:**
        *   Input campaign title, detailed brief, style/vibe keywords.
        *   Upload or link to raw footage/assets.
        *   Specify target social media platforms.
        *   Define budget structure (e.g., amount per X views, max budget).
    *   **Campaign Dashboard/Management:**
        *   View list of created campaigns with statuses (e.g., `"Active"`, `"Pending Approval"`, `"In Progress"`, `"Under Review"`, `"Finished"`, `"Discarded"`).
        *   Select a campaign to view submitted content and details.
    *   **View Submitted Content:**
        *   Review video clips submitted by clippers for a campaign.
        *   Access links to live social media posts provided by clippers.
    *   **Approve/Request Revisions:** Mark submissions as approved or request changes from clippers (with comments).
    *   **Basic Brand Dashboard:** Overview of active campaigns, total submissions, (manually tracked) total views, and (manually tracked) total spend.

### 3.3. Clipper User Features
*   **Description:** Functionality enabling clippers to find projects, submit content, and track earnings.
*   **Details:**
    *   **Clipper Profile Setup:**
        *   Connect primary social media account (e.g., TikTok).
        *   (Future Placeholder) Payout information setup.
        *   (Simplified MVP) Basic profile info, link to connected social profile as portfolio.
    *   **Explore/Browse Campaigns:**
        *   View a list of available campaigns posted by brands.
        *   Search, filter (by niche, platform), and sort campaigns.
        *   View detailed campaign information (brief, brand, payout structure, asset access info).
    *   **Campaign Application:** "One-Click" application to campaigns of interest.
    *   **Content Submission:**
        *   Upload edited video content for an approved/active campaign.
        *   Provide direct links to where the content has been posted on social media.
        *   Add optional notes for the brand.
    *   **My Work/Submissions Dashboard:**
        *   View list of their submissions with status (e.g., "Pending Review," "Approved," "Requires Revision," "Paid").
        *   Track (manually verified/updated for MVP) views for their submissions.
        *   See estimated/actual earnings per submission.
    *   **Earnings Dashboard:**
        *   Overview of pending payout amounts and total earned (payments processed manually outside app for MVP).
        *   Simplified payout history (list of amounts marked as paid by admin).

### 3.4. Platform Core Features
*   **Description:** Essential underlying functionalities for the platform.
*   **Details:**
    *   **User Profile Management (Shared):**
        *   Edit basic profile information (email, password).
        *   (Clipper) Manage connected social accounts.
    *   **Basic In-App Messaging:**
        *   Text-based chat between a brand and a clipper specifically for an active campaign they are engaged in.
        *   List of active chats, chat detail screen.
    *   **View Tracking (MVP - Manual/Link-Based):**
        *   Clippers provide direct links to their live posts.
        *   Admin/system mechanism for basic verification of links and manual input/update of view counts. Data displayed on dashboards.
        > **MVP Simplification:** View counts will initially be updated by admins based on clipper-provided links and manual verification. Automation is a post-MVP goal.
    *   **Payout Calculation & Admin Tracking (MVP - Manual Payouts):**
        *   System calculates earnings based on (manually) verified views and campaign terms.
        *   Admin interface/tool to mark payouts as `"processed"` (actual payment happens outside the app).
        > **MVP Simplification:** Payouts will be calculated by the system but processed manually outside the app. The system will track status.
    *   **Basic Rating System (Post-Campaign):** Brands can give a simple star rating to clippers after a campaign is completed.
    *   **Settings (Shared):** Access to account settings, notification preferences (basic), privacy policy, terms of service, logout.
    *   **Admin Support (Implied Backend/Tooling):**
        *   Manual verification of views.
        *   Manual processing and tracking of payouts.
        *   Basic user management/support.
        *   (Minimal for MVP) Review of suspicious activity/disputes.
        > **Important:** Robust admin tools will be crucial for managing MVP processes like manual view verification and payout tracking.

## 4. User Experience (UX) & Design Principles (Derived from PRD)

### 4.1. "One-Click-Solution" Philosophy
Every core action should be achievable with minimal steps and cognitive load. The design should prioritize efficiency and ease of use.

### 4.2. Mobile-First
Design and optimize primarily for iOS and Android platforms. The user experience should feel native and intuitive on mobile devices.

### 4.3. Sleek, Simple, Intuitive
Inspired by Apple's design language (e.g., iMessage simplicity) and competitor "Payper's" clean UI. The application must avoid lags and ensure fast load times.

### 4.4. Branding & Aesthetics
*   **Name:** ContentFlow (or other TBD, easy to remember, reflects purpose).
*   **Colors & Style:** Modern, energetic, professional, trustworthy.
*   **Inspiration:** Successful aesthetic of profiles like Hormozi, Iman Gadzhi, Belmar (clean lines, possibly dark mode option, strong typography). The branding should reflect ambition and results.

## 5. Proposed Next Steps for Design Phase

This section outlines initial steps for the UI/UX design process, based on the UX principles and MVP scope.

### 5.1. Mood Board & Style Guide Development (Lite for MVP)
*   **Action:** Create a digital mood board collecting visual inspiration (Hormozi, Gadzhi, Belmar, Apple, Payper).
*   **Output:** A simple style guide defining primary/secondary color palettes, typography, iconography style, and general look and feel (e.g., cards, spacing, dark mode considerations).
*   **Rationale:** Establishes a consistent visual language early.

### 5.2. User Flow Mapping for Core MVP Loops
*   **Action:** Visually map step-by-step user journeys for high-priority MVP features (Brand: Signup -> Create Campaign -> View Submissions; Clipper: Signup -> Browse Campaigns -> Apply -> Submit Content -> View Earnings).
*   **"One-Click" Focus:** Critically evaluate each step for simplification.
*   **Output:** User flow diagrams.
*   **Rationale:** Ensures shared understanding of user interaction and identifies friction points.

### 5.3. Wireframing (Low-Fidelity)
*   **Action:** Create basic wireframes for all screens in user flows, focusing on layout, information hierarchy, and core functionality.
*   **Key Screens:** Signup/Login, Profiles, Dashboards, Campaign Creation, Campaign List, Submission Forms.
*   **Output:** Low-fidelity wireframes.
*   **Rationale:** Allows rapid iteration on layout and flow for the "One-Click" concept.

### 5.4. Prototyping (Clickable Wireframes)
*   **Action:** Use a tool (e.g., Figma, Adobe XD) to link wireframes into a simple interactive prototype.
*   **Focus:** Test main user flows.
*   **Output:** A clickable prototype.
*   **Rationale:** Enables early usability testing of navigation and core tasks.

### 5.5. High-Fidelity Mockups (Key Screens)
*   **Action:** Based on approved wireframes and style guide, create detailed visual mockups for a few key screens (e.g., Brand Dashboard, Clipper Campaign Browsing, Campaign Creation).
*   **Output:** Pixel-perfect (or near) mockups.
*   **Rationale:** Provides clear visual specification for development.

### 5.6. Design Review & Iteration
*   **Action:** Regularly review designs with stakeholders for alignment with PRD, technical feasibility, and "One-Click" vision.
*   **Output:** Refined designs.
*   **Rationale:** Keeps design collaborative and agile.

## 6. Technology Considerations & Recommendations

High-level technology stack recommendations for the MVP, prioritizing speed of development and leveraging team skills. (Based on PRD Section 6 and further analysis).

### 6.1. Mobile Development
*   **Recommendation:** The application is a `Next.js` web application, which will be enhanced into a **Progressive Web App (PWA)** for a mobile-first experience.
*   **Rationale:** This leverages the existing web stack (`Next.js`, `React`, `Tailwind CSS`) for rapid delivery of an installable, app-like experience on mobile devices without requiring separate native codebases. It supports the "mobile-first" philosophy efficiently.
*   **Key Considerations for PWA:** Service worker implementation for caching and basic offline capabilities, web app manifest configuration, ensuring HTTPS, and maintaining a responsive design.
> **Note:** This PWA approach aligns with decisions reflected in the Architecture Document, prioritizing speed and leveraging the existing web application foundation.

### 6.2. Backend
*   **Recommendation:** Node.js (with Express.js/NestJS) or Python (Flask/FastAPI).
*   **Rationale:** Rapid development, large communities, good for I/O-bound tasks. JavaScript full-stack option with React Native.
*   **Key Question for Dev Team:** Team's strongest backend language/framework for rapid development?

### 6.3. Database
*   **Recommendation:** PostgreSQL.
*   **Rationale:** Robust relational DB, good for structured data (users, campaigns, submissions), scales well, handles JSONB if needed. MySQL is also a solid alternative.
*   **Key Question for Dev Team:** Strong preference or existing infrastructure for a particular DB?

### 6.4. Cloud Hosting
*   **Recommendation:** AWS, Google Cloud Platform (GCP), or Azure.
*   **Rationale:** Choose based on team familiarity, available managed services (RDS, App Engine, Elastic Beanstalk), and cost-effective tiers for MVP.
*   **Key Question for Dev Team:** Preferred cloud provider or existing credits?

### 6.5. AI/View Tracking (MVP Approach)
*   **Technology:**
    *   **Link Validation/Basic Scraping:** Backend logic (Python with `requests`/`BeautifulSoup` or Node.js with `axios`/`cheerio`).
    *   **API Integration:** Investigate per platform (e.g., TikTok) for any usable official APIs for view counts (often limited).
    *   **Bot Detection (MVP):** Rule-based heuristics or manual flagging.
*   **Key Question for Dev Team:** Initial target platform(s) for view tracking? Simplest viable way to get initial "view count" for MVP loop (even if self-reported with checks)?

### 6.6. Payment Gateway
*   **Recommendation:** Stripe Connect.
*   **Rationale:** Well-suited for marketplace models (platform facilitates payments between brands and clippers, takes commission).
*   **Key Question for Dev Team:** Confirm Stripe Connect. MVP will simulate payouts but design for future integration.

### 6.7. Analytics
*   **Recommendation:**
    *   **In-app:** Log key events to backend DB (signups, campaign creations).
    *   **External Tool:** Mixpanel, Amplitude, or PostHog (free tiers are valuable for MVP).
*   **Key Question for Dev Team:** Experience with any specific product analytics tools?

## 7. Non-Functional Requirements (NFRs) - MVP (Derived from PRD)

Key NFRs to ensure a quality MVP product.

| Category      | Requirement                                                                                                | MVP Goal / Notes                                                                                                |
|---------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| **Performance** | App must be responsive and load quickly.                                                                   | Target P95 for core interactions < 2s. PWA optimizations (caching, lazy loading).                               |
|               | Video uploads/downloads should be optimized.                                                               | Background processing for uploads if feasible; direct links to storage for downloads.                             |
| **Scalability** | Backend architecture should allow for future growth in users and data.                                     | Stateless backend API design where possible; leverage managed cloud services that can scale (e.g., serverless, managed DB). |
| **Security**    | Secure user authentication.                                                                                | Use of industry-standard libraries for auth (`Email+OTP`, JWTs).                                                     |
|               | Protection of personal and payment data.                                                                   | HTTPS/TLS for all communication; secure handling of API keys; no storage of raw payment details (rely on Stripe). |
|               | Secure content handling.                                                                                   | Private storage for raw footage; access controls.                                                               |
| **Usability**   | Extremely high priority; minimal learning curve.                                                           | Align with `"One-Click-Solution"` philosophy; intuitive UI/UX for core flows.                                     |
| **Reliability** | Accurate view tracking (within stated MVP limitations).                                                      | Critical for trust. MVP relies on manual/admin verification of clipper-provided links.                            |
|               | Dependable payout calculation.                                                                             | System calculates based on verified views; payouts are manual for MVP but status tracked.                         |
|               | The system should consistently perform its core functions.                                                   | Focus on robust implementation of core campaign lifecycle.                                                        |

## 8. Conceptual Development Sprints/Phases (Hyper-Focused 3-Week MVP)

> **Important:** This 3-week plan assumes UI designs are largely complete (as per existing Next.js/React project) and focuses on building the minimum viable backend, integrating the UI, basic PWA setup, and preparing for a "go-live" with manual backend processes for many features.

| Sprint (1 Week) | Goal                                                                 | Key Tasks & Features (Backend Focus, UI Integration)                                                                                                                                                              | Est. Hours / Complexity                                                                                                | Notes / Manual Processes                                                                                                |
|-----------------|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| **Sprint 1**    | Backend Foundation & Core APIs                                       | - Backend project setup (Node.js/Express or Python/Flask - *User to specify preference*). <br> - Core DB schema (`Users`, `Campaigns`, `Submissions`). <br> - User Auth API (email/password registration & login). <br> - Campaign Creation API (`POST /campaigns`). <br> - Campaign Listing API (`GET /campaigns`). <br> - Basic PWA: Setup `manifest.json` for Next.js app. | - Backend setup (M, ~15-20h)<br>- Core APIs (L, ~20-25h)<br>- PWA Manifest (S, ~4h)                                   | - User approval might be manual. <br> - No OTP or full Social Connect in this sprint.                                    |
| **Sprint 2**    | Content Submission & UI-Backend Integration                          | - Content Submission API (`POST /campaigns/{id}/submit` - stores content links). <br> - View Submissions API (Brand view - `GET /campaigns/{id}/submissions`). <br> - Connect existing Next.js UI screens for: Registration, Login, Campaign Creation (Brand), Campaign List (Clipper), Submit Content (Clipper), View Submissions (Brand). <br> - Basic PWA: Implement a simple service worker for app shell caching. | - Submission APIs (M, ~15-20h)<br>- UI-Backend Integration (L, ~25-30h)<br>- PWA Service Worker (S, ~5-8h)             | - Campaign approval by Brand is manual. <br> - Clipper application to campaign is implicit by submission for this MVP. |
| **Sprint 3**    | Testing, Manual Process Definition & "Go-Live" Prep                | - End-to-end testing of core Brand & Clipper flows. <br> - Document all manual admin processes (user verification, campaign content review, view count input, payout status updates). <br> - Basic deployment of backend service and Next.js PWA to a cloud host. <br> - Final PWA checks (installability, basic offline fallback). | - Testing (M, ~20h)<br>- Admin Docs (S, ~8-10h)<br>- Deployment (M, ~10-15h)                                          | - View tracking is entirely manual (admin updates DB). <br> - Payouts are entirely manual (admin updates DB status). <br> - Messaging, detailed dashboards, advanced filtering are out of scope. |

> **Note on Estimates:** These are highly conceptual estimates and relative complexity indicators (S=Small, M=Medium, L=Large) intended to provide a general sense of effort for a solo developer with relevant experience. Actual hours can vary significantly based on specific technical choices, familiarity with tools, and unforeseen challenges. They are not a substitute for detailed task breakdown and estimation by the developer.

## 9. Key Challenges & Risks for MVP

Critical risks from PRD Section 10 and MVP context, with mitigation strategies.

### 9.1. Technical Complexity of View Tracking
*   > **Risk:** Accurately tracking views across third-party platforms is difficult; APIs change or are restrictive.
*   **MVP Impact:** Undermines trust if unreliable.
*   > **Mitigation Strategy:**
    *   Radically simplify: Clipper-provided links.
    *   Manual/assisted verification of views by admin.
    *   Focus on one platform first (e.g., TikTok).
    *   Transparency with early users about limitations.
    *   Contingency: Clipper self-reporting with spot-checks.

### 9.2. User Acquisition (Chicken & Egg Problem)
*   > **Risk:** Attracting both brands and clippers simultaneously.
*   **MVP Impact:** Marketplace needs both sides to function.
*   > **Mitigation Strategy:**
    *   Targeted manual onboarding of a small, balanced group.
    *   Incentivize early adopters (e.g., lower commission).
    *   Focus on a specific niche initially.
    *   Leverage founder/team networks.

### 9.3. Fraud Prevention (View-Botting & Inauthentic Engagement)
*   > **Risk:** Clippers inflating views.
*   **MVP Impact:** Brands lose money and trust.
*   > **Mitigation Strategy:**
    *   Manual review of suspicious view patterns.
    *   Clear Terms of Service against fraud.
    *   Basic vetting of clipper social media profiles.
    *   Simple dispute resolution for brands to flag suspected fraud.

### 9.4. Usability & "One-Click-Solution" Philosophy
*   > **Risk:** App is clunky or hard to use, failing the "One-Click" promise.
*   **MVP Impact:** Early adopters churn.
*   > **Mitigation Strategy:**
    *   Ruthless prioritization of simplicity in features.
    *   User testing (informal) of key flows.
    *   Clean, intuitive UI design from the start.
    *   Focus on exceptionally smooth core flows (campaign creation, content submission).

### 9.5. Platform API Reliance
*   > **Risk:** Dependence on social media platforms not changing terms/API access (less critical for initial MVP with manual processes, but risk for scaling).
*   **MVP Impact:** Degradation of view tracking if unofficial methods break.
*   > **Mitigation Strategy:**
    *   Design view-tracking for adaptability (pluggable methods).
    *   Fallback to `manual/self-reported` data if automated methods fail.

## 10. Monetization Strategy (Derived from PRD)

### 10.1. Commission-Based
*   A percentage fee taken from successful campaign payouts (e.g., 10-20% of the amount paid by the brand to the clipper). This aligns platform revenue with user success.

## 11. Success Metrics (MVP - Derived from PRD)

| Metric Category         | Metric                                                              | Description / How to Measure                                                                    | MVP Target (Conceptual)         |
|-------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|---------------------------------|
| **User Adoption**       | Number of Registered Brands                                         | Count of unique brand accounts created.                                                         | e.g., 20-50 active brands       |
|                         | Number of Registered Clippers                                       | Count of unique clipper accounts created with connected social media (e.g., TikTok).              | e.g., 50-100 active clippers    |
|                         | User Acquisition Rate                                               | (New Users / Period). Initially tracked manually or via basic analytics.                         | Steady week-over-week growth    |
| **Platform Engagement** | Number of Campaigns Posted                                          | Count of unique campaigns successfully created by brands.                                         | e.g., 30-60 campaigns           |
|                         | Number of Content Submissions                                       | Count of unique content pieces submitted by clippers.                                           | e.g., 100-200 submissions       |
|                         | Campaign Completion Rate                                            | (Campaigns marked "Finished" / Campaigns Posted).                                               | > 70%                           |
| **Core Loop Validation**| Total Views Tracked (MVP: Manually Verified)                        | Sum of verified views for all submitted content, based on admin input.                          | Demonstrate tracking capability |
|                         | Payouts Processed (MVP: Manually)                                   | Number and total value of payouts successfully processed (manually) and status updated in system. | Successful processing for all valid earnings |
| **User Satisfaction**   | Average Rating of Clippers by Brands                                | Average of 1-5 star ratings given by brands post-campaign.                                      | > 4.0 stars                     |
|                         | Qualitative Feedback (Surveys/Interviews)                           | Themes from direct user feedback on usability, value, and pain points.                          | Positive sentiment, actionable insights |
|                         | App Store/PWA Install Prompts Accepted (Post-MVP for App Store)     | (If PWA install prompt is implemented) Number of users adding to home screen.                   | Monitor acceptance rate         |
| **Platform Health**     | Churn Rate (Early Cohorts)                                          | (Lost Users / Total Users for cohort). Monitor initial user retention.                          | Low initial churn             |
|                         | Core User Flow Completion Rate (Analytics - future)                 | % of users successfully completing key flows (e.g., signup, campaign creation, submission).     | Track for improvement           |

> **Note:** Many MVP targets are conceptual and will be refined based on early user acquisition and platform performance. Initial focus is on validating the core loop and gathering qualitative feedback.

## 12. Future Considerations (Post-MVP - Derived from PRD)

*   Advanced AI for more precise view-bot detection and content performance prediction.
*   Tiered subscriptions for Brands (e.g., more features, lower commission).
*   Enhanced clipper profiles (portfolios, skill endorsements).
*   Direct invite system for brands to connect with specific clippers.
*   Educational resources for clippers and brands.
*   Integration with more social platforms and content tools.
*   Gamification elements.
