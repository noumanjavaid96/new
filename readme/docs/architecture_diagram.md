# System Architecture Diagram

This page displays the System Overview (Logical Architecture) diagram for ContentFlow MVP.

The diagram illustrates the main components of the system and their primary interactions.

***

```mermaid
graph TD
    BU["Brand Users"]
    CU["Clipper Users"]
    MA["Mobile Application (Next.js PWA)"]

    subgraph BE ["Backend Infrastructure (Cloud Hosted)"]
        APIGW["API Gateway / Load Balancer"]
        CBS["Core Backend Service (Monolith - Node.js/Python)\n- User Auth\n- Campaign Mgmt\n- Submission Mgmt\n- View Processing (MVP)\n- Payout Orchestration"]
        DB["Database (PostgreSQL)\n- User Data\n- Campaign Data\n- Submissions, Views"]
        OS["Object Storage (S3/GCS)\n- Raw Footage\n- Edited Clips"]
    end

    PG["Payment Gateway (Stripe Connect)"]

    BU <--> MA
    CU <--> MA
    MA -- "HTTPS/API Calls" --> APIGW
    APIGW <--> CBS
    CBS <--> DB
    CBS <--> OS
    CBS -- "Stripe API" --> PG
```



**Key Components:**

* **Users:** Brand Users, Clipper Users.
* **Mobile Application:** The Next.js PWA serving as the frontend.
* **Backend Infrastructure:** Hosted on a cloud platform, including:
  * API Gateway / Load Balancer
  * Core Backend Service (handling main application logic)
  * Database (PostgreSQL)
  * Object Storage (for media files)
* **Payment Gateway:** External service (Stripe Connect) for payment processing.

