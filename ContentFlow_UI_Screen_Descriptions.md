> **Note on 3-Week MVP Scope:** These screen descriptions detail the comprehensive UI based on the Payper model. The initial 3-week MVP will implement the core UI for essential flows (registration, campaign creation/viewing, content submission). Some described elements or states might be placeholders or have simplified functionality in the 3-week deliverable.

# ContentFlow Mobile UI Screen Descriptions (MVP Focus, based on Payper)

This document describes the key mobile UI screens and their elements for the ContentFlow MVP. These descriptions are designed to support the user flows outlined in `ContentFlow_User_Flows.md`, drawing inspiration from the Payper application flow where applicable.

## I. Onboarding Screens

### 1. Launch Screen (`LaunchScreen`)
*   **Purpose:** First screen users see. Provides options to sign up or log in.
*   **Key Elements:**
    *   **Logo:** ContentFlow Logo.
    *   **Title/Tagline:** "ContentFlow - The future of content creation and collaboration."
    *   **Button:** `"Get Started"` (Primary action, navigates to `SignupScreen_Email`).
    *   **Button:** `"Login"` (Secondary action, navigates to `LoginScreen`).
    *   **Text:** "By continuing, you agree to our Terms of Service and Privacy Policy." (with links).

### 2. Signup - Email Input Screen (`SignupScreen_Email`)
*   **Purpose:** Allows new users to start registration by providing their email. (Inspired by Payper's initial email step).
*   **Key Elements:**
    *   **Title:** `"Join ContentFlow"` or `"What's your email?"`
    *   **Input Field:** Email Address (placeholder: "you@example.com", keyboard: email).
    *   **Button:** `"Continue"` (Navigates to `SignupScreen_OTP` after backend validation of email format and availability).
    *   **Text:** "Already have an account?"
    *   **Link/Button:** `"Login"` (Navigates to `LoginScreen`).
    *   **Progress Indicator:** (Optional, e.g., Step 1 of X).

### 3. Signup - OTP Verification Screen (`SignupScreen_OTP`)
*   **Purpose:** Verifies the user's email address using an OTP. (Inspired by Payper's OTP step).
*   **Key Elements:**
    *   **Title:** `"Verify Your Email"` or `"Enter Code"`.
    *   **Text:** "We've sent a 6-digit code to [user_email@example.com]. Please enter it below."
    *   **Input Field (OTP):** Typically 6 separate input boxes or a single field formatted for OTP entry.
    *   **Button:** `"Verify"` (Validates OTP with backend. On success, navigates to `SignupScreen_PasswordRole`).
    *   **Link/Button:** `"Resend Code"` (Triggers backend to send a new OTP).
    > **MVP Note:** OTP input is crucial for email verification as per the Payper model.
    *   **Link/Button:** `"Change Email"` (Navigates back to `SignupScreen_Email`).

### 4. Signup - Password & Role Screen (`SignupScreen_PasswordRole`)
*   **Purpose:** Allows user to set their password and choose their role (Brand/Clipper). (Combines steps for MVP simplicity).
*   **Key Elements:**
    *   **Title:** `"Create Your Profile"` or `"Almost there!"`
    *   **Input Field:** Password (placeholder: "Min. 8 characters", secure entry).
    *   **Input Field:** Confirm Password (placeholder: "Re-enter password", secure entry).
    *   **Radio Group/Segmented Control (Role Selection):**
        *   Option: `"I'm a Brand"` (Looking for clippers)
        *   Option: `"I'm a Clipper"` (Looking for projects)
    *   **Checkbox:** `"I agree to the Terms of Service and Privacy Policy."` (Required).
    *   **Button:** `"Complete Signup"` or `"Create Account"` (Submits data to backend. On success, navigates to role-specific next step, e.g., `ConnectSocialScreen_Clipper` for Clippers or `BrandProfileSetupScreen` for Brands).

### 5. Connect Social Account Screen (Clipper) (`ConnectSocialScreen_Clipper`)
*   **Purpose:** Prompts Clipper users to connect their primary social media account (e.g., TikTok) for campaign participation and view tracking. (Inspired by Payper's TikTok connect).
*   **Key Elements:**
    *   **Title:** `"Connect Your TikTok Account"`.
    *   **Text:** "Connect your TikTok to apply for campaigns, showcase your work, and enable automated view tracking."
    *   **Button:** `"Connect TikTok"` (Primary action, initiates OAuth flow).
    *   **Image/Icon:** TikTok logo.
    *   **Link/Button:** `"Skip for Now"` or `"Do this Later"` (Optional, may limit functionality. Navigates to `ClipperDashboardScreen_BrowseCampaigns` but with prompts to connect later).
        > **User Choice:** Allowing users to skip this initially might increase signup completion but requires in-app prompts later to ensure core functionality (like campaign application for clippers) isn't blocked.
    *   **Text:** Explaining data permissions ContentFlow will request (transparency).

### 6. TikTok Authorization WebView/Screen (Intermediate)
*   **Purpose:** Displays TikTok's official login and authorization page within a WebView or via app switch. This screen is controlled by TikTok.
    > **Third-Party UI:** The content and behavior of this screen are controlled by TikTok.
*   **Key Elements (Controlled by TikTok):**
    *   TikTok login form (if user not logged into TikTok).
    *   List of permissions ContentFlow is requesting.
    *   `"Authorize"` / `"Cancel"` buttons.
*   **ContentFlow Wrapper (if WebView):**
    *   **Header:** `"Authorize with TikTok"`.
    *   **Close/Cancel Button:** To abort the WebView flow and return to `ConnectSocialScreen_Clipper`.

### 7. Login Screen (`LoginScreen`)
*   **Purpose:** Allows existing users to log in.
*   **Key Elements:**
    *   **Title:** `"Welcome Back!"` or `"Login"`.
    *   **Input Field:** Email Address.
    *   **Input Field:** Password (secure entry).
    *   **Link/Button:** `"Forgot Password?"` (Navigates to `ForgotPasswordScreen`).
    *   **Button:** `"Login"` (Primary action, authenticates with backend).
    *   **Text:** "Don't have an account?"
    *   **Link/Button:** `"Sign Up"` (Navigates to `SignupScreen_Email`).

## II. Main Clipper Screens

### 1. Clipper Dashboard / Explore Campaigns (`ClipperDashboardScreen_BrowseCampaigns`)
*   **Purpose:** Main landing screen for Clippers. Allows browsing and searching for available campaigns. (Similar to Payper's "Explore" or campaign list).
*   **Key Elements:**
    *   **Header:** `"Explore Campaigns"` or `"Hi, [ClipperName]!"`.
    *   **Profile Icon/Button:** Navigates to `ClipperProfileScreen`.
    *   **Search Bar:** For keyword search of campaigns.
    *   **Filter/Sort Controls:**
        *   `Filter` by Niche (e.g., Gaming, Tech).
        *   `Filter` by Platform (e.g., TikTok, Reels).
        *   `Sort` by (e.g., Newest, Highest Payout, Ending Soon).
    *   **Campaign List:** Scrollable list of `CampaignBrowseListItem` components.
        *   **`CampaignBrowseListItem`:** Campaign Title, Brand Name (or logo), Brief Summary, Payout Structure (e.g., "$X per 1k views"), Target Platform icon(s). Tapping navigates to `ClipperCampaignDetailsScreen`.
    *   **Empty State:** Message shown if no campaigns match filters or none are available.
    *   **TabBar:** (See General UI Elements).

### 2. Campaign Details Screen (Clipper) (`ClipperCampaignDetailsScreen`)
*   **Purpose:** Shows detailed information about a specific campaign selected by the Clipper.
*   **Key Elements:**
    *   **Navigation:** `BackButton`.
    *   **Header:** Campaign Title.
    *   **Brand Information:** Brand Name, (Optional: Brand Logo, short description).
    *   **Section: Project Brief:** Full campaign description, objectives, key messages.
    *   **Section: Raw Footage/Assets:** Links or previews of assets provided by the brand (downloadable upon application acceptance).
    *   **Section: Desired Style/Vibe:** `Tags` or descriptive text.
    *   **Section: Target Platforms:** `List` of platforms for content distribution.
    *   **Section: Payout Structure:** Detailed breakdown (e.g., rate per view/milestone, max budget if any).
    *   **Button:** `"Apply to this Campaign"` (Primary action. Changes to `"Applied"` or `"Application Sent"` post-tap. Triggers backend application).
    *   **Button (Conditional):** `"Submit Content"` (Visible if Clipper is approved for the campaign. Navigates to `SubmitEditedContentScreen`).

### 3. My Work / Earnings Dashboard (Clipper) (`ClipperMyWorkScreen_Earnings`)
*   **Purpose:** Allows Clippers to track their active submissions, view status, see earnings, and manage their work. (Combines Payper's "My Campaigns" with earnings info).
*   **Key Elements:**
    *   **Header:** `"My Work & Earnings"`.
    *   **Summary Section:**
        > **Data Source Note:** Pending and Total Earned amounts are based on view counts manually verified and updated by admins in the MVP.
        *   `StatBox`: "Pending Payout" ([Total Amount]).
        *   `StatBox`: "Total Earned" ([Total Amount]).
        *   `StatBox`: "Active Submissions" ([Count]).
    *   **Segmented Control/Tabs:**
        *   `"My Submissions"` (Default view).
        *   `"Payout History"`.
    *   **View: My Submissions:**
        *   **List:** Scrollable list of `MySubmissionListItem` components.
            *   **`MySubmissionListItem`:** Campaign Title, Submission Date, Status (Pending Review, Approved, Requires Revision, Paid), Verified Views, Estimated/Actual Earnings. Tapping could link to `ClipperCampaignDetailsScreen` or a specific submission detail view.
            *   **`Button` (Conditional):** `"Edit Submission"` (if status is `"Requires Revision"`).
        *   **Empty State:** Message if no submissions yet.
    *   **View: Payout History:**
        *   **List:** Scrollable list of `PayoutHistoryItem` components.
            *   **`PayoutHistoryItem`:** Payout Date, Amount, Related Campaign(s), Status (Processed, Cleared).
        *   **Empty State:** Message if no payouts yet.
    *   **TabBar:** (See General UI Elements).

### 4. Submit Edited Content Screen (Clipper) (`SubmitEditedContentScreen`)
*   **Purpose:** Enables Clippers to upload their edited video and provide links to live posts for a specific campaign they are working on.
*   **Key Elements:**
    *   **Navigation:** `BackButton`.
    *   **Header:** `"Submit Content for: [CampaignName]"`.
    *   **Form:**
        *   **File Upload:** `"Upload Edited Video"` (Allows selection of video file. Shows progress bar).
        *   **Repeater Section (Platform Links):**
            *   `Input Field`: Platform Name (e.g., TikTok).
            *   `Input Field`: Direct URL to live post.
            *   `Button`: `"Add Another Link"`.
        *   **Text Area (Optional):** `"Notes for the Brand"`.
        *   **Checkbox:** `"I confirm this work is my original creation and meets campaign requirements."` (Required).
        *   **Button:** `"Submit Content"` (Primary action. Uploads data to backend).

### 5. Clipper Profile Screen (`ClipperProfileScreen`)
*   **Purpose:** Displays and allows editing of the Clipper's public-facing and private profile information. (Payper has a profile view with videos).
*   **Key Elements:**
    *   **Navigation:** `BackButton` (if accessed from tab), `EditButton`.
    *   **Profile Header:** Profile Picture, Clipper Name/Username.
    *   **Section: Connected Accounts:**
        *   Displays connected social accounts (e.g., `"TikTok: @[username]"`).
        *   `Button`: `"Connect More Accounts"` or `"Manage Connections"`.
    *   **Section: Portfolio/Video Showcase (Post-MVP or simplified for MVP):**
        > **MVP Simplification:** For MVP, this might just be a link to their connected social profile. A more integrated showcase is a future enhancement.
        *   Grid/List of video thumbnails from successful/approved submissions or manually uploaded showcase videos.
        *   (MVP: Might just list links to their primary connected social profile).
    *   **Section: About Me (Optional):** Short bio.
    *   **Section: Skills/Niches (Optional):** `Tags` indicating expertise.
    *   **Button:** `"View My Earnings Dashboard"` (Navigates to `ClipperMyWorkScreen_Earnings`).
    *   **Button:** `"Settings"` (Navigates to `SettingsScreen`).
    *   **TabBar:** (See General UI Elements).

### 6. Clipper Messaging Screens (`ClipperMessagesScreen`, `ChatDetailScreen`)
*   **Purpose:** Allows Clippers to communicate with Brands regarding active campaigns.
*   **`ClipperMessagesScreen` (List View):**
    *   **Header:** `"Messages"`.
    *   **List:** Scrollable list of `ChatListItem` components.
        *   **`ChatListItem`:** Brand Name/Logo, Last Message Snippet, Timestamp, Unread Indicator. Tapping navigates to `ChatDetailScreen`.
    *   **Empty State:** `"No messages yet."`
    *   **TabBar:** (See General UI Elements).
*   **`ChatDetailScreen` (Individual Chat):**
    *   **Header:** Brand Name.
    *   **Message Area:** Scrollable list of individual messages (sender/receiver bubbles, timestamps).
    *   **Input Field:** `"Type your message..."`
    *   **Button:** `"Send"`.

### 7. Settings Screen (`SettingsScreen`) - Generic for both roles
*   **Purpose:** Provides access to account settings, notifications, privacy, etc.
*   **Key Elements:**
    *   **Navigation:** `BackButton`.
    *   **Header:** `"Settings"`.
    *   **List of Options:**
        *   `"Account Information"` (Edit email, password - navigates to respective sub-screens).
        *   `"Payout Information"` (Clipper only - setup/manage Stripe Connect, view details).
        *   `"Payment Methods"` (Brand only - setup/manage payment sources).
        *   `"Notification Preferences"`.
        *   `"Privacy Settings"`.
        *   `"Help & Support"`.
        *   `"Terms of Service"`.
        *   `"Privacy Policy"`.
        *   **Button:** `"Logout"`.

## III. Main Brand Screens (Adapted/Implied)

### 1. Brand Dashboard Screen (`BrandDashboardScreen`)
*   **Purpose:** Main landing screen for Brands. Overview of their campaigns and key stats.
*   **Key Elements:**
    *   **Header:** `"Brand Dashboard"` or `"Welcome, [BrandName]!"`.
    *   **Profile Icon/Button:** Navigates to `BrandProfileScreen`.
    *   **Quick Stats Section:**
        *   `StatBox`: "Active Campaigns" ([Count]).
        *   `StatBox`: "Total Views Generated" ([Sum]).
        *   `StatBox`: "Total Spend" ([Sum]).
    *   **Button:** `"Create New Campaign"` (Navigates to `BrandCampaignCreationScreen`).
    *   **Section: Active Campaigns:**
        *   **List:** Scrollable list of their active `CampaignListItem_Brand` components.
            *   **`CampaignListItem_Brand`:** Campaign Title, Submissions Count, Views Generated, Current Spend. Tapping navigates to `BrandViewSubmissionsScreen`.
        *   **Empty State:** If no active campaigns.
    *   **Link/Button:** `"View Past Campaigns"`.
    *   **TabBar:** (See General UI Elements, adapted for Brand).

### 2. Campaign Creation Screen (Brand) (`BrandCampaignCreationScreen`)
*   **Purpose:** Allows Brands to create new campaigns by providing all necessary details.
    > **Design Goal:** This screen should strongly adhere to the "One-Click-Solution" philosophy, making campaign posting as simple and quick as possible.
*   **Key Elements (Similar to Clipper's `SubmitEditedContentScreen` form but for campaign setup):**
    *   **Navigation:** `BackButton`.
    *   **Header:** `"Create New Campaign"`.
    *   **Form:**
        *   `Input Field`: Campaign Title.
        *   `File Upload`/`Link Input`: Raw Footage/Assets.
        *   `Text Area`: Simple Brief / Key Message.
        *   `Tag Input`: Desired Style/Keywords.
        *   `Multi-Select`: Target Platforms.
        *   `Section`: Budget Allocation (Amount per X views, Max budget).
        *   **Button:** `"Launch Campaign"`.
        *   **Button:** `"Save as Draft"`.

### 3. View Submitted Clips Screen (Brand) (`BrandViewSubmissionsScreen`)
*   **Purpose:** Allows Brands to review content submitted by Clippers for a specific campaign.
*   **Key Elements:**
    *   **Navigation:** `BackButton`.
    *   **Header:** `"Submissions for: [CampaignName]"`.
    *   **Filter/Sort Controls:** Status (Pending, Approved, Needs Revision), Date, Views.
    *   **List:** Scrollable list of `SubmittedClipListItem_Brand` components.
        *   **`SubmittedClipListItem_Brand`:** Clipper Name/Icon, Thumbnail of video, Submission Date, View Count (and status: pending verification, verified), Link to live posts.
        *   **Inline Video Player:** Tapping thumbnail plays the video.
        *   **Action Buttons:** `"Approve"`, `"Request Revision"` (with a field for comments), `"View Details"`.
    *   **Empty State:** If no submissions yet.

## IV. General UI Elements (Used across multiple screens)

*   **TabBar:** Standard bottom navigation bar for main sections.
    *   **Clipper:** Browse, My Work, Messages, Profile.
    *   **Brand:** Dashboard, Campaigns (or Create), Messages, Profile.
    *   Each tab has an icon and label, highlights active tab.
*   **BackButton:** Typically in the header to navigate to the previous screen.
*   **ProfileButton/Icon:** Usually in the header, navigates to the user's profile screen.
*   **ListItem Components:** Reusable components for displaying items in lists (e.g., campaigns, submissions, messages). Structure varies by context but generally includes titles, subtitles, icons/thumbnails, and action buttons.
*   **EmptyState Components:** Displayed when lists are empty, providing context and often a call-to-action.
*   **StatBox Components:** Small cards or sections displaying a label and a key metric value.
*   **Form Elements:** Standardized `TextInputs`, `TextAreas`, `Checkboxes`, `RadioGroups`, `FileUploads`, `Buttons`.
*   **Notifications/Alerts:** Pop-ups or banners for success messages, errors, or important information. (e.g., "OTP Sent", "Campaign Launched Successfully", "Network Error").
    > **User Feedback:** Clear and timely notifications are key for a good UX, e.g., "OTP Sent," "Campaign Approved."
*   **Loaders/Spinners:** Indicate background activity or data loading.
*   **Progress Bars:** For file uploads or other long-running tasks.
*   **Headers:** Standard screen headers with titles and navigation elements.
*   **Modals/Dialogs:** For confirmations (e.g., "Are you sure you want to delete?"), quick input, or displaying additional information without navigating away.
